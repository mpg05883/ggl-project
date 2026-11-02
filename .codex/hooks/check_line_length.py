"""PostToolUse hook: fail when an edited Python file breaks the 80-char limit.

Claude Code passes the tool call as JSON on stdin. Exit code 2 sends the
ruff output back to Claude so it can fix the violations in the same turn.
Anything unexpected (bad input, no ruff) only warns, so edits are never
blocked by a broken hook.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

RULES = "E501,W505"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        file_path = (payload.get("tool_input") or {}).get("file_path")
    except (json.JSONDecodeError, AttributeError) as exc:
        print(
            f"check_line_length: ignoring malformed input: {exc}",
            file=sys.stderr,
        )
        return 0

    if not file_path or not file_path.endswith(".py"):
        return 0
    path = Path(file_path)
    if not path.is_file():
        return 0

    if shutil.which("uv"):
        cmd = ["uv", "run", "ruff", "check"]
    elif shutil.which("ruff"):
        cmd = ["ruff", "check"]
    else:
        print("check_line_length: ruff not found, skipping", file=sys.stderr)
        return 0
    cmd += ["--select", RULES, str(path)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as exc:
        print(f"check_line_length: could not run ruff: {exc}", file=sys.stderr)
        return 0

    if result.returncode == 0:
        return 0
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 1:
        # 2+ means ruff itself failed (e.g. not installed in the venv).
        print(
            f"check_line_length: ruff failed, skipping:\n{output}",
            file=sys.stderr,
        )
        return 0
    print(
        f"Line-length violations in {path} "
        f"(limit 80; rewrap, don't shorten):\n{output}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
