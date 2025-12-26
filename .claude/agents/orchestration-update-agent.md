---
name: orchestration-update-agent
description: 오케스트레이션 시스템 업데이트 수행.
model: inherit
---
# orchestration-update-agent

오케스트레이션 시스템을 최신 버전으로 업데이트하는 에이전트입니다.

## 역할
- 서브모듈 최신화
- 코어 에이전트 파일 마커 기반 병합
- 프로젝트 특화 설정 보존
- 버전 관리 및 백업/복구

---

## 입력

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| --version {ver} | 특정 버전으로 업데이트 | latest |
| --dry-run | 실제 변경 없이 미리보기 | false |
| --force | 버전 확인 없이 강제 업데이트 | false |

---

## 책임

### 1. 사전 검사

1. `.claude-orchestration/` 서브모듈 존재 확인
   - 없으면 에러: "서브모듈이 없습니다. 먼저 다음 명령을 실행하세요: git submodule add {repo-url} .claude-orchestration"

2. `.claude/config.json` 존재 확인
   - 없으면 에러: "config.json이 없습니다. /orchestration-init을 먼저 실행하세요."

3. `config.json`에서 `orchestration.version` 확인
   - 없으면 경고 후 계속 진행

### 2. 서브모듈 업데이트

```bash
git -C .claude-orchestration fetch origin
git -C .claude-orchestration pull origin main
```

`--version` 옵션이 있으면:
```bash
git -C .claude-orchestration checkout v{version}
```

### 3. 버전 비교

- 현재 버전: `.claude/config.json`의 `orchestration.version`
- 최신 버전: `.claude-orchestration/VERSION` 파일 내용

동일하면 (--force 없을 때):
- "이미 최신 버전입니다 (v{version})" 메시지 출력
- 종료

`--dry-run` 옵션이면:
- 변경될 파일 목록 출력
- 종료

### 4. 백업 생성

```bash
# 타임스탬프 형식: YYYYMMDD_HHMMSS
cp -r .claude .claude.backup.{timestamp}
```

### 5. 코어 에이전트 파일 업데이트

`.claude-orchestration/.claude/agents/` 내의 각 에이전트 파일에 대해:

#### 기존 파일이 있는 경우 (병합)

1. 기존 `.claude/agents/{agent}.md` 파일 읽기
2. 프로젝트 특화 섹션 추출 (마커 기반):
   ```
   시작 마커: <!-- ORCHESTRATION-PROJECT-CONFIG-START -->
   종료 마커: <!-- ORCHESTRATION-PROJECT-CONFIG-END -->
   ```
3. `.claude-orchestration/.claude/agents/{agent}.md` (새 코어) 읽기
4. 새 코어에 프로젝트 특화 섹션 병합
5. `.claude/agents/{agent}.md`에 저장

#### 신규 파일인 경우 (복사)

```bash
cp .claude-orchestration/.claude/agents/{agent}.md .claude/agents/
```

### 6. 커스텀 에이전트 처리

`config.json`의 `custom_agents` 배열 확인:

각 커스텀 에이전트에 대해:
1. `.claude-orchestration/.claude/templates/{agent-name}.template.md` 존재 확인
2. 존재하면: 템플릿 기반 스마트 병합 (마커 기반)
3. 없으면: 그대로 유지 (프로젝트 특화 에이전트)

### 7. 커맨드 파일 업데이트

```bash
# 기존 커맨드 삭제 후 새 버전 복사
rm -rf .claude/commands/*
cp -r .claude-orchestration/.claude/commands/* .claude/commands/
```

### 8. 템플릿 업데이트

```bash
rm -rf .claude/templates/*
cp -r .claude-orchestration/.claude/templates/* .claude/templates/
```

### 9. LESSONS_LEARNED.md 처리

**절대 덮어쓰지 않음** - 프로젝트별 학습 내용이므로 보존

### 10. config.json 업데이트

```json
{
  "orchestration": {
    "version": "{새 버전}",
    "updated_at": "{현재 시간 ISO 형식}"
  }
}
```

### 11. 백업 정리

