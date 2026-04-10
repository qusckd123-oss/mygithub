# 세션 2: Apple Neural Engine 온디바이스 ML

> **소요시간**: 40분 (설명 10분 + 데모 10분 + 실습 15분 + Q&A 5분)
> **대상**: Apple Silicon Mac 사용자
> **목표**: ANE CLI 도구를 직접 실행하고, 실무에서 활용할 수 있는 시나리오를 체험

---

## 1. Apple Neural Engine이란?

### 핵심 개념
- Apple Silicon 칩에 내장된 **NPU (Neural Processing Unit)**
- ML 연산을 전용 하드웨어로 가속 (M4: 38 TOPS)
- **완전 오프라인** — 데이터가 기기를 떠나지 않음
- **무료** — API 비용 없음
- **빠름** — OCR 0.6초, NLP 즉시 반응

### ANE가 가속하는 8개 프레임워크

| # | 프레임워크 | 주요 기능 | 패션 업무 활용 |
|---|-----------|----------|-------------|
| 1 | **Vision** | 이미지/비디오 분석 | 룩북 OCR, 상품 이미지 분류, 미적 평가 |
| 2 | **NaturalLanguage** | 텍스트 분석 | 리뷰 감정분석, 언어감지, 개체명추출 |
| 3 | **SoundAnalysis** | 소리 분류 (303종) | 매장 음악/환경음 분류 |
| 4 | **Speech** | 음성→텍스트 | 회의 녹취 변환 |
| 5 | **Translation** | 온디바이스 번역 | 해외 바이어 소통, 라벨 번역 |
| 6 | **Create ML** | 모델 훈련 | 커스텀 상품 분류기 훈련 |
| 7 | **Core ML** | ML 모델 추론 | 커스텀 .mlmodel 실행 |
| 8 | **FoundationModels** | 온디바이스 LLM | Apple Intelligence 3B 모델 (macOS 26+) |

---

## 2. 사전 준비 (실습 전 반드시)

### Step 1: 시스템 요구사항 확인

```bash
# Apple Silicon 확인
uname -m
# 출력이 arm64 이면 OK

# macOS 버전 확인
sw_vers
# macOS 15 이상이면 OK
```

### Step 2: CLI 도구 컴파일

```bash
# FPOF 프로젝트 루트로 이동
cd "/Users/sherman/07. FPOF V2.2 Claude"

# ANE CLI 컴파일
cd system/apple-neural-engine/ane-cli
swiftc -O -o ane_tool ane_tool.swift

# 컴파일 확인
./ane_tool devices
```

**예상 출력:**
```json
{"neural_engine": true, "devices": ["NeuralEngine", "GPU", "CPU"]}
```

> ⚠️ `swiftc` 명령이 없으면: `xcode-select --install` 실행 후 재시도

### Step 3: 테스트 이미지 준비

실습에 사용할 파일을 준비합니다:
- **이미지 파일** 1~2개 (룩북, 상품 사진, 텍스트가 포함된 이미지 등)
- **텍스트** (리뷰, 상품 설명 등)

---

## 3. 실습 1: Neural Engine 상태 확인

```bash
./ane_tool devices
```

**확인 포인트:**
- `neural_engine: true` 가 나오면 ANE 사용 가능
- `devices` 배열에 NeuralEngine, GPU, CPU가 모두 포함되어야 함

---

## 4. 실습 2: OCR (텍스트 인식)

이미지에서 텍스트를 추출합니다. 한국어·영어·일본어 모두 지원.

```bash
# 이미지 파일에서 텍스트 추출
./ane_tool ocr /path/to/image.png
```

**예상 출력:**
```json
{
  "text": ["와키윌리", "WACKY WILLY", "2026 S/S COLLECTION"],
  "confidence": [0.98, 0.99, 0.97],
  "language": "ko-KR"
}
```

### 실무 활용 시나리오

