---
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, TodoWrite, AskUserQuestion, Task
argument-hint: "<target> [--rounds=4] [--perspectives=necessity,security,performance,maintainability] [--skip-necessity]"
description: Multi-perspective review analyzing necessity, security, performance, and maintainability
model: sonnet
---

# Iterative Review System

Review Target: $ARGUMENTS

## Overview

Review code, configuration, or documentation from multiple perspectives to discover issues overlooked from single viewpoints. By default, includes Round 0 "Necessity Review" that questions whether features should exist at all before proposing improvements.

## Quick Start

```bash
# Basic usage (4 perspectives: necessity, security, performance, maintainability)
/iterative-review src/components/Button.tsx

# Configuration file review (discover redundant parts to delete)
/iterative-review README.md

# Necessity review only (fastest evaluation of deletion/simplification potential)
/iterative-review feature.ts --perspectives=necessity --rounds=1

# Constructive review (skip Round 0, only propose improvements)
# Use for features with proven value or during new feature implementation
/iterative-review file.ts --skip-necessity

# Custom perspective specification
/iterative-review file.ts --perspectives=necessity,security,accessibility

# Full directory review (discover unnecessary files/features)
/iterative-review src/components/

# MR/PR review (evaluate if large changes are truly necessary)
/iterative-review --mr 123
/iterative-review --pr 456
```

## Argument Validation

Parse and validate $ARGUMENTS before execution:

Extract target:
- File path: validate exists, reject ../ or paths outside project
- Directory: validate exists and is directory
- MR/PR number: validate via --mr or --pr flag with positive integer

Parse optional flags:
- --rounds=N: validate positive integer (default: 4)
- --perspectives=list: validate against allowed perspectives (default: necessity,security,performance,maintainability)
- --skip-necessity: boolean flag (default: false)

Sanitize all arguments:
- Escape special characters before Bash execution
- Reject unexpected flag patterns
- Validate perspective names against allowed list: necessity, security, performance, maintainability, accessibility, i18n, testing, documentation, consistency, scalability, simplicity

If validation fails: report expected format and exit
If target not found: report error with example usage

## Error Handling

Argument errors:
If target missing: use AskUserQuestion to select file/directory
If invalid rounds: report "rounds must be positive integer, got: [value]"
If invalid perspective: report "allowed perspectives: necessity, security, performance, maintainability, accessibility, i18n, testing, documentation, consistency, scalability, simplicity"
If path contains ..: report "paths cannot contain ../ for security reasons"

Execution errors:
If file read fails: report "cannot read [filename]: check permissions"
If git operation fails (MR/PR): report "git operation failed: ensure repository is valid"
If unrecoverable error: report error type and user-actionable guidance

Security:
Never expose absolute file paths
Never expose stack traces or internal details
Report only user-actionable information

## Basic Approach

As an experienced senior engineer, you will iteratively review targets from multiple expert perspectives.

Review attitude:
- Zero-based thinking: Ask "is this even needed?" first rather than "how to improve"
- Don't hesitate to delete: Eliminate status quo bias and actively recommend deletion of unnecessary features
- Bold proposals: Include "fundamental reconsideration" as an option, not just "safe improvements"
- Multi-angle analysis: Comprehensive evaluation from different expert perspectives
- Prioritization: Importance classification of findings (deletion > simplification > improvement)
- Integrated report: Final report consolidating all perspective results

## Execution Flow

Use TodoWrite to track progress:
1. Parse and validate arguments from $ARGUMENTS
2. Identify target (file/directory/MR/PR)
3. Determine perspectives (apply defaults or parse custom list)
4. Apply --skip-necessity if specified (remove necessity from perspectives, set rounds=3)
5. Create TodoWrite with all review rounds
6. Execute each perspective review sequentially
7. Update todo status after each round completes
8. Generate integrated report

Argument parsing logic:

```bash
# Default settings
PERSPECTIVES="necessity,security,performance,maintainability"
ROUNDS=4
SKIP_NECESSITY=false

# If --skip-necessity is specified
if [[ "$SKIP_NECESSITY" == true ]]; then
    PERSPECTIVES="security,performance,maintainability"
    ROUNDS=3
fi
```

## Review Perspective Definitions

### Round 0: Necessity Review

