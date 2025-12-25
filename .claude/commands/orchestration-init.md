# /orchestration-init

프로젝트를 분석하여 오케스트레이션 시스템을 초기화합니다. config.json을 생성하고, 프로젝트에 맞는 커스텀 에이전트를 자동 생성합니다.

## 옵션
- `--force`: 기존 설정 무시하고 재초기화
- `--no-submodule`: 서브모듈 없이 직접 복사 방식 사용

## 실행 지침

### 1. 서브모듈 존재 확인

#### 서브모듈 모드 (기본)

`.claude-orchestration/` 폴더 존재 확인:

**존재하는 경우**:
- 서브모듈에서 파일 복사 진행

**존재하지 않는 경우**:
- 사용자에게 안내:
  ```
  오케스트레이션 서브모듈이 없습니다.

  다음 명령을 실행하여 서브모듈을 추가하세요:
    git submodule add https://github.com/{repo}/claude-orchestration .claude-orchestration
    git submodule update --init

  또는 --no-submodule 옵션으로 직접 복사 방식을 사용하세요:
    /orchestration-init --no-submodule
  ```
- 종료

#### 직접 복사 모드 (`--no-submodule`)

사용자에게 안내:
```
직접 복사 모드입니다. 다음 파일들이 필요합니다:
- .claude/agents/*.md (에이전트 파일들)
- .claude/commands/*.md (커맨드 파일들)
- .claude/templates/*.md (템플릿 파일들)
- VERSION 파일

파일을 수동으로 복사하거나, git clone 후 이 명령을 다시 실행하세요.
```

### 2. 기존 설정 확인

`.claude/config.json` 존재 확인:

**존재하고 `--force` 없음**:
- 경고: "기존 config.json이 있습니다. --force 옵션으로 재초기화하세요."
- 종료

**존재하고 `--force` 있음**:
- 기존 config.json 백업: `config.json.backup.{timestamp}`
- 계속 진행

**존재하지 않음**:
- 계속 진행

### 3. 서브모듈에서 파일 복사

```bash
# 기존 .claude 폴더가 없으면 생성
mkdir -p .claude/agents
mkdir -p .claude/commands
mkdir -p .claude/templates
mkdir -p tasks/archive

# 서브모듈에서 파일 복사
cp -r .claude-orchestration/.claude/agents/* .claude/agents/
cp -r .claude-orchestration/.claude/commands/* .claude/commands/
cp -r .claude-orchestration/.claude/templates/* .claude/templates/

# LESSONS_LEARNED 템플릿 복사 (파일이 없을 때만)
if [ ! -f .claude/LESSONS_LEARNED.md ]; then
  cp .claude-orchestration/.claude/LESSONS_LEARNED.template.md .claude/LESSONS_LEARNED.md
fi

# tasks 폴더
cp .claude-orchestration/tasks/.gitkeep tasks/
cp .claude-orchestration/tasks/archive/.gitkeep tasks/archive/
```

### 4. 프로젝트 분석

프로젝트 루트를 스캔하여 다음 정보를 수집:

#### 4.1 언어/프레임워크 감지

| 파일 | 언어/프레임워크 |
|------|----------------|
| package.json | Node.js/JavaScript/TypeScript |
| tsconfig.json | TypeScript |
| *.csproj | C#/.NET |
| requirements.txt, pyproject.toml | Python |
| Cargo.toml | Rust |
| go.mod | Go |
| pom.xml, build.gradle | Java |
| Gemfile | Ruby |
| composer.json | PHP |

#### 4.2 빌드 시스템 감지

| 파일 | 빌드 명령어 |
|------|------------|
| package.json (scripts.build) | npm run build |
| Makefile | make |
| build.gradle | ./gradlew build |
| pom.xml | mvn package |
| Cargo.toml | cargo build |

#### 4.3 테스트 프레임워크 감지

| 파일/폴더 | 테스트 명령어 |
|----------|--------------|
| jest.config.js | npm test |
| pytest.ini, tests/ | pytest |
| *Test.cs, *Tests.cs | dotnet test |
| *_test.go | go test |

#### 4.4 특수 폴더 감지

