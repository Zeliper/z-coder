# Claude Code 에이전트 오케스트레이션 시스템

## Part 1: Base System (Git Repository)

### 개요
어떤 프로젝트에서든 사용 가능한 범용 멀티 에이전트 오케스트레이션 시스템입니다.
Claude Code의 백그라운드 에이전트(Async Sub-agent) 기능을 활용하여 메인 에이전트가 서브 에이전트들을 병렬로 spawn하고 조율합니다.

### 설치 방법
````bash
# 방법 1: Git clone
git clone https://github.com/{your-repo}/claude-orchestration.git .claude-orchestration
cp -r .claude-orchestration/.claude ./.claude
cp -r .claude-orchestration/tasks ./tasks

# 방법 2: 직접 복사
# .claude/ 폴더와 tasks/ 폴더를 프로젝트 루트에 복사
````

### 초기 설정
````bash
# 프로젝트에 맞게 초기화 (필수)
/orchestration-init
````

### 기본 폴더 구조
````
.claude/
├── commands/
│   ├── orchestrate.md              # 메인 오케스트레이션 커맨드
│   └── orchestration-init.md       # 프로젝트 초기화 커맨드
├── agents/
│   ├── main-agent.md               # 메인 오케스트레이터 (범용)
│   ├── codebase-search-agent.md    # 코드베이스 탐색 (범용)
│   ├── todo-list-agent.md          # 작업 계획 수립 (범용)
│   ├── coder-agent.md              # 코드 작성 (범용)
│   ├── web-search-agent.md         # 웹 검색 (범용)
│   └── builder-agent.md            # 빌드 및 에러 분석 (범용)
├── templates/
│   └── custom-agent.template.md    # 커스텀 에이전트 생성 템플릿
├── LESSONS_LEARNED.md              # 빌드 에러 패턴 누적 (초기 빈 템플릿)
└── config.json                     # 프로젝트 설정 (/orchestration-init이 생성)

tasks/
├── archive/                        # 완료된 태스크
└── .gitkeep
````

---

## 코어 에이전트 정의 (범용)

### 1. main-agent
**역할**: 사용자 요청 수신, 서브 에이전트 spawn 및 조율, 워크플로우 제어

**범용 책임**:
- 사용자 요청 분석 및 작업 계획 수립
- config.json 참조하여 프로젝트 설정 및 커스텀 에이전트 목록 확인
- 서브 에이전트들을 Async 백그라운드로 spawn (모든 spawn은 main-agent만 수행)
- task 파일 상태 확인하여 중복 spawn 방지
- Step별 coder-agent → builder-agent 순차 실행
- 에러 발생 시 LESSONS_LEARNED.md 확인 후 재시도 지시
- 모든 Step 완료 시 마무리 처리

**중복 방지 로직**:
````
task 파일에 {agent_name}_result 섹션이 존재하면 해당 에이전트 spawn 하지 않음
````

### 2. codebase-search-agent
**역할**: 프로젝트 코드베이스에서 관련 코드, 구조, 패턴 탐색

**범용 동작**:
- config.json의 search_paths, excluded_paths 참조
- 관련 파일, 함수, 클래스, 의존성 파악
- 기존 코드 패턴 및 컨벤션 분석

**출력**: 500자 이내 요약

### 3. todo-list-agent
**역할**: 작업을 Step별로 분해하고 TODO 리스트 생성

**범용 동작**:
- 작업을 독립적인 Step으로 분해
- 각 Step의 작업 크기 추정 (S/M/L)
- ./tasks/TASK-{ID}.md 파일 생성

**출력**: task 파일 경로 및 Step 요약

### 4. coder-agent
**역할**: 지정된 Step의 코드 작성/수정

**범용 동작**:
- config.json의 code_conventions 참조
- LESSONS_LEARNED.md 참조하여 알려진 문제 회피
- 담당 Step 범위만 작업

**출력**: 100자 이내 결과 요약

### 5. web-search-agent
**역할**: 외부 정보 검색 및 요약

**범용 동작**:
- 라이브러리 문서, API 레퍼런스, 베스트 프랙티스 검색
- 검색 결과 핵심만 추출

**출력**: 300자 이내 요약 (출처 URL 포함)

### 6. builder-agent
**역할**: 빌드 실행, 에러 분석, 학습 내용 기록

**범용 동작**:
- config.json의 build_command, test_command 사용
- 에러 발생 시 LESSONS_LEARNED.md 업데이트
- task 파일에 빌드 결과 기록

**출력**: 빌드 결과 (성공/실패), 실패 시 에러 분석

---

