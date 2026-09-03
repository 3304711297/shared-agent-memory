---
name: readme-master
description: Analyze project structure and generate comprehensive, production-grade, highly engaging README.md files with architecture diagrams, badges, quickstart guides, and feature showcases. Trigger whenever the user asks to write, improve, optimize, or generate a README for a repository or project.
---

# README Master Skill

Use this skill to automatically audit a software project and generate or polish its `README.md` to top-tier open-source standards (GitHub Awesome style).

## Standard README Structure

When generating a README, analyze the codebase and structure the document into the following sections:

1. **Header & Title**
   - Project Name with clear icon/emoji.
   - One-sentence pitch: Clear, punchy description of what the project solves and who it is for.
   - Badges bar (CI status, Release version, License, Platform/Language, Stars).

2. **Key Features & Highlights (✨ Features)**
   - Bullet points with bold titles describing the most valuable capabilities.
   - Use comparison tables or feature matrices where applicable.

3. **Architecture & Workflow (📐 Architecture)**
   - Include a Mermaid diagram illustrating the data flow, module breakdown, or system architecture.

4. **Quick Start & Installation (🚀 Quick Start)**
   - Prerequisites (Node.js / Python / Go / Rust version, OS requirements).
   - Step-by-step commands (Clone -> Install dependencies -> Configure environment -> Run/Build).
   - Minimal working example code snippet with expected output.

5. **Configuration & Environment Variables (⚙️ Configuration)**
   - Table detailing key configuration options, defaults, and descriptions.

6. **Project Structure (📂 Project Structure)**
   - Clean, annotated directory tree highlighting key modules and entry points.

7. **Roadmap & Contributing (🛣️ Roadmap & 🤝 Contributing)**
   - Checkbox-style roadmap of completed and upcoming milestones.
   - Contribution guidelines and pull request flow.

8. **License & Acknowledgements (📄 License)**
   - Open source license type and credits to underlying libraries.

## Guidelines
- Write in the user's preferred language (Chinese or English, or bilingual header).
- Ensure all command examples are copy-paste ready and syntax-highlighted.
