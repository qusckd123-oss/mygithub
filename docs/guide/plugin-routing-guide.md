# FPOF × Knowledge-Work 플러그인 이중 라우팅 가이드

> FPOF 패션 하우스 스킬(82개)과 Knowledge-Work 범용 플러그인(18개, 118개 스킬)을 자연어로 구분 없이 사용하는 방법을 안내합니다.
> 패션 업무는 FPOF가, 범용 비즈니스 업무는 KW 플러그인이 자동으로 처리합니다.

---

## 1. 개요

### 두 개의 스킬 시스템

| 구분 | FPOF 내장 스킬 | Knowledge-Work (KW) 플러그인 |
|------|---------------|---------------------------|
| **스킬 수** | 82개 | 118개 (18개 플러그인) |
| **특화 영역** | 와키윌리 브랜드, 패션 산업, PDCA 사이클 | 범용 비즈니스 (HR, 법무, 재무, 엔지니어링, 영업 등) |
| **데이터 기반** | `system/presets/` 브랜드 프리셋 JSON | 외부 도구 연동 (CRM, Slack, Snowflake 등) |
| **호출 방식** | 자연어 + `/슬래시 명령어` | 자연어 + `@도메인` 접두사 |
| **산출물 저장** | `workspace/` FPOF 규칙 준수 | 별도 저장 규칙 없음 (범용) |

### 작동 원리

```
사용자 자연어 요청
    │
    ├─ 패션/브랜드 키워드 감지? ──→ FPOF 스킬 (6개 에이전시)
    │   예: "시즌 테마", "SKU", "룩북", "BTA", "IMC"
    │
    ├─ FPOF에 없는 도메인? ──→ KW 플러그인 (자동)
    │   예: "면접 질문", "계약서 검토", "분개 작성", "코드 리뷰"
    │
    ├─ 겹치는 영역? ──→ 컨텍스트 판단 (아래 규칙 참조)
    │   예: "경쟁사 분석", "캠페인 기획", "PRD"
    │
    └─ `@도메인` 접두사? ──→ KW 플러그인 (명시적 지정)
        예: "@sales 이 회사 조사해줘", "@legal 계약서 봐줘"
```

---

## 2. KW 플러그인 전체 목록

### 핵심 플러그인 (11개)

| 플러그인 | `@접두사` | 스킬 수 | 주요 기능 |
|---------|----------|---------|----------|
| **sales** | `@sales` | 9 | 영업 리서치, 콜 준비, 파이프라인 분석, 아웃리치 작성, 예측 |
| **marketing** | `@marketing` | 8 | 콘텐츠 작성, 캠페인 기획, SEO, 이메일 시퀀스, 성과 보고 |
| **product-management** | `@pm` | 8 | 스펙 문서, 로드맵, 메트릭스 리뷰, 리서치 종합, 브레인스토밍 |
| **data** | `@data` | 10 | SQL 쿼리, 시각화, 통계 분석, 대시보드, 데이터 프로파일링 |
| **design** | `@design` | 7 | 접근성 감사, 디자인 비평, 핸드오프, 디자인시스템, UX 카피 |
| **engineering** | `@eng` | 10 | 아키텍처, 코드 리뷰, 디버깅, 배포 체크, 시스템 설계, 테스트 |
| **finance** | `@finance` | 8 | 분개, 계정 대사, 재무제표, 차이 분석, 결산, SOX 테스트 |
| **legal** | `@legal` | 9 | 계약 검토, NDA 분류, 컴플라이언스, 리스크 평가, 벤더 관리 |
| **human-resources** | `@hr` | 9 | 보상 분석, 오퍼 작성, 면접 설계, 온보딩, 조직 설계, 채용 |
| **operations** | `@ops` | 9 | 용량 계획, 변경 관리, 프로세스 문서, 리스크 평가, 런북 |
| **customer-support** | `@cs` | 5 | 티켓 분류, 응대 작성, 에스컬레이션, KB 문서 작성 |

### 유틸리티 플러그인 (4개)

