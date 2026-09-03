---
name: semantic-release-pro
description: Automate conventional git commit messages, calculate semantic version bumps (SemVer), and generate clean GitHub release notes and CHANGELOG entries from commit history. Trigger whenever the user asks to commit changes, draft a release, generate a changelog, or bump version.
---

# Semantic Release Pro Skill

Use this skill to automate conventional commit messages, manage Semantic Versioning (SemVer), and compile structured CHANGELOGs.

## 1. Conventional Commits Standard

Format: `<type>(<scope>): <short description>`

### Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, whitespace changes
- `refactor`: Code restructuring without fixing a bug or adding a feature
- `perf`: Code change that improves performance
- `test`: Adding or correcting existing tests
- `chore`: Build process, dependencies, tooling changes
- `ci`: CI/CD workflow configuration updates

### Scope & Description
- Scope should reflect the module, component, or category (e.g., `docs(AI工具): ...`, `feat(auth): ...`).
- If user prefers Chinese commits, write concise Chinese descriptions without trailing periods.

## 2. SemVer Version Bump Calculation

- **MAJOR (`x.0.0`)**: Breaking changes (denoted by `BREAKING CHANGE:` in body or `!` after type, e.g. `feat!: ...`).
- **MINOR (`0.x.0`)**: Backwards-compatible new features (`feat(...)`).
- **PATCH (`0.0.x`)**: Backwards-compatible bug fixes and small improvements (`fix(...)`, `docs(...)`, `perf(...)`).

## 3. Automated Changelog Compilation

When generating Release Notes or CHANGELOG entries from Git history:
1. Group commits logically:
   - 🚀 Features (`feat`)
   - 🐛 Bug Fixes (`fix`)
   - ⚡ Performance Improvements (`perf`)
   - 📖 Documentation (`docs`)
   - 🔧 Maintenance & Refactor (`refactor`, `chore`, `ci`)
2. Include compare link between previous tag and current release tag.