| 폴더 | 프로젝트 타입 |
|------|-------------|
| Assets/, ProjectSettings/ | Unity |
| Decompiled/, Managed/ | 게임 모딩 |
| migrations/ | Database |
| locales/, i18n/ | 다국어 지원 |

#### 4.5 설치된 도구 감지

시스템에 설치된 도구들을 감지합니다. 각 도구 설치 확인 후 `config.json`의 `installed_tools` 섹션에 기록합니다.

##### 디컴파일러/역공학 도구

| 도구 | 확인 방법 | 용도 |
|------|----------|------|
| ILSpy | `where ilspycmd` 또는 `which ilspycmd` | .NET 디컴파일 |
| dnSpy | 레지스트리/일반 경로 확인 | .NET 디컴파일/디버깅 |
| dotPeek | `where dotPeek*` | .NET 디컴파일 |
| JD-GUI | `where jd-gui` / `which jd-gui` | Java 디컴파일 |
| CFR | `where cfr` / `java -jar cfr.jar` 확인 | Java 디컴파일 |
| jadx | `where jadx` / `which jadx` | Android/Java 디컴파일 |
| Ghidra | `GHIDRA_HOME` 환경변수 또는 경로 확인 | 바이너리 역공학 |
| IDA | `where ida*` / 일반 경로 확인 | 바이너리 역공학 |
| radare2 | `where r2` / `which r2` | 바이너리 분석 |
| objdump | `where objdump` / `which objdump` | 바이너리 분석 |
| dumpbin | `where dumpbin` (VS 설치 시) | Windows 바이너리 분석 |

##### 패키지/의존성 도구

| 도구 | 확인 방법 | 용도 |
|------|----------|------|
| npm | `where npm` / `which npm` | Node.js 패키지 |
| yarn | `where yarn` / `which yarn` | Node.js 패키지 |
| pnpm | `where pnpm` / `which pnpm` | Node.js 패키지 |
| pip | `where pip` / `which pip` | Python 패키지 |
| poetry | `where poetry` / `which poetry` | Python 패키지 |
| cargo | `where cargo` / `which cargo` | Rust 패키지 |
| dotnet | `where dotnet` / `which dotnet` | .NET CLI |
| nuget | `where nuget` / `which nuget` | .NET 패키지 |
| gradle | `where gradle` / `which gradle` | Java 빌드 |
| maven (mvn) | `where mvn` / `which mvn` | Java 빌드 |

##### 코드 분석/품질 도구

| 도구 | 확인 방법 | 용도 |
|------|----------|------|
| SonarQube | `where sonar-scanner` | 코드 품질 분석 |
| ESLint | `npm list eslint` (프로젝트 내) | JS/TS 린팅 |
| Prettier | `npm list prettier` (프로젝트 내) | 코드 포매팅 |
| Black | `where black` / `which black` | Python 포매팅 |
| Ruff | `where ruff` / `which ruff` | Python 린팅 |

##### 디버거

| 도구 | 확인 방법 | 용도 |
|------|----------|------|
| gdb | `where gdb` / `which gdb` | 네이티브 디버깅 |
| lldb | `where lldb` / `which lldb` | 네이티브 디버깅 |
| WinDbg | 레지스트리/경로 확인 | Windows 디버깅 |

##### 도구 감지 스크립트 (Windows PowerShell)

```powershell
# 도구 존재 확인 함수
function Test-Tool {
    param([string]$Name, [string]$Command)
    $result = Get-Command $Command -ErrorAction SilentlyContinue
    if ($result) {
        return @{ name = $Name; path = $result.Source; available = $true }
    }
    return @{ name = $Name; available = $false }
}

# 환경 변수 확인 함수
function Test-EnvPath {
    param([string]$Name, [string]$EnvVar)
    $path = [Environment]::GetEnvironmentVariable($EnvVar)
    if ($path -and (Test-Path $path)) {
        return @{ name = $Name; path = $path; available = $true }
    }
    return $null
}
```

##### 도구 감지 스크립트 (Unix/bash)

