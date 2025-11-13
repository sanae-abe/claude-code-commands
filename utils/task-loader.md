# Task Loader Utility

## Purpose

Load and parse tasks.yml files with automatic:
- YAML parsing
- Schema validation
- Document reference extraction
- Dependency resolution

## Usage in Slash Commands

```markdown
# In any slash command that needs task context

## Load Tasks

1. Check if tasks.yml exists in current directory
2. If not found, check project root
3. If not found, return empty task list

**Execution**:
```bash
# Find tasks.yml
TASKS_FILE=""
if [ -f "tasks.yml" ]; then
  TASKS_FILE="tasks.yml"
elif [ -f "../tasks.yml" ]; then
  TASKS_FILE="../tasks.yml"
elif [ -f "../../tasks.yml" ]; then
  TASKS_FILE="../../tasks.yml"
fi

if [ -z "$TASKS_FILE" ]; then
  echo "No tasks.yml found"
  exit 1
fi

# Validate YAML syntax
python3 -c "import yaml, sys; yaml.safe_load(open('$TASKS_FILE'))" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "ERROR: Invalid YAML syntax in $TASKS_FILE"
  exit 1
fi
```

## Schema Validation

Use Python with jsonschema for validation:

```python
#!/usr/bin/env python3
import yaml
import json
import jsonschema
import sys

# Load tasks.yml
with open(sys.argv[1], 'r') as f:
    tasks_data = yaml.safe_load(f)

# Load schema
with open(os.path.expanduser('~/.claude/schemas/tasks.schema.json'), 'r') as f:
    schema = json.load(f)

# Validate
try:
    jsonschema.validate(tasks_data, schema)
    print("✅ Schema validation passed")
    sys.exit(0)
except jsonschema.ValidationError as e:
    print(f"❌ Schema validation failed: {e.message}")
    sys.exit(1)
```

## Extract Task by ID

```bash
# Get task by ID (e.g., task-1)
TASK_ID="$1"

python3 << PYTHON
import yaml
import sys

with open('tasks.yml', 'r') as f:
    data = yaml.safe_load(f)

for task in data['tasks']:
    if task['id'] == '$TASK_ID':
        print(f"Goal: {task['goal']}")
        print(f"Status: {task['status']}")
        print(f"Priority: {task.get('priority', 'medium')}")
        
        # Extract docs
        if 'docs' in task:
            print("\nDocument References:")
            for doc in task['docs']:
                print(f"  - {doc}")
        
        # Extract acceptance criteria
        if 'acceptance_criteria' in task:
            print("\nAcceptance Criteria:")
            for i, criteria in enumerate(task['acceptance_criteria'], 1):
                print(f"  {i}. {criteria}")
        
        sys.exit(0)

print(f"ERROR: Task {TASK_ID} not found")
sys.exit(1)
PYTHON
```

## Extract Document References

Core functionality for document-driven development:

```python
#!/usr/bin/env python3
import yaml
import sys
import os

