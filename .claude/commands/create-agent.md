# /create-agent

사용자 설명을 기반으로 새로운 에이전트를 생성하고 오케스트레이션 시스템에 통합합니다.

## 사용법
```
/create-agent {에이전트 설명}
```

## 예시
```
/create-agent 디컴파일된 게임 코드를 분석하여 Harmony 패치 대상을 찾는 에이전트
/create-agent API 문서를 크롤링하고 요약하는 에이전트
/create-agent 코드 리뷰를 수행하고 개선점을 제안하는 에이전트
```

## 실행 프로세스 개요

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: [Opus] 요구사항 분석 및 정보 수집                   │
│ Step 2: [Opus] 코드베이스 탐색 및 패턴 분석                 │
│ Step 3: [Opus] 에이전트 설계 (사용자 확인)                  │
│ Step 4: [Opus] 파일 생성 (agent, skill, hook)              │
│ Step 5: [Sonnet] 시스템 통합 (config.json)                   │
│ Step 6: [Haiku] 결과 보고                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: 요구사항 분석 [Opus]

### 1.1 사용자 입력 분석

사용자가 제공한 설명에서 다음 정보를 추출:

- **목적**: 에이전트가 해결하려는 문제
- **입력**: 에이전트가 받을 데이터
- **출력**: 에이전트가 반환할 결과
- **의존성**: 필요한 외부 도구나 다른 에이전트

### 1.2 통합 유형 결정 (AskUserQuestion)

사용자에게 통합 유형을 질문:

| 유형 | 설명 | 예시 | 호출 시점 |
|------|------|------|----------|
| `search` | Phase 1 검색 에이전트 | codebase-search-agent | 태스크 시작 시 병렬 실행 |
| `step` | Step 실행 에이전트 | coder-agent | Step 단위 순차 실행 |
| `utility` | 유틸리티 에이전트 | commit-agent | 특정 이벤트 시 호출 |
| `standalone` | 독립 에이전트 | - | 직접 호출만 |

### 1.3 추가 옵션 확인

- **모델 선택**: sonnet (기본) | opus | haiku | inherit
- **Hook 필요 여부**: 외부 도구 연동이 필요한 경우
- **프로젝트 특화**: 현재 프로젝트에만 적용 vs 범용

---

## Step 2: 코드베이스 탐색 [Opus]

### 2.1 유사 에이전트 분석

`.claude/agents/` 폴더에서 유사한 역할의 에이전트 탐색:

```bash
# 에이전트 목록 확인
ls .claude/agents/*.md
```

### 2.2 관련 코드 패턴 파악

codebase-search-agent를 활용하여:
- 에이전트가 다룰 코드 영역 탐색
- 기존 패턴 및 컨벤션 확인

### 2.3 필요 도구/스킬 확인

```bash
# 설치된 도구 확인
python .claude/hooks/check-tools.py
```

---

## Step 3: 에이전트 설계 [Opus]

### 3.1 설계 문서 작성

다음 형식으로 설계를 정리하고 사용자에게 확인:

```markdown
## 에이전트 설계: {agent-name}

### 기본 정보
- 이름: {agent-name}
- 설명: {description}
- 모델: {model}
- 통합 유형: {integration_type}

### 역할
{role_description}

### 입력/출력
- 입력: {input_format}
- 출력: {output_format}

### 통합 방식
- 호출 시점: {when_to_call}
- 의존성: {dependencies}

### 생성될 파일
1. .claude/agents/{agent-name}.md
2. .claude/skills/spawn-{agent-name}/SKILL.md
3. (필요시) .claude/hooks/{agent-name}.py
```

### 3.2 사용자 승인

AskUserQuestion으로 설계 확인:
- 수정 필요 사항
- 추가 요구사항

---

## Step 4: 파일 생성 [Opus]

### 4.1 에이전트 파일 생성

**경로**: `.claude/agents/{agent-name}.md`

```markdown
---
name: {agent-name}
description: {description}
model: {model}
---

# {agent-name}

## 역할
{role_description}

## 책임
{responsibilities}

## 입력
{input_format}

## 출력
**최대 500자 이내 요약**으로 반환

## 반환 형식
```markdown
## {agent-name} 결과
- 상태: COMPLETED | PENDING_INPUT
- 결과: {result_summary}
- (선택) USER_INPUT_REQUIRED:
  - type: "choice" | "confirm" | "plan"
  - reason: "{이유}"
  - options: [선택지들]
