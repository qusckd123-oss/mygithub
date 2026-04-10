---
type: skill
id: design-generator
name: AI 디자인 제너레이터
agency: creative-studio
role: AI 디자인 제너레이터 (AI Design Generator)
phase: design
triggers:
  - 디자인 시안 만들어줘
  - AI로 디자인 뽑아줘
  - 이 아이템 시각화해줘
  - 디자인 배리에이션 만들어줘
  - 스케치를 디자인으로 만들어줘
  - 컬렉션 시안 생성해줘
  - 그래픽 티 디자인 아이디어 줘
  - 디자인 프롬프트 만들어줘
  - 아이템 브리프로 디자인 시안 만들어줘
presets:
  - visual-identity.json
  - categories.json
  - ip-bible.json
  - brand.config.json
  - personas.json
feeds:
  - skills/creative/moodboard.md
  - skills/creative/design-spec.md
  - skills/data/trend-radar.md
  - skills/creative/pinterest-crawl.md
outputs:
  - "workspace/[시즌]/[프로젝트]/design_generator-sheet.md"
---

# AI 디자인 제너레이터

> 텍스트 브리프, 아이템 브리프, 또는 스케치 이미지를 입력받아
> 와키윌리 브랜드 DNA에 맞는 디자인 시안 세트를 자동 생성하는 크리에이티브 엔진.
> 플랫 스케치 · 착장 룩 · 그래픽 디테일 · 컬러웨이 배리에이션 프롬프트를 한 번에 설계한다.

## 기존 스킬과의 관계

| 기존 스킬 | 역할 | design-generator에서의 위치 |
|-----------|------|--------------------------|
| `moodboard` | 시즌 비주얼 톤 설정 (수동) | Step 1 브리프에서 무드보드 방향 로드 |
| `design-spec` | 아이템별 상세 사양 정의 (수동) | Step 5 산출물이 design-spec 초안으로 연결 |
| `trend-radar` | 트렌드 스코어링 | Step 2 트렌드 적합 요소 자동 반영 |
| `pinterest-crawl` | 비주얼 레퍼런스 수집 | Step 1 레퍼런스 이미지 참조 |

**design-generator = moodboard → design-spec 사이를 잇는 "시각화 가속기"**

무드보드에서 방향을 잡고, design-generator로 시안을 빠르게 뽑고, 확정된 시안을 design-spec으로 상세화한다.

## 언제 사용

- "키치 오버사이즈 후드 디자인 시안 뽑아줘" — 자연어 → 디자인 시각화
- "이 스케치를 디자인으로 발전시켜줘" — 손 스케치 → 프레젠테이션급 시안
- "그래픽 티 디자인 5가지 배리에이션 만들어줘" — 변형 매트릭스 생성
- "이번 시즌 컬렉션 시안 한 번에 뽑아줘" — 복수 아이템 일괄 시안
- Design 단계에서 무드보드 완료 후, design-spec 작성 전

## 사전 준비

1. `.fpof-state.json` → 현재 시즌, 프로젝트 확인
2. `presets/wacky-willy/visual-identity.json` → 디자인 키워드, 컬러 팔레트, 그래픽 스타일
3. `presets/wacky-willy/categories.json` → 카테고리 구조, 히어로 아이템
4. `presets/wacky-willy/ip-bible.json` → IP 캐릭터 정보 (그래픽 활용 시)
5. `presets/wacky-willy/brand.config.json` → 포지셔닝 (UNI/W 구분)
6. 선행 산출물 (있으면 반영, 없으면 생략 가능):
   - `output/[시즌]/design/[아이템]-moodboard.md` — 무드보드
   - `workspace/[시즌]/[프로젝트]/design_item-brief.md` — 아이템 브리프
   - trend-radar 결과 — 트렌드 키워드

---

## 실행 절차

### Step 0: 디자인 브리프 입력 (AskUserQuestion)

