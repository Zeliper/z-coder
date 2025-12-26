#!/usr/bin/env python
"""
copy-files.py - Orchestration 파일 복사 스크립트

.claude-orchestration/ (서브모듈) → .claude/ 로 파일 복사
크로스 플랫폼 지원 (Windows/Linux/macOS)

사용법:
    python copy-files.py [--force]

옵션:
    --force: 기존 파일 덮어쓰기 (LESSONS_LEARNED.md 제외)
"""

import os
import sys
import shutil
import argparse
from pathlib import Path


def get_project_root() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    # 환경 변수에서 프로젝트 디렉토리 가져오기
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        return Path(os.environ["CLAUDE_PROJECT_DIR"])

    # 현재 스크립트 위치에서 추론
    script_path = Path(__file__).resolve()
    # .claude/hooks/copy-files.py → 프로젝트 루트
    # 또는 .claude-orchestration/.claude/hooks/copy-files.py → 프로젝트 루트
    project_root = script_path.parent.parent.parent

    # 서브모듈 내에서 실행된 경우 (.claude-orchestration 폴더 내)
    if project_root.name == ".claude-orchestration":
        project_root = project_root.parent

    return project_root


def copy_directory(src: Path, dst: Path, exclude_files: list[str] = None):
    """디렉토리 복사 (존재하지 않는 파일만)"""
    if not src.exists():
        return

    exclude_files = exclude_files or []
    dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        if item.name in exclude_files:
            continue

        src_item = item
        dst_item = dst / item.name

        if item.is_dir():
            copy_directory(src_item, dst_item, exclude_files)
        else:
            # 파일이 없거나 force 모드일 때만 복사
            if not dst_item.exists():
                shutil.copy2(src_item, dst_item)
                print(f"  복사: {dst_item.relative_to(get_project_root())}")


def copy_file_if_not_exists(src: Path, dst: Path):
    """파일이 없을 때만 복사"""
    if src.exists() and not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  복사: {dst.relative_to(get_project_root())}")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Orchestration 파일 복사")
    parser.add_argument("--force", action="store_true", help="기존 파일 덮어쓰기")
    args = parser.parse_args()

    project_root = get_project_root()
    source_dir = project_root / ".claude-orchestration"
    target_dir = project_root / ".claude"

    # 서브모듈 확인
    if not source_dir.exists():
        print(f"오류: 서브모듈을 찾을 수 없습니다: {source_dir}")
        print("다음 명령으로 서브모듈을 추가하세요:")
        print("  git submodule add https://github.com/Zeliper/z-coder.git .claude-orchestration")
        sys.exit(1)

    print(f"소스: {source_dir}")
    print(f"대상: {target_dir}")
    print()

    # 대상 디렉토리 구조 생성
    directories = [
        "agents",
        "commands",
        "templates",
        "hooks",
        "skills/orchestration-workflow",
        "skills/spawn-search-agents",
        "skills/spawn-coder",
        "skills/spawn-builder",
    ]

    for dir_name in directories:
        (target_dir / dir_name).mkdir(parents=True, exist_ok=True)

    # tasks 디렉토리 생성
    tasks_dir = project_root / "tasks"
    archive_dir = tasks_dir / "archive"
    tasks_dir.mkdir(exist_ok=True)
    archive_dir.mkdir(exist_ok=True)

    # .gitkeep 파일 생성
    gitkeep_tasks = tasks_dir / ".gitkeep"
    gitkeep_archive = archive_dir / ".gitkeep"
    if not gitkeep_tasks.exists():
        gitkeep_tasks.touch()
    if not gitkeep_archive.exists():
        gitkeep_archive.touch()

    print("디렉토리 복사 중...")

    # agents 복사
    source_agents = source_dir / ".claude" / "agents"
    target_agents = target_dir / "agents"
    if source_agents.exists():
        print("\n[agents]")
        copy_directory(source_agents, target_agents)

    # commands 복사
    source_commands = source_dir / ".claude" / "commands"
    target_commands = target_dir / "commands"
    if source_commands.exists():
        print("\n[commands]")
        copy_directory(source_commands, target_commands)

    # templates 복사
    source_templates = source_dir / ".claude" / "templates"
    target_templates = target_dir / "templates"
    if source_templates.exists():
        print("\n[templates]")
        copy_directory(source_templates, target_templates)

    # hooks 복사
    source_hooks = source_dir / ".claude" / "hooks"
    target_hooks = target_dir / "hooks"
    if source_hooks.exists():
        print("\n[hooks]")
        copy_directory(source_hooks, target_hooks)

    # skills 복사
    source_skills = source_dir / ".claude" / "skills"
    target_skills = target_dir / "skills"
    if source_skills.exists():
        print("\n[skills]")
        copy_directory(source_skills, target_skills)

    # LESSONS_LEARNED 템플릿 복사 (파일이 없을 때만)
    print("\n[LESSONS_LEARNED]")
    source_lessons = source_dir / ".claude" / "LESSONS_LEARNED.template.md"
    target_lessons = target_dir / "LESSONS_LEARNED.md"
    if copy_file_if_not_exists(source_lessons, target_lessons):
        print("  LESSONS_LEARNED.md 생성됨")
    else:
        print("  LESSONS_LEARNED.md 이미 존재함 (스킵)")

    # settings.json 복사 (파일이 없을 때만)
    print("\n[settings.json]")
    source_settings = source_dir / ".claude" / "settings.json"
    target_settings = target_dir / "settings.json"
    if copy_file_if_not_exists(source_settings, target_settings):
        print("  settings.json 생성됨")
    else:
        print("  settings.json 이미 존재함 (스킵)")

    print("\n완료!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
