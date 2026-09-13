### 1.1 Security Red-Flag Checklist (admission must-pass)

Every admission evaluation MUST run this mechanical checklist (methodology absorbed from the Hermes Atlas security-review: all 25★+ ecosystem repos screened). Inspect README, install scripts, and post-install hooks for:

1. **Obfuscated code** — minified/encoded blobs, string-encoded payloads, packed binaries without source.
2. **Credential harvesting** — secrets, tokens, cookies written to files or shipped to remote endpoints.
3. **Typosquatting** — repo/skill name closely mimics a known package or org.
4. **Supply-chain risk** — `curl | bash` installers, post-install scripts, unreviewed transitive deps, pinned-to-fork sources.
5. **Crypto mining / resource abuse** — miners, background daemons consuming CPU/GPU.
6. **Excessive permissions** — broad FS/network/exec beyond the stated purpose.

Verdict tiers: **PASS** / **WARN** (not malicious, but patterns needing caution — e.g. curl-pipe-bash installers, hardcoded dev credentials, 0.0.0.0 binds without auth, unauditable docs) / **REJECT**. WARN admissions must record "inspect `<script>` before running" in the inventory note and must never enter auto-install or auto-update paths.

---
