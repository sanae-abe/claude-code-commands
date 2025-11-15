---
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, TodoWrite, Grep, Glob
argument-hint: "[action] [description] | add | complete | uncomplete | remove | list | sync | next | interactive"
description: Simple project task management with interactive UI and priority handling
model: sonnet
---

# Todo Manager

Arguments: $ARGUMENTS

## Execution Flow

1. Parse arguments from $ARGUMENTS
2. Validate and sanitize input (security check using ~/.claude/utils/todo_validation.py)
3. Determine action: add, complete, uncomplete, remove, list, sync, next, or interactive mode
4. Locate or create todos.md file in project root
5. Execute requested action
6. Update todos.md file if modifications made
7. Display results to user

If $ARGUMENTS empty: use AskUserQuestion for interactive mode
If todos.md not found: create new file with empty task list
If validation fails: report error and exit

## Input Validation

Use ~/.claude/utils/todo_validation.py for all user input:

```python
from todo_validation import validate_path, sanitize_input, validate_task_id

# Validate file paths
safe_path = validate_path(path)  # Rejects ../, validates within project, denies .git

# Sanitize user input
safe_text = sanitize_input(description)  # Unicode normalize, limit 4KB bytes, 1000 chars

# Validate task IDs
task_id = validate_task_id(id_str)  # Must match task-\d+ pattern
```

Validation rules:
- File paths: reject ../, validate within project root, deny .git access
- Task descriptions: Unicode normalize (NFKC), limit 4KB bytes, 1000 chars max
- Task IDs: must match task-\d+ pattern
- Priority: must be critical|high|medium|low
- Context: must be ui|api|docs|test|build|security

## Argument Parsing

Parse $ARGUMENTS to extract:
- Action: first token (add, complete, uncomplete, remove, list, sync, next, interactive)
- Task description: quoted string for add action
- Task number: integer for complete, uncomplete, remove actions
- Options: --priority, --context, --due, --filter, --sort

All inputs must pass validation before use

## Tool Usage

TodoWrite: Use when processing multiple tasks or complex operations

AskUserQuestion: Use in interactive mode when $ARGUMENTS empty
- Primary action selection: add-task, review-list, quick-complete
- Task priority selection: critical, high, medium, low
- Task context selection: ui, api, docs, test, build, security

Bash: Use for date parsing and executing Python validation scripts

Read: Read existing todos.md file

Write: Create new todos.md file if not exists

Edit: Update todos.md with task changes

Grep: Search for specific tasks or patterns

## Todo File Format

todos.md uses markdown checklist format with metadata:

```markdown
- [ ] Task description | Priority: high|medium|low | Context: ui|api|test|docs|build|security | Due: YYYY-MM-DD
- [x] Completed task | Priority: medium | Context: ui | Due: 2025-01-15
```

Priority levels: critical, high, medium, low
Context types: ui, api, docs, test, build, security
Date format: ISO 8601 (YYYY-MM-DD) or natural language (tomorrow, next week, in N days)

## Command Actions

add "description" [options]:
- Parse description from quoted string
- Extract --priority, --context, --due options
- Append new task to todos.md
- Default priority: medium, context: none, due: none

complete N | done N:
- Parse task number N
- Mark task as completed ([x])
- Update todos.md

list [options]:
- Read todos.md file
- Display all tasks with numbers
- Apply --filter (priority:X, context:Y) if specified
- Apply --sort (due, priority) if specified
- Use Read tool to load todos.md
- Use Bash for grep filtering if needed
- Format output with task numbers for reference

uncomplete N:
- Parse task number N
- Revert completed task to incomplete ([ ])
- Update todos.md

remove N | delete N:
- Parse task number N
- Remove task from todos.md

next:
- Find next incomplete task from todos.md
- If task contains #task-N pattern, output structured info for Claude
- Claude should ask user once via AskUserQuestion
- If confirmed, execute SlashCommand("/implement task-N") once
- For lightweight tasks, just display the task

