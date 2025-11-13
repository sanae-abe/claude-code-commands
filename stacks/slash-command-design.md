# Slash Command Design Guidelines

Guidelines for creating Claude Code slash commands optimized for LLM parsing and execution.

## Core Principles

- Write in English
- Minimize decorative elements
- Use direct, imperative instructions
- Avoid project-specific information
- Avoid roadmaps and future plans
- Avoid internal cross-references

## YAML Frontmatter Format

Required frontmatter structure:

```yaml
---
allowed-tools: Bash, Read, Write, Edit
argument-hint: "<required> [--optional-flag]"
description: Single-line description shown in command list
model: sonnet
---
```

### Field Specifications

**allowed-tools** (required)
- Grant minimum necessary tools only
- Review and justify each tool before finalizing
- Avoid "full access" unless genuinely required

Common combinations:
- Read-only: `Bash, Read, Grep, Glob`
- Code editing: `Read, Edit, Bash`
- Interactive: `AskUserQuestion, TodoWrite`
- Complex workflows: `Bash, Read, Edit, Grep, Glob, TodoWrite, AskUserQuestion`
- With subagents: add `Task` to any combination above

**argument-hint** (optional)
- Show expected argument syntax
- Use `<required>` and `[--optional]`
- Example: `"<file-path> [--detailed] [--output-format]"`

**description** (required)
- Single line, under 100 characters
- Describes what the command does, not how

**model** (optional)
- `haiku`: < 3 steps, no analysis needed
- `sonnet`: default for most commands
- `opus`: deep reasoning required
- Omit to use user's default model

## Document Structure

Minimal template:

```markdown
---
allowed-tools: [tool list]
argument-hint: "[syntax]"
description: [one-line description]
---

# Command Name

Arguments: $ARGUMENTS

## Execution Flow

1. Parse arguments from $ARGUMENTS
2. Execute main logic
3. Handle errors

## Tool Usage

TodoWrite: Use when 3+ steps required
AskUserQuestion: Use when arguments unclear

## Error Handling

If [condition]: [action]
If unrecoverable error: report error type and user-actionable guidance

Avoid: stack traces, file paths, internal details in user-facing errors
```

Avoid:
- Table of contents
- Version numbers or dates
- Emoji headers
- Related commands sections

## Security Guidelines

### Input Validation

Always validate $ARGUMENTS before use:

```markdown
## Argument Validation

Parse $ARGUMENTS:
- Sanitize file paths: reject ../, validate against project root
- Validate flags against allowed list
- Escape arguments before passing to Bash
- Reject unexpected patterns

Example validation:
If path contains ..: report error and exit
If flag not in [allowed-flags]: report error and exit
```

### Tool Permission Security

Apply least privilege principle:
- Grant only tools actually used in execution flow
- Avoid `Write` if command only reads
- Avoid `Bash` if other tools suffice
- Review tool list before finalizing

### Error Message Security

```markdown
## Error Handling

If validation fails: report error type and required format
If file not found: report filename only, not full path
If command fails: report user-actionable guidance

Never expose:
- Stack traces
- Absolute file paths
- Internal system details
- Sensitive environment information
```

## Argument Processing

Access user input via `$ARGUMENTS` variable.

Simple positional:
```markdown
Extract target from $ARGUMENTS (first token)
If empty: use AskUserQuestion to select target
```

Multiple flags:
```markdown
Parse flags from $ARGUMENTS:
- --detailed: enable verbose output
- --output=format: json|yaml|text (default: text)
- --skip-tests: skip test execution

If invalid flag: report error with available flags
```

Key-value pairs:
```markdown
Parse from $ARGUMENTS:
- Extract key=value pairs
- Validate values against constraints
- Apply defaults for omitted keys
```

## Tool Usage Patterns

### TodoWrite

Use when:
- Command has 3+ distinct steps
- Long-running operations
- Complex workflows needing progress tracking

```markdown
TodoWrite: Create task list at start:
1. Parse and validate arguments
2. Analyze target
3. Execute operation
4. Verify results

Update status as each step completes
```

### AskUserQuestion

Use when:
- Arguments missing or ambiguous
- Multiple valid approaches exist
- User decision required

