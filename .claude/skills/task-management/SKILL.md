---
name: task-management
description: 태스크 파일 CRUD, 상태 업데이트, 아카이빙 가이드
allowed-tools: Read, Edit, Glob, Bash
---

# Task Management 가이드

태스크 파일을 관리하고 상태를 추적하는 방법입니다.

## 태스크 파일 구조

### 위치
- 활성 태스크: `./tasks/TASK-{ID}.md`
- 아카이브: `./tasks/archive/TASK-{ID}.md`

### 기본 형식

```markdown
# TASK-{ID}: {제목}

## 상태
- 현재: {status}
- 생성일: {created_at}
- 마지막 업데이트: {updated_at}

## 요청 내용
{사용자 요청 원문}

## Steps
### Step 1: {제목} [S/M/L]
- 설명: {상세 설명}
- 상태: pending | in_progress | completed
- 관련 파일: {파일 목록}

## 에이전트 결과
### codebase_search_result
{결과}

## 테스트 결과
### [TASK-ID-T01] {테스트명}
- 결과: PASSED | FAILED
- 일시: {timestamp}

## User Interactions
{사용자 입력 기록}
```

## 태스크 상태

| 상태 | 설명 |
|------|------|
| pending | 생성됨, 작업 미시작 |
| in_progress | 작업 진행 중 |
| completed | 모든 Step 완료 |
| pending_test | 테스트 대기 중 |
| archived | 아카이브됨 |

## 조회 작업

### 목록 조회

```bash
# 모든 활성 태스크
ls ./tasks/TASK-*.md

# 상태별 필터링 (Grep 사용)
grep -l "현재: pending" ./tasks/TASK-*.md
grep -l "현재: in_progress" ./tasks/TASK-*.md
grep -l "현재: pending_test" ./tasks/TASK-*.md
```

### ID별 조회

```
Read: ./tasks/TASK-001.md
```

## 상태 업데이트

### Edit 도구 사용

```
old_string: "- 현재: in_progress"
new_string: "- 현재: completed"
```

### 타임스탬프 포함

```markdown
- 현재: completed
- 마지막 업데이트: 2024-01-15T10:30:00
```

## 테스트 결과 기록

### 새 테스트 결과 추가

Task 파일의 `## 테스트 결과` 섹션에 추가:

```markdown
## 테스트 결과

### [TASK-001-T01] 사용자 인증 테스트
- 결과: PASSED
- 일시: 2024-01-15T14:30:00
- 테스터: {user}
- 비고: 모든 케이스 통과

### [TASK-001-T02] 권한 검증 테스트
- 결과: FAILED
- 일시: 2024-01-15T14:45:00
- 에러: 관리자 권한 검증 실패
- 로그: ./logs/test-error-001.txt
```

### 테스트 상태 집계

```markdown
## 테스트 요약
- 총 테스트: 5개
- 통과: 4개
- 실패: 1개
- 마지막 실행: 2024-01-15T14:45:00
```

## 아카이빙

### 아카이브 조건

모든 조건 충족 시에만 아카이브:
1. 모든 Step: completed
2. 모든 테스트: PASSED (또는 테스트 없음)

### 아카이브 실행

```bash
# archive-task.py hook 사용
python3 .claude/hooks/archive-task.py TASK-001

# 미리보기
python3 .claude/hooks/archive-task.py TASK-001 --dry-run
```

### 아카이브 동작

1. `./tasks/TASK-001.md` → `./tasks/archive/TASK-001.md`
2. `./Test/[TASK-001-*].md` → `./Test/Archive/`
3. 상태를 `archived`로 변경

## 내용 추가

### 에이전트 결과 추가

```markdown
## 에이전트 결과

### coder_agent_result (Step 1)
- 상태: COMPLETED
- 수정 파일: src/auth/login.ts, src/middleware/auth.ts
- 변경 내용: JWT 인증 구현
- 타임스탬프: 2024-01-15T10:30:00
```

### 사용자 코멘트 추가

```markdown
## User Interactions

### [2024-01-15 10:30] 입력 요청 #1
- 요청 출처: coder-agent (Step 2)
- 유형: choice
- 질문: "인증 방식 선택"
- 선택지: ["JWT", "Session"]
- **사용자 응답**: JWT
```

## 에러 처리

### 파일 없음

```
Task 파일을 찾을 수 없습니다: TASK-999
→ 올바른 TASK-ID 확인 필요
```

### 아카이브 실패

```
테스트가 완료되지 않았습니다.
→ pending_test 상태 유지
→ /test-report로 테스트 결과 보고 필요
```

---

<!-- SKILL-PROJECT-CONFIG-START -->
<!-- 프로젝트 특화 설정이 /orchestration-init에 의해 이 위치에 추가됩니다 -->
<!-- SKILL-PROJECT-CONFIG-END -->
