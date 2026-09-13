## Regression Test Template

Drop this into `tests/` and run via `terminal('pytest tests/test_api_smoke.py -v')`:

```python
import os, requests, pytest

BASE_URL = os.environ.get("API_BASE_URL", "https://api.example.com")
TOKEN    = os.environ.get("API_TOKEN", "")
HEADERS  = {"Authorization": f"Bearer {TOKEN}"}

class TestAPISmoke:
    def test_health(self):
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        assert resp.status_code == 200

    def test_list_users_returns_array(self):
        resp = requests.get(f"{BASE_URL}/users", headers=HEADERS, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data.get("data", data), list)

    def test_get_user_required_fields(self):
        resp = requests.get(f"{BASE_URL}/users/1", headers=HEADERS, timeout=10)
        assert resp.status_code in (200, 404)
        if resp.status_code == 200:
            user = resp.json()
            assert "id" in user and "email" in user

    def test_invalid_auth_returns_401(self):
        resp = requests.get(
            f"{BASE_URL}/users",
            headers={"Authorization": "Bearer invalid-token"},
            timeout=10,
        )
        assert resp.status_code == 401
```

## Security

### Token handling
- Never log full tokens. Redact: `Bearer <REDACTED>`.
- Never hardcode tokens in scripts. Read from env (`os.environ["API_TOKEN"]`) or `${HERMES_HOME:-~/.hermes}/.env`.
- Rotate immediately if a token surfaces in logs, error messages, or git history.

### Safe logging

```python
def redact_auth(headers: dict) -> dict:
    sensitive = {"authorization", "x-api-key", "cookie", "set-cookie"}
    return {k: ("<REDACTED>" if k.lower() in sensitive else v) for k, v in headers.items()}
```

### Leak checklist

- [ ] **Credentials in URLs.** API keys in query strings end up in server logs, browser history, referrer headers — use headers.
- [ ] **PII in error responses.** `404 on /users/123` shouldn't reveal whether the user exists (enumeration).
- [ ] **Stack traces in prod.** 500s shouldn't leak file paths, framework versions.
- [ ] **Internal hostnames/IPs.** `10.x.x.x`, `internal-api.corp.local` in error bodies.
- [ ] **Tokens echoed back.** Some APIs include the auth token in error details. Verify they don't.
- [ ] **Verbose `Server` / `X-Powered-By`.** Stack-info leaks. Note for security review.
