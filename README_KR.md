# Claude Code 에이전트 오케스트레이션 시스템

Claude Code를 위한 범용 멀티 에이전트 오케스트레이션 시스템입니다. Claude Code의 백그라운드 에이전트(Async Sub-agent) 기능을 활용하여 메인 에이전트가 서브 에이전트들을 병렬로 spawn하고 조율합니다.

[English Documentation](./README.md)

## 주요 기능

- **멀티 에이전트 오케스트레이션**: 메인 에이전트가 여러 서브 에이전트를 병렬로 조율
- **프로젝트 인식**: 프로젝트 타입 자동 감지 및 맞춤형 에이전트 생성
- **간편한 업데이트**: Git Submodule 기반 업데이트로 프로젝트 설정 유지
- **학습 시스템**: LESSONS_LEARNED.md에 빌드 에러 패턴 누적

## 빠른 시작

### 사전 요구사항

- [Claude Code CLI](https://claude.com/claude-code) 설치
- Git 설치
- 에이전트 오케스트레이션을 적용할 프로젝트

### 설치

#### 1단계: Git Submodule로 추가

운영체제에 맞는 명령어를 선택하세요:

<details>
<summary><b>Linux / macOS</b></summary>

```bash
# 프로젝트 루트로 이동
cd /path/to/your-project

# 오케스트레이션 시스템을 서브모듈로 추가
git submodule add https://github.com/Zeliper/z-coder .claude-orchestration
git submodule update --init --recursive

# 설치 확인
ls -la .claude-orchestration/
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
# 프로젝트 루트로 이동
cd C:\path\to\your-project

# 오케스트레이션 시스템을 서브모듈로 추가
git submodule add https://github.com/Zeliper/z-coder .claude-orchestration
git submodule update --init --recursive

# 설치 확인
dir .claude-orchestration\
```

</details>

<details>
<summary><b>Windows (명령 프롬프트)</b></summary>

```cmd
REM 프로젝트 루트로 이동
cd C:\path\to\your-project

REM 오케스트레이션 시스템을 서브모듈로 추가
git submodule add https://github.com/Zeliper/z-coder .claude-orchestration
git submodule update --init --recursive

REM 설치 확인
dir .claude-orchestration\
```

</details>

#### 2단계: Init 명령어 활성화

`/orchestration-init`을 실행하기 전에 먼저 명령어 파일을 복사해야 합니다:

<details>
<summary><b>Linux / macOS</b></summary>

```bash
# commands 디렉토리 생성 및 init 명령어 복사
mkdir -p .claude/commands
cp .claude-orchestration/.claude/commands/orchestration-init.md .claude/commands/
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
# commands 디렉토리 생성 및 init 명령어 복사
New-Item -ItemType Directory -Force -Path .claude\commands
Copy-Item .claude-orchestration\.claude\commands\orchestration-init.md .claude\commands\
```

</details>

<details>
<summary><b>Windows (명령 프롬프트)</b></summary>

```cmd
REM commands 디렉토리 생성 및 init 명령어 복사
mkdir .claude\commands
copy .claude-orchestration\.claude\commands\orchestration-init.md .claude\commands\
```

</details>

#### 3단계: Claude Code에서 초기화

프로젝트에서 Claude Code를 열고 (이미 열려 있다면 재시작) 다음 명령어를 실행합니다:

```
/orchestration-init
```

이 명령어는 다음을 수행합니다:
1. 서브모듈에서 `.claude/` 폴더로 에이전트 파일 복사
2. 프로젝트 구조 분석
3. 감지된 설정으로 `config.json` 생성
4. 프로젝트 타입에 맞는 커스텀 에이전트 생성
5. 코어 에이전트에 프로젝트 특화 설정 추가

### 대안: 수동 설치 (서브모듈 없이)

Git 서브모듈을 사용하지 않으려면:

<details>
<summary><b>Linux / macOS</b></summary>

```bash
# 레포지토리 클론
git clone https://github.com/Zeliper/z-coder.git /tmp/claude-orchestration

# 프로젝트로 파일 복사
cp -r /tmp/claude-orchestration/.claude ./
cp -r /tmp/claude-orchestration/tasks ./
cp /tmp/claude-orchestration/VERSION ./

# 정리
rm -rf /tmp/claude-orchestration

# 초기화
# Claude Code에서: /orchestration-init --no-submodule
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
# 레포지토리 클론
git clone https://github.com/Zeliper/z-coder.git $env:TEMP\claude-orchestration

# 프로젝트로 파일 복사
Copy-Item -Recurse $env:TEMP\claude-orchestration\.claude .\
Copy-Item -Recurse $env:TEMP\claude-orchestration\tasks .\
Copy-Item $env:TEMP\claude-orchestration\VERSION .\

# 정리
Remove-Item -Recurse -Force $env:TEMP\claude-orchestration

# 초기화
# Claude Code에서: /orchestration-init --no-submodule
```

</details>

<details>
<summary><b>Windows (명령 프롬프트)</b></summary>

```cmd
REM 레포지토리 클론
git clone https://github.com/Zeliper/z-coder.git %TEMP%\claude-orchestration

REM 프로젝트로 파일 복사
xcopy /E /I %TEMP%\claude-orchestration\.claude .\.claude
xcopy /E /I %TEMP%\claude-orchestration\tasks .\tasks
copy %TEMP%\claude-orchestration\VERSION .\

REM 정리
rmdir /S /Q %TEMP%\claude-orchestration

REM 초기화
REM Claude Code에서: /orchestration-init --no-submodule
```

</details>

---

## 오케스트레이션 시스템 업데이트

### 방법 1: 업데이트 명령어 사용 (권장)

Claude Code에서 다음 명령어를 실행합니다:

```
/orchestration-update
```

이 명령어는 다음을 수행합니다:
1. 서브모듈에서 최신 변경사항 가져오기
2. 프로젝트 특화 설정을 유지하면서 코어 에이전트 파일 업데이트
3. `LESSONS_LEARNED.md` 보존
4. `config.json`의 버전 정보 업데이트

#### 업데이트 옵션

```
/orchestration-update                    # 최신 버전으로 업데이트
/orchestration-update --version 1.2.0    # 특정 버전으로 업데이트
/orchestration-update --dry-run          # 변경 사항 미리보기 (적용하지 않음)
/orchestration-update --force            # 이미 최신이어도 강제 업데이트
```

### 방법 2: 수동 서브모듈 업데이트

<details>
<summary><b>Linux / macOS</b></summary>

```bash
# 프로젝트로 이동
cd /path/to/your-project

# 서브모듈 업데이트
cd .claude-orchestration
git fetch origin
git pull origin main
cd ..

# Claude Code에서 실행
# /orchestration-update
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
# 프로젝트로 이동
cd C:\path\to\your-project

# 서브모듈 업데이트
cd .claude-orchestration
git fetch origin
git pull origin main
cd ..

# Claude Code에서 실행
# /orchestration-update
```

</details>

### 방법 3: 특정 버전으로 업데이트

<details>
<summary><b>모든 플랫폼</b></summary>

```bash
# 서브모듈로 이동
cd .claude-orchestration

# 사용 가능한 버전 목록 확인
git tag -l

# 특정 버전 체크아웃
git checkout v1.2.0

cd ..

# Claude Code에서 업데이트 적용
# /orchestration-update --force
```

</details>

---

## 사용법

### 태스크 시작

```
/orchestrate JWT를 사용한 사용자 인증 구현
```

### 태스크 이어하기

```
/orchestrate --task TASK-001
```

### 이전 작업 참조

```
/orchestrate --ref TASK-001 리프레시 토큰 지원 추가
```

### 상태 확인

```
/status
/tasks
```

---

## 프로젝트 구조

초기화 후 프로젝트 구조:

```
your-project/
├── .claude-orchestration/        # Git 서브모듈 (원본 소스)
│   ├── VERSION
│   ├── .claude/
│   │   ├── agents/
│   │   ├── commands/
│   │   └── templates/
│   └── tasks/
├── .claude/                      # 활성 설정 (프로젝트 특화)
│   ├── agents/
│   │   ├── main-agent.md
│   │   ├── coder-agent.md
│   │   ├── builder-agent.md
│   │   ├── codebase-search-agent.md
│   │   ├── todo-list-agent.md
│   │   ├── web-search-agent.md
│   │   └── {custom-agents}.md    # 프로젝트 기반 자동 생성
│   ├── commands/
│   │   ├── orchestrate.md
│   │   ├── orchestration-init.md
│   │   └── orchestration-update.md
│   ├── templates/
│   ├── config.json               # 프로젝트 설정
│   └── LESSONS_LEARNED.md        # 빌드 에러 패턴 (보존됨)
└── tasks/
    ├── TASK-001.md               # 진행 중인 태스크
    └── archive/                  # 완료된 태스크
```

---

## 코어 에이전트

| 에이전트 | 역할 |
|---------|------|
| **main-agent** | 워크플로우 조율, 서브 에이전트 spawn |
| **codebase-search-agent** | 코드베이스 탐색, 패턴 분석 |
| **reference-agent** | 레퍼런스 코드, 예제, 템플릿 탐색 |
| **todo-list-agent** | 태스크를 Step으로 분해 |
| **coder-agent** | 코드 변경 구현 |
| **web-search-agent** | 외부 문서 검색 |
| **builder-agent** | 빌드 실행, 에러 분석 |

### 자동 생성 커스텀 에이전트

프로젝트 타입에 따라 추가 에이전트가 생성될 수 있습니다:

| 프로젝트 타입 | 커스텀 에이전트 |
|--------------|---------------|
| Unity/BepInEx | decompiled-search-agent, harmony-patch-agent |
| Node.js/TypeScript | dependency-analyzer-agent |
| Python | python-env-agent |
| Database | db-schema-agent |
| Docker | container-agent |

---

## 설정

### config.json 스키마

```json
{
  "orchestration": {
    "version": "1.0.0",
    "installed_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z",
    "submodule_path": ".claude-orchestration"
  },
  "project": {
    "name": "your-project",
    "type": "nodejs",
    "languages": ["typescript"],
    "frameworks": ["express"]
  },
  "paths": {
    "source": ["./src"],
    "excluded": ["node_modules", ".git"]
  },
  "commands": {
    "build": "npm run build",
    "test": "npm test"
  },
  "custom_agents": ["dependency-analyzer-agent"]
}
```

---

## 기존 프로젝트에 추가 시 주의사항

기존 프로젝트에 이 오케스트레이션 시스템을 서브모듈로 추가할 때 다음 사항에 주의하세요:

### 설치 전 체크리스트

| 항목 | 설명 |
|------|------|
| **기존 `.claude/` 폴더** | 프로젝트에 이미 `.claude/` 폴더가 있다면 먼저 백업하세요. 초기화 시 덮어쓰기됩니다. |
| **팀 동기화 필요** | 모든 팀원이 pull 후 `git submodule update --init --recursive` 실행 필요 |
| **CI/CD 파이프라인** | 클론 시 `--recursive` 플래그를 포함하도록 CI/CD 업데이트 필요 |
| **`.gitmodules` 충돌** | 기존 서브모듈이 있다면 `.gitmodules`에서 경로 충돌 확인 |

### 팀 협업 시

서브모듈 추가 후 팀원에게 안내하세요:

```bash
# 팀원은 pull 후 반드시 이 명령어 실행
git submodule update --init --recursive

# 또는 새로 클론할 때 recursive 플래그 사용
git clone --recursive <your-repo-url>
```

### 기존 설정 백업

기존 `.claude/` 설정이 있는 경우:

```bash
# 설치 전
mv .claude .claude.backup.manual

# /orchestration-init 후, 커스텀 설정을 다시 병합
# 설정은 아래 마커 사이에 추가:
# <!-- ORCHESTRATION-PROJECT-CONFIG-START -->
# <!-- ORCHESTRATION-PROJECT-CONFIG-END -->
```

### 기존 프로젝트 추가 시 흔한 문제

| 문제 | 해결 방법 |
|------|----------|
| 서브모듈 경로 충돌 | 다른 경로 선택: `git submodule add <url> .orchestration` |
| 권한 거부 | 레포지토리 쓰기 권한 확인 |
| 서브모듈 Detached HEAD | `cd .claude-orchestration && git checkout main` 실행 |
| 중첩된 .git 충돌 | 서브모듈 추가 전 중첩된 `.git` 폴더 제거 |

---

## 문제 해결

### 서브모듈을 찾을 수 없음

```bash
# 서브모듈 재초기화
git submodule update --init --recursive
```

### 업데이트 실패 - 롤백

시스템은 업데이트 전에 자동으로 백업을 생성합니다. 업데이트가 실패하면:

```bash
# 백업은 .claude.backup.{timestamp} 형식으로 저장됨
# 필요시 수동 복원:
rm -rf .claude
mv .claude.backup.20250115_120000 .claude
```

### 에이전트 파일 병합 충돌

프로젝트 특화 설정은 마커를 사용하여 보존됩니다:
```markdown
<!-- ORCHESTRATION-PROJECT-CONFIG-START -->
여기에 프로젝트 설정 (업데이트 시 보존됨)
<!-- ORCHESTRATION-PROJECT-CONFIG-END -->
```

충돌이 발생하면 마커가 손상되지 않았는지 확인하세요.

---

## 기여하기

1. 레포지토리 포크
2. 기능 브랜치 생성
3. 변경 사항 작성
4. 필요시 VERSION 파일 업데이트
5. Pull Request 제출

---

## 라이선스

MIT 라이선스 - 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.
