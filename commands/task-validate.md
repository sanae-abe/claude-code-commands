---
allowed-tools: TodoWrite, Bash, Read, AskUserQuestion, SlashCommand
argument-hint: "[--scope=all|lint|test|build] [--report-only] [--auto-proceed]"
description: Validate previous task completion, check quality, suggest next action
model: sonnet
---

# task-validate

Arguments: $ARGUMENTS

## Execution Flow

1. Parse arguments from $ARGUMENTS
2. Check git status and changes
3. Load configuration (if exists)
4. Prompt user for confirmation (unless --report-only)
5. Execute validation commands based on scope
6. Parse validation results
7. Check todo.md status via /todo list
8. Generate report with next actions
9. Auto-proceed to next task (if --auto-proceed and no errors)

## Argument Validation

Parse $ARGUMENTS to extract:
- --scope flag (optional, default: all, values: all|lint|test|build)
- --report-only flag (optional, boolean)
- --auto-proceed flag (optional, boolean)

Validation rules:
- Scope: must be one of: all, lint, test, build
- Flags: boolean values only

If invalid scope: report "Invalid scope. Allowed: all, lint, test, build" and exit
If invalid flag format: report expected format and exit

## Tool Usage

TodoWrite: Create 5-step task list at start:
1. Parse arguments and load config
2. Check git status
3. Execute validation commands
4. Parse results and check todo.md
5. Generate report and proceed if needed

Update status to "in_progress" before each step
Update status to "completed" after each step

Bash: Execute validation commands:
- git status: check working directory state
- git diff --stat: get change statistics
- npm run lint: execute linter (if scope includes lint)
- npm test: execute tests (if scope includes test)
- npm run build: execute build (if scope includes build)

AskUserQuestion: Confirm execution before running commands:
- Show commands to be executed
- Request user confirmation (y/N)
- Skip if --report-only flag set

SlashCommand: Execute /todo list to check task status

Read: Load configuration from project/.claude/task-validate.json (if exists)

## Validation Process

Check git status first:
1. Execute git rev-parse --git-dir to verify git repository
2. Execute git status to get working tree state
3. Execute git diff --stat to get change statistics

If not in git repository: report "Not in git repository" and exit

Load configuration (optional):
1. Check if project/.claude/task-validate.json exists
2. If exists: parse JSON and extract commands
3. Use defaults if file not found or invalid

Configuration format:
```json
{
  "buildCommand": "npm run build",
  "testCommand": "npm test",
  "lintCommand": "npm run lint",
  "confirmBeforeRun": true
}
```

Prompt for confirmation (unless --report-only):
1. Display commands to be executed
2. Use AskUserQuestion with options: ["Continue", "Cancel"]
3. If Cancel selected: exit without running commands

Execute validation based on scope:
- scope=lint: execute lintCommand only
- scope=test: execute testCommand only
- scope=build: execute buildCommand only
- scope=all: execute all three commands sequentially

Capture command exit codes and output for each validation

## Result Parsing

Parse validation output to extract errors:

TypeScript errors format:
```
src/file.tsx:42:5 - error TS2339: Message
```

Extract: file path, line number, column, error code, message

ESLint errors format:
```
/path/to/file.tsx
  42:5  error  Message  rule-name
```

Extract: file path, line number, column, severity, message, rule

Test failures format (Jest/Vitest):
```
FAIL src/component.test.tsx
  Test suite failed to run
    Message
```

Extract: file path, failure message

Categorize errors by severity:
- Critical: build failures, type errors
- Important: test failures
- Minor: linter warnings

## Todo Integration

Execute /todo list to get current task status

Parse todo list to identify:
- Completed tasks count
- In-progress tasks
- Next pending task

If errors found: recommend completing current task before proceeding
If no errors and --auto-proceed: mark current task complete and start next

## Report Generation

Success report (no errors):
```
All validations passed

Validation Results:
- Build: Success (12.3s)
- Tests: Passed (42/42)
- Linter: No issues

Todo Status:
- Completed: 3/5 tasks
- Current: "API integration testing"
- Next: "Error handling implementation"

Next Actions:
1. Mark current task complete: /todo complete "API integration testing"
2. Start next task: "Error handling implementation"
```

Error report (errors found):
```
Validation failed (3 errors)

Error Details:

src/components/Button.tsx:42
Type error TS2339: Property 'onClick' does not exist on type 'ButtonProps'
Fix: Add 'onClick' property to ButtonProps interface

src/utils/api.ts:15
Type error: Argument of type 'string' is not assignable to parameter of type 'number'
Fix: Convert string to number using Number()

Next Actions (priority order):
1. Fix src/components/Button.tsx
2. Fix src/utils/api.ts:15
3. Re-validate: /task-validate --scope=build

Todo Status:
- Current task "API integration" is incomplete
- Fix errors before proceeding
```

## Error Handling

Git validation:
If not in git repository: report "Not in git repository. Initialize git or navigate to git repository" and exit
If git command fails: report "Git command failed" with error details

Configuration errors:
If config file exists but invalid JSON: report "Config file invalid JSON. Using defaults"
If config file has invalid command paths: report "Invalid command in config" and use defaults

Command execution errors:
If npm command not found: report "npm not found. Install Node.js and npm"
If package.json missing: report "package.json not found. Initialize npm project"
If script not defined: report "Script not found in package.json. Define [script-name] script"

Todo integration errors:
If /todo command not found: report "/todo command not available" and skip todo integration
If todo.md not found: report "todo.md not found. Create with /todo project"

Security:
Never expose absolute file system paths
Never execute commands without user confirmation (unless --report-only)
Validate all user input before passing to commands

## Configuration File

Optional configuration: project/.claude/task-validate.json

Expected format:
```json
{
  "buildCommand": "npm run build",
  "testCommand": "npm test",
  "lintCommand": "npm run lint",
  "confirmBeforeRun": true
}
```

If config file exists:
1. Validate JSON format
2. Validate command strings (no shell injection patterns)
3. Apply settings if valid
4. Use defaults if invalid

Defaults:
- buildCommand: "npm run build"
- testCommand: "npm test"
- lintCommand: "npm run lint"
- confirmBeforeRun: true

## Examples

Input: /task-validate
Action: Execute all validations (lint, test, build), check todo.md, generate report with next actions

Input: /task-validate --scope=lint
Action: Execute linter only, fast validation for quick checks

Input: /task-validate --scope=test
Action: Execute tests only, verify test coverage

Input: /task-validate --report-only
Action: Generate report without executing commands, based on previous results

Input: /task-validate --auto-proceed
Action: If all validations pass, automatically mark current task complete and start next task

Input: /task-validate --scope=build --auto-proceed
Action: Execute build only, proceed to next task if successful
