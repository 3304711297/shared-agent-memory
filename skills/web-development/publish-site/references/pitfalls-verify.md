## Pitfalls

- **SPA routes 404 on GitHub Pages.** Pages has no rewrite rules. Copy `index.html` to `404.html` in the output dir (`cp dist/index.html dist/404.html`) so client-side routing recovers. Cloudflare Pages and Netlify handle SPAs via `_redirects` (`/* /index.html 200`).
- **GitHub Pages build lag.** The site can take 1–10 minutes to appear after the first enable, and ~1 minute per subsequent push. Don't declare failure on the first 404 — poll `curl` a few times before investigating.
- **Case-sensitive paths.** Pages hosts are case-sensitive Linux; a site that worked on macOS/Windows can 404 on assets referenced as `Logo.PNG` but committed as `logo.png`. Grep the HTML for mismatched casing when an asset 404s.
- **Project-page base path.** `https://<owner>.github.io/<name>/` serves under `/<name>/` — absolute asset URLs like `/app.js` break. Use relative paths or set the build tool's base (`vite build --base=/<name>/`).
- **`wrangler` auth flow needs a browser.** `wrangler login` opens OAuth; in a headless session prefer `CLOUDFLARE_API_TOKEN` (user creates it at dash.cloudflare.com → API Tokens) and never echo the token into logs.
- **DNS propagation on custom domains.** New CNAMEs can take minutes to hours. Verify against the provider's default URL (`*.pages.dev`, `*.netlify.app`, `*.github.io`) first, then check the custom domain separately — don't conflate the two failures.
- **Deploying source instead of build output.** Publishing the repo root when the real site lives in `dist/` yields a directory listing or raw JSX. Always confirm the output dir contains an `index.html`.

## Verification

Do NOT report success from the deploy log alone. Before telling the user anything:

1. `curl -sS -o /dev/null -w '%{http_code}' <live-url>` returns `200` (retry over ~2 minutes for a first GitHub Pages deploy).
2. `curl -sS <live-url> | head -30` shows the expected `index.html` content — optionally confirm markup with `web_extract` on the live URL.
3. For SPAs, also curl one deep route (e.g. `/about`) and confirm it returns `200`, not `404`.
4. `git tag --list 'deploy-*'` shows the tag for this deploy.

Then report the live URL to the user, along with the deploy tag they can roll back to.
