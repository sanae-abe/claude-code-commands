---
allowed-tools: TodoWrite, SlashCommand, Read, Write, Bash
argument-hint: "<task-name> [--perspectives=security,performance,maintainability] [--rounds=2] [--format=detailed|compact]"
description: Create implementation plan, review with iterative-review, update todo.md
model: sonnet
---

# plan-review

Arguments: $ARGUMENTS

## Execution Flow

1. Parse arguments from $ARGUMENTS
2. Validate all arguments
3. Create task breakdown using TodoWrite
4. Generate plan.md with task details
5. Execute /iterative-review on plan.md
6. Parse review results
7. Update todo.md via /todo add commands
8. Generate final report

## Argument Validation

Parse $ARGUMENTS to extract:
- Task name (required, first token or quoted string)
- --perspectives flag (optional, default: security,performance,maintainability)
- --rounds flag (optional, default: 2, range: 1-5)
- --format flag (optional, default: detailed, values: detailed|compact)

Validation rules:
- Task name: max 500 characters, reject ../ patterns, reject control characters
- Perspectives: validate against allowed list (security, performance, maintainability, accessibility, testing, documentation)
- Rounds: must be integer 1-5
- Format: must be "detailed" or "compact"

If task name missing: use AskUserQuestion to collect task description
If invalid flag value: report error with allowed values and exit
If invalid format: report expected format and exit

Security:
- Reject path traversal patterns (../, ~/)
- Escape all arguments before passing to SlashCommand
- Use mktemp for temporary files
- Set trap to cleanup temporary files on exit

## Tool Usage

TodoWrite: Create 5-step task list at start:
1. Parse and validate arguments
2. Create task breakdown and plan.md
3. Execute /iterative-review
4. Parse review results
5. Update todo.md and generate report

Update status to "in_progress" before each step
Update status to "completed" after each step

SlashCommand: Execute dependent commands:
- /iterative-review plan.md --skip-necessity --perspectives=$PERSPECTIVES --rounds=$ROUNDS
- /todo add "$TASK_CONTENT" --priority=$PRIORITY --depends-on="$DEPENDENCY"

Bash: File operations and validation:
- Create temporary plan.md using mktemp
- Validate git repository if needed
- Execute jq for JSON config parsing

## Task Breakdown Process

Use TodoWrite to structure tasks:
1. Identify main task components from task name
2. Determine dependencies between components
3. Estimate time using three-point estimation (optimistic, most-likely, pessimistic)
4. Assign priority (high, medium, low)
5. Generate plan.md with structured task list

Plan.md format:
```
# Implementation Plan: [TASK_NAME]

## Tasks
1. [Task 1] - [estimate], priority: [high/medium/low], depends: [none/task-id]
2. [Task 2] - [estimate], priority: [high/medium/low], depends: [task-id]

## Dependencies
Task 1 -> Task 2

## Initial Risk Assessment
- Security: [initial concerns]
- Performance: [initial concerns]
- Maintainability: [initial concerns]
```

## Review Integration

Execute /iterative-review with --skip-necessity flag:
- Skip necessity evaluation (assume feature is needed)
- Focus on security, performance, maintainability improvements
- Generate actionable recommendations

Parse review results:
- Extract Critical issues (must fix)
- Extract Important issues (should fix)
- Extract Minor issues (nice to have)
- Identify new tasks from recommendations
- Update time estimates based on review findings

## Todo Update Process

For each task from plan and review results:
1. Determine task content
2. Assign priority based on review severity (Critical -> high, Important -> medium, Minor -> low)
3. Identify dependencies
4. Execute /todo add with appropriate flags

Handle batch updates:
- If 5+ tasks: execute /todo add commands sequentially
- Track success/failure of each add operation
- If any add fails: save remaining tasks to plan-final.md

## Report Generation

Detailed format (default):
- Task breakdown with estimates
- Review results summary (Critical/Important/Minor counts)
- Priority action plan
- Execution timeline
- Next steps

Compact format (--format=compact):
- Task count and total estimate
- Critical/Important issues only
- Top 3 priority actions
- Next immediate step

## Error Handling

Argument validation:
If task name missing: use AskUserQuestion with prompt "Enter task description:"
If invalid perspectives: report "Invalid perspective. Allowed: security, performance, maintainability, accessibility, testing, documentation"
If invalid rounds: report "Invalid rounds value. Must be integer 1-5"
If invalid format: report "Invalid format. Must be: detailed or compact"

Execution errors:
If /iterative-review fails: report "/iterative-review failed. Plan saved to plan.md for manual review"
If /todo add fails: report "/todo add failed. Tasks saved to plan-final.md for manual update"
If plan.md creation fails: report "Failed to create plan.md" and exit
If config file invalid JSON: report "Config file invalid JSON format. Using defaults"

Dependency errors:
If /iterative-review command not found: report "/iterative-review command not available. Install iterative-review.md"
If /todo command not found: report "/todo command not available. Install todo.md"

Security:
Never expose absolute paths in error messages
Never expose stack traces
Report only user-actionable information

## Configuration File

Optional configuration: project/.claude/plan-review.json

Expected format:
```json
{
  "defaultPerspectives": ["security", "performance", "maintainability"],
  "defaultRounds": 2,
  "defaultFormat": "detailed",
  "autoUpdateTodo": true
}
```

If config file exists:
1. Validate JSON format using jq
2. Validate field types and values
3. Apply settings if valid
4. Report warning and use defaults if invalid

## Examples

Input: /plan-review "User authentication feature"
Action: Create plan for authentication feature, review with default perspectives (security, performance, maintainability) for 2 rounds, update todo.md with detailed report

Input: /plan-review "API cache layer" --perspectives=security,performance
Action: Create plan for cache layer, review with security and performance only, update todo.md

Input: /plan-review "Button component refactor" --rounds=1 --format=compact
Action: Create plan for refactor, quick 1-round review, update todo.md with compact summary

Input: /plan-review
Action: Use AskUserQuestion to collect task description, then execute with defaults

Input: /plan-review "Large feature" --perspectives=invalid
Action: Report error: "Invalid perspective. Allowed: security, performance, maintainability, accessibility, testing, documentation" and exit
