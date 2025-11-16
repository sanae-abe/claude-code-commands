---
allowed-tools: AskUserQuestion, TodoWrite
argument-hint: [message] | --no-verify | --amend
description: Create Conventional Commits with emoji formatting through interactive guidance
model: sonnet
---

# Git Commit Command

Create well-formatted commit: $ARGUMENTS

## Execution Flow

1. Parse arguments from $ARGUMENTS
2. If message provided: validate Conventional Commits format and add emoji
3. If no message: use AskUserQuestion to select commit type and scope
4. Generate commit message with appropriate emoji
5. Validate message format (length, structure)
6. Execute git commit with generated message
7. Verify commit created and report next steps

## Argument Validation

Parse $ARGUMENTS:
- Extract message if provided
- Detect flags: --no-verify, --amend
- Validate message format if provided

If message provided:
- Check Conventional Commits format: `type(scope): subject`
- Validate type against allowed list
- Ensure subject length under 72 characters

If validation fails: report error with correct format and examples

## Commit Type Selection

Use AskUserQuestion to determine commit type with emoji:

Question: "Select commit type"
Header: "Type"
Options:
1. feat: New feature (user-facing functionality)
2. fix: Bug fix (user-facing issue resolution)
3. refactor: Code refactoring (no functional changes)
4. docs: Documentation changes only
5. style: Code style changes (formatting, semicolons, etc.)
6. test: Add or modify tests
7. chore: Build, configuration, dependency updates
8. perf: Performance improvements

Each type has associated emoji:
- feat: ✨
- fix: 🐛
- refactor: ♻️
- docs: 📝
- style: 💄
- test: ✅
- chore: 🔧
- perf: ⚡️

## Scope Selection

Use AskUserQuestion to determine scope:

Question: "Select scope (area of change)"
Header: "Scope"
Options:
1. ui: UI components, styling changes
2. api: API, backend, data layer changes
3. core: Core logic, business logic changes
4. config: Configuration, build, tool changes
5. docs: Documentation, comment changes
6. test: Test-related changes
7. none: No specific scope (multiple areas or global changes)

LLM should analyze changed files (via git status/diff) to suggest appropriate scope.

## Message Generation

Based on selected type and scope:

1. Retrieve emoji for type
2. Format message: `<emoji> <type>(<scope>): <subject>`
   - If scope is "none": `<emoji> <type>: <subject>`
3. Validate format:
   - Subject starts with lowercase (except proper nouns)
   - Subject length under 72 characters
   - No period at end of subject

Example generated messages:
- `✨ feat(ui): add user profile editor`
- `🐛 fix(api): resolve authentication timeout`
- `📝 docs: update installation guide`
- `♻️ refactor(core): optimize state management`

## Git Commit Execution

Execute commit with generated message:

```bash
git commit -m "<generated-message>"
```

Flags:
- If --no-verify in $ARGUMENTS: add --no-verify flag (skips pre-commit hooks)
- If --amend in $ARGUMENTS: add --amend flag (amends last commit)

After commit:
- Verify commit created: `git log -1 --oneline`
- Report commit hash and message

## Error Handling

Argument errors:
If invalid format: report "Conventional Commits format required: type(scope): subject"
If unknown type: report "Allowed types: feat, fix, refactor, docs, style, test, chore, perf"
If subject too long: report "Subject must be under 72 characters, got: [length]"

Execution errors:
If no staged files: report "No staged files. Use 'git add' to stage changes first"
If git commit fails: report git error message and suggest resolution
If unrecoverable error: report error type and user-actionable guidance

Security:
Never expose absolute file paths in error messages
Never expose stack traces or internal details
Report only user-actionable information

## Conventional Commits Reference

### Type Definitions

- **feat**: New feature for users (e.g., new UI component, API endpoint)
- **fix**: Bug fix for users (e.g., resolve crash, fix incorrect behavior)
- **refactor**: Code restructuring without functional changes
- **docs**: Documentation only changes (README, comments, guides)
- **style**: Code formatting, whitespace, missing semicolons (no logic change)
- **test**: Adding or modifying tests
- **chore**: Build process, dependencies, tooling, configuration
- **perf**: Performance improvements

### Message Structure

```
<type>(<scope>): <subject>

<optional body>

<optional footer>
```

Examples:
- `✨ feat(ui): add dark mode toggle`
- `🐛 fix(api): handle null response from user service`
- `📝 docs: add API usage examples to README`
- `♻️ refactor(core): extract validation logic to separate module`
- `⚡️ perf(ui): lazy load images in gallery component`

### Best Practices

- Use imperative mood: "add feature" not "added feature"
- Keep subject line under 72 characters
- Separate subject from body with blank line
- Use body to explain what and why, not how
- Reference issues/tickets in footer when applicable

## Integration with Other Commands

After commit:
- `/pr` or `/mr`: Create pull/merge request
- Quality checks: Recommend setting up pre-commit hooks for automated linting, testing

Pre-commit hooks recommendation:
For automated quality checks, configure pre-commit hooks to run:
- Linting (ESLint, Prettier, etc.)
- Type checking (TypeScript, mypy, etc.)
- Tests (unit tests, integration tests)
- Security scans (secret detection, dependency audits)

## Examples

Input: /commit "feat(ui): add user profile component"
Action: Validate format, add emoji ✨, execute commit with message "✨ feat(ui): add user profile component"

Input: /commit "fix: resolve authentication timeout"
Action: Validate format, add emoji 🐛, execute commit with message "🐛 fix: resolve authentication timeout"

Input: /commit
Action: Interactive mode, use AskUserQuestion to select type (e.g., "feat"), select scope (e.g., "api"), generate message "✨ feat(api): [user completes subject]"

