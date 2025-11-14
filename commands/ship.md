---
allowed-tools: Bash, AskUserQuestion, TodoWrite, Read
argument-hint: "[branch-name] [title]"
description: Create GitHub PR/GitLab MR with automatic platform detection
---

# Ship - Unified PR/MR Creation Command

Create GitHub Pull Request or GitLab Merge Request with automatic platform detection.

Arguments: $ARGUMENTS

## Platform Detection

Automatically detect platform from git remote URL:
```bash
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [[ $REMOTE_URL == *"github.com"* ]]; then
  PLATFORM="github"
  CLI_CMD="gh"
elif [[ $REMOTE_URL == *"gitlab.com"* ]] || [[ $REMOTE_URL == *"gitlab"* ]]; then
  PLATFORM="gitlab"
  CLI_CMD="glab"
else
  # Report error: unsupported platform
  exit 1
fi
```

## Argument Processing

Parse from $ARGUMENTS:
- Extract branch-name (first token, optional)
- Extract title (remaining tokens, optional)
- If $ARGUMENTS empty: interactive mode
- Validate title format: `<type>(<scope>): <subject>` pattern

Security validation:
- Sanitize branch names: reject paths with `../`, validate against git branch list
- Escape special shell characters in arguments before Bash execution
- Never pass user input directly to shell commands

## Execution Flow

### 1. Platform & Branch Detection
1. Detect platform (GitHub/GitLab) from remote URL
2. Verify CLI tool installed (gh/glab)
3. Get current branch: `git branch --show-current`
4. Validate git repository and remote

### 2. Argument Handling
**If arguments provided:**
- Validate current branch matches `[branch-name]` from $ARGUMENTS
- Parse and validate `[title]` from $ARGUMENTS for Conventional Commits format
- Auto-detect project type and requirements

**If no arguments (interactive mode):**
- Detect current branch automatically
- Use AskUserQuestion for PR/MR details
- Guide through quality checklist

### 3. Pre-Ship Quality Checks
**Automated validation:**
- Uncommitted changes check: `git status --porcelain`
- Branch push status verification
- Project-specific quality commands execution

### 4. PR/MR Creation with Template
**Template detection priority:**

For GitHub:
1. `.github/pull_request_template.md` (project-specific)
2. `~/.github/PULL_REQUEST_TEMPLATE.md` (global fallback)
3. Built-in template (auto-generated)

For GitLab:
1. `.gitlab/merge_request_template.md` (project-specific)
2. `~/.gitlab/merge_request_template.md` (global fallback)
3. Built-in template (auto-generated)

**Template loading logic:**
```bash
# GitHub template selection
if [[ -f ".github/pull_request_template.md" ]]; then
  TEMPLATE=$(cat .github/pull_request_template.md)
elif [[ -f "$HOME/.github/PULL_REQUEST_TEMPLATE.md" ]]; then
  TEMPLATE=$(cat "$HOME/.github/PULL_REQUEST_TEMPLATE.md")
else
  TEMPLATE="[Auto-generated built-in template]"
fi

# GitLab template selection
if [[ -f ".gitlab/merge_request_template.md" ]]; then
  TEMPLATE=$(cat .gitlab/merge_request_template.md)
elif [[ -f "$HOME/.gitlab/merge_request_template.md" ]]; then
  TEMPLATE=$(cat "$HOME/.gitlab/merge_request_template.md")
else
  TEMPLATE="[Auto-generated built-in template]"
fi
```

### 5. Draft Creation & Verification
```bash
# GitHub
gh pr create --draft --title "title" --body "template"
gh pr view --web

# GitLab
glab mr create --draft --title "title" --description "template"
glab mr view --web
```

## Template Priority & Detection

### Template Sources
1. **Project-specific template**: Platform-specific location (highest priority)
2. **Global template**: User home directory (fallback)
3. **Built-in template**: Auto-generated with detailed quality checklist
4. **Detailed guidelines**: `@<project>/docs/{PR,MR}_GUIDELINES.md` (reference)

## Interactive Creation (AskUserQuestion Integration)

