#!/usr/bin/env python3
"""
Find next incomplete task from todo.md

Identifies the next task to work on and provides structured output for
Claude to handle /implement integration for big tasks.
"""

import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any


def read_todos() -> list[str]:
    """
    Read todo.md file.

    Returns:
        List of lines from todo.md

    Raises:
        FileNotFoundError: If todo.md not found
    """
    if not Path('todo.md').exists():
        raise FileNotFoundError("todo.md not found")

    with open('todo.md', 'r') as f:
        return f.readlines()


def find_next_incomplete_task(lines: list[str]) -> Optional[str]:
    """
    Find first incomplete task.

    Args:
        lines: Lines from todo.md

    Returns:
        Next incomplete task line or None if all completed
    """
    for line in lines:
        if line.strip().startswith('- [ ]'):
            return line.strip()

    return None


def parse_task_info(task_line: str) -> Dict[str, Any]:
    """
    Parse task information from task line.

    Args:
        task_line: Task line from todo.md

    Returns:
        Dict with task_id, priority, effort, description
    """
    info = {
        'task_id': None,
        'priority': 'unknown',
        'effort': 'unknown',
        'description': task_line,
        'is_big_task': False
    }

    # Check for #task-N pattern (big task)
    match = re.search(r'#(task-\d+)', task_line)
    if match:
        info['task_id'] = match.group(1)
        info['is_big_task'] = True

    # Extract priority
    priority_match = re.search(r'Priority:\s*(\w+)', task_line)
    if priority_match:
        info['priority'] = priority_match.group(1)

    # Extract effort
    effort_match = re.search(r'Effort:\s*([^|]+)', task_line)
    if effort_match:
        info['effort'] = effort_match.group(1).strip()

    return info


def display_next_task() -> None:
    """
    Main function: find and display next task with structured output.
    """
    try:
        # Read todo.md
        lines = read_todos()

        # Find next incomplete task
        next_task = find_next_incomplete_task(lines)

        if not next_task:
            print("All tasks completed")
            sys.exit(0)

        # Parse task information
        info = parse_task_info(next_task)

        if info['is_big_task']:
            # Big task - output structured info for Claude to handle
            print(f"NEXT_TASK_ID:{info['task_id']}")
            print(f"PRIORITY:{info['priority']}")
            print(f"EFFORT:{info['effort']}")
            print(f"DESCRIPTION:{next_task}")
        else:
            # Lightweight task - just display
            print(f"Next task (lightweight): {next_task}")
            print("Start working on this task")

    except FileNotFoundError:
        print("ERROR: todo.md not found")
        print("Run '/todo sync' to import tasks or '/todo add' to create tasks")
        sys.exit(1)

    except Exception as e:
        # Safe error message without exposing internals
        msg = str(e).split('\n')[0]
        print(f"Error finding next task: {msg}")
        sys.exit(1)


if __name__ == '__main__':
    display_next_task()
