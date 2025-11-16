---
allowed-tools: Read, Grep, Glob, TodoWrite, AskUserQuestion
argument-hint: "<file-path> [--report=text|json]"
description: Evaluate LLM implementation quality of CLAUDE.md or slash commands
model: sonnet
---

# review-quality

Arguments: $ARGUMENTS

## Purpose

Quantitatively evaluate whether documentation/commands are optimized for LLM implementation quality using a standardized framework.

## Evaluation Framework

### Three Quality Dimensions

1. **Accuracy (正確性)**: 90%+ probability of correct implementation
2. **Maintainability (保守性)**: Code withstands future modifications
3. **Usability (ユーザビリティ)**: Users understand errors when they occur

### Scoring Criteria

| Score | Accuracy | Maintainability | Usability | Overall |
|-------|----------|-----------------|-----------|---------|
| 95-100% | Excellent | Excellent | Excellent | ✅ Optimal |
| 90-94% | Good | Good | Good | ✅ Acceptable |
| 85-89% | Fair | Fair | Fair | ⚠️ Needs Improvement |
| <85% | Poor | Poor | Poor | ❌ Inadequate |

## Execution Flow

1. Parse arguments (file path, report format)
2. Identify target type (CLAUDE.md, slash command, other)
3. Apply type-specific evaluation criteria
4. Generate quality score with evidence
5. Provide actionable improvement suggestions

## Evaluation Criteria by Type

### For Slash Commands

**Accuracy Evaluation**:
- [ ] Bash syntax examples present (IFS, parameter expansion, etc.)
- [ ] Error handling patterns shown
- [ ] Exit code propagation documented
- [ ] Input validation examples provided

**Maintainability Evaluation**:
- [ ] Code examples use standard patterns
- [ ] Validation functions defined
- [ ] Security considerations explicit
- [ ] No code duplication between sections

**Usability Evaluation**:
- [ ] Output format examples with visual elements
- [ ] Error messages include file:line references
- [ ] Suggestions provided for common errors
- [ ] User-actionable guidance present

**Scoring**:
- All criteria met: 95%+
- 75-90% criteria met: 90-94%
- 50-74% criteria met: 85-89%
- <50% criteria met: <85%

### For CLAUDE.md

**Accuracy Evaluation**:
- [ ] Concrete implementation instructions (not abstract principles)
- [ ] Specific examples for complex operations
- [ ] Decision trees with clear conditions
- [ ] No ambiguous "should/consider" without specifics

**Maintainability Evaluation**:
- [ ] Structured format (YAML, tables, code blocks)
- [ ] External references instead of duplication
- [ ] Version-controlled patterns
- [ ] Clear section hierarchy

**Usability Evaluation**:
- [ ] LLM-focused (no user-facing instructions)
- [ ] Token-efficient (no redundant examples)
- [ ] Clear priorities (MUST vs SHOULD vs MAY)
- [ ] Actionable steps (not explanations)

## Risk Assessment

For each low-scoring dimension, identify:

**Impact**:
- Accuracy <90%: LLM generates incorrect code
- Maintainability <90%: Future edits break functionality
- Usability <90%: Users cannot debug issues

**Mitigation**:
- Add concrete examples
- Define validation functions
- Provide output templates
- Remove ambiguous language

## Output Format

