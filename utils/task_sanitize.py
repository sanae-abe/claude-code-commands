#!/usr/bin/env python3
"""
Task Goal Sanitization Utility

Security sanitization for task goals to prevent YAML/Markdown injection attacks.
Used by /todo sync when importing tasks from tasks.yml to todo.md.
"""

import re
import sys


def sanitize_goal(goal: str) -> str:
    """
    Sanitize task goal string for safe inclusion in todo.md.

    Security measures:
    1. Remove newlines (prevents Markdown injection)
    2. Remove checkbox patterns (prevents fake tasks)
    3. Detect dangerous characters (command injection prevention)
    4. Limit length (DoS prevention)

    Args:
        goal: Raw goal string from tasks.yml

    Returns:
        Sanitized goal string safe for todo.md
    """
    if not goal:
        return ""

    # 1. Remove newlines (Markdown injection prevention)
    goal = goal.replace('\n', ' ').replace('\r', ' ')

    # 2. Remove checkbox patterns (prevents fake task injection)
    goal = re.sub(r'- \[[x ]\]', '', goal)
    goal = re.sub(r'#task-\d+', '', goal)  # Remove task ID patterns

    # 3. Detect dangerous characters
    dangerous_chars = [';', '|', '&', '$', '`', '<', '>']
    for char in dangerous_chars:
        if char in goal:
            # Log warning but continue (don't fail)
            print(f"⚠️  Warning: Task goal contains potentially dangerous character: {char}",
                  file=sys.stderr)
            # Optionally escape or remove
            goal = goal.replace(char, '')

    # 4. Collapse multiple spaces
    goal = re.sub(r'\s+', ' ', goal)

    # 5. Length limit (DoS prevention)
    MAX_LENGTH = 200
    if len(goal) > MAX_LENGTH:
        goal = goal[:MAX_LENGTH] + "..."
        print(f"⚠️  Warning: Task goal truncated to {MAX_LENGTH} characters",
              file=sys.stderr)

    # 6. Trim whitespace
    goal = goal.strip()

    return goal


def main():
    """CLI interface for testing sanitization."""
    if len(sys.argv) < 2:
        print("Usage: task-sanitize.py <goal>")
        sys.exit(1)

    goal = sys.argv[1]
    sanitized = sanitize_goal(goal)
    print(sanitized)


if __name__ == "__main__":
    main()