```markdown
If $ARGUMENTS empty or unclear:
1. Use AskUserQuestion with 2-4 clear options
2. Parse user selection
3. Proceed with chosen option
```

### Task Tool (Subagents)

Use when:
- Complex codebase exploration needed
- Specialized analysis required (security, performance)
- Large-scale search across multiple locations

```markdown
Use Task tool with subagent_type:
- Explore: codebase navigation, pattern discovery
- code-reviewer: code quality analysis
- security-auditor: security review
- performance-engineer: performance analysis

Provide clear, specific task description
Specify what information subagent should return
```

### Common Workflow Patterns

**Git operations:**
```markdown
1. Validate git repository via Bash: git rev-parse --git-dir
2. Check working tree state: git status --porcelain
3. Execute git command
4. Verify result: git log -1 or git status
5. Report outcome

Error handling:
If not in git repo: report error and exit
If uncommitted changes detected: use AskUserQuestion to confirm
```

**Code analysis:**
```markdown
1. Parse target from $ARGUMENTS
2. Locate files: Grep for patterns or Glob for file types
3. Read and analyze: use Read tool
4. Generate report
5. Present findings

When target scope unclear: use Task tool with Explore subagent
When searching specific patterns: use Grep directly
```

**Interactive selection:**
```markdown
1. Check if $ARGUMENTS provided
2. If missing: use AskUserQuestion
3. Validate selection
4. Create TodoWrite for multi-step execution
5. Execute based on choice
```

## Error Handling

Always specify error handling behavior:

```markdown
## Error Handling

Argument validation:
If required argument missing: use AskUserQuestion or report required format
If invalid format: report expected format with example

Execution errors:
If tool operation fails: report what failed and how to fix
If recoverable: suggest correction and retry
If unrecoverable: report error type and exit

Security:
Never expose absolute paths, stack traces, or internal details
Report only user-actionable information
```

## Examples Section

Provide concrete input/output examples:

```markdown
## Examples

Input: /command target-name --flag
Action: Execute with flag enabled on target-name

Input: /command
Action: Interactive mode, prompt for target selection

Input: /command invalid-target
Action: Report error with valid target format
```

## Command Naming

Use kebab-case, verb-based names:
- Good: `/analyze`, `/review-mr`, `/clean-jobs`
- Avoid: `/Analysis`, `/MRReview`, `/cleanJobs`

Prefixes:
- No prefix: general-purpose commands
- Avoid tech-specific prefixes unless necessary

## Writing Style

Direct and imperative:
```markdown
Good: "Parse arguments from $ARGUMENTS"
Bad: "You should parse the arguments that the user provided"

Good: "If validation fails: report error and exit"
Bad: "In case the validation doesn't succeed, consider reporting an error"
```

Structured and scannable:
```markdown
Good:
1. Parse arguments
2. Validate input
3. Execute operation

Bad:
First parse the arguments, then validate the input, and finally execute the operation.
```

## Quality Checklist

Before finalizing a slash command:

- [ ] YAML frontmatter complete and valid
- [ ] allowed-tools includes only necessary tools
- [ ] description clear and under 100 characters
- [ ] $ARGUMENTS referenced if command accepts input
- [ ] Argument validation specified
- [ ] Execution flow is step-by-step
- [ ] Error handling specified with security considerations
- [ ] Examples provided
- [ ] No emojis or excessive decoration
- [ ] No table of contents
- [ ] No version numbers or dates
- [ ] No project-specific paths or names
- [ ] No internal cross-references
- [ ] Written in English
- [ ] Direct, imperative instructions

## Testing

After creating a command:

1. Test with arguments: `/command arg1 --flag`
2. Test without arguments: `/command`
3. Test with invalid input: `/command invalid`
4. Verify YAML parsing (command appears in list)
5. Verify allowed-tools restrictions work
6. Test error handling paths

## Maintenance

Slash commands require minimal maintenance:
- Git tracks history (no version fields needed)
- Update when Claude Code APIs change
- Refactor when patterns improve
- Remove obsolete commands entirely (don't deprecate)

Avoid:
- Version fields in documents
- "Last updated" dates
- "TODO" or roadmap sections
- "Deprecated" sections
