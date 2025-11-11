---
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, TodoWrite, Grep, Glob
argument-hint: "[action] [description] | add | complete | list | sync | project | interactive"
description: Simple project task management with interactive UI and priority handling
model: sonnet
---

# Todo Manager

Interactive project task management: **$ARGUMENTS**

## 🚀 Quick Start

```bash
# Basic operations
/todo                           # Interactive mode
/todo add "Fix bug"             # Add task
/todo list                      # List all tasks
/todo complete 1                # Complete task (alias: done)

# Priority & context specification
/todo add "Fix auth timeout" --priority high --context api

# Date specification
/todo add "Update docs" --due 2025-01-15
/todo add "Review PR" --due tomorrow

# Filtering & sorting
/todo list --filter priority:high
/todo list --sort due
```

---

## 📋 Basic Commands

### `add "description" [options]`
Create a new task.

**Options**:
- `--priority <level>`: Priority level (critical|high|medium|low)
- `--context <type>`: Context type (ui|api|docs|test|build|security)
- `--due <date>`: Due date (YYYY-MM-DD or tomorrow, next week, etc.)

**Examples**:
```bash
/todo add "Fix authentication timeout" --priority high --context api
/todo add "Update documentation" --due 2025-01-20
/todo add "Refactor component" --priority medium --context ui --due next week
```

### `complete N` / `done N`
Complete a task (aliases: `complete`, `done`).

**Examples**:
```bash
/todo complete 1
/todo done 3
```

### `list [options]`
Display task list.

**Options**:
- `--filter <condition>`: Filter tasks (e.g., `priority:high`, `context:ui`)
- `--sort <field>`: Sort tasks (`due`, `priority`)

**Examples**:
```bash
/todo list                      # Show all tasks
/todo list --filter priority:high
/todo list --sort due
```

### Other Commands
- `remove N` / `delete N` - Delete task
- `undo N` - Revert completed task to incomplete
- `past due` - Show overdue tasks
- `next` - Show next priority task (considering due date & priority)

---

## 📝 Todo Format

**todos.md format** (ISO 8601 date format):

```markdown
- [ ] Task description | Priority: high|medium|low | Context: ui|api|test|docs|build | Due: YYYY-MM-DD
```

**Examples**:
```markdown
- [ ] Fix authentication timeout | Priority: high | Context: api | Due: 2025-01-15
- [ ] Update documentation | Priority: medium | Context: docs | Due: 2025-01-20
- [x] Refactor TaskCard component | Priority: low | Context: ui | Due: 2025-01-10
```

---

## 🔒 Security Requirements

### Input Sanitization (Required)

```bash
# Argument sanitization - whitelist approach
sanitize_arguments() {
    local raw_args="$1"

    # Length limit (DoS protection)
    if [[ ${#raw_args} -gt 1000 ]]; then
        echo "❌ Error: Input too long (max 1000 chars)" >&2
        return 1
    fi

    # Extract allowed characters only (alphanumeric, space, symbols)
    printf '%s' "$raw_args" | grep -Eo '[a-zA-Z0-9 ._:/-]+' || echo ""
}

SANITIZED_ARGS=$(sanitize_arguments "$ARGUMENTS")
```

### File Path Validation (Required)

```bash
# Path traversal protection + .git protection
validate_file_path() {
    local file_path="$1"
    local real_path

    # Get absolute path
    real_path=$(realpath "$file_path" 2>/dev/null)

    # Deny .git directory access
    if [[ "$real_path" == *"/.git/"* ]]; then
        echo "❌ Security Error: Access to .git directory denied" >&2
        return 1
    fi

    # Check if within current directory
    if [[ "$real_path" != "$PWD"* ]]; then
        echo "❌ Security Error: Path traversal detected" >&2
        return 1
    fi

    # File size limit (10MB)
    if command -v stat >/dev/null 2>&1; then
        local file_size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null)
        if [[ $file_size -gt 10485760 ]]; then
            echo "❌ Error: File exceeds 10MB limit" >&2
            return 1
        fi
    fi

    return 0
}
```