```json
{
  "questions": [
    {
      "question": "어떤 아이템을 디자인할까요?",
      "header": "아이템",
      "multiSelect": false,
      "options": [
        {"label": "그래픽 티셔츠", "description": "반소매/긴소매 그래픽 프린트"},
        {"label": "스웻셔츠/후디", "description": "맨투맨/후드티 (오버사이즈 등)"},
        {"label": "아우터", "description": "자켓/코트/패딩/가디건"},
        {"label": "직접 입력", "description": "아이템 유형을 직접 지정"}
      ]
    },
    {
      "question": "라인은?",
      "header": "라인",
      "multiSelect": false,
      "options": [
        {"label": "UNI (유니섹스)", "description": "스트릿 캐주얼, 트렌드 재해석"},
        {"label": "W (우먼스)", "description": "유니크 걸리시 캐주얼"},
        {"label": "ACC (용품)", "description": "캐릭터 굿즈, 기능성 아이템"}
      ]
    },
    {
      "question": "입력 소스는?",
      "header": "입력",
      "multiSelect": false,
      "options": [
        {"label": "자연어 브리프", "description": "텍스트로 원하는 디자인 설명"},
        {"label": "아이템 브리프 파일", "description": "기존 design_item-brief.md 참조"},
        {"label": "스케치 이미지", "description": "손 스케치 사진을 디자인으로 변환"},
        {"label": "레퍼런스 이미지", "description": "참고 이미지를 와키윌리 스타일로 재해석"}
      ]
    },
    {
      "question": "배리에이션 몇 개 생성할까요?",
      "header": "배리에이션",
      "multiSelect": false,
      "options": [
        {"label": "3개 (핵심)", "description": "핵심 방향 3가지"},
        {"label": "5개 (표준)", "description": "충분한 선택지"},
        {"label": "10개+ (전수)", "description": "컬러웨이/그래픽 매트릭스 포함"}
      ]
    }
  ]
}
```

---

### Step 1: 브리프 파싱 & 브랜드 필터

입력 소스에서 디자인 요소를 추출하고 브랜드 DNA를 적용한다.

#### 1-A: 자연어 브리프 파싱

사용자 텍스트에서 6가지 디자인 요소를 추출한다:

```
① 아이템 유형: 티셔츠, 후디, 자켓, 가디건, 팬츠 ...
② 핏/실루엣: 오버사이즈, 크롭, 레귤러, 와이드, 박시 ...
③ 소재: 코튼, 스웨트, 나일론, 데님, 니트 ...
④ 그래픽/디테일: 프린트, 자수, 와펜, 패치, 컷아웃, 지퍼 ...
⑤ 컬러: 구체적 색상 또는 톤 (비비드, 파스텔, 모노 ...)
⑥ 무드/맥락: 스트릿, 캠퍼스, 페스티벌, 레트로, 키치 ...
```

#### 1-B: 스케치 이미지 파싱

이미지를 분석하여 위 6요소를 추출한다:
- 실루엣/프로포션 읽기
- 디테일 (포켓, 지퍼, 봉제선) 식별
- 그래픽 배치 위치/크기 파악
- 텍스트/로고 요소 확인

#### 1-C: 브랜드 DNA 필터

추출된 요소에 와키윌리 브랜드 DNA를 적용:

```
✅ 와키윌리 DNA 체크리스트:
□ Kitsch Street 감성과 충돌하지 않는가?
□ 디자인 키워드 5개 중 최소 1개 반영 가능?
  (Doodle, Graffiti, Pop Art, Bold Lines, Vivid Colors)
□ IP 캐릭터 접목 가능성? (접목 시 ip-bible.json 참조)
□ 코어타겟(18~25세 트렌드리더)이 "입고 싶다"고 느끼는가?
□ 3B 착장 금지 — bta-guideline.md 준수?
□ 로고 형태 변형 금지?

❌ DNA 충돌 시:
- 어떤 요소가 충돌하는지 사용자에게 알림
- 와키윌리 스타일로 재해석한 대안 제시
```

#### 1-D: 라인별 스타일 프리셋

| 라인 | 핏 경향 | 그래픽 경향 | 컬러 경향 | 타겟 감성 |
|------|---------|-----------|----------|----------|
| **UNI** | 오버사이즈/박시 | 볼드 그래픽, IP 캐릭터 대형 | 비비드, 하이콘트라스트 | "멋있다", "쿨하다" |
| **W** | 크롭/핏티드/레귤러 | 포인트 자수, 미니 캐릭터 | 파스텔+포인트, 페미닌 | "예쁘다", "유니크하다" |
| **ACC** | N/A | 캐릭터 전면, 아이코닉 | 시그니처(Yellow/Black) | "갖고 싶다", "귀엽다" |

