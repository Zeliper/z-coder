# Claude Code Agent Orchestration System

A universal multi-agent orchestration system for Claude Code. Enables parallel sub-agent spawning and coordination using Claude Code's background agent (Async Sub-agent) feature.

[한국어 문서](./README_KR.md)

## Features

- **Multi-Agent Orchestration**: Main agent coordinates multiple sub-agents in parallel
- **Project-Aware**: Auto-detects project type and generates custom agents
- **Easy Updates**: Git Submodule-based update system preserves your project settings
- **Learning System**: Accumulates build error patterns in LESSONS_LEARNED.md

## Quick Start

### Prerequisites

- [Claude Code CLI](https://claude.com/claude-code) installed
- Git installed
- A project you want to enhance with agent orchestration

### Installation

#### Step 1: Add as Git Submodule

Choose the commands for your operating system:

<details>
<summary><b>Linux / macOS</b></summary>

```bash
# Navigate to your project root
cd /path/to/your-project

# Add the orchestration system as a submodule
git submodule add https://github.com/Zeliper/z-coder .claude-orchestration
git submodule update --init --recursive

# Verify installation
ls -la .claude-orchestration/
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
# Navigate to your project root
cd C:\path\to\your-project

# Add the orchestration system as a submodule
git submodule add https://github.com/Zeliper/z-coder .claude-orchestration
git submodule update --init --recursive

# Verify installation
dir .claude-orchestration\
```

</details>

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
REM Navigate to your project root
cd C:\path\to\your-project

REM Add the orchestration system as a submodule
git submodule add https://github.com/Zeliper/z-coder .claude-orchestration
git submodule update --init --recursive

REM Verify installation
dir .claude-orchestration\
```

</details>

#### Step 2: Enable the Init Command

Before running `/orchestration-init`, you need to copy the command file first:

<details>
<summary><b>Linux / macOS</b></summary>

```bash
# Create the commands directory and copy the init command
mkdir -p .claude/commands
cp .claude-orchestration/.claude/commands/orchestration-init.md .claude/commands/
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
# Create the commands directory and copy the init command
New-Item -ItemType Directory -Force -Path .claude\commands
Copy-Item .claude-orchestration\.claude\commands\orchestration-init.md .claude\commands\
```

</details>

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
REM Create the commands directory and copy the init command
mkdir .claude\commands
copy .claude-orchestration\.claude\commands\orchestration-init.md .claude\commands\
```

</details>

#### Step 3: Initialize in Claude Code

Open Claude Code in your project (or restart if already open) and run:

```
/orchestration-init
```

This will:
1. Copy agent files from the submodule to `.claude/`
2. Analyze your project structure
3. Generate `config.json` with detected settings
4. Create custom agents based on your project type
5. Add project-specific configurations to core agents

### Alternative: Manual Installation (Without Submodule)

If you prefer not to use Git submodules:

<details>
<summary><b>Linux / macOS</b></summary>

```bash
# Clone the repository
git clone https://github.com/Zeliper/z-coder.git /tmp/claude-orchestration

# Copy files to your project
cp -r /tmp/claude-orchestration/.claude ./
cp -r /tmp/claude-orchestration/tasks ./
cp /tmp/claude-orchestration/VERSION ./

# Clean up
rm -rf /tmp/claude-orchestration

# Initialize
# In Claude Code: /orchestration-init --no-submodule
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
# Clone the repository
git clone https://github.com/Zeliper/z-coder.git $env:TEMP\claude-orchestration

# Copy files to your project
Copy-Item -Recurse $env:TEMP\claude-orchestration\.claude .\
Copy-Item -Recurse $env:TEMP\claude-orchestration\tasks .\
Copy-Item $env:TEMP\claude-orchestration\VERSION .\

# Clean up
Remove-Item -Recurse -Force $env:TEMP\claude-orchestration

# Initialize
# In Claude Code: /orchestration-init --no-submodule
```

</details>

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
REM Clone the repository
git clone https://github.com/Zeliper/z-coder.git %TEMP%\claude-orchestration

REM Copy files to your project
xcopy /E /I %TEMP%\claude-orchestration\.claude .\.claude
xcopy /E /I %TEMP%\claude-orchestration\tasks .\tasks
copy %TEMP%\claude-orchestration\VERSION .\

REM Clean up
rmdir /S /Q %TEMP%\claude-orchestration

REM Initialize
REM In Claude Code: /orchestration-init --no-submodule
```

</details>

---

## Updating the Orchestration System

### Method 1: Using the Update Command (Recommended)

In Claude Code, simply run:

```
/orchestration-update
```

This will:
1. Pull the latest changes from the submodule
2. Update core agent files while preserving your project-specific settings
3. Keep your `LESSONS_LEARNED.md` intact
4. Update version info in `config.json`

#### Update Options

```
/orchestration-update                    # Update to latest version
/orchestration-update --version 1.2.0    # Update to specific version
/orchestration-update --dry-run          # Preview changes without applying
/orchestration-update --force            # Force update even if already latest
```

### Method 2: Manual Submodule Update

<details>
<summary><b>Linux / macOS</b></summary>

```bash
# Navigate to your project
cd /path/to/your-project

# Update the submodule
cd .claude-orchestration
git fetch origin
git pull origin main
cd ..

# Then run in Claude Code
# /orchestration-update
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
# Navigate to your project
cd C:\path\to\your-project

# Update the submodule
cd .claude-orchestration
git fetch origin
git pull origin main
cd ..

# Then run in Claude Code
# /orchestration-update
```

</details>

### Method 3: Update to Specific Version

<details>
<summary><b>All Platforms</b></summary>

```bash
# Navigate to submodule
cd .claude-orchestration

# List available versions
git tag -l

# Checkout specific version
git checkout v1.2.0

cd ..

# Apply the update in Claude Code
# /orchestration-update --force
```

</details>

---

## Usage

### Starting a Task

```
/orchestrate Implement user authentication with JWT
```

### Resuming a Task

```
/orchestrate --task TASK-001
```

### Referencing Previous Work

```
/orchestrate --ref TASK-001 Add refresh token support
```

### Checking Status

```
/status
/tasks
```

---

## Project Structure

After initialization, your project will have:

```
your-project/
├── .claude-orchestration/        # Git Submodule (source of truth)
│   ├── VERSION
│   ├── .claude/
│   │   ├── agents/
│   │   ├── commands/
│   │   └── templates/
│   └── tasks/
├── .claude/                      # Active configuration (project-specific)
│   ├── agents/
│   │   ├── main-agent.md
│   │   ├── coder-agent.md
│   │   ├── builder-agent.md
│   │   ├── codebase-search-agent.md
│   │   ├── todo-list-agent.md
│   │   ├── web-search-agent.md
│   │   └── {custom-agents}.md    # Auto-generated based on project
│   ├── commands/
│   │   ├── orchestrate.md
│   │   ├── orchestration-init.md
│   │   └── orchestration-update.md
│   ├── templates/
│   ├── config.json               # Project configuration
│   └── LESSONS_LEARNED.md        # Build error patterns (preserved)
└── tasks/
    ├── TASK-001.md               # Active tasks
    └── archive/                  # Completed tasks
```

---

## Core Agents

| Agent | Role |
|-------|------|
| **main-agent** | Orchestrates workflow, spawns sub-agents |
| **codebase-search-agent** | Explores codebase, finds patterns |
| **reference-agent** | Searches reference code, examples, and templates |
| **todo-list-agent** | Breaks down tasks into steps |
| **coder-agent** | Implements code changes |
| **web-search-agent** | Searches external documentation |
| **builder-agent** | Runs builds, analyzes errors |

### Auto-Generated Custom Agents

Based on your project type, additional agents may be created:

| Project Type | Custom Agents |
|--------------|---------------|
| Unity/BepInEx | decompiled-search-agent, harmony-patch-agent |
| Node.js/TypeScript | dependency-analyzer-agent |
| Python | python-env-agent |
| Database | db-schema-agent |
| Docker | container-agent |

---

## Configuration

### config.json Schema

```json
{
  "orchestration": {
    "version": "1.0.0",
    "installed_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z",
    "submodule_path": ".claude-orchestration"
  },
  "project": {
    "name": "your-project",
    "type": "nodejs",
    "languages": ["typescript"],
    "frameworks": ["express"]
  },
  "paths": {
    "source": ["./src"],
    "excluded": ["node_modules", ".git"]
  },
  "commands": {
    "build": "npm run build",
    "test": "npm test"
  },
  "custom_agents": ["dependency-analyzer-agent"]
}
```

---

## Important Notes for Adding to Existing Projects

When adding this orchestration system to an existing project as a submodule, pay attention to the following:

### Pre-Installation Checklist

| Check | Description |
|-------|-------------|
| **Existing `.claude/` folder** | If your project already has a `.claude/` folder, back it up first. The initialization will overwrite it. |
| **Team sync required** | All team members must run `git submodule update --init --recursive` after pulling |
| **CI/CD pipeline** | Update your CI/CD to include `--recursive` flag when cloning |
| **`.gitmodules` conflict** | If you already have submodules, check for path conflicts in `.gitmodules` |

### For Team Collaboration

After adding the submodule, inform your team:

```bash
# Team members must run this after pulling
git submodule update --init --recursive

# Or clone with recursive flag for new clones
git clone --recursive <your-repo-url>
```

### Backup Existing Configuration

If you have an existing `.claude/` configuration:

```bash
# Before installation
mv .claude .claude.backup.manual

# After /orchestration-init, merge your custom settings back
# Your settings should go between the markers:
# <!-- ORCHESTRATION-PROJECT-CONFIG-START -->
# <!-- ORCHESTRATION-PROJECT-CONFIG-END -->
```

### Common Issues When Adding to Existing Projects

| Issue | Solution |
|-------|----------|
| Submodule path conflict | Choose a different path: `git submodule add <url> .orchestration` |
| Permission denied | Ensure you have write access to the repository |
| Detached HEAD in submodule | Run `cd .claude-orchestration && git checkout main` |
| Nested .git conflicts | Remove any nested `.git` folders before adding submodule |

---

## Troubleshooting

### Submodule Not Found

```bash
# Re-initialize submodules
git submodule update --init --recursive
```

### Update Failed - Rollback

The system automatically creates backups before updates. If an update fails:

```bash
# Backups are stored as .claude.backup.{timestamp}
# Manual restore if needed:
rm -rf .claude
mv .claude.backup.20250115_120000 .claude
```

### Merge Conflicts in Agent Files

Project-specific settings are preserved using markers:
```markdown
<!-- ORCHESTRATION-PROJECT-CONFIG-START -->
Your project settings here (preserved during updates)
<!-- ORCHESTRATION-PROJECT-CONFIG-END -->
```

If you see conflicts, ensure the markers are intact.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Update the VERSION file if needed
5. Submit a pull request

---

## License

MIT License - See [LICENSE](LICENSE) for details.
