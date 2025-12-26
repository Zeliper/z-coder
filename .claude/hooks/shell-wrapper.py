#!/usr/bin/env python
"""
Cross-platform shell command wrapper.
Replaces Unix shell commands like echo, cat for Windows/Linux compatibility.

Usage:
    python shell-wrapper.py echo --text "Hello World"
    python shell-wrapper.py echo --json '{"key": "value"}'
    python shell-wrapper.py cat --file path/to/file.txt
    python shell-wrapper.py env --name CLAUDE_PROJECT_DIR --default "."
    python shell-wrapper.py pipe-json --json '{"tools": ["npm"]}' --script .claude/hooks/check-tools.py
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get project root directory."""
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    # Infer from script location: .claude/hooks/shell-wrapper.py -> project root
    return Path(__file__).resolve().parent.parent.parent


def resolve_path(path_str: str) -> Path:
    """Resolve a path relative to project root or as absolute."""
    path = Path(path_str)
    if path.is_absolute():
        return path
    return get_project_root() / path


def cmd_echo(args) -> int:
    """Echo text to stdout (replacement for shell echo)."""
    if args.json:
        try:
            # Parse and re-dump for validation and formatting
            data = json.loads(args.text)
            print(json.dumps(data))
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            return 1
    else:
        print(args.text)
    return 0


def cmd_cat(args) -> int:
    """Print file contents (replacement for cat)."""
    path = resolve_path(args.file)

    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        return 1

    if not path.is_file():
        print(f"Error: Not a file: {path}", file=sys.stderr)
        return 1

    try:
        encoding = args.encoding or "utf-8"
        content = path.read_text(encoding=encoding)
        print(content, end="" if args.no_newline else "\n" if not content.endswith("\n") else "")
        return 0
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1


def cmd_env(args) -> int:
    """Print environment variable value."""
    value = os.environ.get(args.name, args.default or "")
    print(value)
    return 0 if value or args.allow_empty else 1


def cmd_pipe_json(args) -> int:
    """Pipe JSON data to another Python script via stdin."""
    script = resolve_path(args.script)

    if not script.exists():
        print(f"Error: Script not found: {script}", file=sys.stderr)
        return 1

    try:
        # Validate JSON
        json.loads(args.json)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        return 1

    try:
        # Get extra arguments if any
        extra_args = args.args.split() if args.args else []

        result = subprocess.run(
            [sys.executable, str(script)] + extra_args,
            input=args.json,
            text=True,
            capture_output=True
        )

        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")

        return result.returncode
    except Exception as e:
        print(f"Error running script: {e}", file=sys.stderr)
        return 1


def cmd_which(args) -> int:
    """Find executable path (cross-platform which/where)."""
    tool_name = args.name

    try:
        if sys.platform == "win32":
            result = subprocess.run(
                f"where {tool_name}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
        else:
            result = subprocess.run(
                f"which {tool_name}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

        if result.returncode == 0:
            print(result.stdout.strip().split("\n")[0])
            return 0
        else:
            if not args.quiet:
                print(f"Not found: {tool_name}", file=sys.stderr)
            return 1
    except Exception as e:
        if not args.quiet:
            print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_platform(args) -> int:
    """Print current platform (win32, linux, darwin)."""
    print(sys.platform)
    return 0


def cmd_python_path(args) -> int:
    """Print current Python executable path."""
    print(sys.executable)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Cross-platform shell command wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # echo command
    p_echo = subparsers.add_parser("echo", help="Echo text to stdout")
    p_echo.add_argument("--text", required=True, help="Text to echo")
    p_echo.add_argument("--json", action="store_true", help="Validate and format as JSON")

    # cat command
    p_cat = subparsers.add_parser("cat", help="Print file contents")
    p_cat.add_argument("--file", required=True, help="File to read")
    p_cat.add_argument("--encoding", help="File encoding (default: utf-8)")
    p_cat.add_argument("--no-newline", action="store_true", help="Don't add trailing newline")

    # env command
    p_env = subparsers.add_parser("env", help="Print environment variable")
    p_env.add_argument("--name", required=True, help="Environment variable name")
    p_env.add_argument("--default", help="Default value if not set")
    p_env.add_argument("--allow-empty", action="store_true", help="Return 0 even if empty")

    # pipe-json command
    p_pipe = subparsers.add_parser("pipe-json", help="Pipe JSON to another script")
    p_pipe.add_argument("--json", required=True, help="JSON data to pipe")
    p_pipe.add_argument("--script", required=True, help="Python script to run")
    p_pipe.add_argument("--args", help="Additional arguments for the script")

    # which command
    p_which = subparsers.add_parser("which", help="Find executable path")
    p_which.add_argument("--name", required=True, help="Executable name")
    p_which.add_argument("--quiet", action="store_true", help="Suppress error messages")

    # platform command
    subparsers.add_parser("platform", help="Print current platform")

    # python-path command
    subparsers.add_parser("python-path", help="Print Python executable path")

    args = parser.parse_args()

    commands = {
        "echo": cmd_echo,
        "cat": cmd_cat,
        "env": cmd_env,
        "pipe-json": cmd_pipe_json,
        "which": cmd_which,
        "platform": lambda a: cmd_platform(a),
        "python-path": lambda a: cmd_python_path(a),
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
