## 8. Hermes Native Bot Mode & Multi-Profile Orchestration
When orchestrating internal specialized bots (profiles under `~/.hermes/profiles/<name>/`) alongside the default agent:
- **CLI Creation Pattern**: Always use `hermes profile create --clone-from default <name> --description "<role description>"` to inherit current gateway endpoints, `.env` API keys, and essential baseline configurations.
- **Shared Memory Junction (CRITICAL)**: Newly created profiles instantiate an isolated `memories/` directory. To prevent memory fragmentation and state divergence, immediately establish an NTFS Directory Junction pointing `memories/topics` directly to the shared memory single physical source of truth:
  ```cmd
  cmd.exe /c "mklink /J \"%LOCALAPPDATA%\hermes\profiles\<name>\memories\topics\" \"D:\ai coding\GitRepos\shared-agent-memory\projects\default-135ef1b9f66d8a7e\memory\""
  ```
- **Specialized SOUL.md Contracts**: Replace the default prompt in `profiles/<name>/SOUL.md` with explicit role boundaries: Identity, Mandates & Rules, Cross-Bot Handoffs (@mentions / Agent Inbox protocols), and Shared Memory Protocols.
- **In-Session Handoffs**: Use `@<bot-name>` in conversation turns for synchronous task handoffs, or rely on Agent Inbox for asynchronous batch deliveries.
