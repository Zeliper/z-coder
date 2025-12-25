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

## 실행 지침

이 명령어가 실행되면 `main-agent.md`의 지시를 따라 오케스트레이션을 수행합니다.

### 1. 초기화 확인
`.claude/config.json` 존재 확인:
- 없으면: "/orchestration-init을 먼저 실행하세요" 안내

### 2. main-agent 활성화
`.claude/agents/main-agent.md`의 지시에 따라 작업 수행

### 3. 워크플로우

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
