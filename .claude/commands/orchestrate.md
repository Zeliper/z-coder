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

## 중요: main-agent Spawn 필수

**이 커맨드는 반드시 Task tool로 main-agent를 spawn해야 합니다.**

현재 세션에서 직접 코드를 수정하지 마세요. 대신:

```
Task tool 호출:
  subagent_type: "main-agent"
  prompt: "{사용자 요청 전체}"
  run_in_background: false (결과를 기다림)
```

### 실행 순서

1. **초기화 확인**
   - `.claude/config.json` 존재 확인
   - 없으면: "/orchestration-init을 먼저 실행하세요" 안내 후 종료

2. **main-agent Spawn**
   - Task tool로 main-agent spawn
   - 사용자 요청 전체를 prompt로 전달
   - 옵션(--task, --ref)도 함께 전달

3. **결과 처리 및 사용자 입력 중계**

   main-agent 결과에서 `USER_INPUT_REQUIRED` 확인:

   ```
   IF 결과에 USER_INPUT_REQUIRED 포함:
     SWITCH type:
       "choice" → AskUserQuestion으로 선택지 제시
       "confirm" → AskUserQuestion으로 예/아니오 질문
       "plan" → EnterPlanMode 진입, 계획 작성 후 사용자 승인

     사용자 답변 수신 후:
       TaskOutput으로 main-agent resume (agent_id 사용)
       prompt: "사용자 답변: {answer}"

   ELSE:
     결과를 사용자에게 전달
   ```

4. **Plan Mode 처리**

   main-agent가 `type: "plan"` 반환 시:
   - 현재 세션에서 EnterPlanMode 호출
   - main-agent가 전달한 계획 내용을 plan 파일에 작성
   - 사용자 승인 후 ExitPlanMode
   - main-agent resume하여 실행 계속

---

## main-agent 워크플로우 (참고용)

#### Phase 1: 초기화 및 정보 수집
```
1. config.json 읽기
2. tasks/ 폴더에서 진행중인 task 파일 확인
3. 새 태스크인 경우 백그라운드로 동시에 spawn:
   - codebase-search-agent
   - web-search-agent (필요시)
   - {custom_agents from config.json}
4. 결과 수신 → todo-list-agent spawn → task 파일 생성
```

#### Phase 2: Step 실행 루프
```
FOR each Step in task.steps:
  IF step.status == 'completed': CONTINUE

  1. coder-agent 백그라운드 spawn → Step 작업
  2. builder-agent 백그라운드 spawn → 빌드/테스트

  IF 빌드 실패:
    - LESSONS_LEARNED.md 업데이트
    - 재시도 (최대 3회)
    - 3회 실패 시 사용자 보고

  IF 빌드 성공:
    - commit-agent spawn → [TASK-ID] 형식 커밋
    - test-case-agent spawn → 테스트 케이스 생성
    - step.status = 'completed'
    - 결과 기록

  Step 완료 보고
```

#### Phase 3: 테스트 대기
```
모든 Step 완료 시:
1. Task 상태 → pending_test
2. 생성된 테스트 케이스 안내
3. 사용자에게 테스트 실행 요청:
   "/test-report TASK-001-T01 {결과}"
```

#### Phase 4: 마무리 (테스트 통과 후)
```
/test-report 성공 수신 시:
1. task-manager-agent → 테스트 결과 기록
2. 모든 테스트 PASSED 확인
3. archive-task.py hook 실행:
   - task 파일 → tasks/archive/
   - 테스트 파일 → Test/Archive/
4. 완료 보고
```

## 참고
- 모든 에이전트 spawn은 main-agent만 수행
- 진행 상황은 task 파일에 기록됨
- 중단 후 재시작 시 --task 옵션 사용