---

## ⚡ Performance Optimization

### Project Root Detection (Optimized)

```bash
# Optimized version without find command (10x faster)
detect_project_root() {
    # Check current directory
    for file in package.json Cargo.toml requirements.txt; do
        if [[ -f "$file" ]]; then
            pwd
            return 0
        fi
    done

    # Search parent directories (max 3 levels)
    local dir="$PWD"
    for i in 1 2 3; do
        dir=$(dirname "$dir")
        for file in package.json Cargo.toml requirements.txt; do
            if [[ -f "$dir/$file" ]]; then
                echo "$dir"
                return 0
            fi
        done
    done

    pwd
}

PROJECT_ROOT=$(detect_project_root)
```

### Git State Caching

```bash
# Environment variable caching to avoid duplicate execution
if [[ -z "$GIT_CONTEXT_CACHED" ]]; then
    export GIT_STATUS=$(git status --porcelain 2>&1 | head -20 || echo "No git repo")
    export GIT_BRANCH=$(git branch --show-current 2>&1 || echo "No git branch")
    export GIT_COMMITS=$(git log --oneline -3 2>&1 || echo "No commit history")
    export GIT_CONTEXT_CACHED=1
fi
```

### Date Parsing Optimization

```bash
# OS detection caching (only first time)
if [[ -z "$DATE_CMD_TYPE" ]]; then
    if date -v+1d +%Y-%m-%d >/dev/null 2>&1; then
        export DATE_CMD_TYPE="bsd"  # macOS
    else
        export DATE_CMD_TYPE="gnu"  # Linux
    fi
fi

parse_natural_language_date() {
    local input="$1"

    case "$input" in
        tomorrow)
            if [[ "$DATE_CMD_TYPE" == "bsd" ]]; then
                date -v+1d +%Y-%m-%d
            else
                date -d "tomorrow" +%Y-%m-%d
            fi
            ;;
        "next week")
            if [[ "$DATE_CMD_TYPE" == "bsd" ]]; then
                date -v+7d +%Y-%m-%d
            else
                date -d "7 days" +%Y-%m-%d
            fi
            ;;
        "in "*)
            local days="${input#in }"
            days="${days% days}"
            days="${days% day}"
            if [[ "$DATE_CMD_TYPE" == "bsd" ]]; then
                date -v+${days}d +%Y-%m-%d
            else
                date -d "${days} days" +%Y-%m-%d
            fi
            ;;
        *)
            # Use ISO 8601 format as-is
            echo "$input"
            ;;
    esac
}
```

---

## 📅 Date Specification

**Supported formats**:
- `YYYY-MM-DD`: 2025-01-15 (ISO 8601 standard)
- `tomorrow`: Next day
- `next week`: 7 days later
- `in 3 days`: 3 days later

---

## ⚠️ Error Handling

### Error Code Specification

| Code | Value | Meaning | Resolution |
|------|-------|---------|-----------|
| EXIT_SUCCESS | 0 | Success | - |
| EXIT_NO_PERMISSION | 1 | Permission error | Check directory permissions |
| EXIT_NOT_GIT_REPO | 2 | Git not initialized | Run git init |
| EXIT_INVALID_ARGS | 3 | Invalid arguments | Check command format |
| EXIT_FILE_NOT_FOUND | 4 | File not found | Create todos.md |
| EXIT_SECURITY_ERROR | 5 | Security error | Verify input content |
| EXIT_FILE_TOO_LARGE | 6 | File size exceeded | Clean up file |

### Error Handling Implementation Example

