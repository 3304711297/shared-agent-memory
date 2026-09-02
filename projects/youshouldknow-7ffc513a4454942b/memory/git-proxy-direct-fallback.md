---
name: git-proxy-direct-fallback
description: youshouldknow repo uses a local proxy for git push; fall back to
  direct push when the proxy is down
metadata:
  node_type: memory
  type: project
  originSessionId: sess_7ad7ae87-25fb-45bb-916e-807424ab1e84
---

The [[youshouldknow-repo]] has a repo-local git proxy `http.proxy=http://127.0.0.1:3067`. When a push fails with "Failed to connect to github.com ... via 127.0.0.1", the proxy is likely not listening. Check with `curl -x http://127.0.0.1:3067 ...` / `netstat -an | grep 3067`.

If the port isn't listening, push directly without the proxy — it works: `git -c http.proxy= -c https.proxy= push`. (For direct HTTPS fetches use `curl -x`; the WebFetch tool uses no proxy and fails on some sites.)