| 플러그인 | `@접두사` | 스킬 수 | 주요 기능 |
|---------|----------|---------|----------|
| **productivity** | `@productivity` | 4 | 태스크 관리, 메모리 시스템, 일일 업데이트 |
| **enterprise-search** | `@search` | 5 | 크로스 소스 검색, 다이제스트, 지식 종합 |
| **brand-voice** | `@brand` | 3 | 브랜드 가이드라인 생성, 보이스 적용, 발견 |
| **cowork-plugin-management** | `@plugin` | 2 | 플러그인 커스터마이징, 새 플러그인 생성 |

### 파트너 플러그인 (3개)

| 플러그인 | `@접두사` | 스킬 수 | 주요 기능 |
|---------|----------|---------|----------|
| **apollo** | `@apollo` | 3 | 리드 인리치먼트, 프로스펙팅, 시퀀스 로딩 |
| **common-room** | `@commonroom` | 6 | 어카운트 리서치, 콜 준비, 아웃리치, 주간 브리핑 |
| **slack-by-salesforce** | `@slack` | 2+5 | Slack 메시징, 검색, 채널 다이제스트, 공지 |

---

## 3. FPOF ↔ KW 겹침 영역과 해소 규칙

약 15개 영역에서 양쪽 스킬이 겹칩니다. 아래 규칙으로 자동 판단합니다.

### 판단 플로우차트

```
겹치는 요청 수신
  │
  ├─ 현재 PDCA 단계 작업 중? ──→ FPOF 스킬
  ├─ 브랜드 프리셋 데이터 필요? ──→ FPOF 스킬
  ├─ 외부 도구 연동 필요? (CRM, Snowflake, Slack 등) ──→ KW 플러그인
  ├─ 와키윌리/비케이브 맥락? ──→ FPOF 스킬
  ├─ 범용 프레임워크/산업 무관? ──→ KW 플러그인
  └─ 여전히 모호? ──→ 사용자에게 확인
```

### 겹침 해소 상세 테이블

| 영역 | 이렇게 말하면 → FPOF | 이렇게 말하면 → KW 플러그인 |
|------|---------------------|--------------------------|
| **경쟁 분석** | "경쟁 브랜드 분석해줘" "커버낫이랑 비교" | "@sales 경쟁사 조사" "@marketing 포지셔닝 갭 분석" |
| **캠페인** | "26SS 캠페인 기획" "IMC 전략 짜줘" | "@marketing 이메일 드립 캠페인" "@marketing B2B 리드젠" |
| **콘텐츠** | "인스타 캡션 써줘" "PDP 카피" | "@marketing 블로그 포스트" "@marketing 뉴스레터 작성" |
| **PRD/스펙** | "후드티 상품 기획서" "카테고리 브리프" | "@pm 기능 스펙 문서" "@pm API 요구사항 정의" |
| **SQL/데이터** | "매출 분석 쿼리 짜줘" "채널별 실적" | "@data BigQuery 쿼리" "@data 이 테이블 프로파일링" |
| **스프린트** | "이번 주 시즌 작업 계획" | "@pm 개발팀 스프린트 플래닝" |
| **유저리서치** | "코어타겟 리서치" "페르소나 재정의" | "@design 유저빌리티 테스트 설계" "@design 인터뷰 가이드" |
| **로드맵** | "시즌 로드맵 아웃컴 중심으로" | "@pm 분기 프로덕트 로드맵 업데이트" |
| **브레인스토밍** | "신상품 아이디어 내줘" "캡슐 콜라보" | "@pm 프로덕트 기회 탐색" |
| **NDA/법무** | `/brief nda` (간단 NDA 초안) | "@legal NDA 분류" "@legal 계약서 레드라인 검토" |
| **브랜드 톤** | "와키윌리 톤으로 써줘" (tone-manner.json) | "@brand 새 브랜드 가이드라인 생성" |
| **대시보드** | `/sheet` `/metrics` (와키윌리 KPI) | "@data 인터랙티브 HTML 대시보드" |
| **리서치 종합** | "고객 피드백 분석" "인사이트 뽑아줘" | "@pm 인터뷰 노트 종합" "@design 리서치 신디시스" |

---

## 4. 사용법

### 방법 1: 자연어 (자동 라우팅)

그냥 평소처럼 말하면 됩니다. AI가 맥락을 보고 적합한 스킬을 선택합니다.