## config.json 스키마 (범용)
````json
{
  "project": {
    "name": "",
    "description": "",
    "type": "",
    "languages": [],
    "frameworks": []
  },
  "paths": {
    "source": ["./src"],
    "search": ["./"],
    "excluded": ["node_modules", "bin", "obj", ".git", "dist", "build"],
    "decompiled": [],
    "assets": [],
    "tests": []
  },
  "commands": {
    "build": "",
    "test": "",
    "lint": "",
    "run": ""
  },
  "conventions": {
    "naming": "",
    "architecture": "",
    "notes": []
  },
  "custom_agents": []
}
````

---

## Part 2: /orchestration-init 커맨드

### 목적
프로젝트를 분석하여:
1. config.json 생성/업데이트
2. 프로젝트 특화 커스텀 에이전트 자동 생성
3. 기존 에이전트 프롬프트에 프로젝트 특화 정보 추가

### 분석 대상

| 분석 항목 | 확인 방법 |
|----------|----------|
| 언어/프레임워크 | package.json, *.csproj, requirements.txt, Cargo.toml, go.mod, pom.xml 등 |
| 빌드 시스템 | Makefile, build.gradle, webpack.config.js, tsconfig.json 등 |
| 프로젝트 구조 | 폴더 구조 패턴, 진입점 파일 |
| 테스트 프레임워크 | jest.config.js, pytest.ini, *Test.cs 등 |
| 특수 폴더 | Decompiled/, Managed/, Assets/, migrations/ 등 |

### 프로젝트 타입별 커스텀 에이전트 생성 규칙
````yaml
# 게임 모딩 (Unity/BepInEx/Harmony)
triggers:
  - "*.csproj with BepInEx reference"
  - "Harmony" in dependencies
  - "Decompiled/" or "Managed/" folder exists
agents:
  - name: decompiled-search-agent
    role: 원본 게임 코드 탐색, API 시그니처 확인
  - name: harmony-patch-agent
    role: 패치 타겟 메서드 탐색, 패치 충돌 검사

# Unity 프로젝트
triggers:
  - "Assets/" folder
  - "*.unity" files
  - "ProjectSettings/" folder
agents:
  - name: unity-asset-agent
    role: Asset, Prefab, ScriptableObject 구조 분석

# Node.js/TypeScript
triggers:
  - "package.json" exists
  - "tsconfig.json" exists
agents:
  - name: dependency-analyzer-agent
    role: npm 의존성 분석, 버전 충돌 검사

# Python
triggers:
  - "requirements.txt" or "pyproject.toml" exists
  - "setup.py" exists
agents:
  - name: python-env-agent
    role: 가상환경, 의존성, import 구조 분석

# Database 사용
triggers:
  - "migrations/" folder
  - "*.sql" files
  - ORM config files (prisma.schema, alembic.ini 등)
agents:
  - name: db-schema-agent
    role: 스키마 분석, 마이그레이션 계획

# API 서버
triggers:
  - "openapi.yaml" or "swagger.json"
  - Route/Controller 패턴 폴더
agents:
  - name: api-spec-agent
    role: 엔드포인트 분석, API 스펙 확인

# 테스트 존재
triggers:
  - "test/", "tests/", "__tests__/", "*Test.cs", "*_test.go"
agents:
  - name: test-analyzer-agent
    role: 테스트 커버리지 분석, 테스트 케이스 제안

# 다국어 지원
triggers:
  - "locales/", "i18n/", "translations/"
  - "*.po", "*.json" with locale patterns
agents:
  - name: i18n-agent
    role: 번역 키 관리, 누락된 번역 검색

# Docker/컨테이너
triggers:
  - "Dockerfile", "docker-compose.yml"
agents:
  - name: container-agent
    role: 컨테이너 설정 분석, 환경 변수 관리

# Infrastructure as Code
triggers:
  - "terraform/", "*.tf"
  - "cloudformation/", "*.yaml" with AWS patterns
agents:
  - name: infra-agent
    role: 인프라 설정 분석, 리소스 의존성 파악

# Monorepo
triggers:
  - "lerna.json", "pnpm-workspace.yaml"
  - Multiple package.json in subdirectories
agents:
  - name: monorepo-agent
    role: 패키지 간 의존성 분석, 영향 범위 파악
````

### 커스텀 에이전트 템플릿

`.claude/templates/custom-agent.template.md`:
````markdown
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
````

### /orchestration-init 실행 흐름
````
/orchestration-init 실행

1. 프로젝트 루트 스캔
   - 설정 파일 탐색 (package.json, *.csproj, requirements.txt 등)
   - 폴더 구조 분석
   - 기존 config.json 존재 여부 확인

2. 프로젝트 정보 추출
   - 언어/프레임워크 식별
   - 빌드/테스트 명령어 추출
   - 주요 경로 식별

3. config.json 생성 또는 업데이트
   - 신규: 전체 config.json 생성
   - 기존: 변경된 부분만 업데이트 (custom_agents 등)

4. 커스텀 에이전트 필요 여부 판단
   - 프로젝트 타입별 트리거 조건 확인
   - 필요한 커스텀 에이전트 목록 생성

