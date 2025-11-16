---
allowed-tools: Read, TodoWrite, AskUserQuestion
argument-hint: [feature name or requirements]
description: New feature implementation - guided workflow from requirements to implementation
model: sonnet
---

# Feature Implementation Command

New feature development: $ARGUMENTS

## Argument Validation and Sanitization

Parse and validate $ARGUMENTS with security-first approach:

```bash
validate_feature_name() {
  local input="$1"

  # Empty check - proceed to interactive mode
  if [[ -z "$input" ]]; then
    return 0
  fi

  # Length validation
  if [[ ${#input} -gt 100 ]]; then
    echo "ERROR [feature.md:validate]: Feature name too long"
    echo "  Input length: ${#input} characters"
    echo "  Maximum: 100 characters"
    exit 1
  fi

  # Dangerous character check
  local dangerous_pattern='[;|&$`\\"'"'"'../~]'
  if [[ "$input" =~ $dangerous_pattern ]]; then
    echo "ERROR [feature.md:validate]: Special characters detected"
    echo "  Input: $input"
    echo "  Forbidden: ; | & $ \` \\ \" ' ../ ./ / ~"
    echo "  Reason: Security restriction"
    exit 2
  fi

  # Whitelist validation
  if [[ ! "$input" =~ ^[a-zA-Z0-9_\ -]+$ ]]; then
    echo "ERROR [feature.md:validate]: Invalid characters"
    echo "  Allowed: letters, numbers, spaces, hyphens, underscores"
    exit 2
  fi

  echo "$input"
}

# Execute validation
FEATURE_NAME=$(validate_feature_name "$ARGUMENTS")
```

## Execution Flow

1. Parse and validate arguments from $ARGUMENTS with validate_feature_name()
2. If arguments empty or unclear: use AskUserQuestion to clarify requirements
3. Use AskUserQuestion to select implementation approach
4. Use AskUserQuestion to select complexity level
5. Create TodoWrite with implementation steps based on selections
6. Guide user through implementation with references to other commands
7. Report next steps

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

## Examples

```bash
# Basic usage with feature description
/feature "user profile editing"

# Complex feature (triggers architectural TodoWrite)
/feature "real-time notification system"

# Interactive mode (no arguments)
/feature

# Security validation (triggers exit 2)
/feature "test; rm -rf /"
```

- Quality standards (TypeScript strict mode, testing, security)
- Error handling and debugging strategies