```bash
# 도구 존재 확인 함수
check_tool() {
    local name=$1
    local cmd=$2
    if command -v "$cmd" &> /dev/null; then
        echo "{\"name\": \"$name\", \"path\": \"$(which $cmd)\", \"available\": true}"
    else
        echo "{\"name\": \"$name\", \"available\": false}"
    fi
}

# 환경 변수 확인 함수
check_env() {
    local name=$1
    local var=$2
    local path="${!var}"
    if [ -n "$path" ] && [ -d "$path" ]; then
        echo "{\"name\": \"$name\", \"path\": \"$path\", \"available\": true}"
    fi
}
```

### 5. config.json 생성

```json
{
  "orchestration": {
    "version": "{VERSION 파일 내용}",
    "installed_at": "{현재 시간 ISO 형식}",
    "updated_at": "{현재 시간 ISO 형식}",
    "submodule_path": ".claude-orchestration"
  },
  "project": {
    "name": "{폴더명 또는 package.json의 name}",
    "description": "{package.json의 description 또는 빈 문자열}",
    "type": "{감지된 프로젝트 타입}",
    "languages": ["{감지된 언어들}"],
    "frameworks": ["{감지된 프레임워크들}"]
  },
  "paths": {
    "source": ["{감지된 소스 경로}"],
    "search": ["./"],
    "excluded": ["node_modules", "bin", "obj", ".git", "dist", "build"],
    "decompiled": ["{Decompiled 폴더 경로}"],
    "assets": ["{Assets 폴더 경로}"],
    "tests": ["{테스트 폴더 경로}"]
  },
  "commands": {
    "build": "{감지된 빌드 명령어}",
    "test": "{감지된 테스트 명령어}",
    "lint": "{감지된 lint 명령어}",
    "run": "{감지된 실행 명령어}"
  },
  "installed_tools": {
    "decompilers": [
      {
        "name": "ILSpy",
        "command": "ilspycmd",
        "path": "{감지된 경로}",
        "available": true,
        "target": ".NET"
      }
    ],
    "package_managers": [
      {
        "name": "npm",
        "command": "npm",
        "path": "{감지된 경로}",
        "available": true
      }
    ],
    "analyzers": [
      {
        "name": "Ghidra",
        "command": "analyzeHeadless",
        "path": "{GHIDRA_HOME 경로}",
        "available": true,
        "target": "binary"
      }
    ],
    "debuggers": [
      {
        "name": "gdb",
        "command": "gdb",
        "path": "{감지된 경로}",
        "available": true
      }
    ],
    "linters": [
      {
        "name": "ESLint",
        "command": "eslint",
        "available": true,
        "scope": "project"
      }
    ]
  },
  "conventions": {
    "naming": "",
    "architecture": "",
    "notes": []
  },
  "custom_agents": [],
  "tool_agents": []
}
```

### 6. 커스텀 에이전트 생성

프로젝트 타입에 따라 커스텀 에이전트 자동 생성:

#### 게임 모딩 (Unity/BepInEx/Harmony)
트리거:
- *.csproj에 BepInEx 참조
- Harmony 의존성
- Decompiled/ 또는 Managed/ 폴더

생성할 에이전트:
- `decompiled-search-agent`: 원본 게임 코드 탐색
- `harmony-patch-agent`: 패치 타겟 메서드 탐색

#### Unity 프로젝트
트리거:
- Assets/ 폴더
- *.unity 파일
- ProjectSettings/ 폴더

생성할 에이전트:
- `unity-asset-agent`: Asset, Prefab, ScriptableObject 구조 분석

#### Node.js/TypeScript
트리거:
- package.json
- tsconfig.json

생성할 에이전트:
- `dependency-analyzer-agent`: npm 의존성 분석

#### Python
트리거:
- requirements.txt
- pyproject.toml

생성할 에이전트:
- `python-env-agent`: 가상환경, 의존성 분석

#### Database
트리거:
- migrations/ 폴더
- *.sql 파일
- prisma.schema, alembic.ini

생성할 에이전트:
- `db-schema-agent`: 스키마 분석, 마이그레이션 계획

### 6.5 도구 에이전트 생성 (설치된 도구 기반)

설치된 도구가 감지되면 해당 도구를 활용하는 에이전트를 자동 생성합니다.
도구 에이전트는 **Async/Sync 겸용**으로 설계되어, 동기/비동기 모드 모두에서 사용 가능합니다.