```
"면접 질문 만들어줘"           → @hr interview-prep (FPOF에 없으므로 자동)
"매출 분석해줘"               → FPOF sales-analysis (와키윌리 맥락 자동 감지)
"계약서 검토해줘"             → @legal review-contract (FPOF에 없으므로 자동)
"시즌 테마 잡아줘"            → FPOF brand-strategy (패션 키워드 자동 감지)
"코드 리뷰해줘"              → @eng code-review (FPOF에 없으므로 자동)
```

### 방법 2: `@도메인` 접두사 (명시적 KW 지정)

겹치는 영역에서 KW 플러그인을 사용하고 싶을 때, 또는 확실히 KW를 쓰고 싶을 때:

```
"@sales 이 회사 조사해줘"      → sales:account-research
"@marketing SEO 감사해줘"      → marketing:seo-audit
"@data 이 CSV 프로파일링해줘"   → data:explore-data
"@legal 이 계약서 리뷰해줘"    → legal:review-contract
"@hr 보상 벤치마크 분석해줘"   → hr:comp-analysis
"@finance 월말 결산 체크리스트" → finance:close-management
"@eng 시스템 설계 해줘"        → engineering:system-design
"@ops 프로세스 문서화해줘"     → operations:process-doc
```

### 방법 3: FPOF 슬래시 명령어 (기존대로)

패션 하우스 전용 단축 명령은 변경 없이 그대로 사용합니다:

```
/status                        → 현재 시즌·PDCA 상태
/brief trend-brief             → 트렌드 브리프 작성
/review                        → Quality Gate 검수
/next                          → 다음 PDCA 단계
/pinterest dopamine dressing   → 핀터레스트 이미지 수집
/deck lookbook                 → 프레젠테이션 생성
```

### 방법 4: KW 플러그인 슬래시 명령어

일부 KW 플러그인은 자체 슬래시 명령어를 제공합니다:

```
/product-management:brainstorm   → 프로덕트 브레인스토밍
/brand-voice:enforce-voice       → 브랜드 보이스 적용
/brand-voice:generate-guidelines → 브랜드 가이드라인 생성
/brand-voice:discover-brand      → 브랜드 소재 탐색
/slack-by-salesforce:channel-digest     → Slack 채널 요약
/slack-by-salesforce:draft-announcement → Slack 공지 초안
/common-room:weekly-brief        → 주간 브리핑 생성
/common-room:generate-account-plan → 어카운트 플랜 생성
```

---

## 5. FPOF 전용 영역 (KW 플러그인 미개입)

아래 작업은 항상 FPOF 스킬이 처리합니다. KW 플러그인이 개입하지 않습니다.

| 영역 | FPOF 스킬 | 설명 |
|------|----------|------|
| 시즌 전략 | trend-research, brand-strategy, md-planning, line-sheet | 시즌 PDCA Plan 단계 |
| 상품 디자인 | moodboard, design-spec, visual-generation, pinterest-crawl | 크리에이티브 스튜디오 |
| 생산/원가 | techpack, costing-ve, qr-process | 프로덕트 랩 |
| IMC/바이럴 | imc-strategy, social-viral, visual-content | 마케팅 쇼룸 (와키윌리 특화) |
| 품질/QC | quality-gate, gap-analysis, completion-report, pdca-iteration | QC 본부 |
| 인사이트 | sales-analysis, insight-archiving | 와키윌리 매출 데이터 기반 |
| 시스템 관리 | `/status`, `/next`, `/review`, `/team`, `/export` | FPOF 오케스트레이션 |
| 산출물 생성 | `/deck`, `/pdf`, `/sheet`, `/doc` | FPOF 템플릿 기반 |
| 온디바이스 ML | `/apple` | Apple Neural Engine |

---

## 6. KW 플러그인 전용 영역 (FPOF 미개입)

아래 작업은 FPOF에 해당 스킬이 없으므로 KW 플러그인이 자동 처리합니다.