sync:
- Import pending tasks from tasks.yml to todos.md
- Load tasks.yml and extract tasks with status: pending
- Read todos.md and extract existing #task-N IDs
- Filter new tasks (not in existing IDs)
- Sanitize goal strings using ~/.claude/utils/task-sanitize.py
- Append new tasks with format: - [ ] #task-N goal | Priority: X | Effort: Yh
- Idempotent: can be run multiple times safely
- Never modify existing tasks in todos.md

## Sync Implementation

Use external Python script for security and maintainability:

```bash
# Execute sync script
python3 ~/.claude/utils/todo_sync.py

# Script handles:
# 1. Load and validate tasks.yml
# 2. Extract pending tasks
# 3. Get max task ID from last 100 lines (O(1) optimization)
# 4. Filter new tasks (ID > max_id, assumes sequential IDs)
# 5. Validate task IDs (task-\d+ pattern)
# 6. Sanitize goal text
# 7. Quote metadata with shlex.quote (prevent injection)
# 8. Append new tasks to todos.md
# 9. Report results

# Performance optimization:
# - N+1 problem solved: read last 100 lines instead of full file
# - 100x faster for large task lists (10,000+ tasks)
# - Assumes task IDs are sequential (task-1, task-2, ...)

# Security features:
# - Task ID validation (rejects invalid patterns)
# - shlex.quote on priority/effort (prevents command injection)
# - sanitize_goal on task description
# - Safe error messages (no path exposure)
```

Auto-create empty tasks.yml if missing:

```bash
if [ ! -f "tasks.yml" ]; then
  echo "WARNING: tasks.yml not found. Creating empty file..."

  cat > tasks.yml << 'EOF'
project:
  name: "Project Tasks"
  last_updated: ""

tasks: []
EOF

  echo "Created empty tasks.yml"
  echo "No tasks to sync (tasks.yml is empty)"
  exit 0
fi
```

## Next Implementation

Use external Python script for consistency:

```bash
# Execute next task finder
python3 ~/.claude/utils/todo_next.py

# Script outputs:
# - Big tasks: NEXT_TASK_ID:task-N / PRIORITY:X / EFFORT:Y / DESCRIPTION:...
# - Lightweight tasks: "Next task (lightweight): ..."

# Claude should:
# 1. Parse output
# 2. If big task (NEXT_TASK_ID present): use AskUserQuestion for /implement confirmation
# 3. If lightweight task: display to user
```

Error handling:

```bash
if [ ! -f "todos.md" ]; then
  echo "ERROR: todos.md not found"
  echo "Run '/todo sync' to import tasks or '/todo add' to create tasks"
  exit 1
fi
```

## Date Parsing

Parse natural language dates:
- Detect OS date command (BSD for macOS, GNU for Linux)
- tomorrow: next day
- next week: 7 days later
- in N days: N days later
- YYYY-MM-DD: use as-is

Cache OS detection in environment variable for performance

## Error Handling

Use safe_error_message from todo_validation.py for all errors:

```python
from todo_validation import safe_error_message

try:
    # operation
except Exception as e:
    print(safe_error_message(e, "operation context"))
```

Error handling rules:
- If no write permission: report permission error, suggest checking directory permissions
- If invalid arguments: report error with usage example
- If file not found: create new todos.md file
- If security validation fails: report error type without exposing system details
- If file too large (>1MB): report size limit error

Error codes:
- 0: Success
- 1: User error (invalid arguments, permission denied)
- 2: Security error (injection, path traversal)
- 3: File too large
- 4: Unrecoverable error

Security:
- Never expose absolute paths (use safe_error_message)
- Never expose stack traces (first line only)
- Never expose internal system details
- Report only user-actionable information

## Examples

Input: /todo add "Fix authentication bug" --priority high --context api --due tomorrow
Action: Add high-priority API task with tomorrow due date

Input: /todo complete 1
Action: Mark task 1 as completed

Input: /todo uncomplete 1
Action: Revert task 1 to incomplete status

Input: /todo remove 2
Action: Delete task 2 from todos.md

Input: /todo list --filter priority:high --sort due
Action: List high-priority tasks sorted by due date

Input: /todo
Action: Interactive mode - prompt for action selection

Input: /todo next
Action: Show next priority task based on due date and priority
