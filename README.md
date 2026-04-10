# FPOF — 와키윌리 패션 하우스 시스템

> **Fashion PDCA Orchestration Framework v2.2**
>
> AI가 와키윌리(Wacky Willy) 브랜드의 시즌 기획부터 런칭까지를 함께 운영하는 패션 하우스 오케스트레이션 시스템입니다.
>
> 패션 실무자가 자연어로 지시하면, 브랜드 DNA와 전략을 완벽히 숙지한 AI 전문가가 실무 산출물을 만듭니다.

---

## 📋 목차

1. [시스템 개요](#-시스템-개요)
2. [V2.2 업데이트: PM-Skills 통합](#-v22-업데이트-pm-skills-통합)
3. [스킬 아키텍처](#-스킬-아키텍처)
4. [사용법](#-사용법)
5. [PDCA 워크플로우](#-pdca-워크플로우)
6. [스킬 전체 목록](#-스킬-전체-목록)
7. [명령어 가이드](#-명령어-가이드)
8. [폴더 구조](#-폴더-구조)

---

## 🎯 시스템 개요

### 핵심 개념

FPOF는 **3계층 스킬 아키텍처**로 구성된 패션 하우스 시스템입니다.

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: FPOF Main Skills (skills/)                        │
│  ─────────────────────────────────────────────────────────  │
│  21개 패션 실무 전용 스킬 (와키윌리 브랜드 DNA 내장)         │
│  + 65개 PM 프레임워크 스킬 (Paweł Huryn PM-Skills 통합)      │
│  총 86개 스킬 / 8개 카테고리                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Claude Universal Skills (.claude/skills/)          │
│  ─────────────────────────────────────────────────────────  │
│  19개 범용 유틸리티 스킬                                      │
│  모든 프로젝트에서 사용 가능                                  │
│  문서 생성/디자인/개발 도구                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Adapters & Bridges (skills-universal/)             │
│  ─────────────────────────────────────────────────────────  │
│  어댑터: 브랜드/모델 맞춤화                                   │
│  브릿지: FPOF ↔ 유니버설 스킬 연계                           │
└─────────────────────────────────────────────────────────────┘
```

### 주요 특징

| 특징 | 설명 |
|------|------|
| **브랜드 중심** | 와키윌리 브랜드 DNA(Kitsch Street & IP Universe)가 모든 스킬에 내장 |
| **PDCA 워크플로우** | Plan → Design → Do → Check → Act 자동화 |
| **품질 게이트** | 각 단계 완료 시 자동 검수(QG1~QG4) |
| **자연어 라우팅** | 의도 기반 에이전시/역할/스킬 자동 매핑 |
| **65개 PM 프레임워크** | Paweł Huryn PM-Skills 와키윌리 컨텍스트로 통합 |
| **40+ 슬래시 명령어** | 자주 쓰는 작업 단축 실행 |
| **상태 관리** | `.fpof-state.json`으로 실시간 진행 상황 추적 |

### 브랜드 정보

| 항목 | 내용 |
|------|------|
| **브랜드명** | 와키윌리 (Wacky Willy) |
| **컨셉** | Kitsch Street & IP Universe |
| **코어 타겟** | 18~25세 자유로운 트렌드리더 |
| **뮤즈** | 지젤 |
| **비전** | 2029 NO.1 K-Lifestyle Brand |
| **슬로건** | 규칙은 없어, 우리만의 놀이터로 초대할게! |

---

## 🆕 V2.2 업데이트: PM-Skills 통합

V2.2에서 **Paweł Huryn의 PM-Skills (MIT License)** 65개 프레임워크가 FPOF에 통합되었습니다.

### 기존 스킬 보강 (중복 합체)

| FPOF 스킬 | 통합된 PM 프레임워크 |
|-----------|-------------------|
| `trend-research` | 5대 경쟁사 프로파일링, TAM/SAM/SOM 시장 규모 추정 |
| `brand-strategy` | SWOT 크로스 분석(S×O/W×T), 포지셔닝 아이디어 |
| `md-planning` | RICE/ICE/Kano/Opportunity Score 우선순위 프레임워크 |
| `imc-strategy` | GTM 전략, 7가지 GTM 모션, 마케팅 아이디어 |
| `copywriting` | 밸류 프로포지션 스테이트먼트 (마케팅/세일즈/온보딩) |
| `social-viral` | 5가지 그로스 루프 (Viral/Usage/Collaboration/UGC/Referral) |
| `costing-ve` | 가격 포지셔닝 전략, 경쟁 벤치마크, 가격 실험 |
| `sales-analysis` | North Star Metric + Input/Health/Counter Metrics 대시보드 |
| `insight-archiving` | 감성 분석 (세그먼트별 감성 스코어, 테마 클러스터링) |
| `quality-gate` | Pre-Mortem (Tigers/Paper Tigers/Elephants, Go/No-Go) |

### 신규 스킬 카테고리 (65개)

| 폴더 | 스킬 수 | 대표 스킬 |
|------|---------|----------|
| `skills/pm-strategy/` | 10개 | PESTLE, Porter's 5 Forces, Ansoff, BMC, Lean Canvas, Value Proposition |
| `skills/pm-research/` | 4개 | Customer Journey Map, Market Segments, User Personas, Segmentation |
| `skills/pm-gtm/` | 3개 | Beachhead Segment, Competitive Battlecard, ICP |
| `skills/pm-discovery/` | 12개 | OST, Brainstorm Ideas/Experiments, Assumptions, Interview, Prioritize |
| `skills/pm-execution/` | 13개 | OKRs, PRD, Roadmap, Stakeholder Map, Sprint, Retro, User Stories |
| `skills/pm-analytics/` | 3개 | A/B Test, Cohort Analysis, SQL Queries |
| `skills/pm-marketing/` | 1개 | Product Name |
| `skills/pm-toolkit/` | 4개 | Grammar Check, NDA, Privacy Policy, Resume Review |

---

## 🏗️ 스킬 아키텍처

### Layer 1: FPOF Main Skills + PM-Skills

#### 패션 실무 스킬 (21개) — `skills/strategy|creative|product|marketing|data|quality/`

| 에이전시 | 스킬 | PDCA 단계 |
|----------|------|----------|
| **전략기획실** | trend-research, brand-strategy, md-planning, line-sheet | Plan |
| **크리에이티브 스튜디오** | moodboard, design-spec, visual-generation | Design |
| **프로덕트 랩** | techpack, costing-ve, qr-process | Design/Do |
| **마케팅 쇼룸** | imc-strategy, visual-content, copywriting, social-viral | Do |
| **데이터 인텔리전스** | sales-analysis, insight-archiving | Check |
| **QC 본부** | quality-gate, gap-analysis, completion-report, pdca-iteration | All |

#### PM 전략 스킬 (10개) — `skills/pm-strategy/`

| 스킬 | 설명 |
|------|------|
| `pestle-analysis` | 거시 환경 분석 (Political/Economic/Social/Tech/Legal/Environmental) |
| `porters-five-forces` | 산업 경쟁 구조 분석 |
| `ansoff-matrix` | 성장 방향 전략 (시장/제품 확장) |
| `business-model-canvas` | 9블록 비즈니스 모델 설계 |
| `lean-canvas` | 린 스타트업 캔버스 (빠른 가설 수립) |
| `value-proposition` | JTBD 기반 밸류 프로포지션 설계 |
| `product-strategy-canvas` | 9섹션 프로덕트 전략 캔버스 |
| `product-vision` | 브랜드 비전 한 문장 정의 |
| `monetization-strategy` | 수익 모델 다양화 전략 |
| `startup-canvas` | 스타트업 캔버스 (린 캔버스 변형) |

#### PM 리서치 스킬 (4개) — `skills/pm-research/`

| 스킬 | 설명 |
|------|------|
| `customer-journey-map` | 고객 구매 여정 시각화 |
| `market-segments` | 시장 세그먼트 분석 |
| `user-personas` | 데이터 기반 사용자 페르소나 정의 |
| `user-segmentation` | 고객 그룹 세분화 |

#### PM GTM 스킬 (3개) — `skills/pm-gtm/`

| 스킬 | 설명 |
|------|------|
| `beachhead-segment` | 글로벌 첫 진입 시장 선택 |
| `competitive-battlecard` | 경쟁사 비교 배틀카드 |
| `ideal-customer-profile` | ICP(이상적 고객 프로파일) 정의 |

#### PM 디스커버리 스킬 (12개) — `skills/pm-discovery/`

| 스킬 | 설명 |
|------|------|
| `opportunity-solution-tree` | 기회-솔루션 트리 구조화 |
| `brainstorm-ideas-new` | 신규 아이디어 브레인스토밍 |
| `brainstorm-ideas-existing` | 기존 상품 개선 아이디어 |
| `brainstorm-experiments-new` | 신규 실험 설계 |
| `brainstorm-experiments-existing` | 기존 실험 개선 설계 |
| `identify-assumptions-new` | 신규 가설 도출 |
| `identify-assumptions-existing` | 기존 가설 재검토 |
| `prioritize-assumptions` | 가설 우선순위 결정 |
| `prioritize-features` | 피처 우선순위 결정 (RICE/ICE/Kano) |
| `analyze-feature-requests` | 고객 피처 요청 분석 |
| `interview-script` | 고객 인터뷰 스크립트 작성 |
| `summarize-interview` | 인터뷰 결과 요약 |

#### PM 실행 스킬 (13개) — `skills/pm-execution/`

| 스킬 | 설명 |
|------|------|
| `brainstorm-okrs` | OKR 수립 브레인스토밍 |
| `create-prd` | PRD(제품 요구사항 문서) 작성 |
| `user-stories` | 유저 스토리 작성 |
| `job-stories` | 잡 스토리 작성 |
| `outcome-roadmap` | 아웃컴 중심 로드맵 변환 |
| `stakeholder-map` | 이해관계자 맵 작성 |
| `sprint-plan` | 스프린트 계획 수립 |
| `retro` | 스프린트/시즌 회고 |
| `summarize-meeting` | 회의록 정리 |
| `release-notes` | 릴리즈 노트 작성 |
| `test-scenarios` | QA 테스트 시나리오 작성 |
| `dummy-dataset` | 테스트 더미 데이터 생성 |
| `wwas` | What Went / Will / Action Summary |

#### PM 애널리틱스 스킬 (3개) — `skills/pm-analytics/`

| 스킬 | 설명 |
|------|------|
| `ab-test-analysis` | A/B 테스트 결과 분석 |
| `cohort-analysis` | 코호트 분석 (리텐션/이탈 패턴) |
| `sql-queries` | 데이터 쿼리 SQL 작성 |

#### PM 마케팅 스킬 (1개) — `skills/pm-marketing/`

| 스킬 | 설명 |
|------|------|
| `product-name` | 상품/브랜드 네이밍 |

#### PM 툴킷 스킬 (4개) — `skills/pm-toolkit/`

| 스킬 | 설명 |
|------|------|
| `grammar-check` | 문법 & 흐름 교정 |
| `draft-nda` | NDA(비밀유지계약서) 작성 |
| `privacy-policy` | 개인정보처리방침 작성 |
| `review-resume` | 이력서 검토 |

---

### Layer 2: Claude Universal Skills (19개)

**위치**: `.claude/skills/` 폴더 | **목적**: 범용 유틸리티 스킬

#### 문서 생성 (7개)

| 스킬 | 설명 |
|------|------|
| **pptx** | PowerPoint 슬라이드 덱 생성/편집 |
| **docx** | Word 문서 생성/편집 |
| **xlsx** | Excel 스프레드시트 생성/편집 |
| **pdf** | PDF 처리/추출/변환/병합 |
| **doc-coauthoring** | 문서 공동 작성 워크플로우 |
| **executive-summary** | 임원 보고용 요약 보고서 |
| **internal-comms** | 내부 공지/뉴스레터/상태 보고 |

#### 비주얼 & 디자인 (5개)

| 스킬 | 설명 |
|------|------|
| **theme-factory** | 10개 프리셋 테마 적용 |
| **canvas-design** | PNG/PDF 포스터·아트 생성 |
| **algorithmic-art** | p5.js 제너러티브 아트 |
| **slack-gif-creator** | Slack용 애니메이션 GIF |
| **brand-guidelines** | Anthropic/와키윌리 브랜드 스타일 |

#### 웹 & 프론트엔드 (3개)

| 스킬 | 설명 |
|------|------|
| **frontend-design** | 웹 UI/컴포넌트/대시보드 |
| **web-artifacts-builder** | 멀티페이지 React 웹앱 |
| **webapp-testing** | Playwright 웹앱 테스트 자동화 |

#### 지식 구조화 & 개발 (4개)

| 스킬 | 설명 |
|------|------|
| **json-canvas** | Obsidian 캔버스/마인드맵 생성 |
| **mcp-builder** | MCP 서버 개발 가이드 |
| **skill-creator** | 신규 스킬 설계/개선 |
| **claude-api** | Claude API/Agent SDK |

---

## 🚀 사용법

### 자연어 요청

FPOF는 의도를 파악하여 자동으로 적합한 스킬로 라우팅합니다.

```
"26SS 트렌드 분석해줘"         → trend-research
"무드보드 만들어줘"             → moodboard
"세상이 어떻게 변하고 있어?"    → pestle-analysis
"아이디어 좀 내봐"              → brainstorm-ideas-new
"OKR 짜줘"                     → brainstorm-okrs
"고객 여정 그려줘"              → customer-journey-map
```

### 슬래시 명령어

자주 사용하는 작업은 슬래시 명령어로 빠르게 실행합니다.

```
/status          # 현재 상태 확인
/brief trend     # 트렌드 브리프 생성
/market-scan     # 거시환경 종합 분석
/discover        # 프로덕트 디스커버리 사이클
/okrs            # OKR 수립
/launch          # GTM 런칭 전략
```

---

## 🔄 PDCA 워크플로우

```
Plan (기획)
  ↓  trend-research → brand-strategy → md-planning → line-sheet
  ↓  Quality Gate 1 (QG1)
Design (디자인)
  ↓  moodboard → design-spec → costing-ve → visual-generation
  ↓  Quality Gate 2 (QG2)
Do (실행)
  ↓  techpack → imc-strategy → visual-content → copywriting → social-viral
  ↓  Quality Gate 3 (QG3)
Check (분석)
  ↓  sales-analysis → insight-archiving → gap-analysis → completion-report
  ↓  Quality Gate 4 (QG4)
Act (개선)
  ↓  pdca-iteration (Match Rate < 90% 시 자동 루프)
```

### 품질 게이트 (QG)

| 게이트 | 기준 | 통과 조건 |
|-------|------|----------|
| **QG1** | Plan → Design | 트렌드 브리프, 브랜드 전략, MD 전략, 라인시트, 경영목표 정합성 |
| **QG2** | Design → Do | 무드보드, 디자인 스펙, 원가 검증, 비주얼 에셋 |
| **QG3** | Do → Check | 테크팩, 캠페인 브리프, 콘텐츠 기획서, 카피 데크, 런칭 시퀀스 |
| **QG4** | Check → Next Cycle | Match Rate ≥ 90% → COMPLETE / < 90% → Act |

---

## 📚 스킬 전체 목록

### 자연어 → 스킬 라우팅 가이드

#### 시즌 기획 & 전략

| 이렇게 말하면 | 스킬 |
|-------------|------|
| "요즘 뭐가 유행이야?", "트렌드 좀 봐줘" | `trend-research` |
| "시즌 테마 잡아줘", "브랜드 방향" | `brand-strategy` |
| "SKU 어떻게 짜?", "카테고리 믹스" | `md-planning` |
| "라인시트 만들어줘" | `line-sheet` |
| "세상이 어떻게 변해?", "외부 환경 봐줘" | `pestle-analysis` |
| "업계 경쟁 상황이 어때?" | `porters-five-forces` |
| "어디로 성장해야 해?" | `ansoff-matrix` |
| "사업 모델 정리해줘" | `business-model-canvas` |
| "MVP 모델 그려줘" | `lean-canvas` |
| "고객한테 어떤 가치를 줘?" | `value-proposition` |
| "전략 한 장으로 정리" | `product-strategy-canvas` |
| "브랜드 비전 한 문장으로" | `product-vision` |

#### 경쟁 & GTM

| 이렇게 말하면 | 스킬 |
|-------------|------|
| "경쟁사 비교표 만들어줘" | `competitive-battlecard` |
| "글로벌 첫 시장은 어디?" | `beachhead-segment` |
| "핵심 고객 정의해줘" | `ideal-customer-profile` |

#### 아이디어 & 검증

| 이렇게 말하면 | 스킬 |
|-------------|------|
| "고객 기회 구조화해보자" | `opportunity-solution-tree` |
| "아이디어 좀 내봐" | `brainstorm-ideas-*` |
| "이거 어떻게 테스트해?" | `brainstorm-experiments-*` |
| "잘못 가정하는 거 없어?" | `identify-assumptions-*` |
| "뭐부터 해야 해?" | `prioritize-features` / `prioritize-assumptions` |
| "고객들이 뭘 원해?" | `analyze-feature-requests` |
| "인터뷰 질문지 만들어줘" | `interview-script` |

#### 데이터 & 분석

| 이렇게 말하면 | 스킬 |
|-------------|------|
| "매출 분석해줘", "실적 어때?" | `sales-analysis` |
| "왜 잘 팔렸어?", "인사이트 뽑아줘" | `insight-archiving` |
| "A/B 테스트 결과 어때?" | `ab-test-analysis` |
| "재구매율", "코호트 분석" | `cohort-analysis` |
| "SQL 만들어줘" | `sql-queries` |
| "고객 페르소나 잡아줘" | `user-personas` |
| "고객 그룹 나눠줘" | `user-segmentation` / `market-segments` |

#### 실행 & 관리

| 이렇게 말하면 | 스킬 |
|-------------|------|
| "OKR 짜줘" | `brainstorm-okrs` |
| "PRD 만들어줘" | `create-prd` |
| "로드맵 아웃컴으로 바꿔줘" | `outcome-roadmap` |
| "이해관계자 정리해줘" | `stakeholder-map` |
| "스프린트 계획 짜줘" | `sprint-plan` |
| "회의 내용 정리해줘" | `summarize-meeting` |
| "이번 시즌 회고해보자" | `retro` |

---

## 🎮 명령어 가이드

### 핵심 FPOF 명령어

| 명령어 | 기능 |
|--------|------|
| `/status` | 현재 시즌·PDCA 단계·산출물 현황 |
| `/brief [유형]` | 산출물 템플릿 기반 문서 작성 |
| `/review` | 현재 단계 Quality Gate 검수 |
| `/next` | 다음 PDCA 단계 전환 |
| `/team` | 에이전시 팀 현황 조회 |
| `/export` | 시즌 산출물 목록 정리 |

### 문서 생성 명령어

| 명령어 | 기능 |
|--------|------|
| `/deck [유형]` | 프레젠테이션(PPTX) 생성 |
| `/pdf [유형]` | PDF 보고서 생성 |
| `/sheet [유형]` | 엑셀(XLSX) 시트 생성 |
| `/doc [유형]` | 워드(DOCX) 문서 생성 |

### 전략 & 분석 명령어

| 명령어 | 기능 |
|--------|------|
| `/market-scan` | 거시환경 종합 분석 (SWOT+PESTLE+Porter's+Ansoff) |
| `/pricing` | 가격 전략 설계 |
| `/business-model` | 비즈니스 모델 캔버스 |
| `/strategy-canvas` | 9섹션 프로덕트 전략 캔버스 |
| `/value-prop` | JTBD 밸류 프로포지션 설계 |
| `/competitive` | 경쟁 환경 분석 |
| `/battlecard` | 경쟁 배틀카드 |
| `/growth` | 그로스 루프 + GTM 모션 전략 |
| `/launch` | GTM 런칭 전략 |
| `/north-star` | North Star Metric 정의 |

### 리서치 & 디스커버리 명령어

| 명령어 | 기능 |
|--------|------|
| `/discover` | 프로덕트 디스커버리 사이클 (아이디어→가설→실험) |
| `/brainstorm` | 멀티 관점 브레인스토밍 |
| `/interview` | 고객 인터뷰 준비/요약 |
| `/research-users` | 사용자 리서치 종합 |
| `/analyze-feedback` | 고객 피드백 감성 분석 |
| `/triage` | 피처 요청 트리아지 |

### 실행 & 관리 명령어

| 명령어 | 기능 |
|--------|------|
| `/okrs` | OKR 수립 |
| `/prd` | PRD 작성 |
| `/roadmap` | 아웃컴 로드맵 변환 |
| `/stakeholders` | 이해관계자 맵 |
| `/sprint` | 스프린트 계획/회고/릴리즈 |
| `/pre-mortem` | 프리모텀 리스크 분석 |
| `/metrics` | 메트릭스 대시보드 설계 |

### 데이터 & 유틸리티 명령어

| 명령어 | 기능 |
|--------|------|
| `/ab-test` | A/B 테스트 분석 |
| `/cohorts` | 코호트 분석 |
| `/marketing` | 마케팅 크리에이티브 툴킷 |
| `/meeting` | 회의록 정리 |
| `/proofread` | 문법/흐름 체크 |

---

## 📁 폴더 구조

```
FPOF V2.2/
├── README.md                        # 이 파일
├── CLAUDE.md                        # 시스템 기본 설정
├── .fpof-state.json                 # 현재 시즌/PDCA 상태
├── .gitignore
├── package.json                     # 스크립트 패키지 설정
│
├── .claude/                         # Claude 훅 & 명령어
│   ├── hooks.json
│   ├── hooks/
│   │   ├── route-skill.sh           # 자연어 → 스킬 라우팅
│   │   ├── team-idle.sh             # 팀원 유휴 감지
│   │   └── team-task-completed.sh   # 팀원 작업 완료
│   └── commands/                    # 슬래시 명령어 (40+개)
│       ├── status.md, brief.md, review.md, next.md, team.md
│       ├── export.md, deck.md, pdf.md, sheet.md, doc.md
│       ├── market-scan.md, pricing.md, business-model.md
│       ├── strategy-canvas.md, value-prop.md, competitive.md
│       ├── battlecard.md, growth.md, launch.md, north-star.md
│       ├── discover.md, brainstorm.md, interview.md
│       ├── research-users.md, analyze-feedback.md, triage.md
│       ├── okrs.md, prd.md, roadmap.md, stakeholders.md
│       ├── sprint.md, pre-mortem.md, metrics.md
│       ├── ab-test.md, cohorts.md, marketing.md
│       └── meeting.md, proofread.md
│
├── skills/                          # 전체 스킬 (86개)
│   ├── strategy/                    # 전략기획실 패션 스킬 (4개)
│   ├── creative/                    # 크리에이티브 스튜디오 (3개)
│   ├── product/                     # 프로덕트 랩 (3개)
│   ├── marketing/                   # 마케팅 쇼룸 (4개)
│   ├── data/                        # 데이터 인텔리전스 (2개)
│   ├── quality/                     # QC 본부 (4개)
│   ├── task/                        # 태스크 유틸리티 (1개)
│   ├── pm-strategy/                 # PM 전략 프레임워크 (10개) ★NEW
│   ├── pm-research/                 # PM 리서치 스킬 (4개) ★NEW
│   ├── pm-gtm/                      # PM GTM 스킬 (3개) ★NEW
│   ├── pm-discovery/                # PM 디스커버리 스킬 (12개) ★NEW
│   ├── pm-execution/                # PM 실행 관리 스킬 (13개) ★NEW
│   ├── pm-analytics/                # PM 애널리틱스 스킬 (3개) ★NEW
│   ├── pm-marketing/                # PM 마케팅 스킬 (1개) ★NEW
│   └── pm-toolkit/                  # PM 툴킷 스킬 (4개) ★NEW
│
├── agents/                          # 에이전시 README
│   ├── data-intelligence/
│   ├── marketing-showroom/
│   ├── quality-control/
│   └── strategy-planning/
│
├── presets/                         # 와키윌리 브랜드 프리셋 (7개)
│   └── wacky-willy/
│       ├── brand.config.json
│       ├── personas.json
│       ├── tone-manner.json
│       ├── visual-identity.json
│       ├── categories.json
│       ├── channels.json
│       └── ip-bible.json
│
├── scripts/                         # 유틸리티 스크립트
│   ├── generate-strategy-ppt.js
│   ├── generate-weekly-report-ppt.js
│   └── generate-weekly-sales-report-v2.js
│
├── docs/                            # 문서
│   ├── user-manual.md
│   ├── quickstart-guide.md
│   └── reference/
│
└── output/                          # 산출물 저장 (gitignore)
    └── [시즌]/
        ├── _season/                 # 시즌 전체 문서
        └── [프로젝트]/              # 아이템별 프로젝트
```

---

## 📌 요약 통계

| 항목 | V2.1 | V2.2 |
|------|------|------|
| **FPOF 패션 실무 스킬** | 21개 | 21개 |
| **PM 프레임워크 스킬** | - | 65개 ★NEW |
| **Claude 유니버설 스킬** | 19개 | 19개 |
| **슬래시 명령어** | 10개 | 40+개 ★NEW |
| **브랜드 프리셋** | 7개 | 7개 |
| **에이전시** | 6개 | 6개 |
| **총 스킬** | 40개 | **105개** |

---

## 🚀 빠른 시작

```
# 1. 현재 상태 확인
/status

# 2. 자연어로 작업 시작
"26SS 트렌드 분석해줘"
/brief trend

# 3. PM 프레임워크 활용
/market-scan        # PESTLE + Porter's + Ansoff 종합
/discover           # 아이디어 → 가설 → 실험
/okrs               # 분기 OKR 수립

# 4. 품질 검수 & 단계 전환
/review
/next
```

---

## 📖 추가 참고자료

- [CLAUDE.md](./CLAUDE.md) — FPOF 와키윌리 시스템 상세 설정
- [docs/guide/quickstart-guide.md](./docs/guide/quickstart-guide.md) — 5분 퀵스타트 가이드
- [docs/guide/user-manual.md](./docs/guide/user-manual.md) — 전체 사용자 매뉴얼

---

**버전**: 2.2.0
**최종 업데이트**: 2026-03-09
**PM-Skills**: Paweł Huryn (MIT License) 기반 와키윌리 커스터마이징
**라이선스**: Copyright © 2026 Wacky Willy. All rights reserved.
