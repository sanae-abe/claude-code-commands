# Claude Code Commands

My personal collection of custom Claude Code slash commands and workflows.

## 📁 Repository Structure

```
claude-code-commands/
├── commands/           # Custom slash commands
│   ├── todo.md        # Intelligent task management system
│   └── iterative-review.md  # Multi-perspective iterative review
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
```

### Using Symlinks (Recommended for development)

Create symlinks to keep commands in sync with this repository:

```bash
# Create symlinks
ln -sf ~/projects/claude-code-commands/commands/todo.md ~/.claude/commands/todo.md
ln -sf ~/projects/claude-code-commands/commands/iterative-review.md ~/.claude/commands/iterative-review.md
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

## 🔄 Keeping Commands Updated

### Pull latest changes

```bash
cd ~/projects/claude-code-commands
git pull
```

If using symlinks, changes will automatically reflect in `~/.claude/commands/`.

### Backup current commands

```bash
# Commit and push changes
git add .
git commit -m "Update commands"
git push
```

## 📝 Notes

- **Purpose**: Personal backup and version control
- **Compatibility**: Claude Code (CLI)
- **Last Updated**: 2025-11-10

## 🛠️ Customization

Feel free to modify commands to fit your workflow. All commands are in Markdown format and can be edited directly.

## 📄 License

MIT License - See LICENSE file for details.
