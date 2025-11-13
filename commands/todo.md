---
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, TodoWrite, Grep, Glob
argument-hint: "[action] [description] | add | complete | list | sync | project | interactive"
description: Simple project task management with interactive UI and priority handling
model: sonnet
---

# Todo Manager

Arguments: $ARGUMENTS

## Execution Flow

1. Parse arguments from $ARGUMENTS
2. Validate and sanitize input (security check)
3. Determine action: add, complete, list, remove, undo, next, or interactive mode
4. Locate or create todos.md file in project root
5. Execute requested action
6. Update todos.md file if modifications made
7. Display results to user

If $ARGUMENTS empty: use AskUserQuestion for interactive mode
If todos.md not found: create new file with empty task list
If validation fails: report error and exit

## Argument Parsing

Parse $ARGUMENTS to extract:
- Action: first token (add, complete, list, remove, undo, next)
- Task description: quoted string for add action
- Task number: integer for complete, remove, undo actions
- Options: --priority, --context, --due, --filter, --sort

Sanitize input:
- Limit length to 1000 characters maximum (DoS protection)
- Extract alphanumeric characters, spaces, and allowed symbols (._:/-)
- Reject invalid input with error message

Validate file paths:
- Resolve absolute path using realpath
- Deny .git directory access
- Verify path within current working directory
- Check 10MB file size limit

## Tool Usage

TodoWrite: Use when processing multiple tasks or complex operations

AskUserQuestion: Use in interactive mode when $ARGUMENTS empty
- Primary action selection: add-task, review-list, quick-complete
- Task priority selection: critical, high, medium, low
- Task context selection: ui, api, docs, test, build, security

Bash: Use for git commands (status, branch, log) and date parsing

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
- Display all tasks or filtered subset
- Apply --filter (priority:X, context:Y)
- Apply --sort (due, priority)
- Show task numbers for reference

remove N | delete N:
- Parse task number N
- Remove task from todos.md

undo N:
- Parse task number N
- Revert completed task to incomplete ([ ])

next:
- Find next priority task considering due date and priority
- Display single task with details

## Date Parsing

Parse natural language dates:
- Detect OS date command (BSD for macOS, GNU for Linux)
- tomorrow: next day
- next week: 7 days later
- in N days: N days later
- YYYY-MM-DD: use as-is

Cache OS detection in environment variable for performance

## Error Handling

If no write permission: report permission error and suggest checking directory permissions
If not git repository: warn but continue (git features limited)
If invalid arguments: report error with usage example
If file not found: create new todos.md file
If security validation fails: report error type without exposing system details
If file too large (>10MB): report size limit error

Error codes:
- 0: Success
- 1: Permission error
- 2: Git not initialized (warning only)
- 3: Invalid arguments
- 4: File not found (auto-create)
- 5: Security error
- 6: File too large

Never expose: absolute paths, stack traces, internal system details

## Examples

Input: /todo add "Fix authentication bug" --priority high --context api --due tomorrow
Action: Add high-priority API task with tomorrow due date

Input: /todo complete 1
Action: Mark task 1 as completed

Input: /todo list --filter priority:high --sort due
Action: List high-priority tasks sorted by due date

Input: /todo
Action: Interactive mode - prompt for action selection

Input: /todo next
Action: Show next priority task based on due date and priority