| 도메인 | `@접두사` | 대표 스킬 | 사용 예시 |
|--------|----------|----------|----------|
| **HR** | `@hr` | comp-analysis, interview-prep, onboarding, org-planning, performance-review | "면접 질문 만들어줘", "온보딩 체크리스트", "조직 설계 도와줘" |
| **재무** | `@finance` | journal-entry, reconciliation, financial-statements, variance-analysis, sox-testing | "분개 준비해줘", "계정 대사해줘", "재무제표 만들어줘" |
| **엔지니어링** | `@eng` | architecture, code-review, debug, system-design, incident-response, testing-strategy | "ADR 만들어줘", "이 PR 리뷰해줘", "시스템 설계해줘" |
| **운영** | `@ops` | capacity-plan, process-doc, runbook, risk-assessment, vendor-review | "프로세스 문서화해줘", "런북 만들어줘", "벤더 평가해줘" |
| **영업** | `@sales` | account-research, call-prep, pipeline-review, forecast, draft-outreach | "이 회사 조사해줘", "콜 준비해줘", "파이프라인 분석" |
| **고객지원** | `@cs` | ticket-triage, draft-response, customer-escalation, kb-article | "티켓 분류해줘", "고객 응대 초안", "KB 문서 만들어줘" |
| **검색** | `@search` | search, digest, knowledge-synthesis | "그 문서 찾아줘", "이번 주 다이제스트", "소스별 검색" |
| **SEO** | `@marketing` | seo-audit | "SEO 감사해줘", "키워드 리서치" |
| **이메일** | `@marketing` | email-sequence | "이메일 드립 캠페인 설계", "온보딩 시퀀스" |

---

## 7. 외부 도구 연동 (Connectors)

KW 플러그인은 MCP 서버를 통해 외부 도구와 연동할 수 있습니다.
각 플러그인의 `.mcp.json`에 커넥터를 설정하면 실시간 데이터를 가져옵니다.

| 플러그인 | 연동 가능 도구 |
|---------|--------------|
| **sales** | Slack, HubSpot, Close, Clay, ZoomInfo, Notion, Jira, Fireflies, Microsoft 365 |
| **marketing** | Slack, Canva, Figma, HubSpot, Amplitude, Notion, Ahrefs, SimilarWeb, Klaviyo |
| **product-management** | Slack, Linear, Asana, Monday, ClickUp, Jira, Notion, Figma, Amplitude, Pendo, Intercom, Fireflies |
| **data** | Snowflake, Databricks, BigQuery, Definite, Hex, Amplitude, Jira |
| **finance** | Snowflake, Databricks, BigQuery, Slack, Microsoft 365 |
| **legal** | Slack, Box, Egnyte, Jira, Microsoft 365 |
| **enterprise-search** | Slack, Notion, Guru, Jira, Asana, Microsoft 365 |
| **customer-support** | Slack, Intercom, HubSpot, Guru, Jira, Notion, Microsoft 365 |
| **human-resources** | Slack, BambooHR, Greenhouse, Lever, Microsoft 365 |
| **operations** | Slack, Jira, Asana, PagerDuty, Datadog, Microsoft 365 |

> **참고**: 커넥터 설정은 `@plugin 커스터마이징해줘`로 가이드를 받을 수 있습니다.
> 현재 연동된 도구가 없어도 웹 검색과 사용자 입력으로 대부분의 스킬을 사용할 수 있습니다.

---

## 8. 실전 시나리오

### 시나리오 A: 시즌 기획 중 범용 업무 병행

```
사용자: "26SS 트렌드 브리프 작성해줘"
AI: → FPOF trend-research (PDCA Plan 단계, 프리셋 참조)

사용자: "이 시즌 준비하면서 팀 면접도 봐야 하는데, 면접 질문 만들어줘"
AI: → KW hr:interview-prep (FPOF에 없는 영역, 자동 라우팅)

사용자: "트렌드 브리프 기반으로 경쟁사 비교표도 만들어줘"
AI: → FPOF competitive-battlecard (와키윌리 맥락 유지)
```

### 시나리오 B: 마케팅 겹침 영역

```
사용자: "캠페인 기획해줘"
AI: (현재 PDCA Do 단계 + 와키윌리 맥락) → FPOF imc-strategy

사용자: "@marketing 이메일 드립 캠페인 만들어줘"
AI: → KW marketing:email-sequence (명시적 @접두사)

사용자: "SEO 분석 좀 해줘"
AI: → KW marketing:seo-audit (FPOF에 없는 스킬, 자동 라우팅)
```

### 시나리오 C: 데이터 분석 겹침