### Primary Question: Type & Title
```typescript
AskUserQuestion({
  questions: [{
    question: "Select change type and set title",
    header: "Ship Type",
    multiSelect: false,
    options: [
      {
        label: "feature",
        description: "New feature (UI, API, integration)"
      },
      {
        label: "fix",
        description: "Bug fix (functional issues, performance problems)"
      },
      {
        label: "refactor",
        description: "Code improvement (structure, optimization)"
      },
      {
        label: "docs",
        description: "Documentation (README, API specs, comments)"
      },
      {
        label: "chore",
        description: "Configuration (build, dependencies, CI/CD)"
      },
      {
        label: "hotfix",
        description: "Critical fix (production issues, security)"
      }
    ]
  }]
})
```

### Secondary Question: Scope & Priority
```typescript
AskUserQuestion({
  questions: [{
    question: "Select change scope",
    header: "Scope",
    multiSelect: false,
    options: [
      { label: "ui", description: "UI components, frontend" },
      { label: "api", description: "API, backend, data layer" },
      { label: "core", description: "Core logic, business logic" },
      { label: "config", description: "Configuration, build, infrastructure" },
      { label: "docs", description: "Documentation, comments" },
      { label: "test", description: "Testing, quality assurance" }
    ]
  }]
})
```

## Required Rules & Quality Gates

### Basic Requirements
- [ ] Create as draft (`--draft` option required)
- [ ] Conventional Commits format for title (`<type>(<scope>): <subject>`)
- [ ] Use `--set-upstream` on first push (`git push -u origin <branch>`)
- [ ] Complete checklist following template

### Project Quality Checks
- [ ] TypeScript projects: `npm run typecheck` success
- [ ] ESLint: `npm run lint` zero errors (warnings acceptable)
- [ ] Tests: `npm test` or `npm run test` success
- [ ] Build: `npm run build` success
- [ ] Other project-specific CI/CD checks

## Automated Pre-Ship Quality Execution

### Quality Command Execution Flow
```bash
# 1. Uncommitted changes check
git status --porcelain

# 2. TypeScript validation (if applicable)
npm run typecheck || echo "❌ TypeScript errors detected"

# 3. Linting validation (if applicable)
npm run lint || echo "❌ ESLint errors detected"

# 4. Test execution (if applicable)
npm run test:run || echo "❌ Tests failed"

# 5. Build verification (if applicable)
npm run build || echo "❌ Build failed"
```

### General Project Examples

#### Frontend Development
```bash
# Branch: feature/user-profile-page
# Title: feat(ui): add user profile management page
# Scope: ui
# Focus: UI components, styling, user interactions
```

#### Backend Development
```bash
# Branch: fix/api-authentication-bug
# Title: fix(api): resolve authentication token validation
# Scope: api
# Focus: API endpoints, data validation, security
```

#### Infrastructure/Config
```bash
# Branch: chore/ci-pipeline-optimization
# Title: chore(config): optimize CI/CD pipeline performance
# Scope: config
# Focus: Build tools, deployment, configuration
```

## Enhanced Command Flow

### 1. Automated Branch Analysis
```bash
# Current branch detection
CURRENT_BRANCH=$(git branch --show-current)

# Branch type extraction (using safe parameter expansion)
BRANCH_TYPE="${CURRENT_BRANCH%%/*}"

# Description extraction (using safe parameter expansion)
BRANCH_DESC="${CURRENT_BRANCH#*/}"
```

### 2. Interactive Creation (No Arguments)
```bash
# If no arguments provided, guide through interactive process:
# 1. AskUserQuestion for type
# 2. AskUserQuestion for scope
# 3. Auto-generate title from selections
# 4. Execute quality checks
# 5. Create draft PR/MR with template
```

### 3. Direct Creation (With Arguments)
```bash
# Validate provided arguments
# Execute quality checks
# Create PR/MR immediately

# GitHub
gh pr create --draft --title "provided-title" --body "template"

# GitLab
glab mr create --draft --title "provided-title" --description "template"
```

## Conventional Commits Format

### Type Definitions
- **feat**: New feature
- **fix**: Bug fix
- **refactor**: Refactoring
- **docs**: Documentation
- **perf**: Performance improvement
- **style**: Style changes
- **test**: Adding tests
- **chore**: Build/configuration