#### 디컴파일러 도구 에이전트

##### ILSpy (ilspycmd)
트리거: `ilspycmd` 명령어 사용 가능

생성할 에이전트: `ilspy-decompile-agent`
- **역할**: .NET 어셈블리 디컴파일 및 분석
- **동기 모드**: 특정 타입/메서드 디컴파일 후 결과 반환
- **비동기 모드**: 대량 어셈블리 일괄 디컴파일
- **명령어 예시**:
  ```bash
  ilspycmd assembly.dll -o ./Decompiled/
  ilspycmd assembly.dll -t Namespace.ClassName
  ```

##### dnSpy / dotPeek
트리거: dnSpy 또는 dotPeek 설치 감지

생성할 에이전트: `dotnet-decompile-agent`
- **역할**: .NET 어셈블리 디컴파일 (GUI 도구 연동)
- **동기 모드**: 경로 및 분석 대상 안내
- **비동기 모드**: 디컴파일 결과 폴더 감시 및 분석

##### jadx (Android/Java)
트리거: `jadx` 명령어 사용 가능

생성할 에이전트: `jadx-decompile-agent`
- **역할**: APK/DEX/JAR 파일 디컴파일
- **동기 모드**: 특정 클래스 디컴파일
- **비동기 모드**: 전체 APK 디컴파일 (시간 소요)
- **명령어 예시**:
  ```bash
  jadx app.apk -d ./decompiled/
  jadx --show-bad-code app.apk
  ```

##### CFR / JD-GUI (Java)
트리거: `cfr` 또는 `jd-gui` 사용 가능

생성할 에이전트: `java-decompile-agent`
- **역할**: Java 클래스/JAR 파일 디컴파일
- **동기 모드**: 단일 클래스 디컴파일
- **비동기 모드**: JAR 전체 디컴파일
- **명령어 예시**:
  ```bash
  java -jar cfr.jar target.jar --outputdir ./decompiled/
  ```

#### 바이너리 분석 도구 에이전트

##### Ghidra
트리거: `GHIDRA_HOME` 환경변수 또는 Ghidra 설치 경로 감지

생성할 에이전트: `ghidra-analyze-agent`
- **역할**: 바이너리 역공학 분석 (Headless 모드)
- **동기 모드**: 함수/심볼 목록 추출
- **비동기 모드**: 전체 바이너리 분석 (프로젝트 생성)
- **명령어 예시**:
  ```bash
  analyzeHeadless /path/to/project ProjectName -import binary.exe -postScript ExportFunctions.py
  ```

##### radare2 (r2)
트리거: `r2` 명령어 사용 가능

생성할 에이전트: `radare2-analyze-agent`
- **역할**: 바이너리 분석 및 디스어셈블
- **동기 모드**: 함수 목록, 문자열 추출
- **비동기 모드**: 전체 분석
- **명령어 예시**:
  ```bash
  r2 -q -c "aaa; afl" binary.exe
  r2 -q -c "iz" binary.exe  # 문자열 추출
  ```

##### objdump / dumpbin
트리거: `objdump` 또는 `dumpbin` 사용 가능

생성할 에이전트: `binary-dump-agent`
- **역할**: 바이너리 섹션/심볼 덤프
- **동기 모드**: 헤더, 심볼 테이블 추출
- **명령어 예시**:
  ```bash
  objdump -d binary.exe > disasm.txt
  dumpbin /exports library.dll
  ```

#### 패키지/의존성 도구 에이전트

##### npm/yarn/pnpm
트리거: 해당 패키지 매니저 설치 + package.json 존재

생성할 에이전트: `npm-package-agent`
- **역할**: Node.js 의존성 관리 및 분석
- **동기 모드**: 의존성 트리 분석, 취약점 검사
- **비동기 모드**: 패키지 설치, 업데이트
- **명령어 예시**:
  ```bash
  npm list --depth=0
  npm audit
  npm outdated
  ```

##### pip/poetry
트리거: Python 패키지 매니저 설치 + requirements.txt/pyproject.toml 존재

