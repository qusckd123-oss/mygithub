# 세션 3: 에이전트 팀 병렬 실행 (tmux)

> **소요시간**: 30분 (설명 10분 + 데모 10분 + 실습 10분)
> **대상**: Claude Code 사용자
> **목표**: tmux 기반 멀티 에이전트를 실행하고, 프리셋·커스텀 팀 구성을 실습

---

## 1. 에이전트 팀이란?

### 문제
- FPOF에는 6개 에이전시, 20+명의 에이전트가 있음
- 시즌 기획처럼 큰 작업은 여러 에이전트가 **병렬로** 작업해야 효율적
- 하나의 Claude Code 세션에서는 **한 번에 하나**만 작업 가능

### 해결: tmux 멀티 세션
- **tmux** 터미널 멀티플렉서를 사용해 여러 Claude Code 세션을 동시 실행
- 화면 분할로 각 에이전트의 진행 상황을 **실시간 모니터링**
- 결과물은 자동으로 파일에 저장

### 아키텍처

```
터미널 (tmux 세션: fpof-team)
┌──────────────────┬──────────────────┐
│  시장-리서처       │  브랜드-전략가      │
│  claude -p "..."  │  claude -p "..."  │
│  → trend-brief.md │  → strategy.md    │
├──────────────────┼──────────────────┤
│  수석-MD          │  컬렉션-플래너      │
│  claude -p "..."  │  claude -p "..."  │
│  → md-plan.md     │  → line-sheet.md  │
└──────────────────┴──────────────────┘
                    ↓
        workspace/team-results/YYYYMMDD-HHMMSS/
        ├── 시장-리서처.md
        ├── 브랜드-전략가.md
        ├── 수석-MD.md
        └── 컬렉션-플래너.md
```

---

## 2. 사전 준비

### tmux 설치 확인

```bash
# tmux 버전 확인
tmux -V
# tmux 3.x 이상 권장

# 없으면 설치
brew install tmux
```

### Claude Code CLI 확인

```bash
claude --version
# Claude Code 사용 가능해야 함
```

---

## 3. 기본 사용법

### 3.1 프리셋 목록 확인

```bash
cd "/Users/sherman/07. FPOF V2.2 Claude"
./system/scripts/team-tmux.sh list
```

**출력:**
```
사용 가능한 프리셋:

  season-plan      — 시즌 전략 수립 (리서처·전략가·MD·플래너)
  design-sprint    — 디자인 스프린트 (무드보드·디자인스펙·비주얼·원가)
  marketing-blitz  — 마케팅 블리츠 (IMC·카피·비주얼·소셜)
  data-review      — 데이터 리뷰 (매출분석·인사이트·코호트)
  quality-gate     — 품질 검수 (QG·갭분석·리포트)
```

### 3.2 프리셋 실행

```bash
# 시즌 전략 수립 팀 (4명)
./system/scripts/team-tmux.sh season-plan

# 디자인 스프린트 팀 (4명)
./system/scripts/team-tmux.sh design-sprint

# 마케팅 블리츠 팀 (4명)
./system/scripts/team-tmux.sh marketing-blitz

# 데이터 리뷰 팀 (3명)
./system/scripts/team-tmux.sh data-review

# 품질 검수 팀 (3명)
./system/scripts/team-tmux.sh quality-gate
```

### 3.3 실행 상태 확인

```bash
./system/scripts/team-tmux.sh status
```

**출력 예시:**
```
── FPOF Team Status ──
세션: fpof-team | 패인: 4개

  [시장-리서처] 트렌드 브리프 작성 중...
  [브랜드-전략가] 브랜드 전략 수립 중...
  [수석-MD] MD 플래닝 작성 중...
  [컬렉션-플래너] 라인시트 작성 중...

결과 디렉토리: workspace/team-results/20260325-143022/
완료된 결과: 2개
```

### 3.4 세션 종료

```bash
./system/scripts/team-tmux.sh kill
```

---

## 4. 프리셋 상세

### season-plan (시즌 전략 수립)

| 에이전트 | 역할 | 실행 스킬 |
|---------|------|----------|
| 시장-리서처 | 트렌드 분석 | `/brief trend-brief` |
| 브랜드-전략가 | 브랜드 전략 수립 | `/brief brand-strategy` |
| 수석-MD | MD 플래닝 | `/brief md-planning` |
| 컬렉션-플래너 | 라인시트 작성 | `/brief line-sheet` |

### design-sprint (디자인 스프린트)

| 에이전트 | 역할 | 실행 스킬 |
|---------|------|----------|
| 크리에이티브-디렉터 | 무드보드 | `/brief moodboard` |
| 패션-디자이너 | 디자인 스펙 | `/brief design-spec` |
| 아트-디렉터 | 비주얼 에셋 | 비주얼 생성 |
| 프로덕션-매니저 | 원가 분석 | `/brief costing-ve` |

### marketing-blitz (마케팅 블리츠)

| 에이전트 | 역할 | 실행 스킬 |
|---------|------|----------|
| 마케팅-디렉터 | IMC 전략 | `/brief imc-strategy` |
| 패션-에디터 | 상품 카피 | PDP 카피 작성 |
| 콘텐츠-디렉터 | 화보 기획 | 촬영 기획안 |
| 소셜-전략-디렉터 | 바이럴 전략 | 소셜 채널 전략 |

