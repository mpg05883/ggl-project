#!/bin/bash
# Claude Code passes the tool call as JSON on stdin.
file=$(jq -r '.tool_input.file_path // empty')

# Only format Python files that exist.
if [[ "$file" == *.py && -f "$file" ]]; then
  ruff format "$file"
fi
exit 0