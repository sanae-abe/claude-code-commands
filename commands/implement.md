---
allowed-tools: TodoWrite, Bash, Read, Edit, Write, AskUserQuestion
argument-hint: "[task-id]"
description: "Implement a task from tasks.yml with automatic document context injection"
model: sonnet
---

# implement

Arguments: $ARGUMENTS

## Purpose

Document-driven task implementation with automatic context injection from tasks.yml.

## Execution Flow

1. Parse task ID from $ARGUMENTS
2. Load tasks.yml and validate
3. Extract task information
4. Load document references automatically
5. Create TodoWrite task list
6. Implement with full context
7. Update task status in tasks.yml

## Argument Validation

Parse $ARGUMENTS to extract task ID:
- Format: `task-N` where N is a number
- Example: `task-1`, `task-42`

If no argument provided:
- List all pending tasks
- Ask user to select one

If invalid format:
- Report error and show correct format
- Exit

## Tool Usage

TodoWrite: Create implementation task list:
1. Load task from tasks.yml
2. Extract document references
3. Create implementation steps
4. Execute implementation
5. Update task status

Bash: Execute Python scripts:
- Load tasks.yml
- Validate schema
- Extract task context
- Update task status

Read: Load document sections:
- Read referenced documents
- Extract specific sections
- Inject into context

## Load Task Context

Step 1: Validate tasks.yml exists and load task information

Combined Python script for efficiency (single interpreter startup):

```bash
# Auto-create tasks.yml if missing
if [ ! -f "tasks.yml" ]; then
  echo "⚠️  tasks.yml not found. Creating empty tasks.yml..."
  cat > tasks.yml << 'EOF'
project:
  name: "Project Tasks"
  last_updated: ""

tasks: []
EOF
  echo "✅ Created empty tasks.yml"
  echo ""
fi

# Extract and validate task ID
TASK_ID="$ARGUMENTS"

# Unified Python script: list tasks, validate, load context, check dependencies
TEMP_FILE=$(mktemp /tmp/task-context.XXXXXX.json)
trap 'rm -f "$TEMP_FILE"' EXIT

python3 << PYTHON
import yaml
import json
import sys
from datetime import datetime

TASK_ID = "$TASK_ID"

# Load tasks.yml
try:
    with open('tasks.yml', 'r') as f:
        data = yaml.safe_load(f)
except Exception as e:
    print(f"ERROR: Failed to load tasks.yml: {e}")
    sys.exit(1)

# If no task ID provided, list pending tasks
if not TASK_ID:
    print("Available pending tasks:")
    print()
    pending = [t for t in data['tasks'] if t['status'] == 'pending']
    for t in pending:
        priority = t.get('priority', 'medium')
        effort = t.get('effort', '?')
        print(f"  {t['id']}: {t['goal']}")
        print(f"    Priority: {priority}, Effort: {effort}")
        print()
    print("Usage: /implement <task-id>")
    sys.exit(1)

# Find task
task = next((t for t in data['tasks'] if t['id'] == TASK_ID), None)
if not task:
    print(json.dumps({"error": f"Task {TASK_ID} not found in tasks.yml"}))
    sys.exit(1)

# Check dependencies
if 'depends_on' in task and task['depends_on']:
    for dep_id in task['depends_on']:
        dep = next((t for t in data['tasks'] if t['id'] == dep_id), None)
        if dep and dep['status'] != 'completed':
            print(json.dumps({"error": f"Dependency {dep_id} not completed (status: {dep['status']})"}))
            sys.exit(1)

# Build context
context = {
    "task": task,
    "documents": [{"reference": ref} for ref in task.get('docs', [])]
}

# Save to temporary file
with open('$TEMP_FILE', 'w') as f:
    json.dump(context, f, ensure_ascii=False, indent=2)

print("✅ Task context loaded successfully")
PYTHON

# Check if Python script failed
if [ $? -ne 0 ]; then
  exit 1
fi
```

## Create TodoWrite Task List

Parse task context and create implementation steps:

```bash
python3 << PYTHON
import json
import sys

with open('$TEMP_FILE', 'r') as f:
    context = json.load(f)

task = context['task']
docs = context.get('documents', [])

print(f"Task: {task['goal']}")
print(f"Priority: {task.get('priority', 'medium')}")
print(f"Type: {task.get('type', 'implementation')}")
print()

if docs:
    print(f"Document References ({len(docs)}):")
    for doc in docs:
        print(f"  - {doc['reference']}")
    print()

if 'acceptance_criteria' in task:
    print("Acceptance Criteria:")
    for i, criteria in enumerate(task['acceptance_criteria'], 1):
        print(f"  {i}. {criteria}")
    print()

if 'depends_on' in task and task['depends_on']:
    print("Dependencies:")
    for dep in task['depends_on']:
        print(f"  - {dep}")
    print()
PYTHON
```

Use TodoWrite to create implementation steps:
1. "Load task context and documents"
2. "Implement core functionality"
3. "Verify acceptance criteria"
4. "Update task status to completed"

## Inject Document Context

For each document reference in task.docs:

