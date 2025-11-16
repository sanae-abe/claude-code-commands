# Slash Command Security Implementation Template

Use this template to add security validation to slash commands.

## Template: Security Implementation Section

Add this section after the main subcommands documentation:

```markdown
## Security Implementation

**MANDATORY: Execute these validations BEFORE ANY operation**

```bash
# 1. Validate arguments (customize validation logic for your command)
validate_arguments() {
  local arg="$1"

  # Reject dangerous characters
  if [[ "$arg" =~ [;\`\$\(\)] ]]; then
    echo "ERROR: Invalid characters detected"
    exit 2
  fi

  # Add command-specific validation here
  # Example: validate against whitelist
  # Example: check path constraints
  # Example: validate format patterns
}

# 2. Sanitize user input
sanitize_input() {
  local input="$1"

  # Remove dangerous characters
  input="${input//[^a-zA-Z0-9_-]/}"

  # Or: escape for safe use in commands
  # input=$(printf '%q' "$input")

  echo "$input"
}

# 3. Validate file paths (if applicable)
validate_path() {
  local path="$1"

  # Reject directory traversal
  if [[ "$path" =~ \.\. ]]; then
    echo "ERROR: Path traversal detected"
    exit 2
  fi

  # Validate path prefix (customize for your command)
  if [[ ! "$path" =~ ^expected/prefix/ ]]; then
    echo "ERROR: Path must start with expected/prefix/"
    exit 2
  fi

  # Verify path exists (if needed)
  if [[ ! -e "$path" ]]; then
    echo "ERROR: Path not found: $path"
    exit 1
  fi
}

# 4. Parse arguments safely with IFS
IFS=' ' read -r -a args <<< "$ARGUMENTS"

# Extract and validate
ARG1="${args[0]}"
ARG2="${args[1]}"

validate_arguments "$ARG1"

# Sanitize before use
SAFE_ARG=$(sanitize_input "$ARG2")
```

## Exit Code System

Standardize exit codes across all commands:

```bash
# 0: Success
# 1: User error (invalid arguments, missing files)
# 2: Security error (validation failure, permission denied)
# 3: System error (command not found, network failure)
# 4: Unrecoverable error (data corruption, critical failure)
```

## Bash Syntax Examples

Standard patterns for safe argument parsing:

```bash
# Safe IFS usage for argument parsing
IFS=' ' read -r -a args <<< "$ARGUMENTS"

# Safe parameter expansion
BRANCH_TYPE="${CURRENT_BRANCH%%/*}"  # Extract prefix before /
FILE_EXT="${FILENAME##*.}"            # Extract extension after .
PATH_DIR="${FULL_PATH%/*}"            # Extract directory
PATH_BASE="${FULL_PATH##*/}"          # Extract basename

# Safe array iteration
for arg in "${args[@]}"; do
  case "$arg" in
    --flag=*)
      VALUE="${arg#*=}"
      ;;
  esac
done

# Exit code propagation
some_command
RESULT=$?
if [[ $RESULT -ne 0 ]]; then
  echo "ERROR: Command failed"
  exit $RESULT
fi
```
```

## Error Message Format Template

Add this section for standardized error output:

```markdown
## Output Format

**Success example**:
```
✓ Operation completed successfully
✓ Validation: PASSED

Next steps:
  1. [First action]
  2. [Second action]
```

**Error example**:
```
ERROR: [Error category]
File: [command-name.md:function_name]

Reason: [Specific cause with details]
Got: [Actual problematic value]

Suggestions:
1. [First suggested fix]
2. [Alternative approach]
3. [Help/documentation reference]
```
```

## Integration Steps

1. **Add Security Implementation section** after main documentation
2. **Update Execution Flow** to reference security functions
3. **Add Output Format Examples** with ✓ emojis and file:line references
4. **Standardize exit codes** using the 4-level system

## Quality Checklist

After adding security implementation:

- [ ] Bash syntax examples present (IFS, parameter expansion)
- [ ] Error handling patterns shown
- [ ] Exit code propagation documented
- [ ] Input validation examples provided
- [ ] Security functions defined
- [ ] Output format examples with visual elements
- [ ] file:line references in error messages
- [ ] Suggestions provided for common errors
- [ ] User-actionable guidance present
