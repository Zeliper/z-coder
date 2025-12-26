# /orchestration-update

오케스트레이션 시스템을 최신 버전으로 업데이트합니다. 코어 에이전트만 업데이트하고 프로젝트 특화 설정은 유지합니다.

## 옵션
- `--version {ver}`: 특정 버전으로 업데이트 (예: --version 1.0.0)
- `--dry-run`: 실제 변경 없이 업데이트 내용 미리보기
- `--force`: 버전 확인 없이 강제 업데이트

## 실행 지침

이 명령어는 `orchestration-update-agent`를 spawn하여 실행합니다.

### 1. 스킬 참조

`.claude/skills/spawn-orchestration-update/SKILL.md` 참조

### 2. 옵션 파싱

사용자 입력에서 옵션 추출:
```
$ARGUMENTS → version, dry_run, force 파싱
```

### 3. 에이전트 Spawn

```
"백그라운드에서 orchestration-update-agent 역할로 다음 작업을 수행해줘:

옵션: $ARGUMENTS

.claude/agents/orchestration-update-agent.md 의 지시를 따르고,
작업 완료 후 결과만 요약해서 보고해줘."
```

### 4. 결과 보고

에이전트 결과를 사용자에게 전달:
- COMPLETED: 업데이트 성공 내역 표시
- FAILED: 에러 원인 및 복구 상태 안내
- DRY_RUN: 변경 예정 내용 표시

---

## 상세 워크플로우

상세 워크플로우는 `.claude/agents/orchestration-update-agent.md` 참조

---

## 참고

- 이 명령어는 `.claude-orchestration/` 서브모듈이 있어야 작동합니다
- 프로젝트 특화 설정은 마커로 구분되어 자동으로 보존됩니다
- LESSONS_LEARNED.md는 절대 덮어쓰지 않습니다
- 업데이트 전 자동 백업이 생성됩니다