def extract_doc_section(file_path, section):
    """
    Extract a specific section from a markdown file.
    
    Args:
        file_path: Path to markdown file (e.g., "docs/design.md")
        section: Section header (e.g., "Authentication")
    
    Returns:
        Section content as string
    """
    if not os.path.exists(file_path):
        return f"ERROR: File not found: {file_path}"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find section header (supports ## or ### headers)
    import re
    pattern = rf'(##+ {re.escape(section)}.*?)(?=\n##+ |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    else:
        return f"ERROR: Section '{section}' not found in {file_path}"

def get_task_context(task_id):
    """
    Get full context for a task including all document references.
    
    Args:
        task_id: Task ID (e.g., "task-1")
    
    Returns:
        Dictionary with task info and document content
    """
    with open('tasks.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    task = next((t for t in data['tasks'] if t['id'] == task_id), None)
    if not task:
        return {"error": f"Task {task_id} not found"}
    
    context = {
        "task": task,
        "documents": []
    }
    
    # Extract each document reference
    if 'docs' in task:
        for doc_ref in task['docs']:
            # Parse "file.md#Section" format
            if '#' in doc_ref:
                file_path, section = doc_ref.split('#', 1)
                content = extract_doc_section(file_path.strip(), section.strip())
            else:
                # Whole file
                if os.path.exists(doc_ref):
                    with open(doc_ref, 'r') as f:
                        content = f.read()
                else:
                    content = f"ERROR: File not found: {doc_ref}"
            
            context["documents"].append({
                "reference": doc_ref,
                "content": content
            })
    
    return context

if __name__ == "__main__":
    task_id = sys.argv[1] if len(sys.argv) > 1 else "task-1"
    context = get_task_context(task_id)
    
    if "error" in context:
        print(context["error"])
        sys.exit(1)
    
    print(f"Task: {context['task']['goal']}")
    print(f"\nDocuments ({len(context['documents'])}):")
    for doc in context['documents']:
        print(f"\n{'='*60}")
        print(f"Reference: {doc['reference']}")
        print(f"{'='*60}")
        print(doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'])
```

## Resolve Dependencies

```python
#!/usr/bin/env python3
import yaml
import sys

def get_dependencies(task_id, data):
    """
    Recursively get all dependencies for a task.
    
    Returns list of task IDs in dependency order.
    """
    task = next((t for t in data['tasks'] if t['id'] == task_id), None)
    if not task:
        return []
    
    deps = []
    if 'depends_on' in task:
        for dep_id in task['depends_on']:
            # Recursively get dependencies
            deps.extend(get_dependencies(dep_id, data))
            deps.append(dep_id)
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for dep in deps:
        if dep not in seen:
            seen.add(dep)
            result.append(dep)
    
    return result

with open('tasks.yml', 'r') as f:
    data = yaml.safe_load(f)

task_id = sys.argv[1]
deps = get_dependencies(task_id, data)

if deps:
    print(f"Task {task_id} depends on:")
    for dep in deps:
        dep_task = next((t for t in data['tasks'] if t['id'] == dep), None)
        status = dep_task['status'] if dep_task else 'unknown'
        print(f"  - {dep} ({status})")
        
        if status != 'completed':
            print(f"\n⚠️  WARNING: Dependency {dep} is not completed!")
            sys.exit(1)
else:
    print(f"Task {task_id} has no dependencies")
```

## Integration with Read Tool

When implementing /implement or other commands, use Read tool to fetch document sections:

```markdown
# In slash command

## Step 1: Load task context

```bash
TASK_ID="task-1"
python3 ~/.claude/utils/task-context-loader.py "$TASK_ID" > /tmp/task-context.json
```

## Step 2: Extract document references

```bash
# Parse JSON to get document paths
python3 << PYTHON
import json
with open('/tmp/task-context.json', 'r') as f:
    context = json.load(f)

for doc in context['documents']:
    print(doc['reference'])
PYTHON
```

## Step 3: Use Read tool to fetch each document

For each document reference in task.docs:
1. Parse "file.md#Section" format
2. Use Read tool to load file.md
3. Extract section content
4. Inject into agent prompt
```

## Error Handling

**File not found**:
```bash
if [ ! -f "tasks.yml" ]; then
  echo "ERROR: tasks.yml not found in current directory"
  echo "Run: cp ~/.claude/templates/tasks.template.yml tasks.yml"
  exit 1
fi
```

**Invalid YAML**:
```bash
python3 -c "import yaml; yaml.safe_load(open('tasks.yml'))" 2>&1
if [ $? -ne 0 ]; then
  echo "ERROR: Invalid YAML syntax"
  echo "Fix syntax errors before proceeding"
  exit 1
fi
```

**Schema validation failure**:
```python
try:
    jsonschema.validate(data, schema)
except jsonschema.ValidationError as e:
    print(f"ERROR: Schema validation failed")
    print(f"Field: {'.'.join(str(p) for p in e.path)}")
    print(f"Issue: {e.message}")
    sys.exit(1)
```

**Missing document reference**:
```python
if not os.path.exists(file_path):
    print(f"WARNING: Document not found: {file_path}")
    print(f"Task {task_id} references missing document")
    print(f"Continue without this context? (y/N)")
```

## Quick Reference

### Validate tasks.yml
```bash
python3 << 'PYTHON'
import yaml, json, jsonschema, os
data = yaml.safe_load(open('tasks.yml'))
schema = json.load(open(os.path.expanduser('~/.claude/schemas/tasks.schema.json')))
jsonschema.validate(data, schema)
print("✅ Valid")
PYTHON
```

### Get pending tasks
```bash
python3 << 'PYTHON'
import yaml
data = yaml.safe_load(open('tasks.yml'))
pending = [t for t in data['tasks'] if t['status'] == 'pending']
for t in pending:
    print(f"{t['id']}: {t['goal']} ({t.get('priority', 'medium')})")
PYTHON
```

### Get task context
```bash
python3 ~/.claude/utils/task-context-loader.py task-1
```