| 시나리오 | 설명 |
|---------|------|
| **룩북 텍스트 추출** | 촬영 시안의 타이포그래피 검수 |
| **경쟁사 카탈로그 분석** | 스캔 이미지에서 상품명·가격 추출 |
| **핸드라이팅 디자인 메모** | 손으로 적은 스케치 메모 디지털화 |
| **라벨/태그 인식** | 케어라벨, 원산지 라벨 텍스트 추출 |

### 실습 과제
1. 자신의 데스크톱에 있는 아무 이미지(스크린샷도 OK)에 OCR을 실행해 보세요
2. 한국어와 영어가 섞인 이미지를 시도해 보세요

---

## 5. 실습 3: 감정 분석 (Sentiment)

텍스트의 긍정/부정/중립을 판단합니다.

```bash
# 긍정 예시
./ane_tool sentiment "이번 시즌 와키윌리 컬렉션 진짜 예쁘다"

# 부정 예시
./ane_tool sentiment "디자인은 괜찮은데 소재가 좀 아쉽네요"

# 중립 예시
./ane_tool sentiment "와키윌리 매장이 성수에 있습니다"
```

**예상 출력:**
```json
{
  "text": "이번 시즌 와키윌리 컬렉션 진짜 예쁘다",
  "score": 0.85,
  "label": "positive"
}
```

**점수 해석:**
- **0.5 이상** → Positive (긍정)
- **-0.5 ~ 0.5** → Neutral (중립)
- **-0.5 이하** → Negative (부정)

### 실무 활용 시나리오

| 시나리오 | 설명 |
|---------|------|
| **고객 리뷰 분석** | 무신사/자사몰 리뷰 감정 스코어링 |
| **SNS 반응 모니터링** | 캠페인 댓글 긍정/부정 비율 |
| **CS 분류** | 고객 문의 긴급도 자동 분류 |

### 실습 과제
1. 최근 와키윌리 리뷰 3개를 복사해서 감정 분석해 보세요
2. 같은 의미를 다른 표현으로 작성하고 점수 차이를 비교해 보세요

---

## 6. 실습 4: 이미지 분류 (Classify)

이미지가 무엇인지 자동 식별합니다.

```bash
./ane_tool classify /path/to/product-image.jpg
```

**예상 출력:**
```json
{
  "classifications": [
    {"label": "jersey, T-shirt", "confidence": 0.82},
    {"label": "sweatshirt", "confidence": 0.11},
    {"label": "wool", "confidence": 0.03}
  ]
}
```

### 실무 활용 시나리오
- 상품 이미지 **자동 카테고리 태깅** (대량 이미지 분류 시)
- 경쟁사 이미지 수집 후 **아이템 유형 자동 분류**

---

## 7. 실습 5: 미적 평가 (Aesthetics)

이미지의 품질 점수를 0~1 범위로 매깁니다.

```bash
./ane_tool aesthetics /path/to/lookbook-image.jpg
```

**예상 출력:**
```json
{
  "overall_score": 0.78,
  "utility_score": 0.65
}
```

**점수 해석:**
- **overall_score**: 전체 미적 품질 (0.7 이상이면 양호)
- **utility_score**: 실용적 품질 (선명도, 구도 등)

### 실무 활용 시나리오
- **룩북 사진 선별** — 대량 촬영 후 품질 높은 컷 자동 선별
- **SNS 콘텐츠 QC** — 게시 전 이미지 품질 사전 검수
- **경쟁사 비주얼 벤치마크** — 비주얼 품질 정량 비교

### 실습 과제
1. 룩북 이미지 2~3장의 미적 점수를 비교해 보세요
2. 같은 상품의 다른 각도 사진 점수를 비교해 보세요

---

## 8. 실습 6: 언어 감지 & NER

