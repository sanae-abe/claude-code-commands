#!/usr/bin/env python3
"""
Task Context Loader
Extracts task information and document references from tasks.yml
"""
import yaml
import sys
import os
import re
import json

def extract_doc_section(file_path, section):
    """Extract a specific section from a markdown file."""
    if not os.path.exists(file_path):
        return f"ERROR: File not found: {file_path}"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find section header (supports ## or ### headers)
    pattern = rf'(##+ {re.escape(section)}.*?)(?=\n##+ |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    else:
        return f"ERROR: Section '{section}' not found in {file_path}"

def get_task_context(task_id, tasks_file='tasks.yml'):
    """Get full context for a task including all document references."""
    if not os.path.exists(tasks_file):
        return {"error": f"tasks.yml not found"}
    
    with open(tasks_file, 'r') as f:
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
    if len(sys.argv) < 2:
        print("Usage: task-context-loader.py <task-id>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    context = get_task_context(task_id)
    
    if "error" in context:
        print(json.dumps({"error": context["error"]}))
        sys.exit(1)
    
    # Output as JSON for easy parsing
    print(json.dumps(context, indent=2, ensure_ascii=False))
