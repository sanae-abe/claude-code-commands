---
allowed-tools: Read, AskUserQuestion
argument-hint: "<question-or-options>"
description: Framework-driven decision support for tech choices and priority ranking
model: sonnet
---

# /decide - Decision Support Command

Arguments: $ARGUMENTS

Framework-driven decision support using ICE/RICE scoring, Eisenhower Matrix, and First Principles for technology selection, feature prioritization, and architecture evaluation.

Purpose:
- Systematic decision making with quantitative frameworks
- Pre-implementation option comparison and idea generation
- Conclusion-first format with clear recommendations

Timing: Before implementation, when comparing options

Output: Conclusion-first format with comparison tables

## Execution Flow

1. Read decision-frameworks.md for framework reference
2. Parse and validate $ARGUMENTS
3. Auto-detect decision type and output format
4. Apply appropriate framework (ICE/RICE/Eisenhower/First Principles)
5. Generate conclusion-first output with detailed analysis

## Argument Validation

Parse $ARGUMENTS:
- Extract question or options text
- Sanitize special characters
- Detect output format (single recommendation vs multiple proposals)
- Detect framework type (tech selection vs prioritization vs architecture)

If $ARGUMENTS empty or unclear:
- Use AskUserQuestion to clarify evaluation target
- Example: "What options or question would you like to evaluate?"

Security:
- No file path processing required
- No Bash execution needed
- Read-only access to decision-frameworks.md

## Auto-Detection Logic

Step 1: Detect output format from $ARGUMENTS

```
IF question contains "A vs B" OR "which is better" OR "compare":
    Output format: single recommendation (choose one)

ELIF question contains "what to improve" OR "what to add" OR "what should" OR "priorities":
    Output format: multiple proposals (rank top 3-5)

ELIF $ARGUMENTS contains numbered list ("1. A 2. B 3. C"):
    Output format: prioritization (rank all items)

ELSE:
    Output format: auto-decide based on candidate count
    If 2 or fewer candidates: single recommendation
    If 3+ candidates: multiple proposals
```

Step 2: Detect framework type from $ARGUMENTS

```
IF mentions technology, library, tool names:
    Framework: ICE Score evaluation

ELIF mentions architecture, system design, implementation approach:
    Framework: RICE Score + Pre-mortem

ELIF mentions risk, uncertainty, confidence:
    Framework: Confidence analysis + Spike recommendation

ELIF contains 3+ tasks or features:
    Framework: Eisenhower Matrix + ICE Score

ELSE:
    Framework: ICE Score + First Principles (general purpose)
```

## Framework Reference

Read required file:
```
Read ~/.claude/docs/decision-frameworks.md
```

If file read fails:
- Report error with file location
- Suggest checking symbolic link at ~/.claude/docs/decision-frameworks.md
- Exit without attempting analysis

## Output Patterns

### Pattern A: Single Recommendation

Used when: Comparing 2 options or explicit "A vs B" question

Structure:
```
## Conclusion: [Recommended Option] is recommended

Reason: ICE Score [value] ([priority level]). [1-2 sentence rationale]

---

## Detailed Analysis

### ICE Score Evaluation
[Comparison table]

### First Principles Verification
[Premise decomposition]

### Alternative Comparison
[Cost/benefit table]

### Risk Assessment
[Security/Technical/Development risks]

### Final Recommendation
[Action items]
```

### Pattern B: Multiple Proposals

Used when: "What to improve?" or "What should we do?" questions

Structure:
```
## Conclusion: Implement in following order

1. [Proposal 1] (ICE [score]) - Highest priority
   Reason: [Impact/Confidence/Ease rationale]

2. [Proposal 2] (ICE [score]) - High priority
   Reason: [Impact/Confidence/Ease rationale]

3. [Proposal 3] (ICE [score]) - Medium priority
   Reason: [Impact/Confidence/Ease rationale]

Recommended action: Implement top 2 in current sprint

---

## Detailed Analysis

### ICE Score Evaluation (All Candidates)
[Comparison table with 3-5 items]

### First Principles Verification (Top 3)
[Necessity verification for each]

### Risk Assessment (Top 3)
[Risks for each proposal]

### Final Recommendation
[Categorize: Immediate/Next sprint/Backlog/Reject]
```

### Pattern C: Prioritization

Used when: Numbered list provided in $ARGUMENTS

Structure:
```
## Conclusion: Priority ranking

1. [Task A] (ICE [score]) - Immediate
2. [Task B] (ICE [score]) - Next sprint
3. [Task C] (ICE [score]) - Rejected (YAGNI)

Reason: [Eisenhower Matrix + ICE Score + First Principles integration]

---

## Detailed Analysis

### Phase 1: Eisenhower Matrix (Rough Filter)
[Urgency/Importance quadrant table]

### Phase 2: ICE Score (Detailed Evaluation)
[Comparison table]

### Phase 3: First Principles Verification (Top 3)
[Necessity verification]

### Final Priority
[Categorized action plan]
```

## Framework Application

### ICE Score Calculation

For each option:
```
Impact: 1-10 (DX improvement, performance, business value)
Confidence: 0-100% (past success cases, available data)
Ease: 1-10 (implementation effort, learning cost)

ICE Score = (Impact × Confidence × Ease) / 3

Priority levels:
- 20+: Highest priority (immediate)
- 10-20: High priority (scheduled)
- 5-10: Medium priority (backlog)
- <5: Low priority (reject)
```

Always include rationale for each score:
- Impact: Specific effect on system/users
- Confidence: Evidence source (past cases, data, logical reasoning)
- Ease: Time estimate and complexity assessment

