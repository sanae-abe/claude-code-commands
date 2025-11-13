---
allowed-tools: TodoWrite, Bash, Read, AskUserQuestion, SlashCommand
argument-hint: "[--scope] [--layers] [--auto-fix] [--report]"
description: "Validate task completion with multi-layer quality gates (syntax, security, integration)"
model: sonnet
---

# task-validate

Arguments: $ARGUMENTS

## Execution Flow

1. Parse and validate arguments from $ARGUMENTS
2. Check git status and changes
3. Load configuration (if exists)
4. Execute layer-based validation (if --layers specified)
5. Prompt user for confirmation (unless --report-only)
6. Execute validation commands based on scope
7. Parse validation results
8. Check todo.md status via /todo list
9. Generate multi-layer report (text or json)
10. Auto-proceed to next task (if --auto-proceed and no errors)

## Argument Validation

Parse $ARGUMENTS to extract:
- --scope flag (optional, default: all, values: all|lint|test|build)
- --layers flag (optional, default: all, values: syntax|security|integration|all)
- --auto-fix flag (optional, boolean)
- --report flag (optional, default: text, values: text|json)
- --report-only flag (optional, boolean)
- --auto-proceed flag (optional, boolean)

### Input Validation Implementation

Execute validation before any operations:

```bash
# Sanitize and validate scope
safe_validate_scope() {
    local scope="$1"
    case "$scope" in
        all|lint|test|build) echo "$scope" ;;
        *) echo "Error: Invalid scope '$scope'. Allowed: all, lint, test, build" >&2
           exit 1 ;;
    esac
}

# Sanitize and validate layers (max 10, max 20 chars each)
safe_validate_layers() {
    local layers="$1"
    local max_layers=10
    local max_layer_length=20

    # Remove special characters (keep alphanumeric, comma, hyphen)
    layers=$(echo "$layers" | sed 's/[^a-zA-Z0-9,_-]//g')

    IFS=',' read -ra LAYER_ARRAY <<< "$layers"

    if [[ ${#LAYER_ARRAY[@]} -gt $max_layers ]]; then
        echo "Error: Too many layers (max $max_layers)" >&2
        exit 1
    fi

    for layer in "${LAYER_ARRAY[@]}"; do
        if [[ ${#layer} -gt $max_layer_length ]]; then
            echo "Error: Layer name too long: '$layer' (max $max_layer_length chars)" >&2
            exit 1
        fi
        case "$layer" in
            syntax|security|integration|all) ;;
            *) echo "Error: Invalid layer '$layer'. Allowed: syntax, security, integration, all" >&2
               exit 1 ;;
        esac
    done

    echo "$layers"
}

# Validate report format
safe_validate_report() {
    local report="$1"
    case "$report" in
        text|json) echo "$report" ;;
        *) echo "Error: Invalid report format '$report'. Allowed: text, json" >&2
           exit 1 ;;
    esac
}
```

Validation rules:
- Scope: must be one of: all, lint, test, build
- Layers: comma-separated list from: syntax, security, integration, all
  - Maximum 10 layers
  - Maximum 20 characters per layer name
- Report: must be text or json
- Flags: boolean values only

Examples:
- `--layers=security` → Layer 5 only
- `--layers=syntax,security` → Layer 1-2 + Layer 5
- `--layers=all` → All 3 layer categories

If invalid scope: report error and exit
If invalid layers: report error and exit
If invalid flag format: report expected format and exit

## Security: Argument Escaping

Before executing any Bash command with user input:

```bash
# Escape special characters for safe command execution
safe_escape() {
    printf '%s' "$1" | sed "s/[^a-zA-Z0-9,._-]//g"
}

# Usage example
scope=$(safe_escape "$scope")
layers=$(safe_escape "$layers")

# Never use user input directly in:
# - Command substitution: $(user_input)
# - Eval: eval "$user_input"
# - Unquoted variables: command $user_input
```

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

## Layer-Based Validation

### Layer 5: Security (security)

Execute when --layers includes "security" or "all":

**Validation items**:
- .env file change detection
- Credential hardcoding scan
- OWASP Top 10 checks

