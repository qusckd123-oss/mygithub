# FPOF 상세 가이드 (CLAUDE.md 보충)

## 자연어 → 스킬 라우팅 테이블

### 시즌 기획 & 전략
| 이렇게 말하면 | 스킬 |
|-------------|------|
| "트렌드 봐줘", "경쟁사 뭐 하고 있어?" | `trend-research` |
| "시즌 테마 뭘로 하지?", "포지셔닝 괜찮아?" | `brand-strategy` |
| "SKU 어떻게 짜?", "히트상품 뭘로 밀지?" | `md-planning` |
| "라인시트 만들어줘", "물량 얼마나 잡아?" | `line-sheet` |
| "외부 환경 봐줘" | `pestle-analysis` |
| "업계 경쟁 상황?" | `porters-five-forces` |
| "어디로 성장?" | `ansoff-matrix` |
| "사업 모델 정리" | `business-model-canvas` |
| "고객 가치가 뭐야?" | `value-proposition` |
| "전략 한 장 정리" | `product-strategy-canvas` |

### 경쟁 & GTM
| 이렇게 말하면 | 스킬 |
|-------------|------|
| "경쟁사 비교표" | `competitive-battlecard` |
| "글로벌 첫 시장은?" | `beachhead-segment` |
| "핵심 고객 누구?" | `ideal-customer-profile` |

### 디스커버리
| 이렇게 말하면 | 스킬 |
|-------------|------|
| "고객 기회 구조화" | `opportunity-solution-tree` |
| "아이디어 내봐" | `brainstorm-ideas-*` |
| "실험 설계해줘" | `brainstorm-experiments-*` |
| "리스크 뭐가 있지?" | `identify-assumptions-*` |
| "뭐부터 해야 해?" | `prioritize-features` |
| "리뷰 패턴 뽑아줘" | `analyze-feature-requests` |

### 디자인 & 비주얼
| 이렇게 말하면 | 스킬 |
|-------------|------|
| "무드보드 만들어줘" | `moodboard` |
| "핀터레스트 이미지 수집" | `pinterest-crawl` |
| "시즌 컬러", "컬러 팔레트", "컬러웨이 추천" | `color-intelligence` |
| "디자인 시안 생성", "AI 디자인", "배리에이션" | `design-generator` |
| "디자인 스펙 정리" | `design-spec` |
| "이미지 만들어줘" | `visual-generation` |

### 생산 & 원가
| 이렇게 말하면 | 스킬 |
|-------------|------|
| "원가 맞아?", "VE 해줘" | `costing-ve` |
| "용척 계산", "마커 효율", "대안 소재", "패턴 최적화" | `pattern-optimizer` |
| "테크팩 만들어줘" | `techpack` |
| "리오더 진행해줘" | `qr-process` |

### 마케팅 & 콘텐츠
| 이렇게 말하면 | 스킬 |
|-------------|------|
| "마케팅 전략 짜줘" | `imc-strategy` |
| "화보 기획", "숏폼 기획" | `visual-content` |
| "상품 이미지 생성", "채널별 에셋", "비주얼 팩토리" | `visual-factory` |
| "카피 만들어줘", "인스타 캡션" | `copywriting` |
| "바이럴 전략", "런칭 시퀀스" | `social-viral` |
| "구매 여정 그려줘" | `customer-journey-map` |
| "상품명 후보" | `product-name` |

### 데이터 & 분석
| 이렇게 말하면 | 스킬 |
|-------------|------|
| "트렌드 레이더", "트렌드 스캔", "트렌드 스코어링" | `trend-radar` |
| "리오더 타이밍", "재고 소진 예측", "QR 대상", "SPOT 후보" | `demand-optimizer` |
| "매출 분석", "채널별 비교" | `sales-analysis` |
| "인사이트 뽑아줘" | `insight-archiving` |
| "A/B 테스트 결과" | `ab-test-analysis` |
| "코호트 분석" | `cohort-analysis` |
| "무신사 랭킹" | `musinsa-ranking` |
| "무신사 발매" | `musinsa-release` |
| "마켓 동향" | `market-intelligence` |

### 품질 & 검수
| 이렇게 말하면 | 스킬 |
|-------------|------|
| "검수해줘", "QG 돌려줘" | `quality-gate` |
| "갭 분석" | `gap-analysis` |
| "시즌 리포트" | `completion-report` |
| "시즌 회고" | `retro` |
| "문법 체크" | `grammar-check` |

### 실행 관리
| 이렇게 말하면 | 스킬 |
|-------------|------|
| "OKR 짜줘" | `brainstorm-okrs` |
| "PRD 작성" | `create-prd` |
| "로드맵 아웃컴 중심" | `outcome-roadmap` |
| "이해관계자 정리" | `stakeholder-map` |
| "미팅 노트 정리" | `summarize-meeting` |

## 슬래시 명령어 (.claude/commands/)