---

### Step 2: 디자인 컨셉 생성

파싱 결과를 바탕으로 디자인 컨셉 배리에이션을 생성한다.

#### 컨셉 매트릭스

각 배리에이션은 아래 축 중 1~2개를 변화시킨다:

```
축 1: 실루엣 변형 (오버사이즈 ↔ 크롭 ↔ 레귤러)
축 2: 그래픽 변형 (대형 프린트 ↔ 미니 포인트 ↔ 올오버)
축 3: 소재 변형 (헤비 스웨트 ↔ 라이트 코튼 ↔ 기능성)
축 4: 컬러 변형 (비비드 ↔ 모노 ↔ 파스텔)
축 5: IP 변형 (KIKY 변신 ↔ 릴리 ↔ 프렌즈 그룹 ↔ IP 없음)
```

#### 배리에이션 테이블

```markdown
| # | 컨셉명 | 변형 축 | 실루엣 | 그래픽 | 소재 | 컬러 | IP | 무드 |
|---|--------|--------|--------|--------|------|------|---|------|
| V1 | [이름] | 실루엣+그래픽 | | | | | | |
| V2 | [이름] | 컬러+IP | | | | | | |
| V3 | [이름] | 소재+실루엣 | | | | | | |
```

---

### Step 3: 플랫 스케치 프롬프트 생성

각 배리에이션의 도식화(플랫 스케치)용 이미지 생성 프롬프트를 설계한다.

#### 플랫 스케치 프롬프트 구조

```
[View]: Front view / Back view flat lay technical fashion sketch
[Item]: [아이템 유형] with [핵심 디테일]
[Silhouette]: [핏/기장/프로포션]
[Details]: [네크라인, 소매, 포켓, 밑단, 봉제 등]
[Graphic]: [프린트/자수/와펜 위치, 크기, 내용]
[Color]: [메인 컬러 + 배색]
[Style]: Clean technical flat sketch, fashion design illustration,
         black outline on white background, no model, no shadow,
         professional garment technical drawing
[Technical]: High resolution, clean lines, precise proportions
```

#### 프롬프트 예시 — 키키 그래픽 오버사이즈 후디 (정면)

```
Front view flat lay technical fashion sketch of an oversized hoodie.
Drop shoulder, relaxed boxy fit, hip length.
Kangaroo pocket at front, ribbed cuffs and hem.
Large graphic print on chest: a bold doodle-style character illustration
in pop art aesthetic with vivid yellow (#FEF200) and black (#000000).
Main body color: white with sky blue (#68A8DB) hood lining.
Clean technical flat sketch, black outline on white background,
no model, no shadow, professional garment technical drawing.
High resolution, clean lines, precise proportions.
```

#### 뷰별 프롬프트 세트 (배리에이션당)

| 뷰 | 용도 | 프롬프트 차이점 |
|----|------|---------------|
| 정면 (Front) | 메인 디자인 확인 | 그래픽/디테일 풀 표현 |
| 후면 (Back) | 후면 디자인 | 후면 그래픽/프린트 위치 |
| 디테일 (Detail) | 핵심 디테일 클로즈업 | 특정 부분 확대 |

---

### Step 4: 착장 룩 프롬프트 생성

디자인 시안을 실제 착장 이미지로 시각화하는 프롬프트를 설계한다.

#### 착장 룩 프롬프트 구조

```
[Model]: Korean [male/female] model in early 20s, [체형]
[Outfit]: Wearing [아이템 상세 설명 — Step 3 내용 활용]
[Styling]: Paired with [하의, 신발, ACC — BTA 크로스 코디]
[Setting]: [배경 — visual-identity.json 포토 디렉션 참조]
[Mood]: [분위기 — 브랜드 감성]
[Brand]: Wacky Willy aesthetic — [디자인 키워드 2~3개]
[Camera]: [렌즈/앵글/라이팅]
[Format]: [비율]
```

#### 착장 룩 스타일 프리셋

