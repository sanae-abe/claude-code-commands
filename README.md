# Claude Code Workspace

Personal Claude Code configuration workspace with custom commands and development workflows.

## 📋 Overview

This repository is my personal backup and configuration management for Claude Code:

- Custom slash commands for streamlined workflows
- Technology stack configurations for different projects
- LLM-optimized settings for efficient AI-assisted development
- Integrated skills from Anthropic and community collections

## 📁 Repository Structure

```
claude-code-workspace/
├── commands/              # Custom slash commands (8 commands)
│   ├── clean-jobs.md     # Safe background job cleanup
│   ├── decide.md         # Framework-driven decision support
│   ├── i18n-check.md     # Internationalization status check
│   ├── iterative-review.md  # Multi-perspective code review
│   ├── plan-review.md    # Implementation planning with review
│   ├── ship.md           # GitHub PR/GitLab MR creation
│   ├── task-validate.md  # Quality validation and next actions
│   └── todo.md           # Intelligent task management
├── stacks/                # Technology stack configurations (6 stacks)
│   ├── backend-api.md    # Backend API development settings
│   ├── data-science.md   # Data science workflow settings
│   ├── frontend-web.md   # Frontend web development settings
│   ├── mobile-app.md     # Mobile app development settings
│   ├── rust-cli.md       # Rust CLI development settings
│   ├── shell-cli.md      # Shell scripting standards (POSIX)
│   └── slash-command-design.md  # Command design guidelines
├── skills/                # Integrated Claude skills
│   ├── anthropic-skills/ # Official Anthropic skills
│   └── superpowers/      # Community skill collection
├── CLAUDE.md             # LLM behavior configuration
├── USER_GUIDE.md         # User-facing documentation
├── settings.json         # Claude Code system settings
├── docs/                 # Additional documentation
├── projects/             # Session history and project data
└── scripts/              # Utility scripts
```

## 🚀 Setup

### Installation

Since this is already set up in my environment at `~/projects/claude-code-workspace`, commands and configurations are symlinked to `~/.claude/`.

To restore from backup or set up on a new machine:

```bash
# Clone repository
git clone <this-repo-url> ~/projects/claude-code-workspace

# Link commands
ln -sf ~/projects/claude-code-workspace/commands/*.md ~/.claude/commands/

# Link configuration files
ln -sf ~/projects/claude-code-workspace/CLAUDE.md ~/.claude/CLAUDE.md
ln -sf ~/projects/claude-code-workspace/settings.json ~/.claude/settings.json

# Link stacks
mkdir -p ~/.claude/stacks
ln -sf ~/projects/claude-code-workspace/stacks/*.md ~/.claude/stacks/
```

### Verify Setup

```bash
# Check available commands
/help

# Test a command
/todo list
```

## 📚 Available Commands

### Task Management & Planning

**`/todo`** - Intelligent task management with Git integration
- Usage: `/todo add "task"`, `/todo list`, `/todo complete 1`, `/todo sync`
- Git integration, interactive UI, project-wide analysis

**`/decide`** - Framework-driven decision support for tech choices
- Usage: `/decide "question-or-options"`, `/decide "A vs B"`, `/decide "priorities"`
- ICE/RICE scoring, Eisenhower Matrix, First Principles analysis
- Conclusion-first format with detailed comparison tables

**`/plan-review`** - Create implementation plan and review
- Usage: `/plan-review "feature name" [--rounds=3] [--perspectives=security,performance]`
- Task breakdown, automatic review, todo.md updates

**`/task-validate`** - Validate task completion and quality
- Usage: `/task-validate [--scope=lint|test|build] [--report-only] [--auto-proceed]`
- Quality checks, next action suggestions

### Code Quality & Review

**`/iterative-review`** - Multi-perspective code review
- Usage: `/iterative-review <target> [--rounds=4] [--perspectives=...] [--skip-necessity]`
- Round 0: Necessity review (deletion/simplification)
- Security, performance, maintainability analysis

**`/i18n-check`** - Internationalization status check
- Usage: `/i18n-check [language] [--coverage|--consistency|--format|--cultural|--complete]`
- Translation coverage, consistency, format validation

### Version Control

**`/ship`** - Create GitHub PR/GitLab MR with automatic platform detection
- Usage: `/ship [branch-name] [title]`, `/ship` (interactive)
- Auto-detects GitHub/GitLab, applies templates, runs quality checks
- Conventional Commits format, draft PR/MR creation

### Utilities

**`/clean-jobs`** - Safe cleanup of background jobs
- Usage: `/clean-jobs`
- Session-scoped, interactive cleanup options

## 🎯 Technology Stack Configurations

Available in `stacks/` directory:

1. **frontend-web.md** - React/Vue/Angular, component architecture, state management
2. **backend-api.md** - REST/GraphQL, database patterns, API security
3. **mobile-app.md** - iOS/Android, cross-platform frameworks
4. **data-science.md** - Jupyter, data pipelines, ML/AI workflows
5. **rust-cli.md** - Rust patterns, CLI frameworks, error handling
6. **shell-cli.md** - POSIX compliance (52 standards), security practices

### Using Stack Configurations

Automatically applied based on project context, or explicitly set in project `.claude/CLAUDE.md`:

```yaml
tech_stack: frontend-web
project_type: spa
team_size: 3-5
```

## 🛠️ Configuration Files

**CLAUDE.md** - LLM behavior configuration
- Development workflows, code quality standards, security requirements

**USER_GUIDE.md** - User documentation
- Command reference, usage patterns, troubleshooting

**settings.json** - System settings
- Tool permissions, file operation rules, MCP integration

## 🔄 Backup & Sync

### Save Changes

```bash
cd ~/projects/claude-code-workspace
git add .
git commit -m "Update commands and configurations"
git push
```

### Pull Latest

```bash
cd ~/projects/claude-code-workspace
git pull
```

Changes automatically reflect via symlinks.

### Version Management

Commands follow semantic versioning in frontmatter:

```yaml
---
version: 1.1.0
last-modified: 2025-11-13
---
```

## 📖 Resources

### Documentation

- Command docs: `commands/*.md`
- Stack docs: `stacks/*.md`
- Design guide: `stacks/slash-command-design.md`
- Decision frameworks: `docs/decision-frameworks.md` - ICE/RICE scoring, First Principles, practical workflows

### Integrated Skills

- **Anthropic Skills**: PDF, XLSX, Artifacts, MCP builder
- **Superpowers**: Community skill collection

Access via Skill tool in Claude Code.

### Learning & History

- Session history: `projects/`
- Learning sessions tracked for pattern recognition

## 🔒 Security

File permissions enforced by Claude Code:
- Prohibited: `.env`, credentials, secrets
- Git operations via standard commands only
- No direct `.git/` manipulation

All commands enforce OWASP Top 10, input validation, secure patterns.

## 🐛 Troubleshooting

### Commands Not Appearing

```bash
ls -la ~/.claude/commands/
chmod 644 ~/.claude/commands/*.md
# Restart Claude Code CLI
```

### Symlinks Broken

```bash
mkdir -p ~/.claude/commands/ ~/.claude/stacks/
ls -la ~/.claude/
```

### Configuration Issues

1. Verify `CLAUDE.md` syntax
2. Check `settings.json` JSON syntax
3. Review Claude Code logs

## 📄 License

MIT License - Personal use

---

**Last Updated**: 2025-11-13
**Status**: Active personal workspace