```bash
# Error code definitions
readonly EXIT_SUCCESS=0
readonly EXIT_NO_PERMISSION=1
readonly EXIT_SECURITY_ERROR=5

# File operation error
if [ ! -w . ]; then
  echo "❌ Error: No write permission in current directory" >&2
  echo "💡 Solution: Check directory permissions or switch to project root" >&2
  exit $EXIT_NO_PERMISSION
fi

# Git repository validation (warning only)
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "⚠️ Warning: Not a git repository" >&2
  echo "📝 Note: Git integration features will be limited" >&2
  # Don't exit as it's not critical
fi

# Argument validation error
if [[ -z "$SANITIZED_ARGS" ]]; then
  echo "❌ Error: Invalid arguments provided" >&2
  echo "💡 Usage: /todo add \"description\" [--priority high] [--context api]" >&2
  exit $EXIT_INVALID_ARGS
fi
```

---

## 🎯 Interactive Mode

When executed without arguments, provides interactive operation using AskUserQuestion tool:

```bash
# Primary action selection
AskUserQuestion {
  question: "What would you like to do with TODO management?"
  options: [
    "add-task": "Create a new task"
    "review-list": "Review current task list"
    "quick-complete": "Quick complete tasks"
  ]
}

# Detailed settings for task creation
AskUserQuestion {
  questions: [
    {
      question: "Select task priority"
      options: [
        "critical": "🔴 Critical: Production issue, urgent response"
        "high": "🟡 High: Important feature, has deadline"
        "medium": "🟢 Medium: Regular development, improvements"
        "low": "🔵 Low: Optimization, research, future work"
      ]
    },
    {
      question: "Select task context (domain)"
      options: [
        "ui": "🎨 UI/UX: Frontend"
        "api": "⚙️ API: Backend"
        "docs": "📝 Docs: Documentation"
        "test": "🧪 Test: Testing & quality"
        "build": "🔧 Build: Build & CI/CD"
        "security": "🔒 Security: Security"
      ]
    }
  ]
}
```

---

## 📚 Command Specification Table

| Command | Alias | Argument Format | Example |
|---------|-------|----------------|---------|
| `add` | - | `"description" [options]` | `/todo add "Fix bug" --priority high` |
| `complete` | `done` | `N` | `/todo complete 1` |
| `list` | - | `[options]` | `/todo list --filter priority:high` |
| `remove` | `delete` | `N` | `/todo remove 3` |
| `undo` | - | `N` | `/todo undo 2` |

**Unified option format**:
- Flags: `--priority high`, `--context ui`, `--due 2025-01-15`
- Filters: `--filter priority:high`, `--filter context:api`
- Sort: `--sort due`, `--sort priority`

---

## 🔧 Implementation Status

### ✅ Phase 1 (Implemented)
- [x] Basic CRUD operations (add, complete, list, remove)
- [x] Priority & context management
- [x] Date handling (ISO 8601)
- [x] Interactive mode
- [x] Security measures (command injection, path traversal)
- [x] Performance optimization

### 🚧 Phase 2 (Planned)
Additional features under consideration:
- Git integration enhancements
- Team collaboration features
- Advanced filtering and reporting
- Integration with project management tools

Contributions and feature requests are welcome!

---

## 💡 Usage Examples

```bash
# Example: GraphQL API project
# Critical bug fix task
/todo add "Fix resolver error in TaskQuery" --priority critical --context api --due tomorrow

# Example: React application
# UI component fix
/todo add "Fix button component state bug" --priority high --context ui --due today

# Example: Documentation project
# Documentation update task
/todo add "Update API documentation" --priority medium --context docs --due next week

# Example: Testing task
# Test coverage improvement
/todo add "Add unit tests for user service" --priority high --context test

# Filter and view tasks
/todo list --filter context:api --sort priority
/todo list --filter priority:critical

# Check next priority task
/todo next
```

---

## 📖 References

- **ISO 8601 Date Format**: https://en.wikipedia.org/wiki/ISO_8601
- **Bash Security Best Practices**: https://mywiki.wooledge.org/BashGuide