**Execution**:
```bash
# .env change detection
~/.claude/validation/check-env-changes.sh

# Credential scan with secure temp file
SCAN_FILE=$(mktemp /tmp/security-scan.XXXXXX.json)
trap "rm -f $SCAN_FILE" EXIT

# Multi-pattern security scan (single pass)
rg --json \
   -e "(api_key|secret|password|token)\s*=\s*[\"'][^\"']{8,}[\"']" \
   -e "SELECT.*\+.*req\.(body|params|query)" \
   -e "AKIA[0-9A-Z]{16}" \
   -e "AIza[0-9A-Za-z_-]{35}" \
   -e "-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----" \
   --type typescript --type javascript \
   --glob '!node_modules/**' --glob '!dist/**' \
   --timeout 5s \
   > "$SCAN_FILE"
```

**Result parsing**:
- Parse check-env-changes.sh exit code: 0=pass, 1=critical failure
- Parse security-scan.json for findings
- Categorize by severity: Critical, High, Medium

### Layer 1-2: Syntax & Format (syntax)

Execute when --layers includes "syntax" or "all":

**Validation items**:
- TypeScript type checking
- ESLint
- Prettier

**Execution**:
```bash
# TypeScript
npx tsc --noEmit

# ESLint
npx eslint . --ext .ts,.tsx,.js,.jsx

# Prettier (check only)
npx prettier --check "src/**/*.{ts,tsx,js,jsx}"
```

**--auto-fix support**:
```bash
# Prettier auto-fix
npx prettier --write "src/**/*.{ts,tsx,js,jsx}"

# ESLint auto-fix
npx eslint . --ext .ts,.tsx,.js,.jsx --fix
```

### Layer 3-4: Integration (integration)

Execute when --layers includes "integration" or "all":

**Validation items**:
- Test coverage

**Execution**:
```bash
# Test coverage
npm test -- --coverage --coverageReporters=json-summary
```

## Validation Process

Check git status first:
1. Execute git rev-parse --git-dir to verify git repository
2. Execute git status to get working tree state
3. Execute git diff --stat to get change statistics

If not in git repository: report "Not in git repository" and exit

Execute layer validations (if --layers specified):
1. Parse --layers argument to determine which layers to run
2. Execute each layer validation
3. Collect results with severity categorization
4. Continue to scope-based validation

Load configuration (optional):
1. Check if project/.claude/task-validate.json exists
2. Validate file is within project directory (reject symlinks outside project)
3. If exists: parse JSON and extract commands
4. Validate command format before use
5. Use defaults if file not found or invalid

### Configuration Security

```bash
# Validate config file path
validate_config_path() {
    local config_path="project/.claude/task-validate.json"
    local real_path=$(realpath "$config_path" 2>/dev/null)
    local project_root=$(pwd)

    if [[ ! "$real_path" =~ ^"$project_root" ]]; then
        echo "Error: Config file must be within project directory" >&2
        exit 1
    fi

    echo "$config_path"
}

# Validate command format (whitelist npm/yarn/pnpm/bun)
validate_command() {
    local cmd="$1"
    if [[ ! "$cmd" =~ ^(npm|yarn|pnpm|bun)\ (run|test|build|lint) ]]; then
        echo "Error: Invalid command format. Only npm/yarn/pnpm/bun commands allowed" >&2
        exit 1
    fi
    echo "$cmd"
}
```

Configuration format:
```json
{
  "buildCommand": "npm run build",
  "testCommand": "npm test",
  "lintCommand": "npm run lint",
  "confirmBeforeRun": true,
  "layers": {
    "syntax": {
      "typescript": true,
      "eslint": true,
      "prettier": true
    },
    "security": {
      "envCheck": true,
      "credentialScan": true,
      "owaspScan": true,
      "patterns": "~/.claude/validation/security-patterns.json"
    },
    "integration": {
      "testCoverage": {
        "enabled": true,
        "threshold": 80
      }
    }
  }
}
```

User confirmation (skip if --report-only):
1. Display commands to execute
2. AskUserQuestion: ["Continue", "Cancel"]
3. If Cancel: exit

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

Extract: relative file path, line number, column, error code, message

ESLint errors format:
```
/path/to/file.tsx
  42:5  error  Message  rule-name
```

Extract: relative file path, line number, column, severity, message, rule

Test failures format (Jest/Vitest):
```
FAIL src/component.test.tsx
  Test suite failed to run
    Message
```

Extract: relative file path, failure message

### Error Output Sanitization

