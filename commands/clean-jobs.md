---
allowed-tools: Bash, AskUserQuestion
argument-hint:
description: Safe cleanup of background jobs
model: sonnet
---

# Background Job Cleanup

Arguments: None (interactive)

Safely cleans up only background jobs created in the current Claude Code session.
Does not affect other Claude Code sessions or separate terminal processes.

## Execution Flow

1. Check background jobs in current session
2. Present cleanup options via AskUserQuestion
3. Execute based on user selection
4. Verify and report results

## Tool Usage

AskUserQuestion: Present cleanup method selection with 3 options (clean all, select individually, cancel)

## Implementation Details

### Step 1: Check Current Jobs

Check background jobs with `jobs -l`.

```bash
jobs -l
```

If no jobs exist:
- Report "No background jobs to clean up"
- Exit

### Step 2: Present Cleanup Options

Use AskUserQuestion with the following options:

```json
{
  "questions": [{
    "question": "Select background job cleanup method",
    "header": "Cleanup",
    "multiSelect": false,
    "options": [
      {
        "label": "Clean up all",
        "description": "Kill all jobs in current session"
      },
      {
        "label": "Select individually",
        "description": "Kill specific job numbers (specify via \"Other\")"
      },
      {
        "label": "Cancel",
        "description": "Exit without doing anything"
      }
    ]
  }]
}
```

### Step 3: Execute Based on Selection

#### Option A: Clean up all

```bash
# Helper function: validate PID format
validate_pid() {
    local pid=$1
    [[ "$pid" =~ ^[0-9]+$ ]]
}

# Get all job PIDs
pids=($(jobs -p))

if [[ ${#pids[@]} -gt 0 ]]; then
    # Batch kill (single system call for performance)
    if kill "${pids[@]}" 2>/dev/null; then
        echo "All ${#pids[@]} jobs cleaned up"
    else
        # Fallback: count successful kills
        killed_count=0
        for pid in "${pids[@]}"; do
            validate_pid "$pid" && kill "$pid" 2>/dev/null && ((killed_count++))
        done
        echo "$killed_count jobs cleaned up"
        echo "Some jobs may have already terminated"
    fi
else
    echo "No jobs to clean up"
fi
```

#### Option B: Select individually

Receive input from AskUserQuestion "Other" field.
Expected format: space-separated job numbers (e.g., "1 3 5")

```bash
# Input from AskUserQuestion "Other" field
job_numbers="$USER_INPUT"

# Input validation: empty check
if [[ -z "$job_numbers" ]]; then
    echo "Error: No job numbers provided"
    exit 1
fi

# Input validation: format check (digits and spaces only)
if [[ ! "$job_numbers" =~ ^[0-9\ ]+$ ]]; then
    echo "Error: Job numbers must be digits and spaces only"
    echo "Example: 1 3 5"
    exit 1
fi

# Input validation: length limit (DoS prevention)
if [[ ${#job_numbers} -gt 100 ]]; then
    echo "Error: Input too long (max 100 characters)"
    exit 1
fi

# Race condition prevention: pre-fetch PIDs
pids=()
failed_jobs=()

for job_num in $job_numbers; do
    pid=$(jobs -p %$job_num 2>/dev/null)
    if [[ -n "$pid" ]]; then
        pids+=($pid)
    else
        failed_jobs+=($job_num)
    fi
done

# Batch kill (performance optimization)
if [[ ${#pids[@]} -gt 0 ]]; then
    if kill "${pids[@]}" 2>/dev/null; then
        killed_count=${#pids[@]}
        echo "$killed_count jobs cleaned up"
    else
        # Fallback: count successful kills
        killed_count=0
        for pid in "${pids[@]}"; do
            validate_pid "$pid" && kill "$pid" 2>/dev/null && ((killed_count++))
        done
        echo "$killed_count jobs cleaned up"
        echo "Some jobs may have already terminated"
    fi
fi

# Report failed job numbers
if [[ ${#failed_jobs[@]} -gt 0 ]]; then
    echo "Non-existent jobs: ${failed_jobs[*]}"
fi
```

#### Option C: Cancel

Exit without doing anything.

### Step 4: Verify Results

Check and report final state:

```bash
remaining_jobs=$(jobs -l)

if [[ -z "$remaining_jobs" ]]; then
    echo "All background jobs have been cleaned up"
else
    echo "Remaining jobs:"
    jobs -l
fi
```

## Error Handling

Input validation errors:
- If empty input: report "No job numbers provided"
- If invalid format: report "Job numbers must be digits and spaces only" with example
- If input too long: report "Input too long (max 100 characters)"

Execution errors:
- If kill fails: report count of successfully killed jobs
- If job does not exist: report non-existent job numbers
- Never expose absolute paths or internal details

## Examples

Input: /clean-jobs
Action: Display current jobs and present cleanup options

Input: User selects "Clean up all"
Action: Kill all jobs, report count
Output: "All 3 jobs cleaned up"

Input: User selects "Select individually" and enters "1 3 5"
Action: Kill jobs 1, 3, and 5, report results
Output: "3 jobs cleaned up"

Input: User selects "Select individually" and enters "1 99"
Action: Kill job 1, report job 99 does not exist
Output: "1 jobs cleaned up\nNon-existent jobs: 99"

Input: User selects "Cancel"
Action: Exit without changes

## Use Cases

- Cleanup after long development sessions
- Manual stop of processes started by development environment commands
- Periodic job cleanup for memory conservation
- Individual selection recommended when important tasks are running

## Session Isolation

This command only affects jobs in the current Claude Code session:
- Uses `jobs -l` which shows session-scoped jobs only
- Does not affect other Claude Code sessions
- Does not affect separate terminal processes
- OS-level permission controls prevent unauthorized kills
