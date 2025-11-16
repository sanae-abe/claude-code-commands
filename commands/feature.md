---
allowed-tools: Read, TodoWrite, AskUserQuestion
argument-hint: [feature name or requirements]
description: New feature implementation - guided workflow from requirements to implementation
model: sonnet
---

# Feature Implementation Command

New feature development: $ARGUMENTS

## Execution Flow

1. Parse and validate arguments from $ARGUMENTS
2. If arguments empty or unclear: use AskUserQuestion to clarify requirements
3. Use AskUserQuestion to select implementation approach
4. Use AskUserQuestion to select complexity level
5. Create TodoWrite with implementation steps based on selections
6. Guide user through implementation with references to other commands
7. Report next steps

## Argument Validation

Parse $ARGUMENTS:
- Strip special characters: remove ; | & $ ` \ " '
- Validate feature name format: [a-zA-Z0-9-_\s]+ only
- Maximum length: 100 characters
- Reject paths containing: ../ ./ / ~

If validation fails: report error with expected format and exit
If $ARGUMENTS empty: proceed to interactive mode with AskUserQuestion

## Implementation Approach Selection

Use AskUserQuestion to determine implementation type:

Question: "Select the type of feature to implement"
Header: "Implementation Type"
Options:
1. ui-component: UI components and screen features (forms, displays, interactions)
2. api-integration: API integration and data processing (REST API, GraphQL, data fetch/update)
3. business-logic: Business logic and state management (calculations, validation, workflows)
4. integration-feature: Integrated features (multiple component coordination, system integration)
5. infrastructure: Infrastructure and configuration (build, deploy, environment setup)
6. architecture-change: Architecture changes (structural improvements, new pattern introduction)

## Complexity Level Selection

Use AskUserQuestion to determine implementation scope:

Question: "Select the implementation scope and complexity"
Header: "Complexity"
Options:
1. simple: Simple (single file/component, 1-2 hours)
2. moderate: Moderate (multiple files, related feature updates, half day)
3. complex: Complex (new patterns/libraries, 1-2 days)
4. architectural: Architectural level (design changes, long-term implementation)

## TodoWrite Generation

Based on selected implementation type and complexity, create TodoWrite with appropriate steps:

Simple scope (1-2 steps):
1. Implement feature
2. Verify with quality checks

Moderate scope (3-4 steps):
1. Analyze requirements and existing code
2. Implement core functionality
3. Add tests and documentation
4. Run quality validation

Complex scope (5-6 steps):
1. Research existing patterns and design approach
2. Create implementation plan
3. Implement feature incrementally
4. Add comprehensive tests
5. Update documentation
6. Run full quality validation

Architectural scope (7+ steps):
1. Analyze current architecture
2. Design new architecture/patterns
3. Create migration plan
4. Implement phase 1 (minimal changes)
5. Implement phase 2 (core changes)
6. Implement phase 3 (complete migration)
7. Comprehensive testing and validation

## Integration with Other Commands

After feature implementation, guide user to:

Quality validation:
- /task-validate --layers=all: Run comprehensive quality checks
- /task-validate --layers=security: Security-focused validation

Git workflow:
- /branch: Create feature branch with conventional naming
- /commit: Create conventional commit with proper formatting
- /pr or /mr: Create pull/merge request with quality checks

Structured implementation:
- /implement [task-id]: Use tasks.yml-driven implementation for complex features
- Reference: See CLAUDE.md basic development flow for detailed guidance

## Error Handling

Argument validation errors:
If required argument missing: use AskUserQuestion for interactive mode
If invalid format: report "Feature name must contain only letters, numbers, spaces, hyphens, and underscores (max 100 characters)"
If special characters detected: report "Special characters (; | & $ \` \\ \" ') are not allowed for security reasons"

Execution errors:
If AskUserQuestion fails: report error and retry with simplified options
If TodoWrite creation fails: report error and suggest manual task breakdown
If unrecoverable error: report error type and user-actionable guidance

Security:
Never expose absolute file paths in error messages
Never expose stack traces or internal details
Report only user-actionable information

## Exit Code System

```bash
# 0: Success - Feature implementation plan created successfully
# 1: User error - Invalid feature name, arguments missing
# 2: Security error - Validation failure, special characters detected
# 3: System error - AskUserQuestion failed, TodoWrite creation failed
# 4: Unrecoverable error - Critical planning failure
```

## Output Format

**Success example**:
```
✓ Feature implementation plan created
✓ Type: ui-component
✓ Complexity: moderate
✓ Estimated effort: 4-6 hours

Implementation Steps:
  1. Analyze requirements and existing code
  2. Implement core functionality
  3. Add tests and documentation
  4. Run quality validation

Next steps:
  1. Review implementation plan
  2. Start with /implement or manual implementation
  3. Run /validate after completion
```

**Error example**:
```
ERROR: Invalid feature name detected
File: feature.md:validate_arguments

Reason: Feature name contains special characters
Got: "user-profile; rm -rf /"

Suggestions:
1. Use only: letters, numbers, spaces, hyphens, underscores
2. Max 100 characters
3. Example: "user profile editing feature"
```

## Examples

Input: /feature "user profile editing"
Action: Validate input, guide through implementation type selection, create TodoWrite for profile editing feature

Input: /feature "real-time notification system"
Action: Validate input, guide through complexity selection (likely "complex"), create detailed implementation plan

Input: /feature
Action: Interactive mode, use AskUserQuestion to gather feature requirements first

Input: /feature "test; rm -rf /"
Action: Report error "Special characters (; | & $ \` \\ \" ') are not allowed for security reasons" and exit

## Notes

This command focuses on interactive requirement clarification and implementation guidance. For detailed quality checks, use /task-validate. For structured implementation with documentation, use /implement with tasks.yml.

Refer to CLAUDE.md basic development flow for comprehensive development practices including:
- Requirement analysis and planning
- Staged implementation approach
- Quality standards (TypeScript strict mode, testing, security)
- Error handling and debugging strategies
