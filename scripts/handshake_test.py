"""Decisive experiments:
1. Identify ctx3 (chrome.runtime presence) -> ISOLATED (scripting.js) vs USER_SCRIPT (content.js)
2. Fake the broadcastEventFlag handshake from MAIN world, observe acks.
"""
import json
import time

from cdp import CDP

EXT = "liilgpjgabokdklappibcjfablkpcekh"
CH = "0be4e6a5-a95a-4982-ae64-eaed28361dfc"

cdp = CDP()


def find_target(pred):
    r = cdp.send("Target.getTargets")
    for t in r["targetInfos"]:
        if pred(t):
            return t["targetId"]
    return None


page_tid = find_target(lambda t: t["type"] == "page" and t["url"].startswith("https://openrouter.ai/models"))
r = cdp.send("Target.attachToTarget", targetId=page_tid, flatten=True)
sid = r["sessionId"]
cdp.send("Runtime.enable", session_id=sid)

evs = cdp.wait_events("Runtime.executionContextCreated", n=20, timeout=2)
ctxs = [p["context"] for p in evs]
# also default ctx = 1 (main)
print("=== contexts ===")
for ctx in ctxs:
    aux = ctx.get("auxData", {})
    print(f"id={ctx['id']} name={ctx['name']!r} type={aux.get('type')}")

# --- Experiment 1: identify each non-main ctx ---
for ctx in ctxs:
    if ctx.get("auxData", {}).get("type") != "isolated":
        continue
    expr = ("JSON.stringify({hasChromeRuntime: typeof chrome !== 'undefined' && !!chrome.runtime, "
            "hasExtension: typeof chrome !== 'undefined' && !!chrome.extension})")
    r2 = cdp.send("Runtime.evaluate", session_id=sid, contextId=ctx["id"], expression=expr, returnByValue=True)
    print(f"ctx {ctx['id']} ({ctx['name']!r}) -> {r2.get('result', {}).get('value')}")

# --- Experiment 2: fake handshake broadcast from MAIN world ---
probe_js = """
(async () => {
  const CH = '%s';
  const seen = [];
  const flag = '-wdtest' + Math.floor(Math.random()*1e6).toString(36);
  const realListener = (e) => {
    let d = null;
    try { d = JSON.stringify(e.detail); } catch(err) { d = String(e.detail); }
    seen.push({ type: e.type.slice(0, 70), detail: (d||'').slice(0, 200) });
  };
  performance.addEventListener(CH, realListener);
  window.addEventListener(CH, realListener);
  // fake the broadcast that scripting.js would send
  performance.dispatchEvent(new CustomEvent(CH, {
    detail: {
      action: 'broadcastEventFlag',
      eventFlag: flag,
      extensionEnv: { inIncognitoContext: false, incognitoMode: 'span' }
    }
  }));
  await new Promise(r => setTimeout(r, 4000));
  performance.removeEventListener(CH, realListener);
  window.removeEventListener(CH, realListener);
  const injectFns = Object.keys(window).filter(k => k.startsWith('#'));
  const invokedMarker = injectFns.map(k => {
    try { return k + ':' + (typeof window[k]); } catch (e) { return k + ':?'; }
  });
  return JSON.stringify({ flag, seen, injectFns: invokedMarker });
})()
""" % CH

val = None
for ctx in ctxs:
    if ctx.get("auxData", {}).get("type") == "default":
        r3 = cdp.send("Runtime.evaluate", session_id=sid, contextId=ctx["id"],
                      expression=probe_js, awaitPromise=True, returnByValue=True)
        val = r3.get("result", {}).get("value")
        break
print("=== fake handshake result ===")
print(val)
cdp.close()
