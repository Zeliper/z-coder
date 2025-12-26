# /create-testcase

테스트 케이스를 생성하는 커맨드입니다. Task 기반 또는 독립 테스트 케이스를 생성할 수 있습니다.

## 사용법

```
/create-testcase --task TASK-ID [--step N]
/create-testcase --standalone {설명}
/create-testcase --files {파일경로들} {설명}
```

## 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--task TASK-ID` | 특정 Task에 대한 테스트 케이스 생성 | `--task TASK-001` |
| `--step N` | 특정 Step만 대상 (--task와 함께) | `--step 2` |
| `--standalone` | 독립 테스트 케이스 생성 | `--standalone API 응답 검증` |
| `--files` | 특정 파일들 기반 테스트 케이스 | `--files src/auth/*.ts 인증 테스트` |

## 예시

```bash
# Task 전체에 대한 테스트 케이스 생성
/create-testcase --task TASK-001

# Task의 특정 Step에 대한 테스트 케이스 생성
/create-testcase --task TASK-001 --step 2

# 독립 테스트 케이스 생성
/create-testcase --standalone 사용자 로그인 API 응답 형식 검증

# 특정 파일들 기반 테스트 케이스
/create-testcase --files src/utils/validator.ts 입력 검증 유틸리티 테스트
```

---

## 실행 흐름

### Mode 1: Task 기반 (`--task`)

```
┌─────────────────────────────────────────────────┐
│ 1. Task 파일 읽기 (./tasks/TASK-ID.md)          │
│ 2. 완료된 Step 정보 추출                         │
│ 3. 변경된 파일 목록 수집                         │
│ 4. test-case-agent spawn                        │
│ 5. 테스트 케이스 파일 생성                       │
│ 6. Task 파일에 테스트 케이스 링크 추가           │
└─────────────────────────────────────────────────┘
```

### Mode 2: 독립 (`--standalone`)

```
┌─────────────────────────────────────────────────┐
│ 1. 설명 분석 및 관련 코드 탐색                   │
│ 2. 독립 테스트 ID 생성 (STANDALONE-NNN-T01)     │
│ 3. test-case-agent spawn                        │
│ 4. 테스트 케이스 파일 생성                       │
└─────────────────────────────────────────────────┘
```

### Mode 3: 파일 기반 (`--files`)

```
┌─────────────────────────────────────────────────┐
│ 1. 지정된 파일 읽기 및 분석                      │
│ 2. 독립 테스트 ID 생성                           │
│ 3. test-case-agent spawn                        │
│ 4. 테스트 케이스 파일 생성                       │
└─────────────────────────────────────────────────┘
```

---

## test-case-agent 활용

이 명령어는 `test-case-agent`를 spawn하여 테스트 케이스를 생성합니다.

### 에이전트 호출

```
"백그라운드에서 test-case-agent 역할로 다음 작업을 수행해줘:

{Mode에 따른 입력 정보}

.claude/agents/test-case-agent.md 의 지시를 따르고,
작업 완료 후 결과만 요약해서 보고해줘."
```

### 전달 정보

#### Task 기반 모드
| 항목 | 설명 |
|------|------|
| task_id | Task 식별자 |
| step_number | 대상 Step 번호 (없으면 전체) |
| modified_files | 변경된 파일 목록 |
| step_description | Step 작업 내용 |
| coder_result | 구현 결과 요약 |

#### 독립/파일 기반 모드
| 항목 | 설명 |
|------|------|
| test_id | STANDALONE-NNN-T01 형식 |
| description | 사용자 제공 설명 |
| target_files | 대상 파일 목록 |
| code_analysis | 코드 분석 결과 |

---

## 테스트 ID 규칙

### Task 기반
- 형식: `TASK-{NNN}-T{XX}`
- 예시: `TASK-001-T01`, `TASK-001-T02`