```
🔍 LLM Implementation Quality Report

File: <file-path>
Type: <CLAUDE.md / Slash Command / Other>
Date: <YYYY-MM-DD>

═══════════════════════════════════════
Quality Scores
═══════════════════════════════════════

✅/⚠️/❌ Accuracy:        XX% (Good/Fair/Poor)
✅/⚠️/❌ Maintainability: XX% (Good/Fair/Poor)
✅/⚠️/❌ Usability:       XX% (Good/Fair/Poor)

Overall: XX% - Optimal/Acceptable/Needs Improvement/Inadequate

═══════════════════════════════════════
Detailed Findings
═══════════════════════════════════════

Accuracy (XX%):
  ✅ Bash syntax examples present
  ❌ Missing error handling patterns
  ⚠️ Exit code propagation partially documented

Maintainability (XX%):
  ✅ Standard patterns used
  ❌ Code duplication in sections X and Y

Usability (XX%):
  ✅ Output format examples present
  ❌ Error messages lack file:line references

═══════════════════════════════════════
Priority Recommendations
═══════════════════════════════════════

HIGH (Critical for quality):
1. Add error handling patterns (lines XX-XX)
   Impact: Accuracy +10%
   Example: [concrete code example]

2. Remove code duplication (lines XX, YY)
   Impact: Maintainability +5%
   Action: Move to shared section

MEDIUM (Quality improvement):
3. Add file:line references to errors
   Impact: Usability +5%
   Pattern: "file:line - description"

═══════════════════════════════════════
Token Efficiency Analysis
═══════════════════════════════════════

Current lines: XXX
Redundant content: XX lines (X%)
Optimal target: XXX lines

Suggested deletions:
- Lines XX-XX: User-facing instructions (move to USER_GUIDE.md)
- Lines XX-XX: Duplicate examples (consolidate)
```

## Implementation

```bash
# Parse arguments
TARGET_FILE=""
REPORT_FORMAT="text"

IFS=' ' read -r -a args <<< "$ARGUMENTS"

for arg in "${args[@]}"; do
    case "$arg" in
        --report=*)
            REPORT_FORMAT="${arg#*=}"
            ;;
        *)
            if [[ -z "$TARGET_FILE" ]]; then
                TARGET_FILE="$arg"
            fi
            ;;
    esac
done

# Validate target
if [[ -z "$TARGET_FILE" ]]; then
    echo "ERROR: No target file specified"
    echo "Usage: /review-quality <file-path> [--report=text|json]"
    exit 1
fi

if [[ ! -f "$TARGET_FILE" ]]; then
    echo "ERROR: File not found: $TARGET_FILE"
    exit 1
fi

# Identify type
if [[ "$TARGET_FILE" == *"CLAUDE.md" ]]; then
    TARGET_TYPE="CLAUDE.md"
elif [[ "$TARGET_FILE" == *.md ]] && [[ "$TARGET_FILE" == *"/commands/"* ]]; then
    TARGET_TYPE="slash-command"
else
    TARGET_TYPE="other"
fi

# Apply evaluation criteria
# [Use Read tool to analyze file]
# [Apply checklist based on TARGET_TYPE]
# [Generate scores and recommendations]

# Output report
# [Format according to REPORT_FORMAT]
```

## Examples

```bash
# Evaluate slash command
/review-quality ~/.claude/commands/validate.md

# Evaluate CLAUDE.md with JSON output
/review-quality ~/.claude/CLAUDE.md --report=json

# Evaluate project-specific CLAUDE.md
/review-quality .claude/CLAUDE.md
```

## Integration with Workflows

**Before committing changes**:
```bash
/review-quality ~/.claude/commands/my-command.md
# Review scores and apply recommendations
```

**During iterative-review**:
```bash
/iterative-review proposal.md
# Then validate quality:
/review-quality proposal.md
```

## Exit Code System

```bash
# 0: Success - Quality review completed, score calculated
# 1: User error - File not found, invalid file type
# 2: Security error - Path traversal detected, validation failure
# 3: System error - Read tool failed, grep unavailable
# 4: Unrecoverable error - Critical review failure
```

## Bash Syntax Examples

```bash
# Safe file path validation
TARGET_FILE="$ARGUMENTS"
if [[ "$TARGET_FILE" =~ \.\. ]]; then
  echo "ERROR: Path traversal detected"
  exit 2
fi

# Safe parameter expansion for file type detection
if [[ "$TARGET_FILE" == *"CLAUDE.md" ]]; then
  TARGET_TYPE="CLAUDE.md"
elif [[ "$TARGET_FILE" == *.md ]] && [[ "$TARGET_FILE" == *"/commands/"* ]]; then
  TARGET_TYPE="slash-command"
fi

# Safe IFS usage
IFS=' ' read -r -a args <<< "$ARGUMENTS"
TARGET_FILE="${args[0]}"
REPORT_FORMAT="${args[1]:-text}"  # Default to text
```

## Performance Notes

- File size <10KB: <5 seconds
- File size 10-50KB: 5-15 seconds
- Uses Read + Grep (no external tools)