### Examples
- `feat(auth): implement login functionality`
- `fix(api): resolve response error handling`
- `refactor(ui): improve component structure`
- `docs(readme): add installation instructions`
- `perf(query): optimize database queries`
- `test(user): add user registration tests`

## Pre-Ship Quality Checks

### For Node.js/TypeScript Projects
```bash
# TypeScript error check
npm run type-check

# Run linter
npm run lint

# Run tests
npm run test

# Build verification
npm run build
```

### For Other Projects
- Execute project CI scripts
- Run local tests
- Verify build/compilation

## CLI Commands Reference

### GitHub CLI (gh)
```bash
# List PRs
gh pr list

# View specific PR
gh pr view <PR-number>

# Open PR in browser
gh pr view --web <PR-number>

# Mark ready for review (remove draft)
gh pr ready <PR-number>

# Merge PR
gh pr merge <PR-number>

# Close PR
gh pr close <PR-number>
```

### GitLab CLI (glab)
```bash
# List MRs
glab mr list

# View specific MR
glab mr view <MR-number>

# Open MR in browser
glab mr view --web <MR-number>

# Mark ready for review (remove draft)
glab mr update --ready

# Merge MR
glab mr merge <MR-number>

# Close MR
glab mr close <MR-number>
```

## Update & Edit

### GitHub - Update PR Title/Description
```bash
# Update both title and description
gh pr edit <PR-number> --title "New title" --body "New description"

# Update title only
gh pr edit <PR-number> --title "New title"

# Update description only
gh pr edit <PR-number> --body "New description"
```

### GitLab - Update MR Title/Description
```bash
# Update both title and description
glab mr update <MR-number> --title "New title" --description "New description"
```

### Status Changes
```bash
# GitHub: Mark ready for review
gh pr ready <PR-number>

# GitHub: Convert to draft
gh pr edit <PR-number> --draft

# GitLab: Mark ready for review
glab mr update <MR-number> --ready

# GitLab: Convert to draft
glab mr update <MR-number> --draft
```

## Error Handling

### Argument validation errors
If required argument missing: use AskUserQuestion for interactive input
If invalid Conventional Commits format: report expected format with example
If branch name invalid: report error and show current branch

### Execution errors
If platform unsupported: report "Unsupported git platform. Only GitHub and GitLab are supported."
If CLI tool not found (gh/glab): report installation command for detected platform
If git push fails: report push error and verify remote branch exists
If PR/MR creation fails: report specific error from CLI output

### Security
Never expose absolute file paths in error messages
Never expose stack traces or internal details
Report only user-actionable information (command syntax, required format, etc.)

## Project-Specific Requirements

If project has `docs/PR_GUIDELINES.md` or `docs/MR_GUIDELINES.md`, refer to those documents for additional requirements.

## Command Examples

### Complete Ship Flow Example
```bash
# 1. Create branch
git checkout -b feat/user-profile-edit

# 2. Make changes and commit
git add .
git commit -m "feat(profile): add user profile editing feature"

# 3. Push to remote
git push -u origin feat/user-profile-edit

# 4. Create PR/MR (recommended method)
/ship

# Or with arguments
/ship feat/user-profile-edit "feat(profile): add user profile editing feature"

# 5. Browser opens automatically for review

# 6. Mark ready when review-ready
# GitHub: gh pr ready
# GitLab: glab mr update --ready
```

## Important Notes

1. **Always create as draft** (until review-ready)
2. **Prepare detailed description using template** (avoid interactive mode)
3. **Follow Conventional Commits for branch names and commit messages**
4. **Complete checklist following project template**
5. **Platform auto-detection** (supports both GitHub and GitLab)

## Platform-Specific Notes

### GitHub
- CLI: `gh` (GitHub CLI)
- Update command: `gh pr edit`
- Ready command: `gh pr ready`
- Template: `.github/pull_request_template.md`

### GitLab
- CLI: `glab` (GitLab CLI)
- Update command: `glab mr update`
- Ready command: `glab mr update --ready`
- Template: `.gitlab/merge_request_template.md`
