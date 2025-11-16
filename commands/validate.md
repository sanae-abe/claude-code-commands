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

# Verify pipeline exists
PIPELINE_PATH="$HOME/projects/claude-code-workspace/validation/pipeline.sh"
if [[ ! -x "$PIPELINE_PATH" ]]; then
    echo "Error: Quality gate pipeline not found at $PIPELINE_PATH"
    exit 1
fi

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
REPORT_FILE="/tmp/quality-gate-report.json"
REPORT_GENERATOR="$HOME/projects/claude-code-workspace/validation/utils/report-generator.py"

if [[ -f "$REPORT_FILE" ]] && [[ -f "$REPORT_GENERATOR" ]]; then
    if [[ "$REPORT_FORMAT" == "json" ]]; then
        python3 "$REPORT_GENERATOR" "$REPORT_FILE" --format=json
    else
        python3 "$REPORT_GENERATOR" "$REPORT_FILE"
    fi
else
    if [[ ! -f "$REPORT_FILE" ]]; then
        echo "⚠️  Report generation failed: Report file not found"
    fi
    if [[ ! -f "$REPORT_GENERATOR" ]]; then
        echo "⚠️  Report generation failed: Generator script not found"
    fi
fi

exit $VALIDATION_RESULT
```

## User Guidance

If validation fails:
1. Show specific errors with file:line references
2. Suggest fixes (manual or --auto-fix)
3. Link to relevant documentation

Example output:
```
❌ Quality Gate Report
════════════════════════════════════════

❌ Layer 2: Format Validation - FAILED
  Errors:
    tasks.yml:5 - Markdown code block detected

  Suggestions:
    Run with --auto-fix: /validate --auto-fix
    Or manually remove ```yaml blocks

✅ Layer 5: Security Validation - PASSED
  No security issues detected

════════════════════════════════════════
Total Gates: 5
Passed: 4
Failed: 1

💡 Fix errors and re-run validation
```

## Security Considerations

- Pipeline script validates all input arguments
- No user input passed directly to shell commands
- All file paths validated before execution
- Reports generated in secure temporary location

## Performance Optimization

- Parallel gate execution (future enhancement)
- npm audit caching (future enhancement)
- Early exit on critical failures (--stop-on-failure)

## Examples

**Basic validation**:
```
/validate
```

**Security-only check**:
```
/validate --layers=security
```

**Syntax check with auto-fix**:
```
/validate --layers=syntax --auto-fix
```

**Full validation with JSON output**:
```
/validate --layers=all --report=json
```

**Multiple layers**:
```
/validate --layers=syntax,security --auto-fix
```
