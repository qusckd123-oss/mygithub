---
type: skill
id: visual-factory
name: 비주얼 팩토리
agency: marketing-showroom
role: 비주얼 팩토리 매니저 (Visual Factory Manager)
phase: do
triggers:
  - 상품 이미지 만들어줘
  - 채널별 비주얼 에셋 생성해줘
  - 무신사 상세 이미지 만들어줘
  - 상품 촬영 대체 에셋 만들어줘
  - 비주얼 팩토리 돌려줘
  - SNS 콘텐츠 이미지 세트 만들어줘
  - 룩북 이미지 생성해줘
  - PDP 비주얼 세트 만들어줘
  - 모델 착장 이미지 만들어줘
presets:
  - visual-identity.json
  - channels.json
  - tone-manner.json
  - personas.json
  - ip-bible.json
  - categories.json
feeds:
  - skills/marketing/visual-content.md
  - skills/marketing/copywriting.md
  - skills/creative/pinterest-crawl.md
outputs:
  - "workspace/[시즌]/[프로젝트]/do_visual-factory-sheet.md"
---

# 비주얼 팩토리

> 상품 이미지 하나를 입력받아 채널별 비주얼 에셋 풀세트를 자동 설계하는 생산 라인.
> 배경 연출, 모델 착장, 코디 조합, PDP 카피까지 채널 규격에 맞춘 에셋 매트릭스를 생성한다.

## 기존 스킬과의 관계

| 기존 스킬 | 역할 | visual-factory에서의 위치 |
|-----------|------|-------------------------|
| `visual-content` | 화보/영상 촬영 기획 (수동) | Step 2 촬영 디렉션의 기반, AI 생성과 실촬영 구분 |
| `copywriting` | PDP/SNS 카피 작성 | Step 5 카피 연동 — 이미지와 카피를 세트로 생성 |
| `pinterest-crawl` | 레퍼런스 이미지 수집 | Step 1 레퍼런스 소스 — 배경/무드/포즈 방향 참고 |

**visual-factory = visual-content의 "AI 비주얼 생산" 확장판**

실촬영 기획은 `visual-content`, AI 기반 대량 에셋 생산은 `visual-factory`가 담당.
카피는 `copywriting` 스킬을 호출하거나, 간단한 PDP 카피는 직접 생성한다.

## 언제 사용

- "무신사 상품 이미지 세트 만들어줘" — 채널 규격에 맞는 에셋 필요할 때
- "이 상품 SNS 콘텐츠 비주얼 만들어줘" — 마케팅 비주얼 대량 생산
- "룩북 이미지 10컷 만들어줘" — AI 기반 룩북 제작
- "촬영 없이 상품 이미지 뽑아줘" — 촬영 비용 절감이 필요할 때
- Do 단계에서 IMC 전략 확정 후, 대량 비주얼 에셋 생산 시

## 사전 준비

1. `.fpof-state.json` → 현재 시즌, 프로젝트 확인
2. `presets/wacky-willy/visual-identity.json` → 비주얼 스타일 기준
3. `presets/wacky-willy/channels.json` → 채널 구조 및 우선순위
4. `presets/wacky-willy/tone-manner.json` → 카피 톤 기준
5. `presets/wacky-willy/personas.json` → 모델/타겟 체형 참고
6. `presets/wacky-willy/ip-bible.json` → 캐릭터 활용 시
7. 상품 이미지 또는 디자인 스펙 (있을 경우):
   - `output/[시즌]/design/[아이템]-design-spec.md`
   - `output/[시즌]/design/[아이템]-moodboard.md`

---

## 실행 절차

### Step 0: 에셋 주문서 (AskUserQuestion)

비주얼 팩토리의 생산 범위를 설정한다.