생성할 에이전트: `pip-package-agent`
- **역할**: Python 의존성 관리 및 분석
- **동기 모드**: 설치된 패키지 목록, 의존성 트리
- **비동기 모드**: 패키지 설치, 가상환경 관리
- **명령어 예시**:
  ```bash
  pip list
  pip show package-name
  poetry show --tree
  ```

##### dotnet/nuget
트리거: .NET CLI 설치 + *.csproj 존재

생성할 에이전트: `dotnet-package-agent`
- **역할**: NuGet 패키지 관리 및 분석
- **동기 모드**: 패키지 참조 분석
- **비동기 모드**: 패키지 복원, 업데이트
- **명령어 예시**:
  ```bash
  dotnet list package
  dotnet list package --outdated
  ```

#### 코드 품질 도구 에이전트

##### SonarQube Scanner
트리거: `sonar-scanner` 사용 가능

생성할 에이전트: `sonar-analyze-agent`
- **역할**: 코드 품질 및 보안 분석
- **비동기 전용**: 전체 프로젝트 스캔 (시간 소요)
- **명령어 예시**:
  ```bash
  sonar-scanner -Dsonar.projectKey=myproject
  ```

##### ESLint/Prettier/Ruff/Black
트리거: 해당 린터/포매터 설치

생성할 에이전트: `code-quality-agent`
- **역할**: 코드 스타일 검사 및 자동 수정
- **동기 모드**: 특정 파일 검사
- **비동기 모드**: 전체 프로젝트 검사 및 수정
- **명령어 예시**:
  ```bash
  eslint src/ --fix
  prettier --write "src/**/*.ts"
  ruff check . --fix
  black .
  ```

#### 디버거 도구 에이전트

##### gdb/lldb
트리거: 해당 디버거 설치

생성할 에이전트: `debugger-agent`
- **역할**: 프로세스 디버깅 지원
- **동기 모드**: 브레이크포인트 설정 안내, 명령어 생성
- **명령어 예시**:
  ```bash
  gdb -ex "break main" -ex "run" ./program
  lldb -o "breakpoint set --name main" ./program
  ```

### 6.6 도구 에이전트 파일 템플릿

`.claude/templates/tool-agent.template.md` 생성:

```markdown
# {tool-name}-agent

## 역할
{tool_description} 도구를 활용한 분석/실행 에이전트

## 도구 정보
- **도구명**: {tool_name}
- **명령어**: {tool_command}
- **경로**: {tool_path}
- **대상**: {tool_target}

## 실행 모드

### 동기 모드 (Sync)
빠른 결과가 필요한 경우 사용. 결과를 즉시 반환합니다.
- 타임아웃: 30초
- 용도: {sync_use_cases}

### 비동기 모드 (Async)
시간이 오래 걸리는 작업에 사용. 백그라운드에서 실행합니다.
- 용도: {async_use_cases}
- 완료 알림: 작업 완료 시 결과 파일 생성

## 주요 명령어
{common_commands}

## 입력
- 분석 대상 파일/폴더 경로
- 실행 모드 (sync/async)
- 추가 옵션

## 출력
```markdown
## {tool-name} 분석 결과
- 실행 모드: [sync/async]
- 대상: [파일/폴더 경로]
- 결과 요약: [핵심 발견 사항]
- 출력 위치: [결과 파일/폴더 경로]
- 추가 명령어: [후속 분석을 위한 명령어 제안]
```

---

<!-- ORCHESTRATION-PROJECT-CONFIG-START -->
<!-- 프로젝트 특화 설정이 여기에 추가됩니다 -->
<!-- ORCHESTRATION-PROJECT-CONFIG-END -->
```

생성된 도구 에이전트를 `config.json`의 `tool_agents` 배열에 등록.

### 7. 커스텀 에이전트 파일 생성

`.claude/templates/custom-agent.template.md` 템플릿 사용:

