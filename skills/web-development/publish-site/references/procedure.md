## Procedure

### 1. Build and preview locally

Build if needed (`npm run build`, etc.) and identify the output directory. Serve it:

```bash
python3 -m http.server 8080 --directory dist
```

For a shareable preview link (user on another machine, or you want their sign-off before going live), open a quick tunnel in a background `terminal` session:

```bash
cloudflared tunnel --url http://localhost:8080
```

Give the user the `https://*.trycloudflare.com` URL and get sign-off before deploying. Kill the tunnel afterwards.

### 2. Version before deploy — no exceptions

Every deploy must come from a git commit, so every deploy is reproducible and rollback is trivial.

```bash
git init 2>/dev/null; git add -A
git commit -m "deploy: <short description>"
git tag "deploy-$(date +%Y%m%d-%H%M)"
```

If the project already has a repo, just commit + tag. Never deploy uncommitted files.

### 3. Deploy — provider ladder

**Rung 1 — GitHub Pages (default: free, zero extra accounts if `gh` is authed):**

```bash
gh repo create <name> --public --source . --push   # skip if repo exists
git subtree push --prefix dist origin gh-pages      # publish build output
gh api "repos/{owner}/<name>/pages" -X POST \
  -f 'source[branch]=gh-pages' -f 'source[path]=/'  # first time only
```

Site appears at `https://<owner>.github.io/<name>/`. If the site is the repo root (no build dir), push `main` and set Pages source to `main` instead of using subtree. For build-step projects that will redeploy often, prefer the official `actions/deploy-pages` workflow so pushes auto-publish.

**Rung 2 — Cloudflare Pages (when the user wants a custom domain, redirects/headers, or Functions):**

```bash
npx wrangler@latest pages deploy dist --project-name <name>
```

First run creates the project and prints the `https://<name>.pages.dev` URL. Custom domains attach via the Cloudflare dashboard (Pages → project → Custom domains).

**Rung 3 — Netlify (fallback, or when the user already lives there):**

```bash
netlify deploy --prod --dir dist
```

`netlify deploy --dir dist` (no `--prod`) gives a draft URL — useful as a second preview stage.

### 4. Rollback

Rollback = redeploy a previous tag. Never hand-edit live output.

```bash
git checkout deploy-<previous> -- .   # or: git checkout deploy-<previous>; rebuild
# then rerun the same deploy command from step 3
```

Cloudflare Pages and Netlify also keep per-deploy history in their dashboards ("Rollback to this deploy"), which is faster when the CLI isn't handy.

### 5. Secrets and environment variables

- **NEVER commit secrets, API keys, or `.env` files** — they'd be public on Pages hosting. Check with `git status` before the first commit and keep `.env*` in `.gitignore`.
- Runtime env vars belong in the provider's dashboard: Cloudflare Pages → Settings → Environment variables; Netlify → Site settings → Environment variables. GitHub Pages is static-only — no server env; anything embedded in the bundle is public by definition. Warn the user if their build inlines a key.
