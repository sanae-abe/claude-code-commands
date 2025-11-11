---
allowed-tools: Bash, AskUserQuestion
argument-hint:
description: Safe cleanup of background jobs
model: sonnet
---

# Background Job Cleanup

> **Version**: 1.1.0
> **Last Updated**: See Git history
> **Related Commands**: `/web-dev`, `/api-dev`, `/ds-notebook`

## Overview

Safely cleans up only background jobs created in the current Claude Code session.
Does not affect other Claude Code sessions.

**Intended Use Cases**:
- Cleanup after long development sessions
- Manual stop of processes started by `/web-dev` etc.
- Periodic job cleanup for memory conservation

## Execution Flow

1. **Check background jobs in current session**
2. **Present job list to user**
3. **Present cleanup method choices** (AskUserQuestion)
4. **Execute based on selection**

## Implementation Steps

### Step 1: Check Current Jobs

First, check background jobs in the current session with `jobs -l`.

```bash
jobs -l
```

**If 0 jobs:**
Display:
```
✅ No background jobs to clean up
```
and exit.

### Step 2: Present Cleanup Options

**If jobs exist:**

Use AskUserQuestion tool to present the following options:

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

### Step 3: Execute

Execute based on selection:

#### Clean up all

```bash
# Get all job PIDs and kill (optimized with arrays)
pids=($(jobs -p))

if [[ ${#pids[@]} -gt 0 ]]; then
    # Performance optimization with batch kill
    if kill "${pids[@]}" 2>&1; then
        echo "✅ All jobs cleaned up"
    else
        echo "⚠️  Some jobs failed to clean up"
        jobs -l  # Display remaining jobs
    fi
else
    echo "✅ No jobs to clean up"
fi
```

#### Select individually

**Receive input from AskUserQuestion "Other" option:**
- Prompt user for input in "1 3 5" format
- Example input: `1 3 5`

```bash
# Input from AskUserQuestion
# $USER_INPUT is input from "Other" field
job_numbers="$USER_INPUT"

# Input validation: only numbers and spaces allowed
if [[ ! "$job_numbers" =~ ^[0-9\ ]+$ ]]; then
    echo "❌ Error: Job numbers must be digits and spaces only (example: 1 3 5)"
    exit 1
fi

# Race condition prevention: pre-fetch job PIDs
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

# Batch kill collected PIDs
killed_count=0
for pid in "${pids[@]}"; do
    if kill "$pid" 2>/dev/null; then
        ((killed_count++))
    fi
done

# Result report
echo "✅ $killed_count jobs cleaned up"
if [[ ${#failed_jobs[@]} -gt 0 ]]; then
    echo "⚠️  Non-existent jobs: ${failed_jobs[*]}"
fi
```

#### Cancel

Exit without doing anything.

### Step 4: Verify Results

Check and report state after cleanup:

```bash
# Check after cleanup
remaining_jobs=$(jobs -l)

if [[ -z "$remaining_jobs" ]]; then
    echo "🎉 All background jobs have been cleaned up"
else
    echo "📋 Remaining jobs:"
    jobs -l
fi
```

## Notes

- This command only affects jobs in the **current session**
- Does not affect other Claude Code sessions or separate terminal processes
- Individual selection is recommended if important tasks are running

## Security Enhancements (v1.1.0)

- ✅ Unified to AskUserQuestion (eliminated `read` command)
- ✅ Race condition prevention (pre-fetch PIDs)
- ✅ Enhanced input validation (regex check)
- ✅ Performance optimization (use Bash arrays)
