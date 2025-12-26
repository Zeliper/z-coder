# /orchestrate

멀티 에이전트 오케스트레이션을 시작합니다.

## 사용법
```
/orchestrate {요청}
/orchestrate --task TASK-001
/orchestrate --ref TASK-001 {요청}
```

## 옵션
- `--task TASK-ID`: 기존 태스크 이어서 진행
- `--ref TASK-ID`: 완료된 태스크 참조하여 수정/확장

---

## 핵심 원칙: 직접 수행 금지

**이 커맨드는 모든 작업을 sub-agent에 위임합니다:**

- 직접 검색 금지 (Glob, Grep, Search 사용 금지)
- 직접 코드 작성 금지 (Write, Edit 사용 금지)
- 직접 문서 작성 금지 (.md 파일도 markdown-writer-agent 통해)

**할 수 있는 것:**
- config.json, task 파일 읽기 (Read)
- Task tool로 sub-agent spawn
- AskUserQuestion, EnterPlanMode 사용
- TodoWrite로 진행 상황 관리

---

## 실행 순서

### 1. 초기화 확인
- `.claude/config.json` 존재 확인
- 없으면: "/orchestration-init을 먼저 실행하세요" 안내 후 종료

### 2. 워크플로우 실행
- **orchestration-workflow** Skill 참조
- Phase 1~4 순차 진행

### 3. USER_INPUT_REQUIRED 처리

Sub-agent 결과에서 `USER_INPUT_REQUIRED` 확인:

```
IF 결과에 USER_INPUT_REQUIRED 포함:
  SWITCH type:
    "choice" → AskUserQuestion으로 선택지 제시
    "confirm" → AskUserQuestion으로 예/아니오 질문
    "plan" → EnterPlanMode 진입, 계획 작성 후 사용자 승인

  사용자 답변 수신 후:
    TaskOutput으로 sub-agent resume (agent_id 사용)
    prompt: "사용자 답변: {answer}"

ELSE:
  결과 처리 후 다음 작업 진행
```

---

## Phase 개요

> 상세 워크플로우는 `orchestration-workflow` Skill 참조

### Phase 1: 정보 수집
검색 에이전트 병렬 spawn → todo-list-agent → task 파일 생성

### Phase 2: Step 실행
coder-agent → builder-agent → commit-agent → test-case-agent

### Phase 3: 테스트 대기
pending_test 상태 → 사용자에게 테스트 실행 요청

### Phase 4: 마무리
모든 테스트 PASSED → archive-task.py 실행

---

## 에이전트 매핑

| 작업 유형 | 사용할 에이전트 |
|---------|--------------|
| 코드 탐색/분석 | codebase-search-agent |
| 레퍼런스 검색 | reference-agent |
| 외부 정보 검색 | web-search-agent |
| 코드 작성/수정 | coder-agent |
| 빌드/테스트 | builder-agent |
| 커밋 생성 | commit-agent |
| 복잡한 판단 | decision-agent |

---

## 참고
- 상세 워크플로우: `orchestration-workflow` Skill
- 진행 상황은 task 파일에 기록됨
- 중단 후 재시작 시 --task 옵션 사용