### First Principles Verification

For top candidates:
```
Premise: "[Assumption being made]"

Decomposition:
- Question 1: "When does [benefit] occur?"
- Answer: "[Specific condition]"
- Question 2: "Is current situation problematic?"
- Answer: "[Current state analysis]"

Reconstruction from fundamentals:
- Conclusion: "[Is this truly necessary? YAGNI application?]"
- Decision: "MUST/YAGNI/CONDITIONAL - [reasoning]"
```

### Confidence Criteria

From decision-frameworks.md:
- 90-100%: Past success cases exist, real data available
- 70-90%: Inferable from similar cases
- 50-70%: Hypothesis stage with logical basis
- <50%: High uncertainty → Recommend Spike (technical validation)

### Risk Assessment

For each top option:
```
Security Risk (highest priority):
- Level: HIGH/MEDIUM/LOW
- Specific risk: [Details]
- Confidence: [percentage] (Basis: [evidence])
- Mitigation: [Countermeasures]

Technical Risk:
- Level: HIGH/MEDIUM/LOW
- Specific risk: [Breaking changes, performance, maintainability]
- Confidence: [percentage]
- Mitigation: [Countermeasures]

Development Efficiency Risk:
- Level: HIGH/MEDIUM/LOW
- Specific risk: [Effort increase, learning cost]
- Confidence: [percentage]
- Mitigation: [Countermeasures]
```

## Output Requirements

### Conclusion-First Format

Mandatory structure:
```
## Conclusion: [Clear recommendation]

Reason: [Score + key rationale in 1-2 sentences]

---

## Detailed Analysis
[Framework-specific analysis]
```

### Numerical Justification

Bad example:
```
Impact: 7
```

Good example:
```
Impact: 7 (Used 100 times/week, significant DX improvement, affects core features)
```

### Confidence Over-Estimation Prevention

Judgment flow:
```
IF past success cases exist OR real data available:
    Confidence: 90-100%
ELIF inferable from similar cases:
    Confidence: 70-90%
ELIF hypothesis with logical basis:
    Confidence: 50-70%
ELSE:
    Confidence: <50%
    Recommendation: Execute Spike (technical validation)
```

### First Principles Challenge

YAGNI principle application:
- High ICE Score does not guarantee necessity
- Challenge "common sense" and "best practices"
- Reconstruct from fundamental principles

### Action Items Specification

Required items:
- Specific implementation steps
- Measurement metrics (when applicable)
- Rollback strategy (when applicable)
- Post-implementation quality check with /iterative-review

## Error Handling

decision-frameworks.md read failure:
```
ERROR: decision-frameworks.md not found

Resolution:
1. Check symbolic link: ls -la ~/.claude/docs/decision-frameworks.md
2. Check actual file: ls -la ~/projects/claude-code-workspace/docs/decision-frameworks.md
3. Report to user if recreation needed
```

Unclear $ARGUMENTS:
```
IF $ARGUMENTS empty OR ambiguous:
    Use AskUserQuestion for clarification
    Example: "Please specify options or question to evaluate"
```

## Relationship with /iterative-review

Role separation:

| Command | Purpose | Timing | Output Format |
|---------|---------|--------|---------------|
| /decide | Idea generation and decision making | Pre-implementation | Conclusion-first |
| /iterative-review | Multi-perspective review | Post-implementation | Round-by-round analysis |

Recommended workflow:
```
1. /decide "Zod vs Yup"
   → Conclusion: Zod recommended

2. Implement with Zod

3. /iterative-review src/validation/schema.ts
   → Quality check and refinement
```

## Exit Code System

```bash
# 0: Success - Decision analysis completed with recommendation
# 1: User error - Arguments missing, unclear question
# 2: Security error - (Not applicable - read-only command)
# 3: System error - decision-frameworks.md not found, Read tool failed
# 4: Unrecoverable error - Framework analysis failed critically
```

## Output Format

**Success example**:
```
## Conclusion: Zod is recommended

Reason: ICE Score 18.2 (Highest priority). Superior type safety, better DX, seamless TypeScript integration.

---

## Detailed Analysis

### ICE Score Evaluation
| Option | Impact | Confidence | Ease | ICE Score |
|--------|--------|------------|------|-----------|
| Zod    | 8      | 90%        | 9    | 18.2      |
| Yup    | 7      | 85%        | 8    | 15.9      |

### Risk Assessment
Security Risk: LOW - Both options provide adequate validation
Technical Risk: LOW - Well-documented migration path
Development Efficiency Risk: LOW - Zod reduces boilerplate

### Final Recommendation
1. Implement Zod validation schemas
2. Migrate existing Yup schemas incrementally
3. Monitor bundle size impact
```

**Error example**:
```
ERROR: decision-frameworks.md not found
File: decide.md:load_frameworks

Reason: Required reference document missing
Got: File not found at ~/.claude/docs/decision-frameworks.md

Suggestions:
1. Check symbolic link: ls -la ~/.claude/docs/decision-frameworks.md
2. Verify source file exists
3. Recreate symlink if needed
```

## Examples

Input: /decide "Data validation library choice. Zod vs Yup?"
Action: Apply ICE Score evaluation, single recommendation output format

Input: /decide "What tests should we add to improve coverage?"
Action: Apply ICE Score evaluation, multiple proposals output format (top 3-5)

Input: /decide "Priority for these features: 1. Dark mode 2. Export 3. Notifications"
Action: Apply Eisenhower Matrix + ICE Score, prioritization output format

Input: /decide
Action: Use AskUserQuestion to get evaluation target