```json
{
  "questions": [
    {
      "question": "어떤 아이템의 비주얼을 생성할까요?",
      "header": "아이템",
      "multiSelect": false,
      "options": [
        {"label": "특정 아이템", "description": "아이템명/디자인 스펙 지정"},
        {"label": "컬렉션 전체", "description": "시즌 라인업 전체 에셋 생성"},
        {"label": "히어로 아이템만", "description": "시즌 메인 아이템 집중"}
      ]
    },
    {
      "question": "어떤 채널용 에셋이 필요한가요?",
      "header": "채널",
      "multiSelect": true,
      "options": [
        {"label": "무신사 (외부몰)", "description": "860×1148, 화이트 배경, 상세 5컷+"},
        {"label": "자사몰", "description": "히어로 배너 + PDP 세트"},
        {"label": "인스타그램", "description": "피드 1080² + 스토리 1080×1920"},
        {"label": "룩북", "description": "에디토리얼 착장컷 세트"}
      ]
    },
    {
      "question": "비주얼 스타일은?",
      "header": "스타일",
      "multiSelect": false,
      "options": [
        {"label": "스트릿 무드", "description": "도심 배경, 자연광, 움직임 포즈"},
        {"label": "스튜디오 클린", "description": "화이트/그레이 배경, 제품 중심"},
        {"label": "키치 맥시멀", "description": "비비드 배경, 그래피티, IP 캐릭터"},
        {"label": "시즌 테마 맞춤", "description": "현재 시즌 컨셉에 맞춤"}
      ]
    },
    {
      "question": "카피도 함께 생성할까요?",
      "header": "카피 연동",
      "multiSelect": false,
      "options": [
        {"label": "PDP 카피 + SNS 캡션", "description": "이미지와 카피 풀세트"},
        {"label": "PDP 카피만", "description": "상품 상세 텍스트만"},
        {"label": "이미지만", "description": "카피 없이 비주얼만 생성"}
      ]
    }
  ]
}
```

---

### Step 1: 채널 규격 로드 (Channel Spec Sheet)

`channels.json` 기반으로 각 채널의 이미지 규격과 요구사항을 로드한다.

#### 무신사 (외부몰) 규격

