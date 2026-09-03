# Local Custom Provider & Desktop GUI Registration

When exposing a local model proxy/bridge (e.g. `codebuddy2openai`, `antigravity`, `ollama`, or local adapters) to Hermes Desktop and CLI, follow these steps to ensure full visibility across the GUI dropdown and slash commands.

## 1. Local Adapter Execution
- Ensure the local proxy is listening on `127.0.0.1:<PORT>/v1` (e.g., `8787` for CodeBuddy/WorkBuddy, `18080` for Antigravity).
- Test endpoints with `curl http://127.0.0.1:<PORT>/health` and `curl http://127.0.0.1:<PORT>/v1/models`.

## 2. Register Credential in Hermes Auth
Use non-interactive `hermes auth add` with both `--api-key` and `--label` flags (omitting `--label` triggers interactive stdin prompt and raises `EOFError` in headless subshells):
```bash
hermes auth add "custom:<name>-(127.0.0.1:<PORT>)" --api-key "local" --label "<Label>"
```

## 3. Register in `custom_providers` (for Desktop GUI Picker)
Add to `~/.hermes/config.yaml` under `custom_providers`:
```yaml
custom_providers:
  - name: <Display Name> (127.0.0.1:<PORT>)
    base_url: http://127.0.0.1:<PORT>/v1
    api_key: local
    model: auto
    models:
      auto: {}
      glm-5.2: {}
      kimi-k2.7: {}
      deepseek-v4-pro: {}
    models_discovered: true
```

## 4. Update Model Picker Cache
Hermes Desktop GUI populates the dropdown from `~/.hermes/provider_models_cache.json`. Update or insert the cache entry:
```json
{
  "custom:http://127.0.0.1:<PORT>/v1": {
    "fp": "<cache_id>",
    "at": 1788431000.0,
    "models": ["auto", "glm-5.2", "kimi-k2.7", "deepseek-v4-pro"]
  }
}
```

## 5. Configure CLI Model Aliases (Optional)
In `~/.hermes/config.yaml`:
```yaml
model_aliases:
  <alias>:
    model: <model_name>
    provider: custom
    base_url: http://127.0.0.1:<PORT>/v1
```
## 6. WorkBuddy / CodeBuddy Specific Model Names & Upstream Mapping
When bridging Tencent CodeBuddy/WorkBuddy via `codebuddy2openai` (`8787`), the upstream backend (`copilot.tencent.com/v2/chat/completions`) recognizes specific model identifiers (extracted and verified from `product.json` & live tests):
- **Hunyuan**: `hy4-preview` (backend ID; map `hy4` -> `hy4-preview`), `hy3-preview-agent` (backend ID; map `hy3` / `hy3-preview` -> `hy3-preview-agent`).
- **GLM**: `glm-5.3`, `glm-5.3-flash`, `glm-5.2`, `glm-5.1`, `glm-5v-turbo` (`glm-5.0` is retired upstream).
- **Kimi**: `kimi-k3-1` (map `kimi-k3` -> `kimi-k3-1`), `kimi-k2.7`, `kimi-k2.6`, `kimi-k2.5`.
- **DeepSeek**: `deepseek-v4-pro`, `deepseek-v4-flash`.
- **MiniMax**: `minimax-m3-pay` (map `minimax-m3` -> `minimax-m3-pay`).
- **Routing/Defaults**: `auto`, `default`.

Always implement a `MODEL_MAP` in `converter.py` before forwarding the request body to upstream `copilot.tencent.com/v2/chat/completions` so shorthand model names (`hy4`, `hy3`, `kimi-k3`, `minimax-m3`) route seamlessly without 400 errors.