### data-review (데이터 리뷰)

| 에이전트 | 역할 | 실행 스킬 |
|---------|------|----------|
| 트렌드-애널리스트 | 매출 분석 | 채널·카테고리 실적 |
| 인사이트-아키텍트 | 인사이트 도출 | 히트/부진 원인 |
| 데이터-애널리스트 | 코호트 분석 | 리텐션·재구매 |

### quality-gate (품질 검수)

| 에이전트 | 역할 | 실행 스킬 |
|---------|------|----------|
| 품질-검증관 | QG 검수 | Quality Gate |
| 갭-디텍터 | 갭 분석 | 기획 vs 실행 비교 |
| 리포트-제너레이터 | 보고서 | 진행 상황 종합 |

---

## 5. 커스텀 팀 구성

프리셋 외에 자유롭게 팀을 구성할 수 있습니다.

```bash
./system/scripts/team-tmux.sh custom \
  "리서처:트렌드 분석해줘. 2026 SS 스트릿웨어 트렌드 중심으로." \
  "전략가:브랜드 전략 수립해줘. 와키윌리 글로벌 확장 방향." \
  "카피라이터:인스타그램용 캡션 10개 만들어줘. 여름 캠페인용."
```

**형식**: `"역할:프롬프트"` — 콜론(`:`)으로 역할명과 지시를 구분

### 커스텀 구성 팁
- 최대 **6개** 패인까지 지원
- 역할명은 한글/영문 모두 가능
- 프롬프트에 FPOF 슬래시 명령어 사용 가능 (`/brief`, `/review` 등)

---

## 6. tmux 기본 조작

### 세션 접속/이탈

| 동작 | 명령어 |
|------|--------|
| 세션 접속 | `tmux attach -t fpof-team` |
| 세션 이탈 (백그라운드 유지) | `Ctrl+B` → `D` |
| 세션 종료 | `./system/scripts/team-tmux.sh kill` |

### 패인 이동

| 동작 | 단축키 |
|------|--------|
| 다음 패인으로 이동 | `Ctrl+B` → `O` |
| 방향키로 이동 | `Ctrl+B` → `←↑↓→` |
| 패인 최대화/복원 | `Ctrl+B` → `Z` |

### 스크롤

| 동작 | 단축키 |
|------|--------|
| 스크롤 모드 진입 | `Ctrl+B` → `[` |
| 스크롤 이동 | `↑↓` 또는 `PgUp/PgDn` |
| 스크롤 모드 종료 | `Q` |

---

## 7. Claude Code 내에서 실행하기

Claude Code 세션 안에서 `!` 접두사로 실행할 수 있습니다:

```
! ./system/scripts/team-tmux-simple.sh season-plan
! ./system/scripts/team-tmux-simple.sh status
! ./system/scripts/team-tmux-simple.sh kill
```

> `team-tmux-simple.sh`는 `team-tmux.sh`의 간편 래퍼입니다.

---

## 8. 결과물 확인

모든 에이전트의 결과는 아래 경로에 자동 저장됩니다:

```
workspace/team-results/YYYYMMDD-HHMMSS/
├── 시장-리서처.md
├── 브랜드-전략가.md
├── 수석-MD.md
└── 컬렉션-플래너.md
```

각 파일은 해당 에이전트의 전체 출력(스트리밍)을 포함합니다.

---

## 9. 비용 최적화 규칙 (복습)

FPOF CLAUDE.md에 정의된 에이전트 팀 운영 규칙:

| 규칙 | 내용 |
|------|------|
| **모델 믹싱** | 리드 = Opus, 팀원 = Sonnet (비용 4~5배 절감) |
| **계획 승인** | 팀원은 구현 전 계획 작성 → 리드 승인 후 실행 |
| **최소 인원** | 3~5명 제한 (10명 이상은 조율 비용만 증가) |
| **즉시 종료** | 완료된 팀원은 즉시 종료 (유휴 세션 = 토큰 소모) |
| **팀 vs 서브에이전트** | 독립 작업이면 서브에이전트, 소통 필요하면 에이전트 팀 |

---

## 10. 실습 과제

### 과제 1: 프리셋 실행해 보기
```bash
# data-review 프리셋을 실행하고, 상태를 확인한 후, 종료하세요
./system/scripts/team-tmux.sh data-review
# (다른 터미널에서)
./system/scripts/team-tmux.sh status
./system/scripts/team-tmux.sh kill
```

### 과제 2: 커스텀 팀 구성해 보기
```bash
# 자유 주제로 2~3명의 커스텀 팀을 구성하여 실행하세요
./system/scripts/team-tmux.sh custom \
  "분석가:와키윌리 SNS 최근 트렌드 분석해줘" \
  "카피라이터:와키윌리 여름 캠페인 슬로건 5개 제안해줘"
```

---

## 참고 파일

| 파일 | 위치 |
|------|------|
| tmux 런처 (전체) | `system/scripts/team-tmux.sh` |
| tmux 런처 (간편) | `system/scripts/team-tmux-simple.sh` |
| 에이전트 팀 운영 규칙 | `CLAUDE.md` → "에이전트 팀 운영 규칙" 섹션 |