```bash
# Extract document references
DOC_REFS=$(python3 << PYTHON
import json
with open('$TEMP_FILE', 'r') as f:
    context = json.load(f)
for doc in context.get('documents', []):
    print(doc['reference'])
PYTHON
)

# For each document reference
for DOC_REF in $DOC_REFS; do
  # Parse "file.md#Section" format
  FILE_PATH=$(echo "$DOC_REF" | cut -d'#' -f1)
  SECTION=$(echo "$DOC_REF" | cut -d'#' -f2)
  
  echo "Loading: $DOC_REF"
  
  # Use Read tool to load the file
  # The Read tool call will be made by the LLM executing this command
  # Document content will be automatically available in context
done
```

## Implementation Phase

With full context loaded (task info + all referenced documents):

1. **Understand requirements**:
   - Task goal
   - Acceptance criteria
   - Referenced design documents
   - API specifications
   - Security requirements

2. **Implement solution**:
   - Follow patterns from referenced documents
   - Meet all acceptance criteria
   - Apply security best practices
   - Write clean, maintainable code

3. **Verify implementation**:
   - Check all acceptance criteria met
   - Run tests if applicable
   - Validate security requirements

## Update Task Status

After successful implementation:

```bash
# Update task status to completed
python3 << PYTHON
import yaml
from datetime import datetime

with open('tasks.yml', 'r') as f:
    data = yaml.safe_load(f)

for task in data['tasks']:
    if task['id'] == '$TASK_ID':
        task['status'] = 'completed'
        task['completed_at'] = datetime.utcnow().isoformat() + 'Z'
        break

data['project']['last_updated'] = datetime.utcnow().isoformat() + 'Z'

with open('tasks.yml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

print(f"✅ Task {task['id']} marked as completed")
PYTHON

# Update todos.md if it exists
if [ -f "todos.md" ]; then
  python3 << 'PYTHON'
import re
import sys

task_id = '$TASK_ID'

try:
    # Read todos.md
    with open('todos.md', 'r') as f:
        lines = f.readlines()

    # Find and update #task-N line
    updated = False
    for i, line in enumerate(lines):
        if f'#{task_id}' in line and '- [ ]' in line:
            lines[i] = line.replace('- [ ]', '- [x]')
            updated = True
            break

    # Write back if updated
    if updated:
        with open('todos.md', 'w') as f:
            f.writelines(lines)
        print(f"✅ todos.mdも更新しました: #{task_id}")
    else:
        # Task not found in todos.md (not an error)
        pass

except Exception as e:
    # Log warning but don't fail
    print(f"⚠️  Warning: todos.md更新に失敗しました: {e}", file=sys.stderr)
    print(f"⚠️  次回 /todo sync で修正されます", file=sys.stderr)
    # Continue execution (don't exit)
PYTHON
fi
```

## Error Handling

**Note**: Most error handling (tasks.yml not found, task not found, dependencies not met) is now integrated into the unified Python script in the "Load Task Context" section above.

**Invalid task ID format** (optional additional validation):
```bash
if [ -n "$TASK_ID" ] && ! echo "$TASK_ID" | grep -qE '^task-[0-9]+$'; then
  echo "ERROR: Invalid task ID format"
  echo "Expected: task-N (e.g., task-1)"
  exit 1
fi
```

**Document reference not found**:
```bash
# If document file doesn't exist, warn but continue
if [ ! -f "$FILE_PATH" ]; then
  echo "⚠️  WARNING: Document not found: $FILE_PATH"
  echo "Continuing without this reference..."
fi
```

## Examples

### Implement task-1
```
/implement task-1
```

Output:
```
Task: Implement user authentication system
Priority: high
Type: implementation

Document References (3):
  - docs/design.md#Authentication
  - docs/api-spec.md#Auth-Endpoints
  - docs/security.md#JWT-Implementation

Acceptance Criteria:
  1. User can login with email/password
  2. JWT token issued on successful login
  3. Token refresh endpoint working
  4. Logout invalidates token
  5. Protected routes return 401 for invalid tokens

[Loads all 3 document sections automatically]
[Implements with full context]
✅ Task task-1 marked as completed
```

### List pending tasks
```
/implement
```

Output:
```
Available pending tasks:

  task-1: Implement user authentication system
    Priority: high, Effort: 8h

  task-2: Write unit tests for authentication
    Priority: high, Effort: 4h

  task-3: Refactor user service
    Priority: medium, Effort: 6h

Usage: /implement <task-id>
```

## Integration with Other Commands

**After implementation, validate**:
```
/implement task-1
/task-validate --layers=all
```

**Create commit**:
```
/implement task-1
/commit "Implement user authentication (task-1)"
```

**Create PR**:
```
/implement task-1
/pr
```

## Notes

- Document references are automatically loaded from tasks.yml
- No need to manually specify context files
- All referenced sections injected into implementation context
- Task status automatically updated on completion
- Dependencies checked before starting
- Acceptance criteria guide implementation

## Configuration

Optional: Create .claude/implement.json for project-specific settings:

```json
{
  "auto_validate": true,
  "auto_commit": false,
  "document_base_path": "docs/",
  "require_all_criteria": true
}
```
