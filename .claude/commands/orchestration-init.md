# /orchestration-init

프로젝트를 분석하여 오케스트레이션 시스템을 초기화합니다. Hooks와 Skills를 활용하여 효율적으로 설정합니다.

## 옵션
- `--force`: 기존 설정 무시하고 재초기화

## 실행 프로세스 개요

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: [--] 서브모듈 확인 및 사전 조건 검사                │
│ Step 2: [Python] copy-files.py로 파일 복사                  │
│ Step 3: [Haiku] 웹검색으로 프로젝트 타입별 필요 도구 파악   │
│ Step 4: [Python] check-tools.py로 설치 여부 확인            │
│ Step 5: [Sonnet] 프로젝트 분석 → 필요한 에이전트/Skills 판단│
│ Step 6: [Opus] 판단 결과 기반 Skills/에이전트 구현          │
│ Step 7: [Opus] 에이전트 + Skills 프로젝트 특화 설정 추가    │
│ Step 8: [Haiku] config.json 생성 (최종 정리)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: 서브모듈 확인 및 사전 조건 검사

### 1.1 서브모듈 존재 확인

`.claude-orchestration/` 폴더 존재 확인:

**존재하는 경우**: Step 2로 진행

**존재하지 않는 경우**:
```
오케스트레이션 서브모듈이 없습니다.

다음 명령을 실행하여 서브모듈을 추가하세요:
  git submodule add https://github.com/Zeliper/z-coder.git .claude-orchestration
  git submodule update --init
```
- 종료

### 1.2 기존 설정 확인

`.claude/config.json` 존재 확인:

**존재하고 `--force` 없음**:
- 경고: "기존 config.json이 있습니다. --force 옵션으로 재초기화하세요."
- 종료

**존재하고 `--force` 있음**:
- 기존 config.json 백업: `config.json.backup.{timestamp}`
- Step 2로 진행

**존재하지 않음**: Step 2로 진행

---

## Step 2: 파일 복사 [Python]

**copy-files.py 스크립트 실행**

```bash
python .claude-orchestration/.claude/hooks/copy-files.py
```

### 복사되는 항목
- `.claude/agents/` - 에이전트 파일들
- `.claude/commands/` - 커맨드 파일들
- `.claude/templates/` - 템플릿 파일들
- `.claude/hooks/` - Hook 스크립트들
- `.claude/skills/` - Skills 파일들
- `.claude/settings.json` - Hook 설정 (없을 때만)
- `.claude/LESSONS_LEARNED.md` - 학습 기록 (없을 때만)
- `tasks/` 및 `tasks/archive/` 디렉토리

### 주의사항
- 기존 파일은 덮어쓰지 않음
- LESSONS_LEARNED.md는 항상 보존

---

## Step 3: 도구 탐색 [Haiku 웹검색]

**Model: Haiku (web-search-agent 역할)**

프로젝트 파일 감지 후, 해당 프로젝트 타입에 필요한 외부 도구를 웹검색으로 조회합니다.

### 3.1 프로젝트 타입 감지

| 파일 | 프로젝트 타입 |
|------|-------------|
| package.json | Node.js/JavaScript/TypeScript |
| *.csproj, *.sln | C#/.NET |
| requirements.txt, pyproject.toml | Python |
| Cargo.toml | Rust |
| go.mod | Go |
| pom.xml, build.gradle | Java |
| Assets/, ProjectSettings/ | Unity |
| BepInEx 참조, Harmony 의존성 | 게임 모딩 |

### 3.2 웹검색 수행

감지된 프로젝트 타입에 따라 검색:

```
검색 쿼리 예시:
- "{프로젝트타입} 개발에 필요한 CLI 도구 목록"
- "{프로젝트타입} 디컴파일러/분석 도구"
- "{프로젝트타입} 빌드 도구 및 패키지 관리자"
```

### 3.3 출력

조회된 도구 목록을 JSON 형태로 반환:

```json
{
  "project_type": "unity-bepinex",
  "recommended_tools": [
    {"name": "ilspycmd", "purpose": ".NET 디컴파일"},
    {"name": "dotnet", "purpose": ".NET CLI"},
    {"name": "dnSpy", "purpose": ".NET 디버깅/디컴파일"}
  ]
}
```

---

## Step 4: 도구 설치 확인 [Python Hook]

**check-tools.py 스크립트 실행**

Step 3에서 얻은 도구 목록과 프로젝트 타입 기반으로 설치 여부 확인:

```bash
python .claude/hooks/check-tools.py
```

또는 특정 도구 목록 전달 (크로스 플랫폼):

```bash
python .claude/hooks/check-tools.py --tools ilspycmd,dotnet,npm
```

### 출력 형식

```json
{
  "project_root": "/path/to/project",
  "tools": {
    "ilspycmd": {
      "name": "ilspycmd",
      "available": true,
      "version": "ILSpy version 8.0.0.0",
      "path": "/usr/local/bin/ilspycmd"
    },
    "dotnet": {
      "name": "dotnet",
      "available": true,
      "version": "8.0.100",
      "path": "/usr/bin/dotnet"
    }
  },
  "available": ["ilspycmd", "dotnet"],
  "missing": []
}
```