```
사용자: "이번 주 매출 분석해줘"
AI: → FPOF sales-analysis (와키윌리 매출 데이터, weekly/data/ 참조)

사용자: "@data 이 CSV 파일 프로파일링해줘"
AI: → KW data:explore-data (범용 데이터 분석)

사용자: "Snowflake에서 쿼리 짜줘"
AI: → KW data:write-query (외부 도구 연동 맥락)
```

### 시나리오 D: 법무/재무 (FPOF 미보유)

```
사용자: "이 계약서 검토해줘"
AI: → KW legal:review-contract (FPOF에 없으므로 자동)

사용자: "월말 결산 분개 준비해줘"
AI: → KW finance:journal-entry (FPOF에 없으므로 자동)

사용자: "SOX 테스트 샘플 뽑아줘"
AI: → KW finance:sox-testing (FPOF에 없으므로 자동)
```

---

## 9. 자주 묻는 질문

### Q: 두 시스템이 동시에 작동하면 충돌하지 않나요?
**A:** 아닙니다. 라우팅 규칙에 따라 한 번에 하나의 스킬만 활성화됩니다. 겹치는 영역에서는 컨텍스트(패션 vs 범용)로 자동 판단하고, 모호할 때는 사용자에게 확인합니다.

### Q: `@접두사`를 꼭 써야 하나요?
**A:** 아닙니다. 자연어만으로도 대부분 올바르게 라우팅됩니다. `@접두사`는 겹치는 영역에서 KW 플러그인을 명시적으로 지정하고 싶을 때 사용합니다.

### Q: FPOF 산출물 저장 규칙이 KW 플러그인에도 적용되나요?
**A:** KW 플러그인 결과물 중 와키윌리 프로젝트에 포함되는 산출물은 FPOF 저장 규칙(`workspace/` 구조, 파일명 규칙)을 따릅니다. 그 외 범용 결과물(코드 리뷰, 법률 문서 등)은 별도 경로에 저장합니다.

### Q: KW 플러그인의 외부 도구를 연동하려면?
**A:** `@plugin 커스터마이징해줘` 또는 각 플러그인의 `CONNECTORS.md`를 참조하세요. MCP 서버 설정이 필요하며, 연동 없이도 웹 검색과 사용자 입력으로 대부분의 기능을 사용할 수 있습니다.

### Q: 새 플러그인을 추가하거나 기존 플러그인을 커스터마이징하려면?
**A:** `@plugin` 접두사로 요청하면 `cowork-plugin-management` 플러그인이 안내합니다:
- `"@plugin 새 플러그인 만들어줘"` → 신규 플러그인 스캐폴딩
- `"@plugin 마케팅 플러그인 커스터마이징해줘"` → 기존 플러그인 수정 가이드

---

## 10. 설치된 플러그인 전체 스킬 레퍼런스

### sales (9 스킬)
| 스킬 | 트리거 키워드 |
|------|-------------|
| account-research | "이 회사 조사", "prospect 리서치", "intel on" |
| call-prep | "콜 준비", "미팅 준비", "prep me for" |
| call-summary | "콜 노트 정리", "미팅 요약", "follow-up 작성" |
| competitive-intelligence | "경쟁사 조사", "배틀카드", "how do we compare" |
| create-an-asset | "세일즈 자산 만들어줘", "one-pager", "랜딩페이지" |
| daily-briefing | "오늘 뭐 있어?", "morning brief", "하루 준비" |
| draft-outreach | "아웃리치 작성", "콜드 이메일", "reach out to" |
| forecast | "매출 예측", "forecast", "gap-to-quota" |
| pipeline-review | "파이프라인 분석", "딜 우선순위", "pipeline health" |

### marketing (8 스킬)
| 스킬 | 트리거 키워드 |
|------|-------------|
| brand-review | "브랜드 톤 체크", "voice 검토", "카피 감수" |
| campaign-plan | "캠페인 기획", "launch campaign", "리드젠 캠페인" |
| competitive-brief | "경쟁 포지셔닝", "messaging gap", "경쟁사 콘텐츠 분석" |
| content-creation | "콘텐츠 작성", "블로그 써줘", "소셜 포스트" |
| draft-content | "마케팅 콘텐츠", "뉴스레터", "프레스 릴리즈" |
| email-sequence | "이메일 시퀀스", "드립 캠페인", "온보딩 이메일" |
| performance-report | "마케팅 성과", "채널 리포트", "campaign wrap-up" |
| seo-audit | "SEO 감사", "키워드 리서치", "콘텐츠 갭" |

