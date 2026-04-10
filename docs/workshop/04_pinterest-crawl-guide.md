# 세션 4: 핀터레스트 이미지 크롤링

> **소요시간**: 20분 (설명 5분 + 데모 5분 + 실습 10분)
> **대상**: 크리에이티브 스튜디오·마케팅 쇼룸 멤버
> **목표**: 핀터레스트에서 레퍼런스 이미지를 키워드별로 자동 수집하는 워크플로우 실습

---

## 1. 왜 핀터레스트 크롤링인가?

### 기존 문제
- 무드보드·트렌드 리서치 시 **수동으로 이미지를 하나씩 저장**
- 키워드별 분류가 안 되어 **폴더가 뒤섞임**
- 시간 소모가 크고, 빠뜨리는 이미지가 많음

### 해결
- 키워드 입력 → **자동으로 핀터레스트 검색 & 이미지 다운로드**
- 키워드별 **자동 폴더 분류**
- 한 번에 수십~수백 장 수집 가능

---

## 2. 사용법

### 기본 명령어

Claude Code에서 `/pinterest` 슬래시 명령어로 실행합니다.

```
/pinterest [키워드]
/pinterest [키워드] [수량]
```

### 사용 예시

```
# 기본 (기본 수량)
/pinterest dopamine dressing

# 수량 지정
/pinterest 텐션업코디 50

# 여러 키워드
/pinterest streetwear layering 2026
```

---

## 3. 키워드 설계 원칙

### 5단어 규칙

핀터레스트 검색은 **5단어 이내**가 가장 효과적입니다.

| 예시 | 단어 수 | 효과 |
|------|---------|------|
| `street fashion summer 2026` | 4 | ✅ 좋음 |
| `dopamine dressing colorful outfit` | 4 | ✅ 좋음 |
| `korean street fashion young trendy summer colorful oversized` | 8 | ❌ 너무 김 — 결과 분산 |

### 키워드 설계 팁

| 목적 | 추천 키워드 | 비추천 |
|------|-----------|--------|
| 트렌드 리서치 | `dopamine fashion 2026 summer` | `최신 유행 패션` (한글은 결과 적음) |
| 스타일링 레퍼런스 | `streetwear layering outfit` | `좋은 옷 코디` |
| 소재/패턴 | `mesh texture fabric detail` | `메시 소재` |
| 컬러 팔레트 | `pastel color palette fashion` | `예쁜 색깔 조합` |

> **팁**: 영문 키워드가 한글보다 결과가 풍부합니다. 한글이 필요하면 `한글키워드 + 영문보조어` 조합.

---

## 4. 폴더 분류 구조

수집된 이미지는 키워드별로 자동 분류됩니다:

```
workspace/pinterest/
├── dopamine-dressing/
│   ├── pin_001.jpg
│   ├── pin_002.jpg
│   └── ...
├── streetwear-layering/
│   ├── pin_001.jpg
│   └── ...
└── mesh-texture-detail/
    └── ...
```

---

## 5. 실무 활용 시나리오

### 시나리오 1: 시즌 무드보드 제작

```
1. /pinterest dopamine dressing summer 2026
2. /pinterest Y2K street fashion Korean
3. /pinterest oversized graphic tee styling
→ 수집된 이미지로 무드보드 구성
```

### 시나리오 2: 경쟁사 비주얼 벤치마크

```
1. /pinterest [경쟁사명] lookbook 2026
2. /pinterest [경쟁사명] campaign visual
→ 경쟁사 비주얼 톤앤매너 분석
```

### 시나리오 3: 소재·디테일 레퍼런스

```
1. /pinterest mesh fabric fashion detail
2. /pinterest patchwork denim 2026
3. /pinterest holographic material fashion
→ 디자인 스펙 작성 시 참고
```

### 시나리오 4: 매장 VM 레퍼런스

```
1. /pinterest retail display streetwear
2. /pinterest shop window summer visual
→ VM 기획 시 참고
```

---

## 6. 실습 과제

### 과제 1: 트렌드 키워드 수집
다음 키워드로 이미지를 수집해 보세요:
```
/pinterest kitsch fashion colorful 2026
```

### 과제 2: 나만의 키워드 설계
와키윌리 26SS 시즌에 맞는 키워드 3개를 직접 설계하고 수집해 보세요.

**키워드 설계 워크시트:**

| # | 목적 | 키워드 (5단어 이내) | 예상 수량 |
|---|------|-------------------|----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### 과제 3: 무드보드 소스 수집
크리에이티브 디렉터가 되어, 무드보드에 들어갈 4가지 카테고리의 이미지를 수집해 보세요:
1. 전체 무드/감성
2. 컬러 팔레트
3. 소재/텍스처
4. 스타일링/코디

---

## 7. 키워드 선택 인터랙션

Claude Code에서 `/pinterest`를 실행하면, AI가 키워드 후보를 제안합니다.
대화창 내에서 **클릭으로 키워드를 선택**할 수 있습니다 (별도 HTML 페이지를 열지 않음).

```
Claude: 다음 키워드 중 수집할 것을 선택하세요:

  (1) dopamine dressing summer 2026
  (2) Y2K street fashion colorful
  (3) oversized graphic tee Korean
  (4) kitsch pop art fashion

원하는 번호를 입력하세요 (복수 선택: 1,3,4):
```

---

## 8. 주의사항

- **대량 수집 시** 네트워크 부하에 주의 (100장 이상은 분할 수집 권장)
- **저작권**: 수집한 이미지는 **레퍼런스 용도로만** 사용. 상업적 사용 불가.
- **핀터레스트 이용약관** 준수 — 과도한 자동화 요청은 차단될 수 있음
- **회사 네트워크**에서 핀터레스트 접근이 차단된 경우 개인 네트워크 사용

---

## 참고 파일

| 파일 | 위치 |
|------|------|
| 크롤러 설치/활용 가이드 | `docs/guide/pinterest-crawler-guide.md` |
| 크롤링 스킬 정의 | `system/skills/creative/pinterest-crawl.md` |
