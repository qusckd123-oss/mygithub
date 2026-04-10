# AI Committee 워크숍 — FPOF 시스템 업데이트 설명회

> **일시**: 2026년 3월
> **대상**: 비케이브 AI Committee 멤버
> **목적**: FPOF V2.2 시스템 업데이트 내용 공유 및 실습

---

## 워크숍 아젠다

| # | 세션 | 시간 | 내용 | 가이드 문서 |
|---|------|------|------|------------|
| 1 | **전사 방향성 공유** | 30분 | 리워크 프로세스 혁신 가이드 — 5대 전환, AI 조직 변혁, 브랜드 감도 | `01_rework-process-guide.md` |
| 2 | **Apple Neural Engine** | 40분 | 온디바이스 ML 스킬 — OCR·감정분석·이미지분류·사운드분류 실습 | `02_apple-neural-engine-guide.md` |
| 3 | **에이전트 팀 병렬 실행** | 30분 | tmux 기반 멀티 에이전트 — 프리셋 실행·모니터링·커스텀 구성 | `03_agent-team-tmux-guide.md` |
| 4 | **핀터레스트 크롤링** | 20분 | 레퍼런스 이미지 자동 수집 — 키워드 설계·5단어 규칙·폴더 분류 | `04_pinterest-crawl-guide.md` |
| 5 | **나만의 AI 스킬 만들기** | 40분 | Skill Creator — 스킬 구조 이해·SKILL.md 작성·테스트·배포 | `05_skill-creator-guide.md` |
| 6 | **회의록 & 보고서 요약** | 30분 | `/meeting` + Executive Summary — 트랜스크립트→회의록→경영진 보고서 | `06_meeting-summary-guide.md` |
| 7 | **프레젠테이션 만들기** | 35분 | `/deck` + PPTX 스킬 + Frontend Slides — 3가지 방식 비교·실습 | `07_presentation-guide.md` |
| 8 | **문서 생성 3종 세트** | 30분 | `/doc` `/sheet` `/pdf` — 워드·엑셀·PDF 자동 생성 | `08_document-generation-guide.md` |
| 9 | **교정 & 브랜드 보이스** | 25분 | `/proofread` + copywriting — 문법 교정·톤앤매너·채널별 카피 | `09_proofread-copywriting-guide.md` |
| 10 | **경쟁 분석 & 전략 프레임워크** | 35분 | `/market-scan` `/competitive` `/battlecard` — SWOT·PESTLE·Porter's·Ansoff | `10_competitive-strategy-guide.md` |
| 11 | **고객 리서치 종합** | 30분 | `/research-users` `/interview` `/analyze-feedback` — 페르소나·여정맵·감성분석 | `11_user-research-guide.md` |
| 12 | **데이터 분석 & 대시보드** | 35분 | `/north-star` `/metrics` `/cohorts` `/ab-test` — KPI·코호트·A/B테스트 | `12_data-analytics-guide.md` |
| 13 | **OKR & 스프린트 관리** | 30분 | `/okrs` `/sprint` `/roadmap` `/stakeholders` — 분기 목표·스프린트·회고 | `13_okr-sprint-guide.md` |
| 14 | **디스커버리 & 아이디에이션** | 30분 | `/discover` `/brainstorm` `/pre-mortem` `/triage` — 아이디어→가설→실험 | `14_discovery-ideation-guide.md` |
| 15 | **플러그인 에코시스템** | 35분 | 31개 플러그인 통합 — 프로젝트 단위 설치·이중 라우팅·@도메인 호출 | `15_plugin-ecosystem-guide.md` |

---

## 사전 준비사항

### 전원 필수
- [ ] Claude Code 최신 버전 설치 확인
- [ ] FPOF 프로젝트 `git pull` 완료
- [ ] 터미널(iTerm2 또는 Terminal.app) 준비

### Apple Neural Engine 세션 참가자
- [ ] Apple Silicon Mac (M1 이상) 확인
- [ ] macOS 15 (Sequoia) 이상 확인
- [ ] Xcode Command Line Tools 설치: `xcode-select --install`
- [ ] ANE CLI 컴파일: `cd system/apple-neural-engine/ane-cli && swiftc -O -o ane_tool ane_tool.swift`

### 에이전트 팀 세션 참가자
- [ ] tmux 설치 확인: `brew install tmux` (없는 경우)
- [ ] Claude Code CLI 사용 가능 확인: `claude --version`

### 핀터레스트 크롤링 세션 참가자
- [ ] Chrome 브라우저 설치
- [ ] Node.js 설치 확인

---

## 워크숍 진행 방식

1. **설명 (10~15분)**: 각 영역의 배경·목적·아키텍처 설명
2. **데모 (5~10분)**: 강사가 실제 실행 시연
3. **실습 (10~20분)**: 참가자가 직접 따라하기
4. **Q&A (5분)**: 질의응답 및 실무 적용 논의

---

## 문서 규칙

- 각 가이드는 **독립 실행 가능** — 순서 무관하게 개별 참조 가능
- 실습 예제는 모두 **와키윌리 브랜드 컨텍스트** 기반
- 명령어는 모두 **FPOF 프로젝트 루트**에서 실행하는 것을 기준으로 작성
