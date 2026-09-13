## 10. Native Tool Prioritization & Tool Call Efficiency (User Rule)
The user strictly enforces tool execution efficiency and minimal round-trip overhead:
- **Direct Native Tools First**: Always use specialized Hermes native tools directly:
  - File reading: `read_file` (built-in line numbers & pagination; never `python open().read()`).
  - Targeted edits: `patch` (fuzzy matching, AST validation, unified diffs; never full-file python rewrites that destroy indentation/formatting).
  - Search & inspection: `search_files` (ripgrep-backed content/filename search; never custom `python os.walk`).
- **Python Invocation Boundary**: Reserve `python -c` or execution scripts strictly for complex multi-step batch logic that genuinely requires code execution (e.g. process tree auditing, cryptographic/Wbi signing algorithms, SQLite database analysis, cross-store reconciliation).
- **config.yaml Security Exception**: Hermes core prevents `patch`/`write_file` edits on its own `config.yaml` as a security-sensitive guard. For this file specifically, use `python` with `ruamel.yaml` (`preserve_quotes=True`) to maintain structural fidelity without clobbering formatting.
