# 세션 11: 고객 리서치 종합

> **소요시간**: 30분 (설명 10분 + 데모 10분 + 실습 10분)
> **대상**: 마케팅·CX·MD
> **목표**: 페르소나·인터뷰·피드백 분석·고객 여정맵을 연결하는 리서치 파이프라인 실습

---

## 1. 고객 리서치 스킬 구조

```
/research-users ── 페르소나 + 세그먼트 + 여정맵 (3종 통합)
       ↓
/interview ── 인터뷰 스크립트 생성 + 결과 요약
       ↓
/analyze-feedback ── 리뷰·CS·SNS 감성 분석 + 테마 추출
```

---

## 2. `/research-users` — 고객 리서치 종합

### 사용법

```
/research-users [리서치 데이터 또는 대상]
```

데이터 생략 시 와키윌리 기존 페르소나(personas.json) 기반 심화 분석.

### 3가지를 한 번에 실행

| 단계 | 분석 | 산출물 |
|------|------|--------|
| **Step 1** | 페르소나 구축 | 3~4개 구별되는 페르소나 (이름, JTBD, 페인, 게인, 행동 패턴) |
| **Step 2** | 세그먼테이션 | 행동 기반 세그먼트 (규모, 상품 적합성, 지불 의향) |
| **Step 3** | 고객 여정 맵 | 인지→고려→구매→사용→재구매→옹호 (터치포인트, 감정, 이탈 지점) |

### 실습

```
/research-users
```

(와키윌리 UNI/WOMAN 페르소나 기반 심화 분석)

---

## 3. `/interview` — 고객 인터뷰

### 인터뷰 스크립트 생성

```
/interview 코어타겟 18-25 구매 동기 인터뷰
```

The Mom Test 방법론 기반:
- 가설 검증 질문이 아닌 **행동 기반 질문**
- "우리 옷 좋아요?"(X) → "마지막으로 옷 산 게 언제예요? 왜 그걸 골랐어요?"(O)

### 인터뷰 결과 요약

```
/interview 이 인터뷰 내용 정리해줘
→ [인터뷰 트랜스크립트 붙여넣기]
```

JTBD 기반 구조화:
- 인터뷰 정보 (일시, 참석자, 배경)
- 현재 솔루션 (지금 뭘 쓰고 있는지)
- 강점/약점 (현 솔루션의)
- 핵심 인사이트
- 와키윌리 적용 시사점

---

## 4. `/analyze-feedback` — 고객 피드백 분석

### 사용법

```
/analyze-feedback [피드백 데이터]
```

CSV, 텍스트, 파일 모든 형식 지원.

### 분석 내용

| 분석 | 설명 |
|------|------|
| **감성 스코어링** | 각 피드백 긍정/중립/부정 분류 |
| **테마 추출** | 반복 주제 식별 + 클러스터링 |
| **빈도 분석** | 테마별 출현 빈도 |
| **세그먼트 분석** | 고객 등급·채널별 감성 차이 |
| **트렌드 감지** | 시간에 따른 감성 변화 추이 |

### 실습

```
/analyze-feedback
"사이즈가 좀 크게 나와요. 디자인은 예쁜데 핏이 아쉬워요.
캠프키치 그래픽이 너무 귀여워서 바로 구매했어요!
소재가 생각보다 얇아요. 가격 대비 괜찮긴 한데...
색감이 사진이랑 똑같아요. 배송도 빠르고 만족합니다.
후드 조임끈이 빠지기 쉬워요. AS 문의 중입니다."
```

---

## 5. 연계 워크플로우

### 시즌 초 리서치 → 전략 수립

```
/research-users → 페르소나·세그먼트·여정맵
    ↓
/interview → 핵심 가설 인터뷰 검증
    ↓
/analyze-feedback → 기존 고객 피드백 분석
    ↓
/value-prop → JTBD 밸류 프로포지션 설계
    ↓
브랜드 전략 · MD 플래닝에 반영
```

### 시즌 중 모니터링

```
/analyze-feedback → 주간 리뷰·CS 감성 추이
    ↓
/cohorts → 코호트 리텐션 분석
    ↓
인사이트 기반 QR·마케팅 조정
```

---

## 참고 파일

| 파일 | 위치 |
|------|------|
| `/research-users` | `.claude/commands/research-users.md` |
| `/interview` | `.claude/commands/interview.md` |
| `/analyze-feedback` | `.claude/commands/analyze-feedback.md` |
| 페르소나 스킬 | `system/skills/pm-research/user-personas.md` |
| 세그먼테이션 스킬 | `system/skills/pm-research/user-segmentation.md` |
| 고객 여정 맵 스킬 | `system/skills/pm-research/customer-journey-map.md` |
| 인터뷰 스킬 | `system/skills/pm-discovery/interview-script.md` |
| 와키윌리 페르소나 | `system/presets/wacky-willy/personas.json` |
| 와키윌리 채널 | `system/presets/wacky-willy/channels.json` |