| 프리셋 | 배경 | 포즈 | 무드 | 용도 |
|--------|------|------|------|------|
| **스트릿** | 도심 골목/벽화 | 움직임, 캐주얼 | 자유분방 | 룩북/인스타 |
| **스튜디오** | 라이트그레이 | 정면/측면 | 클린 | PDP/무신사 |
| **에디토리얼** | 로케이션 | 연출 포즈 | 감성적 | 캠페인/화보 |
| **키치** | 네온 컬러 월 | 과장된/펑키 | 에너지틱 | SNS/바이럴 |

---

### Step 5: 그래픽/프린트 프롬프트 생성 (해당 시)

그래픽 아이템의 경우, 프린트 디자인 자체를 독립 생성한다.

#### 그래픽 프롬프트 구조

```
[Subject]: [캐릭터/모티프/텍스트 설명]
[Style]: Wacky Willy brand style — bold outline, flat color fill,
         doodle/graffiti aesthetic, pop art influenced
[Color]: [사용 컬러 — 시그니처 컬러 우선]
[Composition]: [배치, 크기, 여백]
[Technical]: Vector-ready illustration, clean edges,
             print-ready for garment application
[Size]: Suitable for [가슴 프린트 / 등 전면 / 소매] placement
```

#### IP 캐릭터 활용 시 (ip-bible.json 참조)

| 캐릭터 | 그룹 | 활용 | 프롬프트 추가 |
|--------|------|------|-------------|
| **KIKY** | A (메인) | 변신 모드 활용 | "KIKY character in [변신 테마] transformation, doodle style" |
| **릴리** | A (메인) | 여성스러운 포인트 | "Lilly character floating gently, soft pastel accent" |
| **레오** | A (메인) | 캐주얼/유머 | "Leo the leopard cat, lazy confident pose" |
| **쿼바오** | A (메인) | 여행/어드벤처 | "Quokka-bao munching, travel adventure theme" |
| **하운드** | A (메인) | 로맨틱/츤데레 | "Hound heart-shaped silhouette, tsundere expression" |
| 프렌즈 그룹 | A 전체 | 그룹샷 | "Wacky Universe friends group, playful interaction" |

**KIKY 변신 프롬프트 규칙:**
- 변신 테마는 시즌 컨셉과 연결 (예: 시즌 테마 "서핑" → KIKY 서퍼 변신)
- ip-bible.json의 기존 변신 예시 참조: 자유의 여신상, 바이커, 화가, 복서, 낚시꾼, 식물, 파일럿, 기사
- 신규 변신 테마 창작 가능 — 와키윌리 DNA와 정합성 필수

---

### Step 6: 컬러웨이 매트릭스

각 배리에이션의 컬러 변형을 매트릭스로 설계한다.

#### 시그니처 컬러 기반 (visual-identity.json)

```
Primary:
  - Signature Yellow (#FEF200) × Black (#000000) — 브랜드 시그니처
  - Black (#000000) × White (#FFFFFF) — 클래식

Secondary:
  - Sky Blue (#68A8DB) × White — 시즌 악센트
  - Signature Yellow × Sky Blue — 포인트 조합

시즌 추가: [trend-radar 또는 color-intelligence 결과 반영]
```

#### 컬러웨이 테이블

```markdown
| # | 컬러웨이명 | 바디 | 배색1 | 배색2 | 그래픽 | BTA | 비고 |
|---|-----------|------|-------|-------|--------|-----|------|
| C1 | 시그니처 | #000000 | #FEF200 | — | #FEF200 | T | 메인 컬러 |
| C2 | 클래식 | #FFFFFF | #000000 | — | #000000 | B | 베이직 |
| C3 | 스카이 | #68A8DB | #FFFFFF | — | #FFFFFF | T | 시즌 |
| C4 | [시즌색] | | | | | A | 악센트 |
```

**BTA 컬러 배분 원칙:**
- Basic: 블랙, 화이트, 그레이 — 안정적, 리오더 대상
- Trend: 시그니처 컬러, 시즌 트렌드 컬러 — 시즌 메인
- Accent: 실험적 컬러, 한정 컬러 — 화제성, IP 특별판

---

### Step 7: 디자인 시트 최종 출력

모든 설계를 통합한 디자인 제너레이터 시트를 생성한다.

---

## 산출물 포맷

