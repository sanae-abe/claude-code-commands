# Claude Code Commands

My personal collection of custom Claude Code slash commands and workflows.

## 📋 Table of Contents

- [Repository Structure](#-repository-structure)
- [Installation](#-installation)
  - [Manual Installation](#manual-installation)
  - [Using Symlinks (Recommended for development)](#using-symlinks-recommended-for-development)
  - [Updating Commands](#updating-commands)
- [Available Commands](#-available-commands)
  - [/todo - Intelligent Task Management](#todo---intelligent-task-management)
  - [/iterative-review - Multi-Perspective Review](#iterative-review---multi-perspective-review)
  - [/i18n-check - Internationalization Status Check](#i18n-check---internationalization-status-check)
  - [/clean-jobs - Safe Background Job Cleanup](#clean-jobs---safe-background-job-cleanup)
- [Additional Information](#-additional-information)
- [License](#-license)

## 📁 Repository Structure

```
claude-code-commands/
├── commands/           # Custom slash commands
│   ├── todo.md        # Intelligent task management system
│   ├── iterative-review.md  # Multi-perspective iterative review
│   ├── i18n-check.md  # Comprehensive i18n status check
│   └── clean-jobs.md  # Safe cleanup of background jobs
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## 🚀 Installation

### Manual Installation

Copy commands to your Claude Code commands directory:

```bash
# Copy individual commands
cp commands/todo.md ~/.claude/commands/
cp commands/iterative-review.md ~/.claude/commands/
cp commands/i18n-check.md ~/.claude/commands/
cp commands/clean-jobs.md ~/.claude/commands/
```

### Using Symlinks (Recommended for development)

Create symlinks to keep commands in sync with this repository:

```bash
# Create symlinks
ln -sf ~/projects/claude-code-commands/commands/todo.md ~/.claude/commands/todo.md
ln -sf ~/projects/claude-code-commands/commands/iterative-review.md ~/.claude/commands/iterative-review.md
ln -sf ~/projects/claude-code-commands/commands/i18n-check.md ~/.claude/commands/i18n-check.md
ln -sf ~/projects/claude-code-commands/commands/clean-jobs.md ~/.claude/commands/clean-jobs.md
```

### Updating Commands

**Pull latest changes:**

```bash
cd ~/projects/claude-code-commands
git pull
```

If using symlinks, changes will automatically reflect in `~/.claude/commands/`.

**Backup and push your changes:**

```bash
git add .
git commit -m "Update commands"
git push
```

## 📚 Available Commands

### `/todo` - Intelligent Task Management

Integrated todo management system with Git coordination and interactive UI.

**Usage:**
```bash
/todo add "Implement feature X"
/todo list
/todo complete 1
/todo sync          # Sync with Git
/todo project       # Project-wide analysis
/todo interactive   # Interactive UI
```

**Features:**
- Git integration for commit-based task tracking
- Interactive dialog UI
- Project-wide task analysis
- Automatic synchronization

**Use Cases:**
- Managing development tasks within coding sessions
- Tracking feature implementation progress
- Coordinating tasks with Git commits
- Project-wide task organization and analysis

### `/iterative-review` - Multi-Perspective Review

Iterative code review with multiple security, performance, and maintainability perspectives.

**Usage:**
```bash
/iterative-review <target>
/iterative-review <target> --rounds=3
/iterative-review <target> --perspectives=security,performance,maintainability
```

**Features:**
- Security-focused analysis (OWASP, XSS, authentication)
- Performance optimization review
- Maintainability assessment
- Multiple review rounds for deep analysis

**Use Cases:**
- Comprehensive code quality review before merge
- Security audit of critical components
- Performance bottleneck identification
- Documentation and configuration review

### `/i18n-check` - Internationalization Status Check

Comprehensive internationalization (i18n) status check for any project with coverage, consistency, and cultural sensitivity analysis.

**Usage:**
```bash
/i18n-check [language-code]
/i18n-check ja --coverage
/i18n-check en --consistency
/i18n-check --format
/i18n-check --cultural
/i18n-check --complete
```

**Features:**
- Translation coverage analysis across all supported languages
- Consistency checking for translation keys and formats
- Format validation (placeholders, variables, HTML tags)
- Cultural sensitivity and locale-specific content review
- Complete internationalization audit across entire codebase

**Use Cases:**
- Pre-release internationalization audit
- Missing translation detection across languages
- Translation quality consistency verification
- Cultural appropriateness review for global products

### `/clean-jobs` - Safe Background Job Cleanup

Safely cleans up only background jobs created in the current Claude Code session.

**Usage:**
```bash
/clean-jobs
```

**Features:**
- Interactive cleanup options (all jobs, select individually, or cancel)
- Safe cleanup limited to current session only
- Input validation and race condition prevention
- Detailed cleanup results reporting
- Does not affect other Claude Code sessions

**Use Cases:**
- Cleanup after long development sessions
- Manual stop of processes started by `/web-dev`, `/api-dev`, etc.
- Periodic job cleanup for memory conservation

## 📝 Additional Information

### About This Repository

- **Purpose**: Personal backup and version control of custom Claude Code commands
- **Compatibility**: Claude Code (CLI)
- **Last Updated**: 2025-11-11

### Prerequisites

- Claude Code CLI must be installed and configured
- Basic familiarity with command-line operations
- Git installed (for symlink workflow and updates)

### Customization

Feel free to modify commands to fit your workflow. All commands are in Markdown format and can be edited directly in the `commands/` directory.

### Troubleshooting

**Symlink creation fails:**
- Ensure `~/.claude/commands/` directory exists: `mkdir -p ~/.claude/commands/`
- Check file permissions: `ls -la ~/.claude/commands/`

**Commands not appearing in Claude Code:**
- Restart Claude Code CLI
- Verify symlinks are created correctly: `ls -la ~/.claude/commands/`
- Check that command files are valid Markdown with proper frontmatter

## 📄 License

MIT License - See LICENSE file for details.
