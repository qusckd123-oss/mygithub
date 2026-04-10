# Apple Neural Engine (ANE) Skill

> Apple Silicon의 Neural Engine을 활용한 온디바이스 AI 스킬.
> **macOS 전용** (Apple Silicon M1+ 필수, macOS 15+ 권장, macOS 26+ 최적)

## 이게 뭔가요?

Apple Silicon 칩에 내장된 **Neural Engine (NPU)**이 가속하는 8개 ML 프레임워크를 하나의 스킬로 통합한 것입니다.
AI 어시스턴트가 `/apple` 명령어 하나로 이미지 분석, 텍스트 분석, 사운드 분류, 번역 등을 **로컬에서 즉시** 수행합니다.

### 주요 기능

| 기능 | 프레임워크 | 예시 |
|------|-----------|------|
| OCR (한/영/일) | Vision | 이미지에서 텍스트 추출 |
| 이미지 분류 | Vision | 사진이 무엇인지 식별 |
| 미적 평가 | Vision | 이미지 품질 점수 (0~1) |
| 감정 분석 | NaturalLanguage | 텍스트 긍정/부정 판단 |
| 언어 감지 | NaturalLanguage | 텍스트 언어 자동 식별 |
| 개체명 인식 (NER) | NaturalLanguage | 인명, 지명, 조직명 추출 |
| 단어 유사도 | NaturalLanguage | 유사 단어 검색 (임베딩) |
| 사운드 분류 | SoundAnalysis | 303개 카테고리 (음성, 음악, 동물 등) |
| 온디바이스 번역 | Translation | 오프라인 번역 |
| 온디바이스 LLM | FoundationModels | Apple Intelligence 3B 모델 |
| 포즈/얼굴 감지 | Vision | 사람/손/동물 포즈 |
| 커스텀 ML 모델 | Core ML | .mlmodel 추론 |

### 핵심 특징
- **완전 오프라인** — 네트워크 불필요, 데이터가 기기를 떠나지 않음
- **무료** — API 비용 없음
- **빠름** — Neural Engine 하드웨어 가속 (OCR 0.6초, NLP 즉시)
- **의도 자동 파악** — 애매한 요청 시 사용자에게 질문하여 명확화

## 설치 방법

### 1. 스킬 파일 배치

```bash
# Claude Code 스킬 디렉토리에 복사
cp -r apple-neural-engine/ ~/.claude/plugins/local/all-in-one/skills/apple-neural-engine/
# 또는 원하는 스킬 디렉토리에 배치
```

### 2. CLI 도구 컴파일

```bash
cd apple-neural-engine/ane-cli/
swiftc -O -o ane_tool ane_tool.swift

# (선택) PATH에 추가
cp ane_tool /usr/local/bin/
# 또는
cp ane_tool ~/bin/
```

### 3. 동작 확인

```bash
# Neural Engine 감지 확인
./ane_tool devices
# 출력: {"neural_engine": true, "devices": ["NeuralEngine", "GPU", "CPU"]}

# OCR 테스트
./ane_tool ocr /path/to/image.png

# 감정 분석 테스트
./ane_tool sentiment "이 제품은 정말 훌륭합니다"
```

## 사용법

### AI 어시스턴트에서 (스킬 호출)

```
/apple 이 이미지에서 텍스트 추출해줘
/apple 이 텍스트의 감정 분석해줘
/apple 이 오디오 파일이 무슨 소리인지 분류해줘
/apple Neural Engine 상태 확인
```

**애매한 요청 시:**
```
/apple 이 파일 분석해줘
→ AI가 질문: "어떤 분석을 원하시나요? (1) OCR (2) 분류 (3) 미적 평가 ..."
```

### CLI에서 직접 사용

```bash
ane_tool ocr <이미지>           # OCR (한/영/일)
ane_tool classify <이미지>       # 이미지 분류
ane_tool aesthetics <이미지>     # 미적 평가
ane_tool sentiment "텍스트"      # 감정 분석
ane_tool language "텍스트"       # 언어 감지
ane_tool ner "텍스트"            # 개체명 인식
ane_tool embedding "단어"        # 유사 단어
ane_tool sound <오디오>          # 사운드 분류 (303종)
ane_tool devices                # 디바이스 확인
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
result = ane("ocr", "image.png")
print(result["text"])

result = ane("sentiment", "좋은 하루입니다")
print(result["label"])  # "positive" / "neutral" / "negative"
```

## 파일 구조

```
apple-neural-engine/
├── README.md                      # 이 파일
├── SKILL.md                       # 스킬 정의 (AI가 읽는 메인 파일)
├── ane-cli/
│   └── ane_tool.swift             # CLI 도구 소스 (308줄)
└── references/
    └── pipeline-integration.md    # 파이프라인 통합 상세 코드
```

## 시스템 요구사항

| 항목 | 최소 | 권장 |
|------|------|------|
| **OS** | macOS 15 (Sequoia) | macOS 26 (Tahoe) |
| **칩** | Apple Silicon M1 | M3/M4 |
| **Swift** | 5.9+ | 6.2+ |
| **Xcode** | Command Line Tools | Xcode 16+ |

> **Windows/Linux**: 지원 불가 — Apple Neural Engine은 Apple Silicon 전용 하드웨어입니다.

## 검증 상태

- SKILL.md 코드 예제: 25개 테스트 전부 PASS (A/B 테스트 완료)
- CLI 도구: 9/9 명령어 E2E 검증 PASS
- Python 래퍼: 4/4 테스트 PASS
- 기능 체크리스트: 12/12 PASS

## 라이선스

자유롭게 사용, 수정, 배포 가능합니다.
