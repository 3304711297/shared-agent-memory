"""Persistent CDP client for Edge Dev remote debugging (fixed UUID from DevToolsActivePort).

Usage:
  python cdp_live.py targets                 # list targets
  python cdp_live.py eval <file.js>          # eval JS file in SW context (auto-wake)
  python cdp_live.py check-register          # verify scriptcat registration state
  python cdp_live.py fix-register            # re-register scriptcat-scripting content script
"""
import json
import sys
import threading
import time

import websocket

USER_DATA = r"C:\Users\VOS-User\AppData\Local\Microsoft\Edge Dev\User Data"


def browser_ws_url():
    with open(USER_DATA + r"\DevToolsActivePort", "r", encoding="utf-8") as f:
        port, path = f.read().splitlines()
    return f"ws://127.0.0.1:{port}{path}"


class CDP:
    def __init__(self, timeout=30):
        self.timeout = timeout
        last_err = None
        for _ in range(6):
            try:
                self.ws = websocket.create_connection(
                    browser_ws_url(), timeout=timeout, suppress_origin=True)
                break
            except Exception as e:
                last_err = e
                time.sleep(2)
        else:
            raise last_err
        self.id = 0
        self.lock = threading.Lock()
        self.pending = {}
        self.events = []
        self.ev_cond = threading.Condition(self.lock)
        self._run = True
        threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        while self._run:
            try:
                data = json.loads(self.ws.recv())
            except Exception:
                break
            with self.ev_cond:
                if "id" in data:
                    ev = self.pending.pop(data["id"], None)
                    if ev is not None:
                        ev.append(data)
                        self.ev_cond.notify_all()
                else:
                    self.events.append(data)
                    self.ev_cond.notify_all()

    def send(self, method, session_id=None, timeout=None, **params):
        with self.lock:
            self.id += 1
            mid = self.id
            msg = {"id": mid, "method": method, "params": params}
            if session_id:
                msg["sessionId"] = session_id
            ev = self.pending[mid] = []
            self.ws.send(json.dumps(msg))
            ok = self.ev_cond.wait_for(
                lambda: len(ev) > 0, timeout or self.timeout)
            if not ok:
                self.pending.pop(mid, None)
                raise TimeoutError(f"{method} timed out")
            data = ev[0]
        if "error" in data:
            raise RuntimeError(f"{method}: {data['error']}")
        return data.get("result", {})

    def close(self):
        self._run = False
        try:
            self.ws.close()
        except Exception:
            pass


def find_target(cdp, needle):
    r = cdp.send("Target.getTargets")
    for t in r.get("targetInfos", []):
        if needle in t.get("url", "") or needle in (t.get("title") or ""):
            return t
    return None


def sw_session(cdp):
    """Attach to ScriptCat service worker, waking it if asleep."""
    for attempt in range(3):
        t = find_target(cdp, "service_worker.js")
        if t:
            r = cdp.send("Target.attachToTarget",
                         targetId=t["targetId"], flatten=True)
            return r["sessionId"], t
        # wake: open options page via a new tab then close it
        r = cdp.send("Target.createTarget",
                     url="chrome-extension://liilgpjgabokdklappibcjfablkpcekh/src/options.html")
        time.sleep(3)
        cdp.send("Target.closeTarget", targetId=r["targetId"])
    raise RuntimeError("ScriptCat service worker target not found")


CHECK_JS = r"""
(async () => {
  const us = await chrome.userScripts.getScripts();
  let cs = null, csErr = null;
  try { cs = await chrome.scripting.getRegisteredContentScripts(); }
  catch (e) { csErr = e.message; }
  return {
    userScriptsCount: us.length,
    userScriptIds: us.map(s => s.id.slice(0, 12)),
    injectRegistered: us.some(s => s.id === 'scriptcat-inject'),
    contentRegistered: us.some(s => s.id === 'scriptcat-content'),
    scriptingInContentScripts: (cs || []).some(c => c.id === 'scriptcat-scripting'),
    contentScripts: (cs || []).map(c => c.id),
    csErr
  };
})()
"""

FIX_JS = r"""
(async () => {
  const cs = await chrome.scripting.getRegisteredContentScripts();
  if (cs.some(c => c.id === 'scriptcat-scripting')) {
    return { status: 'already-registered' };
  }
  await chrome.scripting.registerContentScripts([{
    id: 'scriptcat-scripting',
    js: ['/src/scripting.js'],
    matches: ['<all_urls>'],
    allFrames: true,
    runAt: 'document_start',
    persistAcrossSessions: true
  }]);
  const after = await chrome.scripting.getRegisteredContentScripts();
  return { status: 'registered', now: after.map(c => c.id) };
})()
"""


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check-register"
    cdp = CDP()
    try:
        if cmd == "targets":
            r = cdp.send("Target.getTargets")
            for t in r.get("targetInfos", []):
                print(t["targetId"][:12], t["type"], t["url"][:70])
        elif cmd in ("check-register", "fix-register"):
            sid, t = sw_session(cdp)
            js = CHECK_JS if cmd == "check-register" else FIX_JS
            r = cdp.send("Runtime.evaluate", session_id=sid,
                         expression=js, awaitPromise=True, returnByValue=True)
            if "exceptionDetails" in r:
                ed = r["exceptionDetails"]
                print("EXCEPTION:", ed.get("exception", {}).get("description") or ed.get("text"))
            else:
                print(json.dumps(r["result"]["value"], indent=2, ensure_ascii=False))
        else:
            print("unknown command:", cmd)
    finally:
        cdp.close()


if __name__ == "__main__":
    main()
