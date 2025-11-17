#!/usr/bin/env python3
"""
Sync tasks from tasks.yml to todo.md

Imports pending tasks from tasks.yml and appends new tasks to todo.md
with metadata (priority, effort). Idempotent - can be run multiple times safely.
"""

import os
import re
import shlex
import sys
from pathlib import Path
from typing import List, Dict, Any, Set

import yaml

# Add utils directory to path
utils_dir = Path(__file__).parent
sys.path.insert(0, str(utils_dir))

from task_sanitize import sanitize_goal
from todo_validation import validate_task_id, safe_error_message


def load_tasks_from_yaml() -> List[Dict[str, Any]]:
    """
    Load and validate tasks from tasks.yml.

    Returns:
        List of task dictionaries

    Raises:
        ValueError: If tasks.yml is invalid
        FileNotFoundError: If tasks.yml not found
    """
    with open('tasks.yml', 'r') as f:
        data = yaml.safe_load(f)

    # Validate data structure
    if not isinstance(data, dict):
        raise ValueError("Invalid tasks.yml: must be dict")

    tasks = data.get('tasks', [])
    if not isinstance(tasks, list):
        raise ValueError("Invalid tasks.yml: tasks must be list")

    return tasks


def get_max_task_id() -> int:
    """
    Get maximum task ID from last 100 lines of todo.md.

    This is more efficient than reading all task IDs for large files.
    Assumes task IDs are sequential (task-1, task-2, ...).

    Returns:
        Maximum task ID number (e.g., 5 for task-5), or 0 if no tasks
    """
    try:
        with open('todo.md', 'r') as f:
            lines = f.readlines()

            # Search last 100 lines in reverse (newest tasks are at bottom)
            for line in reversed(lines[-100:]):
                match = re.search(r'#task-(\d+)', line)
                if match:
                    return int(match.group(1))

    except FileNotFoundError:
        # Create empty todo.md if not exists
        Path('todo.md').touch()

    return 0


def filter_pending_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter tasks with status: pending or completed.

    Note: Despite the name, this now includes both pending and completed tasks
    to support syncing completed tasks with completed_at timestamps.

    Args:
        tasks: All tasks from tasks.yml

    Returns:
        List of pending and completed tasks
    """
    return [t for t in tasks if isinstance(t, dict) and t.get('status') in ['pending', 'completed']]


def append_new_tasks(new_tasks: List[Dict[str, Any]]) -> int:
    """
    Append new tasks to todo.md with security validation.

    Args:
        new_tasks: List of new tasks to append

    Returns:
        Number of tasks appended
    """
    import datetime
    from task_sanitize import sanitize_tags

    count = 0
    sync_date = datetime.date.today().isoformat()

    with open('todo.md', 'a') as f:
        for task in new_tasks:
            try:
                # Validate task ID (task-N pattern)
                task_id = validate_task_id(task['id'])

                # Sanitize goal text
                goal = sanitize_goal(task.get('goal', ''))

                # Get task status (pending or completed)
                status = task.get('status', 'pending')
                checkbox = '- [x]' if status == 'completed' else '- [ ]'

                # Quote metadata to prevent injection
                priority = shlex.quote(str(task.get('priority', 'medium')))

                # Build task line
                line = f"{checkbox} {goal} | Priority: {priority}"

                # Add Due field if exists
                due_date = task.get('due')
                if due_date:
                    # Parse ISO format to YYYY-MM-DD
                    if isinstance(due_date, str):
                        due_date = due_date.split('T')[0]  # Remove time part
                    line += f" | Due: {due_date}"

                # Add Created field (sync date)
                line += f" | Created: {sync_date}"

                # Add Completed field if task is completed
                if status == 'completed':
                    completed_at = task.get('completed_at')
                    if completed_at:
                        # Parse ISO format to YYYY-MM-DD
                        completed_date = completed_at.split('T')[0]
                    else:
                        completed_date = sync_date
                    line += f" | Completed: {completed_date}"

                # Add tags (#task-id #type)
                tags = [task_id]  # Always include task ID
                task_type = task.get('type')
                if task_type:
                    tags.append(task_type)

                # Sanitize and format tags
                tags_str = sanitize_tags(' '.join(tags))
                if tags_str:
                    hashtags = ' '.join(f'#{tag}' for tag in tags_str.split())
                    line += f" {hashtags}"

                line += "\n"
                f.write(line)

                count += 1

            except (KeyError, ValueError) as e:
                # Skip invalid tasks
                print(f"WARNING: Skipping invalid task: {safe_error_message(e, 'task validation')}", file=sys.stderr)
                continue

    return count


def sync_tasks() -> None:
    """
    Main sync function: import pending tasks from tasks.yml to todo.md.
    """
    try:
        # Load tasks from YAML
        all_tasks = load_tasks_from_yaml()
        pending_tasks = filter_pending_tasks(all_tasks)

        # Get maximum existing task ID (optimized for large files)
        max_id = get_max_task_id()

        # Filter new tasks (ID > max_id, assumes sequential IDs)
        new_tasks = []
        for t in pending_tasks:
            task_id = t.get('id', '')
            # Extract numeric part from task-N
            match = re.match(r'task-(\d+)', task_id)
            if match and int(match.group(1)) > max_id:
                new_tasks.append(t)

        # Append new tasks
        if new_tasks:
            count = append_new_tasks(new_tasks)
            print(f"Imported {count} new tasks")

            skipped = len(pending_tasks) - count
            if skipped > 0:
                print(f"  (Skipped {skipped} existing tasks)")
        else:
            print("No new tasks to import")

    except FileNotFoundError:
        print("ERROR: tasks.yml not found in current directory")
        print("Create tasks.yml or run from project root")
        sys.exit(1)

    except ValueError as e:
        print(safe_error_message(e, "loading tasks.yml"))
        sys.exit(1)

    except Exception as e:
        print(safe_error_message(e, "syncing tasks"))
        sys.exit(1)


if __name__ == '__main__':
    sync_tasks()