```markdown
# {agent-name}

## 역할
{role_description}

## 프로젝트 컨텍스트
- 프로젝트: {project_name}
- 기술스택: {tech_stack}

## 책임
{responsibilities}

## 탐색 경로
{search_paths}

## 입력
- 사용자 요청 요약
- 탐색 키워드

## 출력
**최대 500자 이내 요약**으로 반환

## 반환 형식
```markdown
## {agent-name} 결과
- 발견 항목: [목록]
- 핵심 정보: [요약]
- 관련 참조: [파일/경로 목록]
- 권장 사항: [있는 경우]
```

---

<!-- ORCHESTRATION-PROJECT-CONFIG-START -->
<!-- 프로젝트 특화 설정이 여기에 추가됩니다 -->
<!-- ORCHESTRATION-PROJECT-CONFIG-END -->
```

생성된 에이전트를 `config.json`의 `custom_agents` 배열에 등록.

### 8. 코어 에이전트 프로젝트 특화 섹션 추가

각 코어 에이전트 파일에 프로젝트 특화 섹션 추가:

```markdown
---
## 프로젝트 특화 설정 (자동 생성됨 - /orchestration-init)
<!-- ORCHESTRATION-PROJECT-CONFIG-START -->

### 프로젝트 정보
- 이름: {project_name}
- 타입: {project_type}
- 기술스택: {tech_stack}

### 프로젝트 특화 지시
{project_specific_instructions}

### 참조 경로
{relevant_paths}

<!-- ORCHESTRATION-PROJECT-CONFIG-END -->
```

### 9. 결과 보고

```markdown
## 오케스트레이션 시스템 초기화 완료

### 프로젝트 정보
- 이름: {project_name}
- 타입: {project_type}
- 언어: {languages}
- 프레임워크: {frameworks}

### 감지된 빌드 설정
- 빌드: {build_command}
- 테스트: {test_command}

### 생성된 파일
- .claude/config.json
- .claude/LESSONS_LEARNED.md

### 코어 에이전트 (프로젝트 특화 적용)
- main-agent.md
- codebase-search-agent.md
- todo-list-agent.md
- coder-agent.md
- web-search-agent.md
- builder-agent.md

### 커스텀 에이전트 (자동 생성)
- {custom_agent_1}
- {custom_agent_2}
- ...

### 감지된 도구
| 카테고리 | 도구 | 상태 |
|---------|------|------|
| 디컴파일러 | {decompiler_name} | ✅ 사용 가능 |
| 바이너리 분석 | {analyzer_name} | ✅ 사용 가능 |
| 패키지 관리 | {package_manager} | ✅ 사용 가능 |
| 코드 품질 | {linter_name} | ✅ 사용 가능 |

### 도구 에이전트 (자동 생성)
- {tool_agent_1} (Sync/Async)
- {tool_agent_2} (Sync/Async)
- ...

### 다음 단계
/orchestrate {요청} 명령으로 작업을 시작할 수 있습니다.

**도구 에이전트 사용 예시**:
- 동기: "ILSpy로 GameAssembly.dll의 PlayerController 클래스 디컴파일해줘"
- 비동기: "Managed 폴더의 모든 DLL을 ILSpy로 디컴파일해줘" (백그라운드 실행)
```

---

## 에이전트 프로젝트 특화 지시 예시

### Unity/BepInEx 프로젝트
```markdown
### 프로젝트 특화 지시
- Harmony 패치 작성 시 HarmonyPatch 어트리뷰트 사용
- Decompiled/ 폴더에서 원본 메서드 시그니처 확인 필수
- BepInEx 로거 사용: Logger.LogInfo(), Logger.LogWarning()
- 게임 업데이트 시 패치 충돌 가능성 항상 고려
```

### Node.js/TypeScript 프로젝트
```markdown
### 프로젝트 특화 지시
- TypeScript 타입 정의 필수
- ESLint 규칙 준수
- 비동기 함수는 async/await 사용
- 테스트는 Jest 프레임워크 사용
```

### Python 프로젝트
```markdown
### 프로젝트 특화 지시
- PEP 8 스타일 가이드 준수
- Type hints 사용 권장
- 가상환경 내에서 패키지 설치
- pytest로 테스트 작성
```

---

## 참고

- 이 명령어는 프로젝트 루트에서 실행해야 합니다
- 서브모듈 방식을 권장합니다 (업데이트 용이)
- 기존 설정이 있으면 --force 옵션이 필요합니다
- 프로젝트 분석은 자동이지만, 수동 수정도 가능합니다
