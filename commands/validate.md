---
allowed-tools: Bash, Read, TodoWrite, AskUserQuestion
argument-hint: "[--layers=all|syntax,security] [--auto-fix] [--report=text|json]"
description: Multi-layer quality gate validation with auto-fix support
model: sonnet
---

# validate

Arguments: $ARGUMENTS

## Execution Flow

1. Parse arguments (layers, auto-fix, report format)
2. Run quality gate pipeline: `~/projects/claude-code-workspace/validation/pipeline.sh`
3. Parse validation report
4. Display results to user
5. If failures: show actionable suggestions
6. If auto-fix enabled: show what was fixed

## Implementation

```bash
# Parse arguments with safe handling
LAYERS="all"
AUTO_FIX="false"
REPORT_FORMAT="text"

# Split $ARGUMENTS into array safely
IFS=' ' read -r -a args <<< "$ARGUMENTS"

for arg in "${args[@]}"; do
    case "$arg" in
        --layers=*)
            LAYERS="${arg#*=}"
            ;;
        --auto-fix)
            AUTO_FIX="true"
            ;;
        --report=*)
            REPORT_FORMAT="${arg#*=}"
            ;;
        *)
            echo "⚠️  Unknown argument: $arg (ignoring)"
            ;;
    esac
done

# SECURITY: Validate inputs (see Security Implementation section)
validate_layers "$LAYERS"
validate_auto_fix "$AUTO_FIX"

# SECURITY: Resolve paths safely (see Security Implementation section)
resolve_paths
# This sets: WORKSPACE_ROOT, PIPELINE_PATH, REPORT_GENERATOR

# SECURITY: Create secure temp file and verify python3 (see Security Implementation section)
create_secure_temp
check_python3
# This sets: REPORT_FILE with auto-cleanup trap

# Run quality gate pipeline
echo "🔍 Running quality gate validation..."
echo "   Layers: $LAYERS"
echo "   Auto-fix: $AUTO_FIX"
echo ""

if bash "$PIPELINE_PATH" --layers="$LAYERS" --auto-fix="$AUTO_FIX" --stop-on-failure=true; then
    VALIDATION_RESULT=0
else
    VALIDATION_RESULT=$?
fi

# Display report
if [[ -f "$REPORT_FILE" ]]; then
    if [[ "$REPORT_FORMAT" == "json" ]]; then
        python3 "$REPORT_GENERATOR" "$REPORT_FILE" --format=json
    else
        python3 "$REPORT_GENERATOR" "$REPORT_FILE"
    fi
else
    echo "⚠️  Report generation failed: Report file not found"
fi

# Temp file cleanup handled automatically by trap
exit $VALIDATION_RESULT
```

## Output Format

Use this structure with emojis for clarity:

```
❌/✅ Quality Gate Report
════════════════════════════════════════
❌/✅ Layer N: Name - FAILED/PASSED
  Errors: (if failed)
    file:line - description
  Suggestions: (if fixable)
    Run with --auto-fix: /validate --auto-fix
    Or manually fix the reported issues
════════════════════════════════════════
Total Gates: X | Passed: Y | Failed: Z

💡 Fix errors and re-run validation
```

- Show errors with file:line references
- Suggest --auto-fix for fixable errors
- Display summary counts

## Security Implementation

**MANDATORY: Execute these validations BEFORE ANY pipeline execution**

```bash
# 1. Validate layers argument
validate_layers() {
  local layers="$1"
  IFS=',' read -ra layer_array <<< "$layers"

  for layer in "${layer_array[@]}"; do
    case "$layer" in
      all|syntax|security|integration) ;;
      *)
        echo "ERROR: Invalid layer '$layer'"
        echo "Allowed: all, syntax, security, integration (comma-separated)"
        exit 1
        ;;
    esac
  done
}

# 2. Validate auto-fix argument
validate_auto_fix() {
  local auto_fix="$1"
  if [[ "$auto_fix" != "true" && "$auto_fix" != "false" ]]; then
    echo "ERROR: Invalid auto-fix value '$auto_fix'"
    echo "Allowed: true or false"
    exit 1
  fi
}

# 3. Resolve paths safely
resolve_paths() {
  WORKSPACE_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

  if [[ -z "$WORKSPACE_ROOT" ]]; then
    if [[ -d "$HOME/.claude/validation" ]]; then
      WORKSPACE_ROOT="$HOME/.claude"
    else
      echo "ERROR: Not in git repo and ~/.claude/validation not found"
      exit 1
    fi
  fi

  PIPELINE_PATH="${WORKSPACE_ROOT}/validation/pipeline.sh"
  REPORT_GENERATOR="${WORKSPACE_ROOT}/validation/utils/report-generator.py"

  if [[ ! -x "$PIPELINE_PATH" ]]; then
    echo "ERROR: Pipeline not found or not executable: $PIPELINE_PATH"
    exit 1
  fi

  if [[ ! -f "$REPORT_GENERATOR" ]]; then
    echo "ERROR: Report generator not found: $REPORT_GENERATOR"
    exit 1
  fi
}

# 4. Create secure temp file
create_secure_temp() {
  # Use system default secure location (not /tmp)
  REPORT_FILE=$(mktemp)
  trap "rm -f '$REPORT_FILE'" EXIT
}

# 5. Verify python3 availability
check_python3() {
  if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.6+"
    exit 1
  fi
}
```

**Execution order**:
1. validate_layers "$LAYERS"
2. validate_auto_fix "$AUTO_FIX"
3. resolve_paths
4. create_secure_temp
5. check_python3
6. Execute pipeline.sh with validated arguments

## Performance Notes

- Early exit on failures (--stop-on-failure=true)

## Examples

```bash
/validate  # Basic (all layers)
/validate --layers=security --auto-fix  # Security with auto-fix
/validate --layers=syntax,security --report=json  # Multiple layers, JSON output
```