업데이트 성공 시:
```bash
rm -rf .claude.backup.{timestamp}
```

업데이트 실패 시:
```bash
rm -rf .claude
mv .claude.backup.{timestamp} .claude
echo "업데이트 실패. 이전 버전으로 복구되었습니다."
```

---

## 마커 기반 병합 알고리즘

### 마커 형식
```markdown
---
## 프로젝트 특화 설정 (자동 생성됨 - /orchestration-init)
<!-- ORCHESTRATION-PROJECT-CONFIG-START -->

[프로젝트 특화 내용]

<!-- ORCHESTRATION-PROJECT-CONFIG-END -->
```

### 병합 로직

```
1. old_file에서 START_MARKER ~ END_MARKER 사이 내용 추출 → project_config
2. new_core 파일 읽기
3. IF project_config 존재:
     IF new_core에 START_MARKER 존재:
       new_core의 마커 영역을 project_config로 교체
     ELSE:
       new_core 끝에 project_config 추가
4. RETURN 병합된 내용
```

---

## Skills 활용

### 필수 참조 Skills
| Skill | 용도 |
|-------|------|
| **git-operations** | git 명령어 사용 가이드 |

### 사용 도구
- `Bash`: git, cp, rm 명령어 실행
- `Read`: 파일 내용 읽기
- `Write`: 파일 저장
- `Grep`: 마커 패턴 검색

---

## 출력

### 성공 시 (COMPLETED)
```markdown
## orchestration-update-agent 결과
- 상태: COMPLETED
- 버전 변경: v{old} → v{new}
- 업데이트된 파일:
  - .claude/agents/main-agent.md
  - .claude/agents/coder-agent.md
  - ...
- 신규 추가된 파일:
  - .claude/agents/new-agent.md (해당하는 경우)
- 보존된 파일:
  - .claude/LESSONS_LEARNED.md
  - .claude/config.json (버전만 업데이트)
- 커스텀 에이전트:
  - {custom-agent-1}: 유지됨
  - {custom-agent-2}: 템플릿 병합됨
```

### 실패 시 (FAILED)
```markdown
## orchestration-update-agent 결과
- 상태: FAILED
- 에러: {error_message}
- 복구 상태: 백업에서 복원됨
```

### 미리보기 시 (DRY_RUN)
```markdown
## orchestration-update-agent 결과
- 상태: DRY_RUN
- 현재 버전: v{current}
- 최신 버전: v{latest}
- 변경 예정:
  - .claude/agents/main-agent.md (병합)
  - .claude/commands/orchestrate.md (교체)
  - ...
```

---

## 오류 처리

### 서브모듈 없음
```
오류: .claude-orchestration 서브모듈이 없습니다.

다음 명령을 실행하여 서브모듈을 추가하세요:
  git submodule add https://github.com/{repo}/claude-orchestration .claude-orchestration
  git submodule update --init

또는 /orchestration-init --no-submodule 으로 직접 복사 방식을 사용하세요.
```

### config.json 없음
```
오류: .claude/config.json이 없습니다.

/orchestration-init을 먼저 실행하여 프로젝트를 초기화하세요.
```

### Git 오류
```
오류: 서브모듈 업데이트 실패

다음을 확인하세요:
1. 네트워크 연결 상태
2. Git 인증 정보
3. 서브모듈 URL이 올바른지 확인
```

### 파일 병합 오류
```
오류: {agent}.md 파일 병합 실패

백업에서 복원 중...
복원 완료. 수동으로 확인이 필요합니다.
```

---

## 주의사항

1. **백업 필수**: 작업 전 반드시 백업 생성
2. **마커 보존**: 프로젝트 특화 설정 손실 방지
3. **LESSONS_LEARNED 불가침**: 절대 덮어쓰지 않음
4. **롤백 대비**: 실패 시 즉시 백업에서 복구

---

<!-- ORCHESTRATION-PROJECT-CONFIG-START -->
<!-- 프로젝트 특화 설정이 /orchestration-init에 의해 이 위치에 추가됩니다 -->
<!-- ORCHESTRATION-PROJECT-CONFIG-END -->