---

## Step 5: 프로젝트 분석 및 판단 [Sonnet]

**Model: Sonnet (분석 및 의사결정)**

### 5.1 프로젝트 구조 분석

프로젝트 루트를 스캔하여 수집:

- 언어/프레임워크 구성
- 소스 코드 디렉토리 구조
- 빌드/테스트 설정
- 특수 폴더 (Decompiled/, Assets/ 등)

### 5.2 필요 항목 판단

다음을 JSON 형태로 결정:

```json
{
  "analysis_result": {
    "project_name": "my-project",
    "project_type": "unity-bepinex",
    "languages": ["C#"],
    "frameworks": ["Unity", "BepInEx", "Harmony"]
  },
  "decisions": {
    "custom_agents": [
      {
        "name": "decompiled-search-agent",
        "purpose": "디컴파일된 게임 코드 탐색",
        "search_paths": ["Decompiled/", "Managed/"]
      }
    ],
    "required_skills": [
      {
        "name": "ilspy",
        "purpose": ".NET DLL 디컴파일",
        "tool": "ilspycmd"
      },
      {
        "name": "harmony-patching",
        "purpose": "Harmony 패치 작성 가이드"
      }
    ],
    "build_command": "dotnet build",
    "test_command": "dotnet test"
  }
}
```

### 5.3 판단 기준

#### 커스텀 에이전트 필요 조건
| 조건 | 생성할 에이전트 |
|------|----------------|
| Decompiled/, Managed/ 폴더 존재 | decompiled-search-agent |
| Assets/ 폴더 (Unity) | unity-asset-agent |
| migrations/ 폴더 | db-schema-agent |

#### Skills 필요 조건
| 조건 | 생성할 Skill |
|------|-------------|
| ilspycmd 설치됨 | ilspy Skill |
| npm/yarn 설치됨 | npm Skill |
| BepInEx 프로젝트 | harmony-patching Skill |

---

## Step 6: Skills/에이전트 구현 [Opus]

**Model: Opus (구현)**

Step 5의 판단 결과를 기반으로 실제 파일 생성:

### 6.1 외부 도구 Skills 생성

`.claude/skills/{tool-name}/SKILL.md` 형식으로 생성:

```yaml
---
name: {tool-name}
description: {도구 설명}
allowed-tools: Bash, Read, Glob
---

# {Tool Name} Skill

## 요구사항
{설치 방법}

## 사용법
{주요 명령어와 예시}

## 예시
{구체적인 사용 시나리오}

---
<!-- SKILL-PROJECT-CONFIG-START -->
<!-- 프로젝트 특화 설정이 /orchestration-init에 의해 이 위치에 추가됩니다 -->
<!-- SKILL-PROJECT-CONFIG-END -->
```

### 6.2 커스텀 에이전트 생성

`.claude/agents/{agent-name}.md` 형식으로 생성합니다.

#### 필수 YAML Frontmatter

에이전트 파일은 **반드시 YAML frontmatter**를 포함해야 합니다:

| 필드 | 필수 | 설명 | 예시 |
|------|------|------|------|
| `name` | ✅ | 에이전트 식별자 (파일명과 동일) | `decompiled-search-agent` |
| `description` | ✅ | 에이전트의 역할 설명 | `디컴파일된 게임 코드 탐색` |
| `model` | ✅ | 사용할 Claude 모델 | `sonnet`, `opus`, `haiku`, `inherit` |

#### 에이전트 파일 형식

```markdown
---
name: {agent-name}
description: {에이전트 설명}
model: {sonnet | opus | haiku | inherit}
---

# {agent-name}

## 역할
{role_description}

## 프로젝트 컨텍스트
- 프로젝트: {project_name}
- 기술스택: {tech_stack}

## 탐색 경로
{search_paths}

## 입력
- 사용자 요청 요약
- 탐색 키워드

## 출력
**최대 500자 이내 요약**으로 반환

---

<!-- ORCHESTRATION-PROJECT-CONFIG-START -->
<!-- 프로젝트 특화 설정이 여기에 추가됩니다 -->
<!-- ORCHESTRATION-PROJECT-CONFIG-END -->
```

---

## Step 7: 프로젝트 특화 설정 추가 [Opus]

**Model: Opus (프로젝트 맞춤화)**

### 7.1 코어 에이전트 프로젝트 특화

각 코어 에이전트의 `<!-- ORCHESTRATION-PROJECT-CONFIG-START -->` 마커 내에 프로젝트 특화 내용 추가:

**대상 에이전트:**
- main-agent.md
- coder-agent.md
- builder-agent.md
- codebase-search-agent.md
- reference-agent.md
- web-search-agent.md
- todo-list-agent.md

**추가 내용:**
```markdown
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

### 7.2 Skills 프로젝트 특화

각 Skill의 `<!-- SKILL-PROJECT-CONFIG-START -->` 마커 내에 프로젝트 특화 내용 추가:

**추가 내용:**
```markdown
<!-- SKILL-PROJECT-CONFIG-START -->
## 프로젝트 특화 설정