| 명령어 | 기능 |
|--------|------|
| `/status` | 시즌·PDCA 단계·산출물 현황 |
| `/brief [유형]` | 산출물 템플릿 기반 문서 작성 |
| `/review` | Quality Gate 검수 |
| `/next` | 다음 PDCA 단계 전환 |
| `/team` | 에이전시 팀 현황 |
| `/export` | 산출물 목록 정리 |
| `/deck [유형]` | PPTX 생성 |
| `/pdf [유형]` | PDF 보고서 |
| `/sheet [유형]` | XLSX 시트 |
| `/doc [유형]` | DOCX 문서 |
| `/pinterest [키워드]` | 핀터레스트 이미지 수집 |
| `/musinsa-ranking` | 무신사 랭킹 수집 |
| `/musinsa-release` | 무신사 발매 수집 |
| `/market-scan` | 거시환경 종합 분석 |
| `/pricing` | 가격 전략 설계 |
| `/business-model` | BMC 탐색 |
| `/strategy-canvas` | 전략 캔버스 |
| `/value-prop` | 밸류 프로포지션 |
| `/research-users` | 사용자 리서치 종합 |
| `/analyze-feedback` | 피드백 감성 분석 |
| `/competitive` | 경쟁 환경 분석 |
| `/battlecard` | 경쟁 배틀카드 |
| `/growth` | 그로스 전략 |
| `/launch` | GTM 런칭 전략 |
| `/discover` | 디스커버리 사이클 |
| `/brainstorm` | 멀티 관점 브레인스토밍 |
| `/interview` | 고객 인터뷰 |
| `/triage` | 피처 요청 트리아지 |
| `/metrics` | 메트릭스 대시보드 |
| `/okrs` | OKR 수립 |
| `/prd` | PRD 작성 |
| `/pre-mortem` | 프리모텀 리스크 |
| `/sprint` | 스프린트 관리 |
| `/meeting` | 회의록 정리 |
| `/stakeholders` | 이해관계자 맵 |
| `/roadmap` | 아웃컴 로드맵 |
| `/ab-test` | A/B 테스트 분석 |
| `/cohorts` | 코호트 분석 |
| `/marketing` | 마케팅 크리에이티브 |
| `/north-star` | North Star Metric |
| `/proofread` | 문법/흐름 체크 |
| `/apple [작업]` | Apple Neural Engine ML |
| `/market-intel` | MD 마켓 인텔리전스 |
| `/trend-radar` | 트렌드 레이더 (멀티소스 스코어링) |
| `/visual-factory` | 비주얼 팩토리 (채널별 에셋 생성) |
| `/demand-optimizer` | 수요 예측 & 가격 최적화 |
| `/design-generator` | AI 디자인 시안 생성 |
| `/color-intelligence` | 시즌 컬러 인텔리전스 |
| `/pattern-optimizer` | 패턴 & 소재 최적화 |

## 이중 스킬 라우팅 (FPOF vs KW 플러그인)

### 라우팅 판단 흐름
```
요청 수신
  ├─ 와키윌리/비케이브/패션/시즌/PDCA 키워드? → FPOF 스킬
  ├─ HR/법무/재무/엔지니어링/운영/영업/CS? → KW 플러그인
  ├─ 겹치는 영역?
  │   ├─ PDCA 단계 작업 중? / 프리셋 필요? → FPOF
  │   ├─ 외부 도구(CRM, Slack, Snowflake)? → KW 플러그인
  │   └─ 범용 프레임워크? → KW 플러그인
  └─ 모호? → 사용자에게 확인
```

### `@도메인` 명시적 호출
`@sales`, `@marketing`, `@data`, `@pm`, `@design`, `@eng`, `@hr`, `@legal`, `@finance`, `@ops`, `@cs`, `@search`, `@brand`, `@productivity`

## 에이전트 팀 상세

### 에이전시별 팀 구성 가이드
| 작업 유형 | 방식 | 팀원 수 |
|----------|------|---------|
| 시즌 전체 Plan | 에이전트 팀 | 3~4명 |
| 개별 아이템 디자인 | 서브에이전트 | 각 1명 |
| 병렬 마케팅 콘텐츠 | 서브에이전트 | 각 1명 |
| PDCA 단계 전환 검수 | 에이전트 팀 | 2~3명 |

### 프롬프트 템플릿
```
[팀 목적]: {작업 설명}
[모델 지시]: 팀원 모두 Sonnet을 사용해
[계획 승인]: 각 팀원은 구현 전에 반드시 계획을 작성하여 리드의 승인을 받을 것
[팀원 역할]: 팀원 1: {역할} — {스킬} ...
[완료 조건]: {기준}
[정리]: 모든 작업 완료 후 팀 정리
```

### 계획 자동 거절 기준
- 전사 가이드라인(`bcave/`) 미준수 → 거절
- 브랜드 프리셋(`wacky-willy/`) 미참조 → 거절
- 현재 PDCA 단계와 무관한 작업 → 거절
- `.fpof-state.json` 업데이트 누락 → 보완 요청

## 이중 트래킹 구조
| 구분 | 추적 위치 | 접두사 |
|------|----------|--------|
| 시즌 PDCA | `pdca.phases` | plan/design/do/check/act |
| 프로젝트 | `projects.[name]` | 자체 PDCA |
| 일상 운영 | `operational.weekly` | review/meeting/deck/board/sheet/report/data |
| 대시보드 | `operational.dashboard` | data/board |

## 온디맨드 유틸리티
- `format-converter`: 문서 포맷 변환 (`system/skills/task/format-conversion.md`)
- `apple-neural-engine`: 온디바이스 ML — OCR, 분류, 감정분석, NER (`/apple`)

## 문서 맵
- `docs/guide/` — 사용 매뉴얼, 퀵스타트, 플러그인 라우팅, 크롤러
- `docs/reference/` — 아키텍처, 컨벤션, 브랜드 원문 (presets=AI용, reference=사람용)
- `docs/workshop/` — AI Committee 워크숍 14세션
- `docs/generated/` — HTML/PDF 생성물

## PM-Skills 통합 (65개)
기존 스킬에 SWOT, RICE/ICE/Kano, GTM 모션, Pre-Mortem 등 보강.
신규: pm-strategy(10), pm-research(4), pm-gtm(3), pm-discovery(12), pm-execution(13), pm-analytics(3), pm-marketing(1), pm-toolkit(4)
