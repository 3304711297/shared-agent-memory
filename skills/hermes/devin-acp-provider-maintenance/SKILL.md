---
name: devin-acp-provider-maintenance
description: "改 hermes-devin-acp 插件/模型选择报错时必用。ACP session 才是模型真源。"
---

# Maintaining the Hermes Devin ACP provider

Repo: `D:/ai coding/GitRepos/hermes-devin-acp` (single plugin file
`plugins/model-providers/devin-acp/__init__.py` + `tests/`).

## The authority rule that drives every design decision

`session/new`'s `configOptions` model option is the ONLY thing
`session/set_config_option` will accept. `devin models list` is an
account-global catalog and routinely returns ~44 models while a real session
advertises one (e.g. `swe-1-6-slow`).

Consequence: never expose CLI-catalog entries in the picker unless the session
advertised no model option at all, and never raise on an unadvertised choice —
resolve (exact -> dotted-id normalization -> family-token match in Devin's own
advertised order -> session default) and return the value actually sent.

Only the bare `swe` alias reliably resolves across accounts; `adaptive`, `gpt`,
`opus`, `sonnet` were all measured failing on an SWE-only account. Keep
`fallback_models=("swe",)`.

## Test-isolation trap (burns real quota if missed)

`DevinACPProfile.fetch_models()` calls
`hermes_cli.auth.resolve_external_process_provider_credentials`, which on a
developer machine returns the REAL authenticated `devin.EXE` path. Any test that
touches `fetch_models()` without stubbing it will spawn the real CLI.

Install the stub globally in `tests/conftest.py` (fake `providers`,
`hermes_cli.auth`, `hermes_cli._subprocess_compat`, `tools.environments.local`)
and import the plugin through a shared cached loader (`tests/_plugin_loader.py`),
so no test can ever resolve real credentials. A test that sees `fetch_models()`
returning `None` is the tell that stubbing was missed.

## Windows pitfalls

- `shlex.split(raw, posix=True)` mangles Windows paths — `"D:\ai coding\..."`
  splits at the spaces and loses backslashes. If a test passes a path via
  `HERMES_DEVIN_ACP_ARGS`, expect garbage; pass `command=` / `args=[...]`
  explicitly instead.
- Forward-slash native paths (`D:/...`) for native programs; `$LOCALAPPDATA/Temp`
  over `/tmp` for scratch files a native binary must read.
- CJK commit messages: set `PYTHONIOENCODING=utf-8`.

## Non-determinism to watch for

`set` iteration order varies with `PYTHONHASHSEED` (measured: the same session
sent 3 different models across 5 seeds). Any "pick one from a set" logic must be
replaced by an explicit order — prefer the order the remote advertises, since
the first advertised family entry is the upstream default.

## Verification loop

```bash
cd "D:/ai coding/GitRepos/hermes-devin-acp"
PYTHONIOENCODING=utf-8 python -m pytest tests/ -q      # needs a python WITH pytest
PYTHONIOENCODING=utf-8 python tests/run_integration.py  # prints "integration OK"
```

The ambient `python` (Hermes venv 3.11) has NO pytest; the machine's
`Python314` (`/c/Users/.../Programs/Python/Python314/python`) does. Pick one that
can import pytest, and report which interpreter you used.

Prove a fix by temporarily restoring the old implementation and watching the new
tests fail (`git show HEAD:<path> > <path>` then re-run, then restore) — that is
the RED evidence for a bug fix retrofitted onto existing code.

## Env seams

`HERMES_DEVIN_ACP_COMMAND`, `HERMES_DEVIN_ACP_ARGS`,
`HERMES_DEVIN_ACP_MODE`, `HERMES_DEVIN_ACP_WINDSURF_VERSION`.
`tests/fake_devin_acp.py` doubles as both the fake ACP server and a fake
`models list` CLI (env: `FAKE_DEVIN_MODEL_OPTIONS`, `FAKE_DEVIN_CATALOG`,
`FAKE_DEVIN_FAIL_SESSION`).