### 이 프로젝트에서의 사용
- 주요 대상 파일: {target_files}
- 출력 경로: {output_path}

### 프로젝트별 명령어
{project_specific_commands}
<!-- SKILL-PROJECT-CONFIG-END -->
```

### 7.3 프로젝트 타입별 특화 예시

#### Unity/BepInEx 프로젝트
```markdown
### 프로젝트 특화 지시
- Harmony 패치 작성 시 HarmonyPatch 어트리뷰트 사용
- Decompiled/ 폴더에서 원본 메서드 시그니처 확인 필수
- BepInEx 로거 사용: Logger.LogInfo(), Logger.LogWarning()
- 게임 업데이트 시 패치 충돌 가능성 항상 고려
```

#### Node.js/TypeScript 프로젝트
```markdown
### 프로젝트 특화 지시
- TypeScript 타입 정의 필수
- ESLint 규칙 준수
- 비동기 함수는 async/await 사용
- 테스트는 Jest 프레임워크 사용
```

#### Python 프로젝트
```markdown
### 프로젝트 특화 지시
- PEP 8 스타일 가이드 준수
- Type hints 사용 권장
- 가상환경 내에서 패키지 설치
- pytest로 테스트 작성
```

---

## Step 8: config.json 생성 [Haiku]

**Model: Haiku (정리 및 요약)**

모든 분석 결과를 종합하여 config.json 생성:

```json
{
  "orchestration": {
    "version": "{VERSION 파일 내용}",
    "installed_at": "{현재 시간 ISO 형식}",
    "updated_at": "{현재 시간 ISO 형식}",
    "submodule_path": ".claude-orchestration"
  },
  "project": {
    "name": "{프로젝트명}",
    "description": "{설명}",
    "type": "{프로젝트 타입}",
    "languages": ["{언어들}"],
    "frameworks": ["{프레임워크들}"]
  },
  "paths": {
    "source": ["{소스 경로}"],
    "search": ["./"],
    "excluded": ["node_modules", "bin", "obj", ".git", "dist", "build"],
    "decompiled": ["{Decompiled 경로}"],
    "tests": ["{테스트 경로}"]
  },
  "commands": {
    "build": "{빌드 명령어}",
    "test": "{테스트 명령어}",
    "lint": "{lint 명령어}"
  },
  "agent_models": {
    "main-agent": "sonnet",
    "decision-agent": "opus",
    "coder-agent": "opus",
    "builder-agent": "sonnet",
    "orchestration-update-agent": "sonnet",
    "markdown-writer-agent": "haiku",
    "task-manager-agent": "sonnet",
    "test-case-agent": "sonnet",
    "commit-agent": "sonnet",
    "codebase-search-agent": "haiku",
    "todo-list-agent": "sonnet",
    "reference-agent": "haiku",
    "web-search-agent": "haiku"
  },
  "installed_tools": [
    {
      "name": "ilspycmd",
      "path": "{경로}",
      "version": "{버전}",
      "available": true
    }
  ],
  "enabled_skills": [
    "ilspy",
    "npm"
  ],
  "custom_agents": [
    "decompiled-search-agent"
  ]
}
```

---

## 결과 보고

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
- .claude/settings.json

### 코어 에이전트 (프로젝트 특화 적용)
| 에이전트 | 모델 | 역할 |
|---------|------|------|
| main-agent | Sonnet | 오케스트레이션 조율 |
| decision-agent | Opus | 고수준 판단 (Plan Mode, 아키텍처) |
| coder-agent | Opus | 코드 구현 |
| builder-agent | Sonnet | 빌드/테스트 실행 |
| orchestration-update-agent | Sonnet | 시스템 업데이트 |
| markdown-writer-agent | Haiku | 비정형 마크다운 생성 |
| task-manager-agent | Sonnet | 태스크 파일 관리 |
| test-case-agent | Sonnet | 테스트 케이스 생성 |
| commit-agent | Sonnet | 커밋 생성 |
| codebase-search-agent | Haiku | 코드베이스 탐색 |
| todo-list-agent | Sonnet | 할일 목록 관리 |
| reference-agent | Haiku | 레퍼런스 조회 |
| web-search-agent | Haiku | 웹 검색 |

### 감지된 도구 및 Skills
| 도구 | 상태 | Skill 생성 |
|------|------|-----------|
| {tool_name} | ✅ 설치됨 | ✅ 생성됨 |
| {tool_name} | ❌ 미설치 | ❌ 스킵 |

### 커스텀 에이전트 (자동 생성)
- {custom_agent_1}
- {custom_agent_2}

### 다음 단계
/orchestrate {요청} 명령으로 작업을 시작할 수 있습니다.
```

---

## 참고

- 이 명령어는 프로젝트 루트에서 실행해야 합니다
- 서브모듈 방식을 권장합니다 (업데이트 용이)
- 기존 설정이 있으면 --force 옵션이 필요합니다
- 각 Step의 모델은 config.json의 agent_models로 오버라이드 가능
- Hooks는 Python으로 크로스플랫폼 지원 (Windows/Linux 호환)
- Python 호출은 `python` 명령어 사용 (python3 아님)