| 컷 | 용도 | 사이즈 | 배경 | 요구사항 |
|----|------|--------|------|----------|
| 대표 이미지 | 썸네일/검색 노출 | 860×1148px | 화이트 (#FFFFFF) | 상품 전체 보이게, 여백 10%+ |
| 모델 착장 정면 | PDP 메인 | 860×1148px | 화이트/라이트그레이 | 전신 착장, 자연스러운 포즈 |
| 모델 착장 후면 | PDP 서브 | 860×1148px | 화이트/라이트그레이 | 후면 디테일 |
| 디테일 컷 1~3 | PDP 서브 | 860×1148px | 화이트 | 소재감, 프린트, 라벨, 봉제 |
| 코디네이트 컷 | PDP 서브 | 860×1148px | 라이프스타일 | 상하의+ACC 코디 제안 |

#### 자사몰 규격

| 컷 | 용도 | 사이즈 | 배경 | 요구사항 |
|----|------|--------|------|----------|
| 히어로 배너 | 메인 페이지 | 1920×800px | 시즌 테마 | 임팩트, 텍스트 오버레이 영역 |
| PDP 메인 | 상품 상세 | 1000×1300px | 화이트 | 고해상도, 확대 가능 |
| PDP 스타일링 | 코디 제안 | 1000×1300px | 무드 배경 | 3~5 코디 제안 |
| 카테고리 배너 | 카테고리 페이지 | 1200×400px | 시즌 테마 | 텍스트 영역 좌/우 |

#### 인스타그램 규격

| 컷 | 용도 | 사이즈 | 배경 | 요구사항 |
|----|------|--------|------|----------|
| 피드 — 무드 | 브랜드 감성 | 1080×1080px | 스트릿/무드 | 와키윌리 비주얼 톤 |
| 피드 — 상품 | 신상 소개 | 1080×1350px | 클린/무드 | 상품 중심, 카피 오버레이 |
| 스토리 | 인터랙티브 | 1080×1920px | 비비드 | CTA 영역, 스와이프업 |
| 릴스 커버 | 영상 썸네일 | 1080×1920px | 임팩트 | 텍스트 크게, 5초 내 주목 |

#### 룩북 규격

| 컷 | 용도 | 사이즈 | 배경 | 요구사항 |
|----|------|--------|------|----------|
| 에디토리얼 전신 | 룩북 메인 | 2000×3000px | 로케이션/스튜디오 | 고해상도, 감성적 |
| 착장 반신 | 룩북 서브 | 2000×2000px | 로케이션 | 상반신 디테일 |
| 디테일 크로즈업 | 룩북 서브 | 2000×2000px | 블러 배경 | 소재/디테일 강조 |

---

### Step 2: 비주얼 디렉션 설계 (Visual Direction)

`visual-identity.json` 기반으로 에셋 전체의 비주얼 톤을 설정한다.

#### 브랜드 비주얼 기본값

```
컬러 팔레트:
  - 주조: Black + Signature Yellow (#FEF200)
  - 보조: Sky Blue (#68A8DB) + White
  - 시즌 악센트: [trend-radar 또는 color-intelligence 결과 참조]

그래픽 스타일:
  - Bold outline + flat color fill
  - Doodle / Graffiti aesthetic
  - IP 캐릭터: KIKY, 릴리 — 필요 시 ip-bible.json 참조

포토 디렉션:
  - Street context, 자연광
  - 움직임이 있는 포즈
  - 레이아웃: asymmetric, bold-crop, text-overlay-ok
```

#### 스타일별 디렉션 프리셋

| 스타일 | 배경 | 조명 | 포즈 | 컬러 톤 |
|--------|------|------|------|---------|
| **스트릿 무드** | 도심 골목, 스케이트파크, 벽화 | 자연광, 골든아워 | 움직임, 캐주얼 | 하이콘트라스트, 비비드 |
| **스튜디오 클린** | 화이트/라이트그레이 무지 | 소프트박스, 균일광 | 정면/측면 정적 | 뉴트럴, 상품색 그대로 |
| **키치 맥시멀** | 네온 컬러 월, 그래피티 벽 | 네온/컬러 조명 | 과장된, 펑키 | 과포화, 팝아트 |
| **시즌 테마** | 시즌 무드보드 참조 | 테마 맞춤 | 테마 맞춤 | 시즌 팔레트 |

---

### Step 3: 에셋 매트릭스 생성 (Asset Matrix)

아이템 × 채널 × 컷 유형의 전체 매트릭스를 생성한다.

**매트릭스 포맷:**

```markdown
## 에셋 매트릭스

| # | 아이템 | 채널 | 컷 유형 | 사이즈 | 배경 | 포즈 | 파일명 |
|---|--------|------|---------|--------|------|------|--------|
| 1 | [아이템A] | 무신사 | 대표 이미지 | 860×1148 | 화이트 | 정면 전신 | do_vf_[아이템]_musinsa-hero.jpg |
| 2 | [아이템A] | 무신사 | 모델 착장 정면 | 860×1148 | 화이트 | 정면 전신 | do_vf_[아이템]_musinsa-front.jpg |
| 3 | [아이템A] | 인스타 | 피드 무드 | 1080×1080 | 스트릿 | 움직임 | do_vf_[아이템]_ig-mood.jpg |
| ... | | | | | | | |
```

**에셋 수량 가이드 (아이템당):**

| 채널 | 최소 | 표준 | 풀세트 |
|------|------|------|--------|
| 무신사 | 5컷 | 8컷 | 12컷+ |
| 자사몰 | 3컷 | 6컷 | 10컷+ |
| 인스타 | 2컷 | 4컷 | 8컷+ |
| 룩북 | 3컷 | 6컷 | 10컷+ |

---

### Step 4: 이미지 생성 프롬프트 설계 (Prompt Engineering)

에셋 매트릭스의 각 컷에 대해 이미지 생성 프롬프트를 설계한다.

#### 프롬프트 구조

```
[Subject]: 상품 설명 (아이템 유형, 소재, 컬러, 그래픽/프린트 디테일)
[Model]: 모델 설명 (연령대, 체형, 포즈, 표정)
[Setting]: 배경/환경 (로케이션, 조명, 시간대)
[Style]: 촬영 스타일 (카메라 앵글, 렌즈, 분위기)
[Brand]: 와키윌리 비주얼 키워드 (Doodle, Graffiti, Pop Art, Bold Lines, Vivid Colors)
[Technical]: 기술 스펙 (해상도, 비율, 배경색)
```

#### 프롬프트 예시 — 무신사 대표 이미지

```
A Korean male model in his early 20s wearing a [아이템 상세 설명].
Full-body front view, natural standing pose with slight attitude.
Clean white background (#FFFFFF), soft even studio lighting.
Fashion e-commerce product photography style, high resolution.
Sharp focus on garment details, natural fabric texture visible.
Aspect ratio 3:4 (860×1148px equivalent).
```

#### 프롬프트 예시 — 인스타 무드컷

```
A young Korean trendsetter wearing [아이템 상세 설명],
walking through a colorful Seoul street with graffiti walls.
Golden hour natural lighting, candid movement shot.
Wacky Willy brand aesthetic: bold, vivid colors, kitsch street vibe.
Pop art influenced composition with asymmetric framing.
Shot on 35mm lens, slight motion blur for dynamic feel.
Square format 1:1 (1080×1080px).
```

#### 프롬프트 예시 — 키치 맥시멀

```
A confident Gen-Z model posing against a neon yellow (#FEF200) wall
covered in doodle-style graffiti, wearing [아이템 상세 설명].
Playful, exaggerated pose with bold attitude.
Neon lighting mixing yellow and sky blue (#68A8DB).
Maximalist pop art aesthetic, vivid saturated colors.
Bold graphic overlays possible, text-overlay-friendly composition.
Vertical format 9:16 (1080×1920px).
```

#### IP 캐릭터 연동 프롬프트 (ip-bible.json 참조)

```
[기본 프롬프트] +
Include a small doodle-style [KIKY/릴리] character illustration
in the corner of the image, drawn in bold outline + flat color style.
Character should complement the outfit, not overpower the product.
```

**프롬프트 생성 규칙:**
- 프롬프트는 영문으로 작성 (생성 AI 최적화)
- 브랜드 키워드 5개 중 최소 2개 포함: Doodle, Graffiti, Pop Art, Bold Lines, Vivid Colors
- 시그니처 컬러 HEX 코드 명시 (#FEF200, #000000, #68A8DB)
- 코어 타겟 반영: 모델 연령 20대 초반, Korean, 트렌디한 분위기
- `photo_direction` 키워드 반영: Street context, 자연광, 움직임 포즈
- 금지: 로고 형태 변형, 3B 착장 (bta-guideline.md 준수)

---

### Step 5: 카피 연동 (Copy Integration)

사용자가 카피 연동을 선택한 경우, 각 채널에 맞는 텍스트를 생성한다.
`tone-manner.json`을 반드시 참조한다.

#### PDP 카피 세트 (무신사/자사몰)

```markdown
### [아이템명] PDP 카피

**상품명**: [국문] / [영문]

**한 줄 후크**: [스크롤 멈추는 첫 문장 — 유쾌하고 자유분방한 톤]

**상품 스토리** (3~5문장):
[시즌 테마 + IP 세계관 연결, Gen-Z 친화적 언어]

**셀링 포인트** (3개):
1. [기능적 장점]
2. [감성적 장점]
3. [스타일링 장점]

**추천 스타일링**:
[코디 제안 — BTA 크로스 조합]
```

#### SNS 캡션 세트 (인스타그램)

```markdown
### [아이템명] 인스타 캡션

**피드 캡션** (2~3줄):
[감성적, Gen-Z 언어, 이모지 적정]

**해시태그** (10~15개):
#와키윌리 #WackyWilly #[시즌태그] #[아이템태그] ...

**스토리 CTA**:
[스와이프업 유도 문구]
```

#### 카피 톤 체크 (매번 확인):
- [ ] 유쾌하고 자유분방한 톤?
- [ ] Gen-Z 친화적 언어?
- [ ] 브랜드 필수 어휘 포함? (와키윌리, KIKY 등)
- [ ] 금지 어휘 미사용? (저렴한, 짝퉁, 따라하기, 평범한)
- [ ] 채널에 맞는 톤과 길이?

---

### Step 6: 코디 조합 설계 (Coordination Matrix)

착장컷/코디컷을 위한 스타일링 조합을 설계한다.
`categories.json`의 히어로 아이템과 BTA 가이드라인을 참조한다.

#### BTA 크로스 코디 원칙

```
[Basic 하의] × [Trend 상의] × [Accent ACC]  ← 메인 조합
[Trend 하의] × [Basic 상의] × [Trend ACC]   ← 서브 조합
[Accent 상의] × [Basic 하의]                 ← IP/실험 조합
```

#### 코디 매트릭스

```markdown
| # | 상의 (BTA) | 하의 (BTA) | ACC (BTA) | 무드 | 대상 채널 |
|---|-----------|-----------|----------|------|----------|
| 1 | 그래픽 티 (T) | 데님 (B) | 플라이트 백팩 (A) | 스트릿 캐주얼 | 무신사/인스타 |
| 2 | 로고 스웻 (T) | 조거 (B) | 볼캡 (T) | 릴렉스 | 자사몰/룩북 |
| 3 | 릴리 크롭 가디건 (A) | 와이드 슬랙스 (B) | 캐릭터 폰케이스 (A) | 걸리시 | 인스타/룩북 |
```

**UNI / W 라인 구분:**
- UNI라인: 스트릿 캐주얼, 젠더뉴트럴 스타일링
- W라인: 걸리시, 페미닌, 유니크 포인트
- 코디당 라인 혼합 가능하되, 대상 채널의 주요 타겟 고려

---

### Step 7: 생산 시트 최종 출력

모든 설계를 하나의 생산 시트로 통합한다.

**에셋별 상태 추적:**

| 상태 | 의미 |
|------|------|
| `PROMPT` | 프롬프트 설계 완료, 생성 대기 |
| `GENERATED` | AI 이미지 생성 완료, 검수 대기 |
| `APPROVED` | 검수 통과, 채널 업로드 가능 |
| `REJECTED` | 검수 탈락, 재생성 필요 |
| `UPLOADED` | 채널 업로드 완료 |

---

## 산출물 포맷

```markdown
# [시즌] [프로젝트/아이템] 비주얼 팩토리 시트

## 작성일: YYYY-MM-DD
## 작성자: Visual Factory Manager
## 아이템: [대상 아이템/컬렉션]
## 채널: [대상 채널 목록]
## 비주얼 스타일: [선택된 스타일]

---

## 비주얼 디렉션

### 컬러 팔레트
[브랜드 기본 + 시즌 악센트]

### 포토 디렉션
[배경, 조명, 포즈, 분위기]

### IP 캐릭터 활용
[사용 여부, 캐릭터, 활용 방식]

---

## 에셋 매트릭스

| # | 아이템 | 채널 | 컷 유형 | 사이즈 | 배경 | 포즈 | 상태 | 파일명 |
|---|--------|------|---------|--------|------|------|------|--------|
| 1 | | | | | | | PROMPT | |
| ... | | | | | | | | |

**에셋 총계**: [N]컷 ([채널별 내역])

---

## 이미지 생성 프롬프트

### 컷 #1: [아이템] — [채널] [컷 유형]
```
[전체 프롬프트]
```

### 컷 #2: ...
[반복]

---

## 코디 조합

| # | 상의 (BTA) | 하의 (BTA) | ACC (BTA) | 무드 | 대상 채널 |
|---|-----------|-----------|----------|------|----------|
| 1 | | | | | |

---

## PDP 카피 (카피 연동 시)

### [아이템명]
- 상품명:
- 한 줄 후크:
- 상품 스토리:
- 셀링 포인트:
- 추천 스타일링:

---

## SNS 캡션 (카피 연동 시)

### [아이템명] 인스타그램
- 피드 캡션:
- 해시태그:
- 스토리 CTA:

---

## 생산 일정

| 단계 | 내용 | 예상 소요 | 비고 |
|------|------|----------|------|
| 프롬프트 설계 | 에셋 매트릭스 + 프롬프트 | 완료 | 본 시트 |
| AI 생성 | 이미지 생성 실행 | [N]컷 × [시간] | |
| 검수 | 브랜드 적합도 확인 | | visual-identity.json 기준 |
| 카피 작성 | PDP + SNS 카피 | | tone-manner.json 기준 |
| 업로드 | 채널별 업로드 | | |

## 비용 효과 (실촬영 대비)

| 항목 | 실촬영 (추정) | AI 생성 |
|------|-------------|---------|
| 모델 섭외 | ₩500,000~2,000,000 | ₩0 |
| 스튜디오 대여 | ₩300,000~1,000,000 | ₩0 |
| 포토그래퍼 | ₩500,000~1,500,000 | ₩0 |
| 보정/편집 | ₩200,000~500,000 | 프롬프트 조정 |
| 총 예상 | ₩1,500,000~5,000,000 | AI 생성 비용만 |

---

## 연결 스킬 (Next Actions)

| 후속 스킬 | 입력 데이터 | 추천 타이밍 |
|----------|-----------|-----------|
| `copywriting` | 에셋별 상세 카피 필요 시 | 에셋 승인 후 |
| `social-viral` | 인스타/TikTok 콘텐츠 런칭 시퀀스 | 에셋 완성 후 |
| `imc-strategy` | 채널별 에셋 배분 확정 | 에셋 매트릭스 확정 후 |
| `virtual-fitting` | 가상 피팅용 에셋 연동 | 자사몰/매장 적용 시 |
```

---

## 반복 실행 (에셋 추가 생산)

프로젝트 내에서 재실행 시:
- 기존 에셋 매트릭스를 로드하여 추가분만 생성
- 신규 채널/컷 유형 추가 가능
- 시즌 중 신상품 추가 시 동일 비주얼 디렉션 유지

---

## 완료 조건

- [ ] 에셋 매트릭스 작성 완료 (아이템 × 채널 × 컷)
- [ ] 채널 규격(사이즈/배경/포맷) 정확히 반영
- [ ] 이미지 생성 프롬프트 전 컷 작성 완료
- [ ] 프롬프트에 브랜드 비주얼 키워드 최소 2개 포함
- [ ] 코디 조합 BTA 크로스 원칙 준수
- [ ] 카피 연동 시 tone-manner.json 톤 체크 완료
- [ ] 생산 일정 및 비용 효과 산출

## 체크리스트

- [ ] visual-identity.json의 디자인 키워드(5개)가 프롬프트에 반영?
- [ ] channels.json의 채널 우선순위(high-growth)에 맞는 에셋 배분?
- [ ] personas.json 코어타겟 체형/스타일이 모델 디렉션에 반영?
- [ ] ip-bible.json 캐릭터 활용 시 세계관 정합성 확인?
- [ ] bta-guideline.md 준수? (3B 착장 금지, 로고 변형 금지)
- [ ] 시그니처 컬러(#FEF200, #000000, #68A8DB) 정확한 HEX 사용?
- [ ] 실촬영 vs AI 생성 구분이 명확한가?
- [ ] 금지 어휘(저렴한, 짝퉁, 따라하기, 평범한) 미사용 확인?