```markdown
# [시즌] [아이템] 디자인 제너레이터 시트

## 작성일: YYYY-MM-DD
## 작성자: AI Design Generator
## 아이템: [아이템 유형]
## 라인: [UNI / W / ACC]
## 입력 소스: [자연어/브리프파일/스케치/레퍼런스]

---

## 디자인 브리프 분석

### 추출된 디자인 요소
| 요소 | 내용 |
|------|------|
| 아이템 유형 | |
| 핏/실루엣 | |
| 소재 | |
| 그래픽/디테일 | |
| 컬러 | |
| 무드/맥락 | |

### 브랜드 DNA 체크
[체크리스트 결과]

---

## 디자인 배리에이션

| # | 컨셉명 | 변형 축 | 실루엣 | 그래픽 | 소재 | 컬러 | IP | 무드 |
|---|--------|--------|--------|--------|------|------|---|------|

---

## 플랫 스케치 프롬프트

### V1: [컨셉명]

#### 정면 (Front)
```
[프롬프트]
```

#### 후면 (Back)
```
[프롬프트]
```

#### 디테일
```
[프롬프트]
```

### V2: [컨셉명]
[반복]

---

## 착장 룩 프롬프트

### V1: [컨셉명] — [스타일 프리셋]
```
[프롬프트]
```

### V2: ...
[반복]

---

## 그래픽/프린트 프롬프트 (해당 시)

### 그래픽 #1: [이름]
```
[프롬프트]
```

### IP 캐릭터 활용
[캐릭터, 변신 테마, 활용 방식]

---

## 컬러웨이 매트릭스

| # | 컬러웨이명 | 바디 | 배색1 | 배색2 | 그래픽 | BTA |
|---|-----------|------|-------|-------|--------|-----|

---

## design-spec 연동 데이터

확정된 배리에이션을 design-spec 스킬로 전달할 데이터:

| 항목 | V[확정 번호] |
|------|-------------|
| 실루엣 | |
| 핵심 디테일 | |
| 소재 | |
| 컬러웨이 | |
| 그래픽 위치/기법/사이즈 | |
| IP 캐릭터 | |

---

## 연결 스킬 (Next Actions)

| 후속 스킬 | 입력 데이터 | 추천 타이밍 |
|----------|-----------|-----------|
| `design-spec` | 확정 배리에이션 → 상세 사양서 | 시안 승인 후 |
| `visual-factory` | 확정 디자인 → 채널별 에셋 | design-spec 완료 후 |
| `costing-ve` | 소재/디테일 → 원가 검증 | design-spec과 동시 |
| `moodboard` | 추가 레퍼런스 필요 시 | 시안 방향 조정 시 |
| `trend-radar` | 트렌드 적합도 재검증 | 시즌 중간 디자인 시 |
```

---

## 반복 실행

같은 아이템에 대해 재실행 시:
- 이전 배리에이션 결과를 로드하여 "좋았던 방향" 유지
- 사용자 피드백을 반영한 조정 배리에이션 추가 생성
- 컬러웨이/그래픽만 변형하는 "미세 조정" 모드 지원

---

## 완료 조건

- [ ] 디자인 브리프 6요소 추출 완료
- [ ] 브랜드 DNA 체크 통과
- [ ] 배리에이션 요청 수량만큼 생성
- [ ] 배리에이션당 플랫 스케치 프롬프트 (정면+후면) 완료
- [ ] 착장 룩 프롬프트 최소 1종 이상
- [ ] 그래픽 아이템의 경우 프린트 프롬프트 완료
- [ ] 컬러웨이 매트릭스 (최소 3색) 완료
- [ ] design-spec 연동 데이터 정리

## 체크리스트

- [ ] visual-identity.json 디자인 키워드(5개) 반영?
- [ ] 시그니처 컬러 HEX 정확히 사용? (#FEF200, #000000, #68A8DB)
- [ ] IP 캐릭터 사용 시 ip-bible.json 그룹/관계 준수?
- [ ] KIKY 변신 테마가 시즌 컨셉과 연결?
- [ ] 라인별 스타일 프리셋(UNI/W/ACC) 적용?
- [ ] bta-guideline.md 준수? (3B 착장 금지, 로고 변형 금지)
- [ ] categories.json 히어로 아이템과의 정합성?
- [ ] 코어타겟(18~25세)이 "입고 싶다"고 느끼는 디자인인가?
- [ ] 플랫 스케치 프롬프트가 생산자 이해 가능한 수준인가?
