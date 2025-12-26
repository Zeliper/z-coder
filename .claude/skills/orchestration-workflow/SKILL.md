---
name: orchestration-workflow
description: 작업 요청 시 전체 워크플로우를 안내. 어떤 에이전트를 언제 사용할지 결정하는 데 활용
allowed-tools: Task, Read, Glob
---

# 오케스트레이션 워크플로우

Main-agent가 작업을 효율적으로 처리하기 위한 워크플로우 가이드입니다.

## 모드 선택 (작업 시작 전)

### Plan Mode (계획 검토 필요 시)

작업 시작 전에 계획을 검토하고 싶다면:
1. 정보 수집 완료 후 계획 작성
2. 사용자에게 계획 제시 및 승인 요청
3. 승인 후 Execute Mode로 전환

**Plan Mode 진입 조건:**
- 사용자가 명시적으로 "계획 먼저 보여줘" 요청
- 복잡한 작업 (다수 파일 수정, 아키텍처 변경)
- 파괴적 변경 (삭제, 대규모 리팩토링)
- 다중 구현 방식 존재

### Execute Mode (기본)

계획 검토 없이 바로 실행:
- 단순한 작업
- 사용자가 신뢰 표시한 경우
- 명확한 요구사항

## 에이전트 선택 기준

### 정보 수집이 필요한 경우

**→ spawn-search-agents Skill 참조**

| 상황 | 에이전트 |
|------|----------|
| 프로젝트 코드 탐색 | codebase-search-agent |
| 레퍼런스/예제 탐색 | reference-agent |
| 외부 정보 검색 | web-search-agent |

### 코드 작성이 필요한 경우

**→ spawn-coder Skill 참조**

- **직접 코드 작성 금지**
- 반드시 coder-agent에 위임

### 빌드/테스트가 필요한 경우

**→ spawn-builder Skill 참조**

- 반드시 builder-agent에 위임
- 코드 변경 후 항상 빌드 확인

## 작업 흐름

### Plan Mode 흐름

```
1. 사용자 요청 분석
   ↓
2. 정보 수집 (검색 에이전트들 병렬 spawn)
   ├─ codebase-search-agent
   ├─ reference-agent
   └─ web-search-agent (필요시)
   ↓
3. 작업 분해 (todo-list-agent)
   ↓
4. [PLAN] 계획 제시 및 사용자 승인 요청
   ↓
5. 승인 후 → Execute Mode로 전환
```

### Execute Mode 흐름

```
1. Step별 코딩 (coder-agent)
   ↓
2. Step별 빌드 (builder-agent)
   ↓
3. 결과 확인
   ├─ 성공 → 다음 Step
   └─ 실패 → 재시도 (최대 3회)
   ↓
4. 완료 보고
```

## 병렬 Spawn 전략

### 정보 수집 단계

다음 에이전트들을 **동시에** 백그라운드 spawn (단일 메시지에 여러 Task tool 호출):

**반드시 Task tool을 사용합니다. Bash 명령어로 실행하지 마세요.**

```
Task tool #1:
  subagent_type: "codebase-search-agent"
  run_in_background: true
  prompt: "..."

Task tool #2:
  subagent_type: "reference-agent"
  run_in_background: true
  prompt: "..."

Task tool #3:
  subagent_type: "web-search-agent"
  run_in_background: true
  prompt: "..."
```

### Step 실행 단계

coder-agent와 builder-agent는 **순차 실행**:

```
coder-agent 완료 → builder-agent 실행
```

## USER_INPUT_REQUIRED 처리

Sub-agent 결과에 `USER_INPUT_REQUIRED` 플래그 감지 시:

| input_type | 행동 |
|------------|------|
| choice | AskUserQuestion (선택지 제시) |
| confirm | AskUserQuestion (예/아니오) |
| plan | EnterPlanMode (상세 계획 필요) |

## 핵심 원칙

1. **직접 코드 작성 금지** - coder-agent를 통해서만
2. **검색 먼저** - 코딩 전에 충분한 정보 수집
3. **Step 단위 진행** - 한 번에 모든 것을 하지 않음
4. **빌드 확인 필수** - 코드 변경 후 항상 빌드

---
<!-- SKILL-PROJECT-CONFIG-START -->
<!-- 프로젝트 특화 설정이 /orchestration-init에 의해 이 위치에 추가됩니다 -->
<!-- SKILL-PROJECT-CONFIG-END -->