Purpose: Eliminate status quo bias and question the necessity of the target with zero-based thinking

Important principles:
- Ask "is this even needed?" not "how to improve it"
- Actively consider deletion/consolidation rather than protecting existing implementation
- Strictly evaluate the cost of complexity
- Always present simpler alternatives

Required check items:

Fundamental necessity evaluation:
- Real use cases: Do concrete scenarios exist where this is actually used?
  - Can you list 3+ scenarios where it's "actually used" not just "seems useful"
  - Predicted weekly/monthly usage frequency?
- Alternative means exist: Can existing features/commands/tools substitute?
- Cost of complexity: Is the value worth the added complexity?

Deletion/consolidation potential:
- Deletion impact analysis: What is the actual harm if this feature is deleted?
- Consolidation possibility: Can it be consolidated into existing features?
- Simplification potential: Can the same value be provided with simpler implementation?

Value proposition clarification:
- Clear value: Can the raison d'être of this feature be explained in one sentence?
- Priority evaluation: Should this be prioritized over other improvements/new features?

Evaluation criteria:

| Item | Recommend Deletion | Needs Review | Justified Retention |
|------|-------------------|--------------|---------------------|
| Real use cases | 0-1 cases | 2-3 cases | 4+ cases |
| Alternative means | Easily achievable | Some effort required | Difficult |
| Usage frequency | Less than monthly | Weekly | 3+ times/week |
| Maintenance cost | High | Medium | Low |

Review result expression:
- Recommend deletion: "This feature is unnecessary. Reason: [specific reason]. Alternative: [how to achieve with existing features]"
- Recommend simplification: "Current implementation is excessive. Should narrow to [X feature] only"
- Justified retention: "Clear value exists. However, [Y] improvement needed"

### Round 1: Security Perspective

Key check items:
- **Input validation**: Proper validation of all user input
- **Output escaping**: XSS/injection countermeasure implementation status
- **Authentication/Authorization**: Appropriateness of permission checks, session management
- **Sensitive information**: Hardcoded secrets, API keys, etc.
- Encrypted communication: HTTPS/TLS usage, sensitive data protection
- Dependencies: Use of libraries with known vulnerabilities
- OWASP compliance: Response status to each OWASP Top 10 item

Analysis methods:
```bash
# Search for sensitive information
rg -i "password|api_key|secret|token" --type typescript

# Check for dangerous function usage
rg "dangerouslySetInnerHTML|eval\(|Function\(|execSync" --type typescript
```

### Round 2: Performance Perspective

Key check items:
- **Computational complexity**: Appropriateness of algorithm time/space complexity
- **N+1 problem**: Efficiency of database queries, API calls
- **Memory leaks**: Proper cleanup of event listeners, timers
- **Bundle size**: Unnecessary dependencies, Tree Shaking optimization
- Rendering: React rendering optimization (useMemo, useCallback)
- Async processing: Proper use of Promise, async/await
- Caching: Implementation of appropriate cache strategies

Analysis methods:
```bash
# Detect API calls in loops
rg "for.*await|while.*await|\.map\(async" --type typescript

# Identify large files
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec wc -l {} + | sort -rn | head -10
```

### Round 3: Maintainability Perspective

Key check items:
- **Single responsibility principle**: Clarity of each function/component responsibility
- **DRY principle**: Code duplication, appropriateness of abstraction
- **Naming conventions**: Consistency, self-documenting naming
- **Type safety**: TypeScript strict mode, type inference utilization
- Testability: Unit test ease, dependency injection
- Documentation: Appropriateness of comments, JSDoc, README
- Error handling: Exception handling, error message appropriateness
- Scalability: Response to future expansion

Analysis methods:
```bash
# Check for missing type annotations
rg ": any|as any" --type typescript

# Detect code duplication
rg -n "function.*\{" --type typescript | awk -F: '{print $2}' | sort | uniq -c | sort -rn | head -10
```

## Review Mode Selection

### Default Mode: Zero-Based Thinking Review

Characteristics:
- Includes Round 0 "Necessity Review" (4 rounds)
- Asks "is this even needed?" first
- Actively considers deletion/simplification

Use cases:
- New feature proposal/design stage
- Existing feature inventory
- Organization of configuration files like CLAUDE.md
- Preventing feature bloat