Input: /commit --no-verify
Action: Interactive mode, skip pre-commit hooks when executing git commit

Input: /commit "update docs"
Action: Report error "Conventional Commits format required: type(scope): subject. Example: docs: update installation guide"

## Notes

This command focuses on creating well-formatted Conventional Commits with emoji annotations. For automated quality checks, configure pre-commit hooks in your repository. The LLM can analyze changed files to suggest appropriate scope based on file patterns and directories.

---

## Security Implementation

**MANDATORY: Execute these validations BEFORE ANY commit operation**

```bash
# 1. Validate Conventional Commit format
validate_conventional_commit() {
  local message="$1"

  # Check format: type(scope): subject
  if [[ ! "$message" =~ ^(feat|fix|refactor|docs|style|test|chore|perf)(\([a-z0-9_-]+\))?:\ .+ ]]; then
    echo "ERROR: Invalid Conventional Commit format"
    echo "Expected: type(scope): subject"
    echo "Got: $message"
    return 1
  fi

  # Check subject length (max 72 characters after type/scope)
  local subject=$(echo "$message" | sed 's/^[^:]*: //')
  if [[ ${#subject} -gt 72 ]]; then
    echo "ERROR: Subject too long (${#subject} chars, max 72)"
    return 1
  fi

  # Check subject doesn't end with period
  if [[ "$subject" =~ \.$ ]]; then
    echo "ERROR: Subject should not end with period"
    return 1
  fi

  echo "✓ Conventional Commit format valid"
  return 0
}

# 2. Handle pre-commit hook failures
handle_pre_commit_hook() {
  local hook_result="$1"

  if [[ $hook_result -eq 0 ]]; then
    echo "✓ Pre-commit hooks passed"
    return 0
  fi

  # Detect hook failure type
  echo "ERROR: Pre-commit hook failed (exit code: $hook_result)"

  # Check for common hook failures
  if git diff --cached --name-only | grep -q "\.ts$\|\.tsx$"; then
    echo "Likely cause: TypeScript type errors"
    echo "Fix: npm run type-check"
  fi

  if git diff --cached --name-only | grep -q "\.js$\|\.jsx$\|\.ts$\|\.tsx$"; then
    echo "Likely cause: ESLint errors"
    echo "Fix: npm run lint:fix"
  fi

  return $hook_result
}

# 3. Validate GPG signature (if enabled)
validate_gpg_signature() {
  # Check if commit signing is configured
  local sign_commits=$(git config --get commit.gpgsign)

  if [[ "$sign_commits" == "true" ]]; then
    # Verify GPG key is available
    if ! git config --get user.signingkey >/dev/null; then
      echo "ERROR: GPG signing enabled but no signing key configured"
      echo "Fix: git config user.signingkey YOUR_KEY_ID"
      return 2
    fi

    echo "✓ GPG signature validation enabled"
  fi

  return 0
}

# 4. Safe argument parsing
IFS=' ' read -r -a args <<< "$ARGUMENTS"
COMMIT_MSG="${args[0]}"
COMMIT_FLAGS=("${args[@]:1}")

# Sanitize commit message (allow alphanumeric, spaces, common punctuation)
if [[ -n "$COMMIT_MSG" ]]; then
  # Detect injection attempts
  if [[ "$COMMIT_MSG" =~ [\`\$\(] ]]; then
    echo "ERROR: Dangerous characters detected in commit message"
    exit 2
  fi
fi
```

## Exit Code System

```bash
# 0: Success - Commit created successfully
# 1: User error - Invalid format, no staged files
# 2: Security error - Dangerous characters, GPG key missing
# 3: System error - Git command failed, hook execution error
# 4: Unrecoverable error - Repository corruption
```

## Bash Syntax Examples

```bash
# Safe IFS usage for parsing commit message parts
IFS=':' read -r type_scope subject <<< "$COMMIT_MSG"

# Safe parameter expansion for commit components
COMMIT_TYPE="${type_scope%%(*}"           # Extract type before (
COMMIT_SCOPE="${type_scope#*(}"            # Extract after (
COMMIT_SCOPE="${COMMIT_SCOPE%)*}"          # Remove trailing )

# Exit code propagation with git commit
git commit -m "$COMMIT_MSG" "${COMMIT_FLAGS[@]}"
COMMIT_RESULT=$?
if [[ $COMMIT_RESULT -ne 0 ]]; then
  handle_pre_commit_hook $COMMIT_RESULT
  exit $COMMIT_RESULT
fi

# Verify commit was created
git log -1 --oneline
```

## Output Format Examples

**Success example**:
```
✓ Commit created successfully
✓ Format: Conventional Commits
✓ Pre-commit hooks: PASSED
✓ Signature: GPG signed

Commit details:
  Hash: a3f7b2c
  Type: feat
  Scope: ui
  Subject: add user profile editor
  Files: 3 modified, 128 insertions, 45 deletions

Next steps:
  1. Review commit: git show
  2. Amend if needed: /commit --amend
  3. Push changes: git push
  4. Create PR: /ship
```

**Error example**:
```
ERROR: Pre-commit hook failed
File: commit.md:handle_pre_commit_hook

Reason: TypeScript type errors detected
Got: 5 type errors in 2 files
Hook exit code: 1

Failed checks:
  ✗ TypeScript compilation (5 errors)
  ✗ ESLint (12 warnings)
  ✓ Prettier formatting

Affected files:
  - src/components/UserProfile.tsx (3 errors)
  - src/api/users.ts (2 errors)

Suggestions:
1. Fix type errors: npm run type-check
2. Auto-fix ESLint: npm run lint:fix
3. Skip hooks (NOT recommended): /commit --no-verify
4. Review errors in detail: cat type-check-output.log
```

---
