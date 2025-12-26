#!/usr/bin/env python
"""
Cross-platform file operations utility.
Replaces Unix commands like cp, rm, mkdir for Windows/Linux compatibility.

Usage:
    python file-ops.py backup --src .claude --dst .claude.backup.20240101
    python file-ops.py rmtree --path .claude/commands
    python file-ops.py copytree --src .source --dst .dest [--merge]
    python file-ops.py mkdir --path .claude/new_dir
"""
import argparse
import shutil
import sys
from pathlib import Path
import os
from datetime import datetime


def get_project_root() -> Path:
    """Get project root directory."""
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    # Infer from script location: .claude/hooks/file-ops.py -> project root
    return Path(__file__).resolve().parent.parent.parent


def resolve_path(path_str: str) -> Path:
    """Resolve a path relative to project root or as absolute."""
    path = Path(path_str)
    if path.is_absolute():
        return path
    return get_project_root() / path


def cmd_backup(args) -> int:
    """Create a backup copy of a directory."""
    src = resolve_path(args.src)
    dst = resolve_path(args.dst)

    if not src.exists():
        print(f"Error: Source path does not exist: {src}", file=sys.stderr)
        return 1

    if dst.exists():
        print(f"Error: Destination already exists: {dst}", file=sys.stderr)
        return 1

    try:
        shutil.copytree(src, dst)
        print(f"Backup created: {src} -> {dst}")
        return 0
    except Exception as e:
        print(f"Error creating backup: {e}", file=sys.stderr)
        return 1


def cmd_rmtree(args) -> int:
    """Remove a directory tree."""
    path = resolve_path(args.path)

    if not path.exists():
        if args.ignore_missing:
            print(f"Path does not exist (ignored): {path}")
            return 0
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return 1

    try:
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
        print(f"Removed: {path}")
        return 0
    except Exception as e:
        print(f"Error removing path: {e}", file=sys.stderr)
        return 1


def cmd_copytree(args) -> int:
    """Copy a directory tree."""
    src = resolve_path(args.src)
    dst = resolve_path(args.dst)

    if not src.exists():
        print(f"Error: Source path does not exist: {src}", file=sys.stderr)
        return 1

    try:
        if args.merge:
            # Merge copy: preserve existing files, only add/overwrite from source
            dst.mkdir(parents=True, exist_ok=True)
            for item in src.rglob("*"):
                rel = item.relative_to(src)
                target = dst / rel
                if item.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)
            print(f"Merged: {src} -> {dst}")
        else:
            # Clean copy: remove destination first if exists
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"Copied: {src} -> {dst}")
        return 0
    except Exception as e:
        print(f"Error copying: {e}", file=sys.stderr)
        return 1


def cmd_mkdir(args) -> int:
    """Create a directory (with parents)."""
    path = resolve_path(args.path)

    try:
        path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {path}")
        return 0
    except Exception as e:
        print(f"Error creating directory: {e}", file=sys.stderr)
        return 1


def cmd_copy(args) -> int:
    """Copy a single file."""
    src = resolve_path(args.src)
    dst = resolve_path(args.dst)

    if not src.exists():
        print(f"Error: Source file does not exist: {src}", file=sys.stderr)
        return 1

    if not src.is_file():
        print(f"Error: Source is not a file: {src}", file=sys.stderr)
        return 1

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"Copied: {src} -> {dst}")
        return 0
    except Exception as e:
        print(f"Error copying file: {e}", file=sys.stderr)
        return 1


def cmd_move(args) -> int:
    """Move a file or directory."""
    src = resolve_path(args.src)
    dst = resolve_path(args.dst)

    if not src.exists():
        print(f"Error: Source does not exist: {src}", file=sys.stderr)
        return 1

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"Moved: {src} -> {dst}")
        return 0
    except Exception as e:
        print(f"Error moving: {e}", file=sys.stderr)
        return 1


def cmd_exists(args) -> int:
    """Check if a path exists."""
    path = resolve_path(args.path)
    exists = path.exists()
    print("true" if exists else "false")
    return 0 if exists else 1


def cmd_timestamp(args) -> int:
    """Print current timestamp in specified format."""
    fmt = args.format or "%Y%m%d_%H%M%S"
    print(datetime.now().strftime(fmt))
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Cross-platform file operations utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # backup command
    p_backup = subparsers.add_parser("backup", help="Create a backup copy of a directory")
    p_backup.add_argument("--src", required=True, help="Source directory")
    p_backup.add_argument("--dst", required=True, help="Destination directory")

    # rmtree command
    p_rmtree = subparsers.add_parser("rmtree", help="Remove a directory tree")
    p_rmtree.add_argument("--path", required=True, help="Path to remove")
    p_rmtree.add_argument("--ignore-missing", action="store_true", help="Don't error if path doesn't exist")

    # copytree command
    p_copytree = subparsers.add_parser("copytree", help="Copy a directory tree")
    p_copytree.add_argument("--src", required=True, help="Source directory")
    p_copytree.add_argument("--dst", required=True, help="Destination directory")
    p_copytree.add_argument("--merge", action="store_true", help="Merge with existing directory")

    # mkdir command
    p_mkdir = subparsers.add_parser("mkdir", help="Create a directory")
    p_mkdir.add_argument("--path", required=True, help="Directory path to create")

    # copy command
    p_copy = subparsers.add_parser("copy", help="Copy a single file")
    p_copy.add_argument("--src", required=True, help="Source file")
    p_copy.add_argument("--dst", required=True, help="Destination file")

    # move command
    p_move = subparsers.add_parser("move", help="Move a file or directory")
    p_move.add_argument("--src", required=True, help="Source path")
    p_move.add_argument("--dst", required=True, help="Destination path")

    # exists command
    p_exists = subparsers.add_parser("exists", help="Check if a path exists")
    p_exists.add_argument("--path", required=True, help="Path to check")

    # timestamp command
    p_timestamp = subparsers.add_parser("timestamp", help="Print current timestamp")
    p_timestamp.add_argument("--format", help="strftime format (default: %%Y%%m%%d_%%H%%M%%S)")

    args = parser.parse_args()

    commands = {
        "backup": cmd_backup,
        "rmtree": cmd_rmtree,
        "copytree": cmd_copytree,
        "mkdir": cmd_mkdir,
        "copy": cmd_copy,
        "move": cmd_move,
        "exists": cmd_exists,
        "timestamp": cmd_timestamp,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