### product-management (8 스킬)
| 스킬 | 트리거 키워드 |
|------|-------------|
| competitive-brief | "경쟁 분석", "feature parity", "배틀카드" |
| metrics-review | "메트릭스 리뷰", "KPI 분석", "spike 조사" |
| product-brainstorming | "아이디어 브레인스토밍", "기회 탐색", "문제 정의" |
| roadmap-update | "로드맵 업데이트", "우선순위 재조정", "Now/Next/Later" |
| sprint-planning | "스프린트 플래닝", "백로그 사이징", "스프린트 목표" |
| stakeholder-update | "이해관계자 업데이트", "리더십 보고", "launch 공지" |
| synthesize-research | "리서치 종합", "인터뷰 노트 정리", "피드백 테마 추출" |
| write-spec | "스펙 문서", "PRD 작성", "feature scope" |

### data (10 스킬)
| 스킬 | 트리거 키워드 |
|------|-------------|
| analyze | "데이터 분석", "메트릭 조회", "트렌드 조사" |
| build-dashboard | "대시보드 만들어줘", "KPI 보드", "executive overview" |
| create-viz | "차트 만들어줘", "시각화", "plot" |
| data-context-extractor | "데이터 컨텍스트 추출", "스키마 분석", "tribal knowledge" |
| data-visualization | "시각화 디자인", "chart type 추천", "접근성 차트" |
| explore-data | "데이터 프로파일링", "null rate 체크", "data quality" |
| sql-queries | "SQL 짜줘 (범용)", "쿼리 최적화", "dialect 변환" |
| statistical-analysis | "통계 분석", "가설 검정", "이상치 탐지" |
| validate-data | "분석 QA", "결과 검증", "methodology 체크" |
| write-query | "쿼리 작성 (Snowflake/BQ)", "CTE 쿼리", "파티션 최적화" |

### engineering (10 스킬)
| 스킬 | 트리거 키워드 |
|------|-------------|
| architecture | "ADR 작성", "기술 선택", "아키텍처 결정" |
| code-review | "코드 리뷰", "PR 검토", "보안 체크" |
| debug | "디버깅", "에러 분석", "스택 트레이스" |
| deploy-checklist | "배포 체크리스트", "릴리즈 전 확인", "롤백 계획" |
| documentation | "기술 문서", "README", "런북 작성" |
| incident-response | "인시던트", "장애 대응", "포스트모템" |
| standup | "스탠드업", "어제/오늘/블로커", "daily update" |
| system-design | "시스템 설계", "서비스 아키텍처", "API 설계" |
| tech-debt | "기술 부채", "리팩토링 우선순위", "코드 건강도" |
| testing-strategy | "테스트 전략", "커버리지", "테스트 아키텍처" |

### finance (8 스킬)
| 스킬 | 트리거 키워드 |
|------|-------------|
| audit-support | "감사 지원", "SOX 404", "control testing" |
| close-management | "결산 관리", "month-end close", "close calendar" |
| financial-statements | "재무제표", "P&L", "balance sheet" |
| journal-entry-prep | "분개 준비", "accrual", "depreciation" |
| journal-entry | "분개 작성", "debit/credit", "journal entry" |
| reconciliation | "계정 대사", "bank rec", "GL 대사" |
| sox-testing | "SOX 테스트", "control sample", "ITGC" |
| variance-analysis | "차이 분석", "budget vs actual", "variance" |

### legal (9 스킬)
| 스킬 | 트리거 키워드 |
|------|-------------|
| brief | "법률 브리핑", "daily legal scan", "legal research" |
| compliance-check | "컴플라이언스 체크", "규제 확인", "GDPR" |
| legal-response | "법적 문의 응답", "DSR 처리", "소환장" |
| legal-risk-assessment | "법적 리스크 평가", "계약 리스크", "severity 분류" |
| meeting-briefing | "법무 미팅 준비", "협상 준비", "board meeting" |
| review-contract | "계약서 검토", "레드라인", "clause 분석" |
| signature-request | "서명 요청", "e-signature", "signing order" |
| triage-nda | "NDA 분류", "GREEN/YELLOW/RED", "non-compete 확인" |
| vendor-check | "벤더 체크", "계약 현황 확인", "expiration 체크" |