### 독립 테스트
- 형식: `STANDALONE-{NNN}-T{XX}`
- 예시: `STANDALONE-001-T01`
- 순번: `./Test/` 폴더의 기존 STANDALONE 번호 + 1

---

## 템플릿 활용

### 사용 스킬
- `markdown-templates`: test-case-template.md 활용
- `spawn-markdown-writer`: 테스트 항목 상세 생성 위임

### 워크플로우

```
1. .claude/templates/test-case-template.md 읽기
2. 기본 변수 치환 (TEST_ID, TASK_ID 등)
3. 정형 항목: 직접 작성
4. 복잡한 설명 필요 시: markdown-writer-agent spawn
5. {{TEST_ITEMS}} 위치에 내용 삽입
6. 최종 파일 Write
```

---

## 출력 파일

### 파일 위치
- 활성: `./Test/[TEST-ID] Description.md`
- 예시: `./Test/[TASK-001-T01] User Authentication Test.md`
- 예시: `./Test/[STANDALONE-001-T01] API Response Validation.md`

### 파일 구조

```markdown
# [TEST-ID] 테스트 제목

## 관련 정보
- Task: {TASK-ID 또는 N/A}
- Step: {Step 번호 또는 N/A}
- 대상: {대상 파일 또는 기능}

## 테스트 목적
{테스트 목적 설명}

## 테스트 환경
- 필요 설정: {설정 항목}
- 선행 조건: {선행 조건}

## 테스트 항목

### TC-01: {테스트 케이스 제목}
- [ ] **입력**: {입력값}
- [ ] **예상 결과**: {예상 결과}
- [ ] **확인 방법**: {확인 방법}

### TC-02: ...

## 관련 파일
- {파일 목록}

## 참고사항
- {참고사항}

---

## 테스트 결과

| 항목 | 결과 | 비고 |
|------|------|------|
| TC-01 | | |
| TC-02 | | |

**최종 결과**:
**테스트 일시**:
**테스터**:
```

---

## 결과 보고

### 성공 시

```markdown
## 테스트 케이스 생성 완료

- 모드: {Task 기반 | 독립 | 파일 기반}
- 생성된 테스트 케이스:
  - [TEST-ID-1] 테스트 제목 1
  - [TEST-ID-2] 테스트 제목 2
- 테스트 파일:
  - ./Test/[TEST-ID-1] Description.md
  - ./Test/[TEST-ID-2] Description.md
- 총 테스트 항목: {N}개

다음 단계:
1. 테스트 케이스 확인 및 필요시 수정
2. 테스트 실행
3. 결과 보고: /test-report {TEST-ID} {결과}
```

### 실패 시

```markdown
## 테스트 케이스 생성 실패

- 에러: {에러 메시지}
- 원인: {원인 분석}

권장 조치:
- {조치 사항}
```

---

## 에러 처리

### Task 파일 없음
```
에러: Task를 찾을 수 없습니다: TASK-001
→ ./tasks/ 폴더에서 Task 파일 확인 필요
```

### 완료된 Step 없음
```
에러: 완료된 Step이 없습니다: TASK-001
→ Step 완료 후 테스트 케이스 생성 가능
```

### 대상 파일 없음
```
에러: 지정된 파일을 찾을 수 없습니다
→ 파일 경로 확인 필요
```

---

## 세션 독립 지원

이 명령어는 별도 세션에서도 실행 가능합니다:

```bash
# 새 세션에서 바로 실행
/create-testcase --task TASK-001

# 독립 테스트 케이스도 바로 생성 가능
/create-testcase --standalone 배치 처리 성능 테스트
```

---

## 주의사항

1. **Task 기반 모드**: Task 파일과 완료된 Step이 존재해야 함
2. **독립 모드**: 충분한 설명 제공 권장
3. **파일 기반 모드**: 파일 경로가 정확해야 함
4. **중복 방지**: 기존 테스트 케이스와 중복되지 않도록 확인
5. **한국어 내용**: 테스트 내용은 한국어로 작성 (파일명은 영어)
