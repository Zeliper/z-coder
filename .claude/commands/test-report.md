# /test-report

테스트 결과를 보고하고 처리하는 커맨드입니다.

## 사용법

```
/test-report {TASK-ID-TXX} {결과}
/test-report {TASK-ID-TXX} {파일경로}
```

## 예시

```bash
# 성공 보고
/test-report TASK-001-T01 성공
/test-report TASK-001-T01 PASSED

# 실패 보고
/test-report TASK-001-T01 실패: 로그인 시 500 에러 발생
/test-report TASK-001-T01 FAILED: Authentication token expired

# 파일로 보고
/test-report TASK-001-T01 ./error-log.txt
/test-report TASK-001-T01 ./test-results.json
```

## 파라미터

| 파라미터 | 설명 | 필수 |
|----------|------|------|
| TASK-ID-TXX | 테스트 케이스 ID (예: TASK-001-T01) | ✓ |
| 결과 | 성공/PASSED 또는 실패 메시지/파일경로 | ✓ |

---

## 실행 흐름

### 1. 테스트 ID 파싱

```
TASK-001-T01 → TASK-001 (Task ID) + T01 (Test 번호)
```

### 2. 파일 확인

1. Task 파일 확인: `./tasks/TASK-001.md`
2. 테스트 파일 확인: `./Test/[TASK-001-T01] *.md`

### 3. 결과 분석

#### 성공 키워드
- `성공`, `PASSED`, `pass`, `통과`, `OK`

#### 실패 키워드
- `실패`, `FAILED`, `fail`, `에러`, `error`

#### 파일 경로
- `.txt`, `.log`, `.json` 등 파일 확장자 감지
- 파일 내용 읽어서 분석

### 4. 결과별 처리

```
테스트 결과 분석
    ↓
[성공] → task-manager-agent
         → 테스트 결과 기록
         → 모든 테스트 PASSED 확인
         → 아카이브 (archive-task.py)
    ↓
[실패] → coder-agent 직접 spawn
         → 에러 분석 및 수정
         → builder-agent로 재빌드
         → commit-agent로 재커밋
```

---

## 성공 시 워크플로우

### 1. 결과 기록

task-manager-agent 호출:
```
액션: record_test
대상: TASK-001
테스트 결과:
  - 테스트 ID: TASK-001-T01
  - 결과: PASSED
  - 일시: {현재시간}
  - 비고: 사용자 보고
```

### 2. 전체 테스트 확인

Task 파일의 모든 테스트 결과 확인:
- 모두 PASSED → 아카이브 진행
- 일부 미완료 → 대기

### 3. 아카이브

모든 테스트 PASSED 시:
```bash
python3 .claude/hooks/archive-task.py TASK-001
```

결과:
- `./tasks/TASK-001.md` → `./tasks/archive/`
- `./Test/[TASK-001-*].md` → `./Test/Archive/`

---

## 실패 시 워크플로우

### 1. 에러 분석

실패 메시지 또는 로그 파일 분석:
- 에러 유형 파악
- 관련 코드 위치 추정
- 수정 방향 도출

### 2. coder-agent 수정 실행

coder-agent spawn:
- 에러 원인 분석
- 코드 수정
- 관련 파일 업데이트

### 3. 재빌드 및 재커밋

```
coder-agent → builder-agent → commit-agent
```

### 4. 테스트 케이스 업데이트

필요 시 test-case-agent 호출:
- 테스트 조건 수정
- 예상 결과 업데이트

### 5. 재테스트 안내

사용자에게 재테스트 요청:
```
수정이 완료되었습니다.
테스트를 다시 실행하고 결과를 보고해주세요:
/test-report TASK-001-T01 {결과}
```

---

## 별도 세션 지원

이 커맨드는 별도 세션에서도 실행 가능합니다:

### 세션 독립적 동작

1. TASK-ID-TXX로 Task 파일 조회
2. 테스트 파일 조회
3. 결과 기록 및 처리

### 컨텍스트 없이 실행

```bash
# 새 세션에서도 바로 실행 가능
/test-report TASK-001-T01 성공
```

Task 파일과 테스트 파일이 존재하면 정상 처리됨.

---

## 에러 처리

### Task 파일 없음

```
에러: Task를 찾을 수 없습니다: TASK-001
→ ./tasks/ 폴더에서 Task 파일 확인 필요
```

### 테스트 파일 없음

```
에러: 테스트 케이스를 찾을 수 없습니다: TASK-001-T01
→ ./Test/ 폴더에서 테스트 파일 확인 필요
```

### 잘못된 ID 형식

```
에러: 잘못된 테스트 ID 형식: ABC-123
→ 형식: TASK-NNN-TXX (예: TASK-001-T01)
```

---

## 출력

### 성공 시

```markdown
## 테스트 결과 처리 완료

- 테스트: TASK-001-T01
- 결과: PASSED
- 처리:
  - Task 파일에 결과 기록 완료
  - 모든 테스트 통과 확인
  - Task 아카이브 완료

아카이브된 파일:
- ./tasks/archive/TASK-001.md
- ./Test/Archive/[TASK-001-T01] User Auth Test.md
```

### 실패 시

```markdown
## 테스트 실패 처리 중

- 테스트: TASK-001-T01
- 결과: FAILED
- 에러: 로그인 시 500 에러 발생

수정 작업을 시작합니다...

coder-agent가 다음을 수정합니다:
- src/auth/login.ts
- src/middleware/auth.ts

수정 완료 후 다시 테스트해주세요:
/test-report TASK-001-T01 {결과}
```