### human-resources (9 스킬)
| 스킬 | 트리거 키워드 |
|------|-------------|
| comp-analysis | "보상 분석", "연봉 벤치마크", "equity 모델링" |
| draft-offer | "오퍼레터 작성", "total comp 패키지", "협상 가이드" |
| interview-prep | "면접 설계", "스코어카드", "역량 질문" |
| onboarding | "온보딩 체크리스트", "Day 1 플랜", "30/60/90" |
| org-planning | "조직 설계", "헤드카운트 플랜", "reorg" |
| people-report | "인원 리포트", "이직률 분석", "다양성 지표" |
| performance-review | "성과 리뷰", "self-assessment", "calibration" |
| policy-lookup | "정책 확인", "PTO 규정", "경비 처리 방법" |
| recruiting-pipeline | "채용 파이프라인", "후보자 현황", "sourcing" |

### operations (9 스킬)
| 스킬 | 트리거 키워드 |
|------|-------------|
| capacity-plan | "용량 계획", "리소스 배분", "인력 여유" |
| change-request | "변경 요청", "CAB 리뷰", "롤백 계획" |
| compliance-tracking | "컴플라이언스 트래킹", "ISO 27001", "SOC 2" |
| process-doc | "프로세스 문서", "RACI", "SOP 작성" |
| process-optimization | "프로세스 개선", "병목 해소", "워크플로우 최적화" |
| risk-assessment | "리스크 평가", "위험 식별", "risk register" |
| runbook | "런북 작성", "on-call 절차", "트러블슈팅 가이드" |
| status-report | "상태 보고서", "주간 업데이트", "green/yellow/red" |
| vendor-review | "벤더 평가", "TCO 분석", "계약 갱신 검토" |

### customer-support (5 스킬)
| 스킬 | 트리거 키워드 |
|------|-------------|
| customer-escalation | "에스컬레이션", "버그 엔지니어링 전달", "churn 위험" |
| customer-research | "고객 조사", "이전 문의 확인", "ticket history" |
| draft-response | "고객 응답 작성", "bad news 전달", "billing 이슈" |
| kb-article | "KB 문서 작성", "self-service 문서", "FAQ" |
| ticket-triage | "티켓 분류", "P1-P4 우선순위", "duplicate 체크" |

### design (7 스킬)
| 스킬 | 트리거 키워드 |
|------|-------------|
| accessibility-review | "접근성 감사", "WCAG", "a11y 체크" |
| design-critique | "디자인 비평", "mockup 피드백", "UI 리뷰" |
| design-handoff | "개발 핸드오프", "스펙시트", "디자인 토큰" |
| design-system | "디자인 시스템", "컴포넌트 문서", "네이밍 일관성" |
| research-synthesis | "리서치 신디시스", "인터뷰 종합", "NPS 분석" |
| user-research | "유저 리서치 계획", "인터뷰 가이드", "서베이 설계" |
| ux-copy | "UX 카피", "마이크로카피", "에러 메시지 문구" |

### 기타 플러그인
| 플러그인 | 스킬 | 트리거 키워드 |
|---------|------|-------------|
| productivity | task-management, memory-management, start, update | "태스크 정리", "할 일 관리", "메모리 업데이트" |
| enterprise-search | search, digest, knowledge-synthesis | "문서 찾아줘", "주간 다이제스트", "크로스 검색" |
| brand-voice | brand-voice-enforcement, discover-brand, guideline-generation | "브랜드 가이드라인 생성", "보이스 적용", "브랜드 소재 탐색" |
| apollo | enrich-lead, prospect, sequence-load | "리드 인리치", "ICP 프로스펙팅", "시퀀스 로딩" |
| common-room | account-research, call-prep, compose-outreach, contact-research, prospect, weekly-prep-brief | "Common Room 리서치", "주간 브리핑" |
| slack-by-salesforce | slack-messaging, slack-search | "Slack 메시지 작성", "Slack 검색" |
| cowork-plugin-management | create-cowork-plugin, cowork-plugin-customizer | "플러그인 만들어줘", "플러그인 커스터마이징" |
