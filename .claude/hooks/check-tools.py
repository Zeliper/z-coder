#!/usr/bin/env python3
"""
check-tools.py - 도구 설치 여부 확인 Hook

SessionStart 또는 수동 실행 시 시스템에 설치된 도구들을 확인합니다.
결과는 JSON 형태로 출력되며, Claude Code Hook 시스템과 호환됩니다.

사용법:
    python check-tools.py [--tools tool1,tool2,...]
    echo '{"tools": ["python", "npm"]}' | python check-tools.py

Hook 이벤트:
    SessionStart - 세션 시작 시 자동 실행

출력:
    - 설치된 도구 목록
    - 각 도구의 경로 및 버전
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Optional


# 도구별 버전 확인 명령어
TOOL_COMMANDS = {
    # 런타임/언어
    "python": {"check": "python --version", "version_arg": "--version"},
    "python3": {"check": "python3 --version", "version_arg": "--version"},
    "node": {"check": "node --version", "version_arg": "--version"},
    "npm": {"check": "npm --version", "version_arg": "--version"},
    "go": {"check": "go version", "version_arg": "version"},
    "cargo": {"check": "cargo --version", "version_arg": "--version"},
    "rustc": {"check": "rustc --version", "version_arg": "--version"},
    "dotnet": {"check": "dotnet --version", "version_arg": "--version"},
    "java": {"check": "java --version", "version_arg": "--version"},

    # 버전 관리
    "git": {"check": "git --version", "version_arg": "--version"},

    # 디컴파일러
    "ilspycmd": {"check": "ilspycmd --version", "version_arg": "--version"},
    "jadx": {"check": "jadx --version", "version_arg": "--version"},

    # 빌드 도구
    "make": {"check": "make --version", "version_arg": "--version"},
    "cmake": {"check": "cmake --version", "version_arg": "--version"},
    "gradle": {"check": "gradle --version", "version_arg": "--version"},
    "maven": {"check": "mvn --version", "version_arg": "--version"},

    # 패키지 관리자
    "pip": {"check": "pip --version", "version_arg": "--version"},
    "pip3": {"check": "pip3 --version", "version_arg": "--version"},
    "yarn": {"check": "yarn --version", "version_arg": "--version"},
    "pnpm": {"check": "pnpm --version", "version_arg": "--version"},
    "composer": {"check": "composer --version", "version_arg": "--version"},

    # 코드 포매터
    "black": {"check": "black --version", "version_arg": "--version"},
    "prettier": {"check": "prettier --version", "version_arg": "--version"},
    "eslint": {"check": "eslint --version", "version_arg": "--version"},
    "gofmt": {"check": "gofmt -h", "version_arg": None},
    "rustfmt": {"check": "rustfmt --version", "version_arg": "--version"},

    # 테스트 도구
    "pytest": {"check": "pytest --version", "version_arg": "--version"},
    "jest": {"check": "jest --version", "version_arg": "--version"},

    # 컨테이너
    "docker": {"check": "docker --version", "version_arg": "--version"},
    "docker-compose": {"check": "docker-compose --version", "version_arg": "--version"},
    "kubectl": {"check": "kubectl version --client", "version_arg": "version --client"},
}


def check_command(cmd: str, timeout: int = 5) -> dict:
    """명령어 실행 가능 여부 확인"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            timeout=timeout,
            text=True,
        )
        return {
            "available": result.returncode == 0,
            "version": result.stdout.strip() if result.returncode == 0 else None,
            "stderr": result.stderr.strip() if result.returncode != 0 else None,
        }
    except subprocess.TimeoutExpired:
        return {"available": False, "error": "timeout"}
    except Exception as e:
        return {"available": False, "error": str(e)}


def get_tool_path(tool_name: str) -> Optional[str]:
    """도구의 실행 경로 반환"""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                f"where {tool_name}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
        else:
            result = subprocess.run(
                f"which {tool_name}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
    except Exception:
        pass
    return None


def check_tool(tool_name: str) -> dict:
    """단일 도구 확인"""
    tool_info = TOOL_COMMANDS.get(tool_name)

    if tool_info:
        cmd = tool_info["check"]
    else:
        # 알 수 없는 도구는 --version으로 확인
        cmd = f"{tool_name} --version"

    result = check_command(cmd)
    result["name"] = tool_name
    result["path"] = get_tool_path(tool_name) if result.get("available") else None

    return result


def detect_project_tools(project_root: Path) -> list[str]:
    """프로젝트 타입에 따라 확인할 도구 목록 반환"""
    tools = ["git"]  # 기본

    # Python
    if (project_root / "requirements.txt").exists() or (project_root / "pyproject.toml").exists():
        tools.extend(["python", "pip", "pytest", "black"])

    # Node.js
    if (project_root / "package.json").exists():
        tools.extend(["node", "npm", "prettier", "eslint"])

    # .NET
    if list(project_root.glob("*.csproj")) or list(project_root.glob("*.sln")):
        tools.extend(["dotnet", "ilspycmd"])

    # Go
    if (project_root / "go.mod").exists():
        tools.extend(["go", "gofmt"])

    # Rust
    if (project_root / "Cargo.toml").exists():
        tools.extend(["cargo", "rustc", "rustfmt"])

    # Java
    if (project_root / "pom.xml").exists():
        tools.extend(["java", "maven"])
    if (project_root / "build.gradle").exists():
        tools.extend(["java", "gradle"])

    # Docker
    if (project_root / "Dockerfile").exists() or (project_root / "docker-compose.yml").exists():
        tools.extend(["docker", "docker-compose"])

    return list(set(tools))


def main():
    # Hook 입력 데이터 받기 (stdin에서)
    input_data = {}
    if not sys.stdin.isatty():
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            pass

    # 프로젝트 루트 결정
    project_root = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()

    # 확인할 도구 목록 결정
    tools_to_check = input_data.get("tools", [])

    if not tools_to_check:
        # 프로젝트 타입에 따라 자동 감지
        tools_to_check = detect_project_tools(project_root)

    # 도구 확인
    results = {}
    available_tools = []
    missing_tools = []

    for tool in tools_to_check:
        info = check_tool(tool)
        results[tool] = info
        if info.get("available"):
            available_tools.append(tool)
        else:
            missing_tools.append(tool)

    # 결과 구성
    output = {
        "project_root": str(project_root),
        "tools": results,
        "available": available_tools,
        "missing": missing_tools,
        "summary": f"설치됨: {len(available_tools)}, 미설치: {len(missing_tools)}",
    }

    # Hook 출력 형식
    context = f"도구 확인 결과: {output['summary']}\n"
    context += f"설치된 도구: {', '.join(available_tools)}\n"
    if missing_tools:
        context += f"미설치 도구: {', '.join(missing_tools)}\n"

    hook_output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        },
        "toolCheckResults": output,
    }

    print(json.dumps(hook_output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
