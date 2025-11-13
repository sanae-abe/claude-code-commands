#!/usr/bin/env python3
"""
Agent Metadata Parser
Extract and validate frontmatter from .agent.md files
"""
import re
import yaml
import json
import jsonschema
import os
import sys
import fnmatch

def parse_agent_metadata(agent_file_path):
    """Parse frontmatter from .agent.md file."""
    with open(agent_file_path, 'r') as f:
        content = f.read()
    
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return None
    
    frontmatter = match.group(1)
    metadata = yaml.safe_load(frontmatter)
    return metadata

def validate_agent_metadata(metadata):
    """Validate metadata against schema."""
    schema_path = os.path.expanduser('~/.claude/schemas/agent-metadata.schema.json')
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    try:
        jsonschema.validate(metadata, schema)
        return (True, None)
    except jsonschema.ValidationError as e:
        return (False, e.message)

def get_tool_restrictions(metadata):
    """Generate tool restriction list."""
    restrictions = {
        "allowed": [],
        "forbidden": [],
        "mode": "none"
    }
    
    if 'tools' in metadata:
        restrictions["allowed"] = metadata['tools']
        restrictions["mode"] = "whitelist"
    
    if 'forbidden_tools' in metadata:
        restrictions["forbidden"] = metadata['forbidden_tools']
        if restrictions["mode"] == "none":
            restrictions["mode"] = "blacklist"
    
    if metadata.get('security_level') == 'high':
        restrictions["allowed"] = ["Read", "Grep", "Glob"]
        restrictions["forbidden"] = ["Write", "Edit", "Bash"]
        restrictions["mode"] = "whitelist"
    
    if metadata.get('readonly', False):
        if "Write" not in restrictions["forbidden"]:
            restrictions["forbidden"].append("Write")
        if "Edit" not in restrictions["forbidden"]:
            restrictions["forbidden"].append("Edit")
        if restrictions["mode"] == "none":
            restrictions["mode"] = "blacklist"
    
    return restrictions

def get_path_restrictions(metadata):
    """Generate path restriction rules."""
    restrictions = {
        "forbidden": [
            "~/.ssh",
            "~/.ssh/*",
            "~/.aws",
            "~/.aws/*",
            "~/.env*",
            ".env",
            ".env.*",
            "credentials.json",
            "secrets.*"
        ],
        "allowed": [],
        "mode": "blacklist"
    }
    
    if 'forbidden_paths' in metadata:
        restrictions["forbidden"].extend(metadata['forbidden_paths'])
    
    if 'allowed_paths' in metadata:
        restrictions["allowed"] = metadata['allowed_paths']
        restrictions["mode"] = "whitelist"
    
    return restrictions

def is_tool_allowed(tool_name, restrictions):
    """Check if tool is allowed."""
    mode = restrictions["mode"]
    
    if mode == "whitelist":
        return tool_name in restrictions["allowed"]
    elif mode == "blacklist":
        return tool_name not in restrictions["forbidden"]
    else:
        return True

def is_path_allowed(file_path, restrictions):
    """Check if path is allowed."""
    file_path = os.path.expanduser(file_path)
    
    for pattern in restrictions["forbidden"]:
        pattern = os.path.expanduser(pattern)
        if fnmatch.fnmatch(file_path, pattern) or file_path.startswith(pattern):
            return False
    
    if restrictions["mode"] == "whitelist":
        for pattern in restrictions["allowed"]:
            pattern = os.path.expanduser(pattern)
            if fnmatch.fnmatch(file_path, pattern) or file_path.startswith(pattern):
                return True
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: agent-metadata-parser.py <agent-file.md>")
        sys.exit(1)
    
    agent_file = sys.argv[1]
    
    metadata = parse_agent_metadata(agent_file)
    if not metadata:
        print(json.dumps({"error": "No frontmatter found"}))
        sys.exit(1)
    
    valid, error = validate_agent_metadata(metadata)
    if not valid:
        print(json.dumps({"error": f"Invalid metadata: {error}"}))
        sys.exit(1)
    
    tool_restrictions = get_tool_restrictions(metadata)
    path_restrictions = get_path_restrictions(metadata)
    
    output = {
        "metadata": metadata,
        "restrictions": {
            "tools": tool_restrictions,
            "paths": path_restrictions
        }
    }
    
    print(json.dumps(output, indent=2, ensure_ascii=False))
