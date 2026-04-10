# 세션 13: OKR & 스프린트 관리

> **소요시간**: 30분 (설명 10분 + 데모 10분 + 실습 10분)
> **대상**: 관리자·팀 리더
> **목표**: 분기 OKR 수립, 스프린트 운영, 이해관계자 매핑을 실습

---

## 1. 프로젝트 관리 스킬 구조

```
/okrs ── 분기 OKR 수립 (5대 경영목표 연결)
  ↓
/roadmap ── 아웃컴 로드맵 변환 (기능→성과 중심)
  ↓
/stakeholders ── 이해관계자 맵 (Power × Interest)
  ↓
/sprint ── 스프린트 계획 / 회고 / 릴리즈
```

---

## 2. `/okrs` — OKR 수립

### 사용법

```
/okrs [팀 또는 목표 영역]
```

대상 생략 시 와키윌리 5대 경영목표 기준.

### 5대 경영목표와 자동 연결

| # | 경영목표 | OKR 연결 예시 |
|---|---------|-------------|
| 1 | 브랜드 아이덴티티 정립 | O: 코어타겟 인지도 1위 달성 |
| 2 | 히트상품 + IMC 강화 | O: 상위 20% 매출 기여 50% 돌파 |
| 3 | QR 비중 확대 | O: 인시즌 리오더 매출 비중 30% |
| 4 | 용품 라인업 경쟁력 | O: 용품 매출 YoY 40% 성장 |
| 5 | 글로벌 대응 강화 | O: 해외 D2C 매출 5억원 달성 |

### OKR 품질 검증

| 기준 | 체크 |
|------|------|
| 목표(O)가 영감적인가? | 팀을 결집시킬 만큼 |
| 핵심결과(KR)가 측정 가능한가? | 판단이 아닌 데이터로 |
| 70% 달성 = 잘 보정된 목표? | 너무 쉽거나 불가능하지 않은 |
| 게이밍 가능한 KR? | 카운터 메트릭 제안 |

### 실습

```
/okrs 마케팅팀 Q2
```

---

## 3. `/roadmap` — 아웃컴 로드맵

기능 나열 로드맵을 **성과(Outcome) 중심**으로 전환.

```
/roadmap
```

### 전환 예시

```
[기존] 기능 로드맵
4월: 자사몰 리뉴얼 → 5월: 무신사 단독 상품 → 6월: 글로벌 몰 오픈

[전환] 아웃컴 로드맵
4월: 자사몰 전환율 2.5% 달성 → 5월: 무신사 채널 매출 YoY +30% → 6월: 해외 D2C 첫 매출 발생
```

---

## 4. `/stakeholders` — 이해관계자 맵

```
/stakeholders [프로젝트명]
```

### Power × Interest 매트릭스

```
         High Power
    ┌─────────┬─────────┐
    │ 관리    │ 긴밀    │
    │ (Keep   │ 협업    │
    │ Satisfied)│(Manage  │
    │         │ Closely)│
    ├─────────┼─────────┤
    │ 모니터  │ 정보    │
    │ (Monitor│ 공유    │
    │  Only)  │(Keep    │
    │         │Informed)│
    └─────────┴─────────┘
  Low Interest      High Interest
```

각 이해관계자별 커뮤니케이션 빈도·방법·핵심 메시지를 포함.

---

## 5. `/sprint` — 스프린트 관리

### 3가지 모드

```
/sprint plan    → 스프린트 계획
/sprint retro   → 스프린트 회고
/sprint release → 릴리즈 노트
```

### 스프린트 계획 (plan)

| 요소 | 설명 |
|------|------|
| **용량 배분** | 팀원별 가용 시간 × 속도 계산 |
| **스토리 선택** | 우선순위 기반 작업 선택 |
| **의존성 매핑** | 팀 간·작업 간 의존성 식별 |
| **리스크 표시** | 블로커·불확실성 사전 식별 |

### 스프린트 회고 (retro)

3가지 프레임워크 중 선택:

| 프레임워크 | 구조 |
|-----------|------|
| **Start/Stop/Continue** | 시작할 것 / 멈출 것 / 계속할 것 |
| **4Ls** | Liked / Learned / Lacked / Longed for |
| **Sailboat** | 바람(추진력) / 닻(방해) / 암초(리스크) / 섬(목표) |

### 실습

```
/sprint retro
```

최근 2주 작업을 회고해 보세요.

---

## 6. 연계 워크플로우

### 분기 초 셋업

```
/okrs → 분기 OKR 수립
    ↓
/roadmap → 아웃컴 로드맵 전환
    ↓
/stakeholders → 이해관계자 커뮤니케이션 계획
    ↓
/sprint plan → 첫 스프린트 계획
```

### 분기 말 클로즈

```
/sprint retro → 스프린트 회고
    ↓
/metrics → KPI 달성 현황 점검
    ↓
OKR 스코어링 → 다음 분기 OKR 수립
```

---

## 참고 파일

| 파일 | 위치 |
|------|------|
| `/okrs` | `.claude/commands/okrs.md` |
| `/roadmap` | `.claude/commands/roadmap.md` |
| `/stakeholders` | `.claude/commands/stakeholders.md` |
| `/sprint` | `.claude/commands/sprint.md` |
| OKR 스킬 | `system/skills/pm-execution/brainstorm-okrs.md` |
| 로드맵 스킬 | `system/skills/pm-execution/outcome-roadmap.md` |
| 5대 경영목표 | `system/presets/wacky-willy/brand.config.json` |
