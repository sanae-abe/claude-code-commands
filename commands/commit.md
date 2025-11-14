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