Sanitize all error messages before displaying:

```bash
sanitize_error() {
    local error_output="$1"
    # Strip absolute paths to relative
    error_output="${error_output//$HOME/~}"
    error_output="${error_output//$PWD/.}"
    # Remove stack traces
    echo "$error_output" | grep -v "^    at " | head -20
}

# Usage
if ! npm test 2>&1 | tee /tmp/test-output.txt; then
    sanitized=$(sanitize_error "$(cat /tmp/test-output.txt)")
    echo "$sanitized"
    rm -f /tmp/test-output.txt
fi
```

Path normalization:
- Convert absolute paths to relative: /Users/x/project/src/file.ts → src/file.ts
- Strip home directory: /Users/x → ~
- Remove stack traces from error output

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

### Text Format (default)

Success report:
```
Multi-Layer Validation Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Layer 5: Security
✅ .env files: Not staged
✅ Credential scan: No hardcoded secrets
✅ OWASP scan: No vulnerabilities

Layer 1-2: Syntax & Format
✅ TypeScript: No errors
✅ ESLint: No issues
✅ Prettier: Formatted

Scope Validation:
✅ Build: Success (12.3s)
✅ Tests: Passed (42/42)
✅ Linter: No issues

Summary: All Checks Passed

Todo Status: 3/5 tasks completed
Next: "Error handling implementation"
```

Error report:
```
Multi-Layer Validation Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Layer 5: Security
❌ CRITICAL: 1 issue found
  - .env.local changed (staged)
  Recommendation: git reset HEAD .env.local

Layer 1-2: Syntax & Format
❌ TypeScript: 2 errors

Error Details:
src/components/Button.tsx:42
  Type error TS2339: Property 'onClick' does not exist
  Fix: Add 'onClick' property to ButtonProps interface

src/utils/api.ts:15
  Type error: Argument type mismatch
  Fix: Convert string to number using Number()

Summary: 1 Critical Issue, 2 Type Errors

Priority Actions:
1. Fix .env.local staging issue
2. Fix src/components/Button.tsx:42
3. Fix src/utils/api.ts:15
4. Re-validate: /task-validate --layers=all
```

### JSON Format (--report=json)

Structured output for CI/CD integration. See test fixtures for full format examples.

Basic structure:
```json
{
  "timestamp": "2025-01-14T10:00:00Z",
  "layers": {
    "security": {"status": "pass"},
    "syntax": {"status": "fail", "errors": [...]}
  },
  "summary": {"overall_status": "fail", "critical_issues": 1},
  "next_actions": [...]
}
```

## Error Handling

Argument validation:
If required argument missing: use AskUserQuestion or report required format
If invalid format: report expected format with example

Git validation:
If not in git repository: report "Not in git repository. Initialize git or navigate to git repository" and exit
If git command fails: report sanitized error message

Configuration errors:
If config file exists but invalid JSON: report "Config file invalid JSON. Using defaults"
If config file outside project: report "Config file must be within project directory" and exit
If config has invalid commands: report "Invalid command in config" and use defaults

Command execution errors:
If npm command not found: report "npm not found. Install Node.js and npm"
If package.json missing: report "package.json not found. Initialize npm project"
If script not defined: report "Script not found in package.json. Define [script-name] script"

Todo integration errors:
If /todo command not found: report "/todo command not available" and skip todo integration
If todo.md not found: report "todo.md not found. Create with /todo project"

Security:
Never expose absolute file paths (convert to relative)
Never expose stack traces (filter with grep -v)
Never execute commands without validation
Validate all user input before passing to Bash

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
1. Validate path is within project directory
2. Validate JSON format
3. Validate command strings (whitelist npm/yarn/pnpm/bun only)
4. Apply settings if valid
5. Use defaults if invalid

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

Input: /task-validate --layers=security
Action: Execute Layer 5 security validation only (env check, credential scan, OWASP scan)

Input: /task-validate --layers=syntax --auto-fix
Action: Execute Layer 1-2 syntax validation with automatic fixes (Prettier, ESLint)

Input: /task-validate --layers=all --report=json
Action: Execute all layers, output JSON format for CI/CD integration

Input: /task-validate --layers=security --scope=build
Action: Execute security layer + build validation

Input: /task-validate --layers=syntax,security
Action: Execute syntax and security layers only (skip integration layer)