### Constructive Review Mode: --skip-necessity

Characteristics:
- Skip Round 0 (3 rounds)
- Only propose improvements
- Don't consider deletion/simplification

Use cases:
- Improving features with proven value
- During new feature implementation (not yet complete)
- During refactoring (features remain)
- Security/performance improvement purposes

Usage examples:
```bash
# Quality improvement of existing critical features
/iterative-review src/auth/login.ts --skip-necessity

# Review of features under new implementation
/iterative-review src/features/new-feature.ts --skip-necessity
```

## Perspective Customization

Perspectives other than defaults can be specified:

### Additional Perspective Examples

- **necessity**: Necessity evaluation (Round 0) ← **Included by default**
- **accessibility**: Accessibility (WCAG compliance)
- **i18n**: Internationalization support
- **testing**: Test coverage/quality
- **documentation**: Documentation completeness
- **consistency**: Coding conventions/consistency
- **scalability**: Scalability
- **simplicity**: Simplicity/complexity evaluation

### Custom Perspective Usage Examples

```bash
# Accessibility + i18n focus
/iterative-review components/ --perspectives=accessibility,i18n

# Comprehensive 5-perspective review
/iterative-review src/ --perspectives=necessity,security,performance,maintainability,testing
```

## Target-Specific Reviews

### Document Review (.md)

Additional check items:
- Structure: Hierarchy, table of contents, section division
- Links: Broken internal links, external link validity
- Consistency: Term unification, format unification
- Completeness: Sufficiency/excess of necessary information
- Currency: Old information, date appropriateness

### Configuration File Review (CLAUDE.md, etc.)

Additional check items:
- Practicality: Actually usable commands/procedures
- Maintainability: Bloat, duplication, organization status
- Learning curve: Ease of understanding for new users
- Extensibility: Ease of adding new features

## Integrated Report Format

After all rounds complete, generate an integrated report in the following format:

```markdown
# Iterative Review Results

## Basic Information
- Target: [filename/directory/MR number]
- Type: [TypeScript/Python/Document, etc.]
- Review Date/Time: [YYYY-MM-DD HH:MM]
- Number of Perspectives: [4 (necessity, security, performance, maintainability)]

## Round 0: Necessity Review

### Final Decision: Recommend Deletion / Recommend Simplification / Justified Retention

Reason: [Specific justification for decision]
Alternative: [Specific alternative means for deletion/simplification case]

## Round 1: Security Perspective
[Findings and recommended actions]

## Round 2: Performance Perspective
[Findings and recommended actions]

## Round 3: Maintainability Perspective
[Findings and recommended actions]

## Overall Evaluation

### Round 0 Decision Result

Recommend Deletion / Recommend Simplification / Justified Retention

Note: If Round 0 recommends deletion, detailed improvements from subsequent rounds are treated as reference information

### Findings Summary
- Critical: [X items]
- Important: [Y items]
- Minor: [Z items]

### Priority Action Plan

Top Priority (Fundamental response based on Round 0 decision):
[Specific steps for deletion/simplification/improvement]

High Priority (Only if retention is justified):
[Response to Critical Issues]

Medium Priority (Only if retention is justified):
[Response to Important Issues]

### Overall Observations

Round 0 Decision Impact:
- Recommend deletion: This feature is fundamentally unnecessary. No need to implement subsequent improvement proposals.
- Recommend simplification: Current implementation is excessive. Prioritize major simplification; defer minor improvements.
- Justified retention: Clear value exists; worth implementing the following improvements.

Overall Assessment:
[Comprehensive direction considering Round 0 decision]
```

## Notes

- Session independence: Each round executes as a new session
- Time management: Target 5-10 minutes per round
- Emphasis on specifics: Specify filename:line number, not abstract issues
- Constructive attitude: Present solutions, not just problem identification

## Examples

Input: /iterative-review src/components/Button.tsx
Action: Execute 4-round review (necessity, security, performance, maintainability) on Button.tsx

Input: /iterative-review src/ --skip-necessity
Action: Execute 3-round review (security, performance, maintainability) on src directory

Input: /iterative-review feature.ts --perspectives=necessity --rounds=1
Action: Execute necessity review only on feature.ts

Input: /iterative-review
Action: Interactive mode, use AskUserQuestion to select target