5. 커스텀 에이전트 파일 생성
   - .claude/agents/{agent-name}.md 생성
   - config.json의 custom_agents 배열에 등록

6. 기존 에이전트 업데이트
   - main-agent.md: 프로젝트 컨텍스트 섹션 추가/업데이트
   - coder-agent.md: 코드 컨벤션, 프레임워크 특화 지시 추가
   - builder-agent.md: 빌드/테스트 명령어 업데이트

7. 결과 보고
   - 생성/업데이트된 파일 목록
   - 식별된 프로젝트 특성
   - 등록된 커스텀 에이전트 목록
````

### 에이전트 업데이트 규칙

기존 에이전트 파일에 프로젝트 특화 섹션을 추가합니다:
````markdown
# 기존 내용 유지
...

---
## 프로젝트 특화 설정 (자동 생성됨 - /orchestration-init)
<!-- DO NOT EDIT BELOW - Auto-generated by /orchestration-init -->

### 프로젝트 정보
- 이름: {project_name}
- 타입: {project_type}
- 기술스택: {tech_stack}

### 프로젝트 특화 지시
{project_specific_instructions}

### 참조 경로
{relevant_paths}

<!-- END AUTO-GENERATED -->
````

---

## 워크플로우

### Phase 1: 초기화 및 정보 수집
````
사용자 → /orchestrate {요청}

main-agent:
  1. config.json 읽기 (없으면 /orchestration-init 실행 안내)
  2. tasks/ 폴더에서 진행중인 task 파일 확인
  3. 새 태스크인 경우 **백그라운드로 동시에** spawn:
     - codebase-search-agent
     - web-search-agent (필요시)
     - {custom_agents from config.json} (해당하는 것만)
  4. 결과 수신 → todo-list-agent spawn → task 파일 생성
  5. 결과를 task 파일에 기록
````

### Phase 2: Step 실행 루프
````
main-agent:
  FOR each Step in task.steps:
    IF step.status == 'completed': CONTINUE
    
    1. coder-agent **백그라운드** spawn → Step 작업
    2. builder-agent **백그라운드** spawn → 빌드/테스트
    
    IF 빌드 실패:
      - LESSONS_LEARNED.md 업데이트
      - 재시도 (최대 3회)
      - 3회 실패 시 사용자 보고
    
    IF 빌드 성공:
      - step.status = 'completed'
      - 결과 기록
    
    Step 완료 보고
````

### Phase 3: 마무리
````
main-agent:
  1. todo-list-agent → 최종 결과 정리
  2. task 파일 → tasks/archive/ 이동
  3. 완료 보고
````

---

## 사용자 명령어

| 명령어 | 설명 |
|--------|------|
| /orchestration-init | 프로젝트 분석 및 오케스트레이션 시스템 초기화 |
| /orchestration-init --force | 기존 설정 무시하고 재초기화 |
| /orchestrate {요청} | 새 태스크 시작 |
| /orchestrate --task TASK-001 | 기존 태스크 이어서 진행 |
| /orchestrate --ref TASK-001 {요청} | 완료된 태스크 참조하여 수정/확장 |
| /status | 현재 태스크 상태 확인 |
| /tasks | 진행중/완료된 태스크 목록 |

---

## 백그라운드 에이전트 spawn 형식
````
"백그라운드에서 {에이전트명} 역할로 다음 작업을 수행해줘: {작업 내용}
.claude/agents/{에이전트명}.md 의 지시를 따르고,
작업 완료 후 결과만 요약해서 보고해줘."
````

---

## 생성 요청

### Base System 파일 (Git에 올릴 범용 파일)
1. `.claude/commands/orchestrate.md`
2. `.claude/commands/orchestration-init.md` - 프로젝트 분석 및 초기화 로직 포함
3. `.claude/agents/main-agent.md` (범용)
4. `.claude/agents/codebase-search-agent.md` (범용)
5. `.claude/agents/todo-list-agent.md` (범용)
6. `.claude/agents/coder-agent.md` (범용)
7. `.claude/agents/web-search-agent.md` (범용)
8. `.claude/agents/builder-agent.md` (범용)
9. `.claude/templates/custom-agent.template.md`
10. `.claude/LESSONS_LEARNED.md` (빈 템플릿)
11. `tasks/.gitkeep`
12. `tasks/archive/.gitkeep`
13. `README.md` - 설치 및 사용법

**중요**:
- 모든 에이전트 파일은 범용으로 작성 (프로젝트 특화 정보 없이)
- `/orchestration-init` 커맨드가 프로젝트 분석 후 특화 내용을 추가하는 구조
- 에이전트 파일에 `<!-- AUTO-GENERATED -->` 섹션 위치를 미리 마킹
- **파일 생성만 하고, 실제 작업은 수행하지 마세요**