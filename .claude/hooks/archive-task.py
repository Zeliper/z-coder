#!/usr/bin/env python3
"""
archive-task.py - Task 및 관련 테스트 파일 아카이브 처리

사용법:
    python3 archive-task.py TASK-001
    python3 archive-task.py TASK-001 --dry-run

동작:
    1. ./tasks/TASK-{ID}.md → ./tasks/archive/TASK-{ID}.md
    2. ./Test/[TASK-{ID}-*].md → ./Test/Archive/
"""

import os
import sys
import shutil
import glob
import json
import argparse
from pathlib import Path
from datetime import datetime


def get_project_root():
    """프로젝트 루트 디렉토리 반환"""
    if 'CLAUDE_PROJECT_DIR' in os.environ:
        return Path(os.environ['CLAUDE_PROJECT_DIR'])
    # 스크립트 위치 기준으로 찾기
    script_dir = Path(__file__).parent
    return script_dir.parent.parent  # .claude/hooks -> .claude -> project_root


def find_task_file(project_root: Path, task_id: str) -> Path | None:
    """Task 파일 찾기"""
    task_file = project_root / 'tasks' / f'{task_id}.md'
    if task_file.exists():
        return task_file
    return None


def find_test_files(project_root: Path, task_id: str) -> list[Path]:
    """해당 Task의 테스트 파일들 찾기"""
    test_dir = project_root / 'Test'
    if not test_dir.exists():
        return []

    # [TASK-ID-*] 패턴으로 시작하는 파일 찾기
    pattern = f'[{task_id}-*]*'
    test_files = list(test_dir.glob(pattern))

    # 추가 패턴: TASK-ID-T01.md 형식
    pattern2 = f'{task_id}-*.md'
    test_files.extend(test_dir.glob(pattern2))

    # 중복 제거
    return list(set(test_files))


def ensure_archive_dirs(project_root: Path):
    """아카이브 디렉토리 생성"""
    (project_root / 'tasks' / 'archive').mkdir(parents=True, exist_ok=True)
    (project_root / 'Test' / 'Archive').mkdir(parents=True, exist_ok=True)


def archive_file(src: Path, dest_dir: Path, dry_run: bool = False) -> dict:
    """파일을 아카이브 디렉토리로 이동"""
    dest = dest_dir / src.name
    result = {
        'source': str(src),
        'destination': str(dest),
        'success': False,
        'error': None
    }

    if dry_run:
        result['success'] = True
        result['dry_run'] = True
        return result

    try:
        shutil.move(str(src), str(dest))
        result['success'] = True
    except Exception as e:
        result['error'] = str(e)

    return result


def archive_task(task_id: str, dry_run: bool = False) -> dict:
    """Task 및 관련 테스트 파일 아카이브"""
    project_root = get_project_root()

    result = {
        'task_id': task_id,
        'timestamp': datetime.now().isoformat(),
        'dry_run': dry_run,
        'task_file': None,
        'test_files': [],
        'success': False,
        'error': None
    }

    # 아카이브 디렉토리 확인
    ensure_archive_dirs(project_root)

    # Task 파일 찾기
    task_file = find_task_file(project_root, task_id)
    if not task_file:
        result['error'] = f'Task file not found: {task_id}.md'
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result

    # 테스트 파일 찾기
    test_files = find_test_files(project_root, task_id)

    # Task 파일 아카이브
    task_archive_dir = project_root / 'tasks' / 'archive'
    task_result = archive_file(task_file, task_archive_dir, dry_run)
    result['task_file'] = task_result

    # 테스트 파일들 아카이브
    test_archive_dir = project_root / 'Test' / 'Archive'
    for test_file in test_files:
        test_result = archive_file(test_file, test_archive_dir, dry_run)
        result['test_files'].append(test_result)

    # 전체 성공 여부
    all_success = task_result['success']
    if test_files:
        all_success = all_success and all(t['success'] for t in result['test_files'])

    result['success'] = all_success

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Task 및 관련 테스트 파일 아카이브'
    )
    parser.add_argument(
        'task_id',
        help='아카이브할 Task ID (예: TASK-001)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 파일 이동 없이 미리보기'
    )

    args = parser.parse_args()

    # Task ID 형식 정규화
    task_id = args.task_id.upper()
    if not task_id.startswith('TASK-'):
        task_id = f'TASK-{task_id}'

    result = archive_task(task_id, args.dry_run)

    # JSON 출력
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 종료 코드
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
