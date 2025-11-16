---
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, TodoWrite, AskUserQuestion
argument-hint: "[create|list|switch|merge|delete|status] [branch-name]"
description: Git worktree management for parallel development workflows
model: sonnet
---

# Worktree Management

Arguments: $ARGUMENTS

## Execution Flow

1. Parse subcommand and arguments from $ARGUMENTS
2. Execute worktree operation based on subcommand
3. Provide user-actionable output

## Subcommands

### create <branch-name> [--from <base-branch>]

Create new worktree for parallel development:

1. Validate branch name (no spaces, special chars except `-_/`)
2. Determine base branch (default: current branch or main)
3. Calculate worktree path: `../worktree-<branch-name>`
4. Create new branch and worktree:
   ```bash
   git worktree add -b <branch-name> ../worktree-<branch-name> <base-branch>
   ```
5. Output worktree path and next steps

**Error handling**:
- If branch exists: offer to switch instead
- If path exists: suggest alternative path or cleanup
- If git error: show error and suggest `git worktree list`

### list [--detailed]

List all worktrees:

1. Run `git worktree list --porcelain` for machine-readable output
2. Parse output to extract:
   - Worktree path
   - Branch name
   - Commit hash (if --detailed)
   - Lock status
3. Format as table with clear headers

**Output format**:
```
BRANCH              PATH                           STATUS
main                /Users/.../project             (main)
feature-auth        /Users/.../worktree-auth
bugfix-login        /Users/.../worktree-login      locked
```

### switch <branch-name>

Switch to existing worktree:

1. List worktrees to find target branch
2. If found: output `cd` command for user
3. If not found: suggest creating with `create` subcommand

**Note**: Cannot change directory in parent shell, output instruction instead

### merge <branch-name> [--no-delete]

Merge worktree branch to main and cleanup:

1. Verify worktree exists
2. Check for uncommitted changes in worktree
3. Switch to main branch in current directory
4. Pull latest changes: `git pull origin main`
5. Merge worktree branch: `git merge <branch-name>`
6. If merge successful and no conflicts:
   - Push to remote: `git push origin main`
   - Unless --no-delete: delete worktree and branch
7. If conflicts: halt and instruct user to resolve

**Cleanup steps** (unless --no-delete):
```bash
git worktree remove ../worktree-<branch-name>
git branch -d <branch-name>
```

### delete <branch-name> [--force]

Remove worktree and branch:

1. Verify worktree exists
2. Check for uncommitted changes
3. If uncommitted changes and not --force:
   - Warn user and ask for confirmation via AskUserQuestion
4. Remove worktree: `git worktree remove <path>`
5. If --force or confirmed: `git worktree remove --force <path>`
6. Delete branch: `git branch -d <branch-name>` (or `-D` if --force)

### status

Show comprehensive worktree status:

1. List all worktrees with TodoWrite tracking:
   - For each worktree: check git status
   - Count uncommitted changes
   - Check if branch is ahead/behind remote
2. Output summary:
   - Total worktrees
   - Worktrees with uncommitted changes
   - Worktrees ahead/behind remote
   - Locked worktrees

## Tool Usage

**TodoWrite**: Use for multi-step operations (merge, delete with conflicts)

**AskUserQuestion**: Use when:
- Uncommitted changes detected (confirm deletion)
- Merge conflicts require user decision
- Ambiguous arguments (multiple matches)

## Security Considerations

**Input validation**:
- Branch names: `^[a-zA-Z0-9/_-]+$` (no spaces, special chars)
- Paths: Must be within parent directory of current repo
- No command injection via branch names in git commands

**Safe command construction**:
```bash
# BAD: direct interpolation
git worktree add ../worktree-$BRANCH

# GOOD: validated and quoted
if [[ "$BRANCH" =~ ^[a-zA-Z0-9/_-]+$ ]]; then
  git worktree add "../worktree-${BRANCH}"
fi
```

**Path validation**:
- Worktree paths must be absolute or relative to repo root
- Prevent directory traversal: reject `..` in branch names
- Verify worktree path before removal operations

## Error Handling

**Git errors**:
- Branch already exists: suggest `switch` or use different name
- Worktree path exists: offer cleanup or alternative path
- No worktrees found: suggest creating first worktree
- Uncommitted changes: warn and require --force or confirmation

**File system errors**:
- Permission denied: check directory permissions
- Disk full: report error and suggest cleanup
- Path too long: suggest shorter branch name

**User-actionable error format**:
```
Error: Branch 'feature-auth' already exists

Suggestions:
1. Switch to existing worktree: /worktree switch feature-auth
2. Use different branch name: /worktree create feature-auth-v2
3. Delete existing: /worktree delete feature-auth
```

## Workflow Integration

**Parallel development pattern**:
```bash
# Main development in main worktree
/worktree create feature-payments
# -> cd ../worktree-feature-payments to work on feature

# Simultaneously work on bugfix
/worktree create bugfix-login
# -> cd ../worktree-bugfix-login to work on bugfix

# Merge when ready
/worktree merge feature-payments  # Auto-cleanup
/worktree merge bugfix-login
```

**Best practices**:
- Keep main worktree for stable/release code
- Create worktrees for features, bugfixes, experiments
- Merge frequently to avoid divergence
- Clean up completed worktrees promptly

## Examples

**Create feature worktree**:
```
/worktree create feature-websocket

Output:
✓ Created worktree: ../worktree-feature-websocket
✓ Branch: feature-websocket (from main)

Next steps:
  cd ../worktree-feature-websocket
  # Start development
```

**List all worktrees**:
```
/worktree list

Output:
BRANCH              PATH                                STATUS
main                /Users/.../claude-code-workspace    (main)
feature-websocket   /Users/.../worktree-feature-websocket
```

**Merge and cleanup**:
```
/worktree merge feature-websocket

Output:
✓ Switched to main
✓ Merged feature-websocket
✓ Pushed to origin/main
✓ Removed worktree
✓ Deleted branch feature-websocket
```

## Performance Optimization

**Parallel execution**:
- List operation: single `git worktree list` call
- Status check: parallel `git status` for each worktree (if > 3 worktrees)

**Caching**:
- Cache worktree list for 5 seconds to avoid repeated git calls
- Invalidate cache on create/delete operations

## Default Behavior

When no arguments provided:
1. Show `list` output
2. Display usage hint with common subcommands

**Argument parsing**:
- First argument: subcommand (create, list, switch, merge, delete, status)
- Remaining arguments: subcommand-specific
- Flags: `--force`, `--detailed`, `--from`, `--no-delete`