```bash
# 언어 감지
./ane_tool language "ワッキーウィリーの新しいコレクション"
# 출력: {"language": "ja", "confidence": 0.99}

# 개체명 인식 (NER) — 인명, 지명, 조직명 추출
./ane_tool ner "와키윌리의 지젤이 서울 성수동 플래그십 스토어에서 팬사인회를 합니다"
# 출력: {"entities": [{"text":"와키윌리","type":"Organization"}, {"text":"지젤","type":"Person"}, {"text":"성수동","type":"Place"}]}
```

### 실무 활용 시나리오
- **다국어 리뷰 자동 분류** — 한/영/일/중 리뷰 언어별 라우팅
- **보도자료 분석** — 브랜드명, 인물명, 지역명 자동 추출
- **해외 바이어 커뮤니케이션** — 수신 메시지 언어 자동 감지

---

## 9. 실습 7: 사운드 분류

```bash
./ane_tool sound /path/to/audio-file.wav
```

303개 카테고리 분류 가능 (음성, 음악, 동물, 환경음 등)

### 실무 활용 시나리오
- **매장 환경음 분석** — 매장 내 음악/소음 비율 측정
- **이벤트 현장 모니터링** — 팝업스토어 현장음 분류

---

## 10. Claude Code에서 사용하기

### `/apple` 슬래시 명령어

CLI를 직접 실행하지 않아도, Claude Code에서 자연어로 호출할 수 있습니다.

```
/apple 이 이미지에서 텍스트 추출해줘
/apple 이 텍스트의 감정 분석해줘
/apple 이 사진의 미적 점수 매겨줘
/apple Neural Engine 상태 확인
```

**애매한 요청 시 자동 질문:**
```
/apple 이 파일 분석해줘
→ "어떤 분석을 원하시나요? (1) OCR (2) 분류 (3) 미적 평가 ..."
```

### Python에서 사용

```python
import subprocess, json

def ane(cmd, arg):
    return json.loads(subprocess.run(
        ["ane_tool", cmd, arg],
        capture_output=True, text=True, timeout=30
    ).stdout)

# 사용 예시
result = ane("sentiment", "이번 시즌 정말 좋다")
print(result["label"])  # "positive"
```

---

## 11. FPOF 파이프라인 통합

ANE는 다른 FPOF 스킬의 **품질 보조 레이어**로 활용됩니다:

| FPOF 스킬 | ANE 연동 | 효과 |
|-----------|---------|------|
| `copywriting` | 감정분석으로 톤 검증 | 브랜드 톤앤매너 일관성 체크 |
| `visual-content` | 미적 평가로 이미지 QC | 게시 전 품질 자동 검수 |
| `trend-research` | OCR로 해외 매거진 분석 | 비디지털 소스 텍스트 추출 |
| `quality-gate` | 다중 검증 레이어 | OCR 교차검증, 감정 일관성 체크 |

---

## 12. 제한사항 & 주의사항

| 가능 (ANE 가속) | 불가능 (ANE 범위 밖) |
|----------------|-------------------|
| OCR (한/영/일/중 등) | 이미지 **생성** (Stable Diffusion 등) |
| 이미지 분류/객체 감지 | 비디오 편집/렌더링 |
| 감정/언어/NER 분석 | 3D 모델링 |
| 사운드 분류 (303종) | 클라우드 API 호출 |
| 온디바이스 LLM (3B) | 대형 LLM 추론 (70B+) |

> **핵심**: ANE는 **분석·인식·분류** 전문. **생성**은 클라우드 AI(Claude, GPT 등)가 담당.

---

## 참고 파일

| 파일 | 위치 |
|------|------|
| SKILL.md (전체 레퍼런스) | `system/apple-neural-engine/SKILL.md` |
| CLI 소스코드 | `system/apple-neural-engine/ane-cli/ane_tool.swift` |
| README | `system/apple-neural-engine/README.md` |
| 파이프라인 통합 상세 | `system/apple-neural-engine/references/pipeline-integration.md` |