```

---

<!-- ORCHESTRATION-PROJECT-CONFIG-START -->
<!-- 프로젝트 특화 설정이 /orchestration-init에 의해 이 위치에 추가됩니다 -->
<!-- ORCHESTRATION-PROJECT-CONFIG-END -->
```

### 4.2 Spawn 스킬 생성

**경로**: `.claude/skills/spawn-{agent-name}/SKILL.md`

```markdown
---
name: spawn-{agent-name}
description: {agent-name} 활용 가이드 (project)
---

# {Agent Name} 활용 가이드

## 핵심 원칙
{core_principles}

## 언제 사용하나?
{use_cases}

## Spawn 방법

Task tool 사용:
```
subagent_type: "{agent-name}"
prompt: "{작업 내용}"
```

## 입력 형식
{input_format}

## 결과 처리
{result_handling}

---
<!-- SKILL-PROJECT-CONFIG-START -->
<!-- SKILL-PROJECT-CONFIG-END -->
```

### 4.3 Hook 스크립트 생성 (필요시)

**경로**: `.claude/hooks/{agent-name}.py`

```python
#!/usr/bin/env python
"""
{agent-name}.py - {description}

사용법:
    python {agent-name}.py [options]
"""
import os
import sys
import json
import argparse
from pathlib import Path


def get_project_root() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    return Path(__file__).resolve().parent.parent.parent


def main():
    parser = argparse.ArgumentParser(description="{description}")
    # 인자 정의
    args = parser.parse_args()

    # 구현
    result = {
        "success": True,
        "data": {}
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## Step 5: 시스템 통합 [Sonnet]

### 5.1 config.json 업데이트

`.claude/config.json` 파일이 있으면 업데이트:

```json
{
  "agent_models": {
    "{agent-name}": "{model}"
  },
  "custom_agents": [
    "...(기존)",
    "{agent-name}"
  ]
}
```

### 5.2 통합 안내

새 에이전트가 생성되면 `/orchestrate` 커맨드에서 config.json의 custom_agents를 참조하여 자동으로 활용합니다.

**통합 유형별 동작:**
- **search 유형**: Phase 1에서 병렬 spawn됨
- **step 유형**: Step 실행 시 필요에 따라 호출
- **utility 유형**: 특정 이벤트(빌드 성공 등) 시 호출
- **standalone 유형**: 직접 Task tool로만 호출

---

## Step 6: 결과 보고 [Haiku]

### 6.1 생성 결과 요약

```markdown
## /create-agent 완료

### 생성된 에이전트
- **이름**: {agent-name}
- **모델**: {model}
- **통합 유형**: {integration_type}
- **설명**: {description}

### 생성된 파일
| 파일 | 경로 |
|------|------|
| 에이전트 | .claude/agents/{agent-name}.md |
| Spawn 스킬 | .claude/skills/spawn-{agent-name}/SKILL.md |
| Hook (옵션) | .claude/hooks/{agent-name}.py |

### 업데이트된 파일
- .claude/config.json (있는 경우)

### 사용 방법

**직접 호출:**
```
Task tool:
  subagent_type: "{agent-name}"
  prompt: "작업 내용"
```

**워크플로우 내:**
{integration_type}에 따라 main-agent가 자동 호출
```

---

## 주의사항

1. **YAML Frontmatter 필수**: 에이전트 파일은 반드시 `name`, `description`, `model` 필드 포함
2. **프로젝트 마커**: `<!-- ORCHESTRATION-PROJECT-CONFIG-START/END -->` 마커 필수
3. **크로스 플랫폼**: Hook 스크립트는 Windows/Linux 호환되게 작성
4. **명명 규칙**: 에이전트 이름은 `kebab-case` 사용 (예: `code-review-agent`)

---

## 관련 명령어

- `/orchestration-init`: 오케스트레이션 시스템 초기화
- `/orchestrate`: 멀티 에이전트 워크플로우 실행
- `/orchestration-update`: 시스템 업데이트
