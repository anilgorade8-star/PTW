# Antigravity: 3 Essential Skills

*The practical setup guide for AI-assisted web development*

1. **Get Shit Done**
2. **Ralph Loop**
3. **CodeRabbit**

**Inside:** official links • installation • setup • first workflow • useful commands

---

## 01. Get Shit Done

*Break big projects into clear, manageable work.*

### What it does

GSD helps turn a large development goal into structured phases and smaller tasks so an AI coding agent has clearer context and a more reliable workflow.

### Official project link

[github.com/toonight/get-shit-done-for-antigravity](https://github.com/toonight/get-shit-done-for-antigravity)

### Install on Windows / PowerShell

Open PowerShell inside your project folder and run:

```powershell
cd your-project
git clone https://github.com/toonight/get-shit-done-for-antigravity.git gsd-template
Copy-Item -Recurse gsd-template\.agent .\
Copy-Item -Recurse gsd-template\.agents .\
Copy-Item -Recurse gsd-template\.gemini .\
Copy-Item -Recurse gsd-template\.gsd .\
Copy-Item -Recurse gsd-template\adapters .\
Copy-Item -Recurse gsd-template\docs .\
Copy-Item -Recurse gsd-template\scripts .\
Copy-Item -Force gsd-template\PROJECT_RULES.md .\
Copy-Item -Force gsd-template\GSD-STYLE.md .\
Copy-Item -Force gsd-template\model_capabilities.yaml .\
Remove-Item -Recurse -Force gsd-template
```

### Start your first project

Open the project in Antigravity and run `/new-project`. Define the goal, requirements, and project context when prompted.

**Useful workflow:**

```
/new-project → /discuss-phase → /plan → /execute → /verify
```

> **Tip:** Keep each phase small enough that you can review the generated changes before moving forward.

---

## 02. Ralph Loop

*Let an agent repeatedly work through defined tasks.*

### What it does

Ralph-style workflows repeatedly run an AI agent against a task list or PRD, using project state and progress files to continue the work between iterations.

### Antigravity project link

[github.com/abhishekbhakat/ralph-loop-for-antigravity](https://github.com/abhishekbhakat/ralph-loop-for-antigravity)

### Installation / setup

1. Install the Ralph Loop VS Code extension using the project's published VSIX/install method.
2. Open your project in VS Code or Antigravity.
3. Prepare a PRD/task file with small, clearly defined tasks.
4. Open the Ralph Loop panel from the Activity Bar.
5. Select the task file, progress file, model/mode, and iteration limit.
6. Start the loop and review the generated changes.

### How to write better tasks

Instead of "Build my website," use a task such as: "Create the hero section, make it responsive, run the build, and fix any build errors." Small tasks give the agent a clearer definition of done.

### Alternative Ralph CLI

[github.com/iannuttall/ralph](https://github.com/iannuttall/ralph)

```bash
npm i -g @iannuttall/ralph
ralph prd
ralph build 1
```

This CLI is a separate Ralph implementation. Use it only if its workflow matches your project.

---

## 03. CodeRabbit

*Catch bugs and code-quality issues earlier.*

### What it does

CodeRabbit reviews code and can help identify bugs, security concerns, and quality issues. It supports pull-request workflows and coding-agent integrations.

### Official links

- [coderabbit.ai](https://coderabbit.ai)
- [github.com/coderabbitai/skills](https://github.com/coderabbitai/skills)
- [docs.coderabbit.ai/cli](https://docs.coderabbit.ai/cli)

### Antigravity CLI plugin

```bash
agy plugin install https://github.com/coderabbitai/skills
agy plugin list
```

The CodeRabbit skills repository documents this Antigravity CLI installation route.

### Skills installer route

You can also use the skills installer documented by the repository:

```bash
npx skills add coderabbitai/skills
```

### CLI review examples

```bash
coderabbit --version
coderabbit review --agent --uncommitted
coderabbit review --agent --base main
coderabbit review --agent --dir path/to/directory
```

> **Security reminder:** Never intentionally send API keys, passwords, private tokens, or other secrets for review.

---

## The 3-Skill Workflow

Use them together instead of treating them as three unrelated tools.

| Step | Phase | Tool | Purpose |
|------|-------|------|---------|
| 01 | **Plan** | Get Shit Done | Break the big idea into phases and tasks. |
| 02 | **Build** | Ralph Loop | Iterate through prepared tasks with less manual intervention. |
| 03 | **Review** | CodeRabbit | Review changes and surface bugs and quality issues. |

---

## Quick Checklist

- [ ] Antigravity opens your project correctly.
- [ ] GSD is installed and `/new-project` works.
- [ ] Your 3D website idea is split into small tasks.
- [ ] Ralph Loop has a task/PRD file and a sensible iteration limit.
- [ ] CodeRabbit is installed/authenticated.
- [ ] You review AI-generated changes before shipping.

---

## Start Here

Save this guide. Open the official links above, install one skill at a time, and test it on a small project before using it on a large production site.

*Project instructions can change over time, so follow the latest README/docs if a command has been updated.*
