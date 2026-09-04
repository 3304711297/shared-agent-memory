"""Fix: re-register the missing scriptcat-scripting content script.

Runs from the SW context:
1. Probe chrome.extension availability in ISOLATED world of the test tab
2. Re-register scriptcat-scripting via chrome.scripting.registerContentScripts
3. Verify getRegisteredContentScripts
"""
import json
import time

from cdp import CDP

EXT = "liilgpjgabokdklappibcjfablkpcekh"

cdp = CDP()


def find_target(pred):
    r = cdp.send("Target.getTargets")
    for t in r["targetInfos"]:
        if pred(t):
            return t["targetId"]
    return None


# wake SW
opts = find_target(lambda t: t["type"] == "page" and f"chrome-extension://{EXT}/src/options.html" in t["url"])
if not opts:
    r = cdp.send("Target.createTarget", url=f"chrome-extension://{EXT}/src/options.html")
    opts = r["targetId"]
    time.sleep(2)

sw_tid = None
for _ in range(20):
    sw_tid = find_target(lambda t: t["type"] == "service_worker" and EXT in t["url"])
    if sw_tid:
        break
    time.sleep(0.5)
if not sw_tid:
    raise SystemExit("SW did not wake")
print("SW:", sw_tid)

r = cdp.send("Target.attachToTarget", targetId=sw_tid, flatten=True)
sid = r["sessionId"]

# 1. probe chrome.extension in ISOLATED world (on a https tab)
tab_tid = find_target(lambda t: t["type"] == "page" and t["url"].startswith("https://openrouter.ai/models"))
probe_js = """
(async () => {
  const res = await chrome.scripting.executeScript({
    target: { tabId: %d },
    func: () => ({
      extType: typeof chrome.extension,
      hasInIncog: typeof chrome.extension !== 'undefined' && typeof chrome.extension.inIncognitoContext,
      runtimeType: typeof chrome.runtime
    }),
    world: 'ISOLATED'
  });
  return JSON.stringify(res && res[0] ? res[0].result : res);
})()
""" % 0  # placeholder replaced below

# get tabId via Target.getTargetInfo
ti = cdp.send("Target.getTargetInfo", targetId=tab_tid)
tab_id = ti["targetInfo"]["targetId"]
# chrome.tabs needs numeric tabId: use chrome.tabs.query to find url match
q = cdp.send("Runtime.evaluate", session_id=sid, expression="""
(async () => {
  const tabs = await chrome.tabs.query({url: 'https://openrouter.ai/models*'});
  return JSON.stringify(tabs.map(t => t.id));
})()
""", awaitPromise=True, returnByValue=True)
tab_ids = json.loads(q["result"]["value"])
print("tab ids:", tab_ids)
if not tab_ids:
    raise SystemExit("no tab found")
tab_id_num = tab_ids[0]

probe_js = probe_js.replace("%d", str(tab_id_num))
r1 = cdp.send("Runtime.evaluate", session_id=sid, expression=probe_js, awaitPromise=True, returnByValue=True)
print("ISOLATED world probe:", r1["result"].get("value"))

# 2. re-register scriptcat-scripting
reg_js = """
(async () => {
  try {
    const before = await chrome.scripting.getRegisteredContentScripts();
    const already = before.some(s => s.id === 'scriptcat-scripting');
    if (already) return JSON.stringify({status: 'already', before: before.map(s=>s.id)});
    await chrome.scripting.registerContentScripts([{
      id: 'scriptcat-scripting',
      js: ['/src/scripting.js'],
      matches: ['<all_urls>'],
      allFrames: true,
      runAt: 'document_start',
      persistAcrossSessions: true
    }]);
    const after = await chrome.scripting.getRegisteredContentScripts();
    return JSON.stringify({status: 'registered', after: after.map(s=>({id:s.id, js:s.js, matches:s.matches}))});
  } catch (e) {
    return JSON.stringify({status: 'error', error: String(e), msg: e.message});
  }
})()
"""
r2 = cdp.send("Runtime.evaluate", session_id=sid, expression=reg_js, awaitPromise=True, returnByValue=True)
print("register result:", r2["result"].get("value"))

cdp.close()
