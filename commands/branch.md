---
allowed-tools: Bash, Read, AskUserQuestion
argument-hint: "[branch-type] [description]"
description: Create Git branch following Conventional Branch naming rules
model: sonnet
---

# Branch Creation Command

Arguments: $ARGUMENTS

Usage: `/branch [branch-type] [description]`

Examples:
- `/branch feature user-settings`
- `/branch fix login-validation`
- `/branch hotfix security-patch`
- `/branch` (interactive mode)

## Argument Validation

Parse from $ARGUMENTS:
- Extract first token as branch-type
- Extract remaining tokens as description
- Validate branch-type against allowed list: feature, fix, refactor, docs, chore, hotfix
- Sanitize description:
  - Convert to lowercase
  - Replace spaces with hyphens
  - Remove special characters: ; | & $ ( ) < > ` \ ' "
  - Validate final format: ^[a-z]+/[a-z0-9-]+$

If $ARGUMENTS empty or unclear: use AskUserQuestion for interactive mode
If validation fails: report expected format and exit

Security requirements:
- Always quote variables in Bash: git checkout -b "${branch_name}"
- Never expose absolute file paths in error messages
- Reject paths containing ../

## Execution Flow

### 1. Determine Branch Type

**If arguments provided:**
- Parse branch-type and description from $ARGUMENTS
- Validate and sanitize inputs
- Generate branch name: {type}/{kebab-case-description}

**If no arguments:**
- Use AskUserQuestion for interactive selection
- Present 6 branch types with descriptions

### 2. Pre-creation Validation

Execute minimal checks for fast execution:

```bash
# 1. Verify git repository
git rev-parse --is-inside-work-tree

# 2. Check uncommitted changes
git status --porcelain
```

If uncommitted changes detected: use AskUserQuestion with options:
- stash: temporarily save changes
- commit: commit changes before branch creation
- cancel: abort branch creation

Note: Branch collision detection deferred to `git checkout -b` (automatic error handling)

### 3. Create and Push Branch

```bash
# Create local branch (quoted for security)
git checkout -b "${branch_name}"

# Push to remote with upstream tracking
git push -u origin "${branch_name}"
```

## Branch Types

Conventional branch type definitions:

- **feature/**: New feature development
- **fix/**: Bug fixes and error resolution
- **refactor/**: Code improvement and refactoring
- **docs/**: Documentation creation and updates
- **chore/**: Configuration and tooling
- **hotfix/**: Emergency fixes for production issues

Examples:
- `feature/user-authentication`
- `fix/validation-error`
- `refactor/api-optimization`
- `docs/api-documentation`
- `chore/eslint-update`
- `hotfix/security-patch`

## Interactive Mode

When $ARGUMENTS is empty or unclear, use AskUserQuestion:

```typescript
AskUserQuestion({
  questions: [{
    question: "What type of branch do you want to create?",
    header: "Branch Type",
    multiSelect: false,
    options: [
      {
        label: "feature",
        description: "New feature development (UI, API, integrations)"
      },
      {
        label: "fix",
        description: "Bug fixes and error resolution"
      },
      {
        label: "refactor",
        description: "Code improvement and refactoring"
      },
      {
        label: "docs",
        description: "Documentation creation and updates"
      },
      {
        label: "chore",
        description: "Configuration and tooling (build, dependencies, CI/CD)"
      },
      {
        label: "hotfix",
        description: "Emergency fixes (production issues, security)"
      }
    ]
  }]
})
```

After type selection, prompt for description:
- Use Read tool if description file provided
- Otherwise, use text input from AskUserQuestion "Other" option

## Error Handling

### Validation Errors

If branch-type invalid:
- Report: "Invalid branch type. Allowed: feature, fix, refactor, docs, chore, hotfix"
- Exit

If description contains special characters:
- Report: "Description contains invalid characters. Use only: a-z, 0-9, hyphens"
- Exit

If final format invalid:
- Report: "Invalid format. Expected: {type}/{kebab-case-description}"
- Exit

### Execution Errors

If not in git repository:
- Report: "Not a git repository. Run 'git init' first"
- Exit

If uncommitted changes detected:
```typescript
AskUserQuestion({
  questions: [{
    question: "Uncommitted changes detected. How to proceed?",
    header: "Changes",
    multiSelect: false,
    options: [
      { label: "stash", description: "Temporarily save changes" },
      { label: "commit", description: "Commit changes first" },
      { label: "cancel", description: "Cancel branch creation" }
    ]
  }]
})
```

Execute based on selection:
- stash: `git stash push -m "Auto-stash for branch ${branch_name}"`
- commit: `git add . && git commit -m "WIP: save work before ${branch_name}"`
- cancel: Exit

If branch already exists:
- git checkout -b will fail with clear error
- Report: "Branch already exists. Suggested alternatives: {name}-v2, {name}-{date}"
- Exit

If network issues during push:
- Report: "Local branch created. Push failed due to network issues"
- Provide command: `git push -u origin "${branch_name}"`

### Security

Never expose in error messages:
- Absolute file paths
- Stack traces
- Internal system details
- Environment variables

Report only:
- Error type (validation, git operation, network)
- User-actionable guidance
- Sanitized branch names only

## Tool Usage

TodoWrite: Not required (< 3 steps, fast execution)
AskUserQuestion: Required for interactive mode and uncommitted changes
Bash: Required for git operations
Read: Optional for reading description from file

## Examples

Input: `/branch feature user-login`
Action: Create branch feature/user-login, validate format, execute git commands

Input: `/branch fix "Bug in API"`
Action: Sanitize to fix/bug-in-api, create and push branch

Input: `/branch`
Action: Interactive mode, prompt for branch type and description

Input: `/branch invalid test`
Action: Report error "Invalid branch type. Allowed: feature, fix, refactor, docs, chore, hotfix"
