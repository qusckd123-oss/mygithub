---
name: apple-neural-engine
description: Apple Neural Engine 전체 프레임워크 통합 — Vision, NaturalLanguage, Speech, SoundAnalysis, Translation, CreateML, FoundationModels, CoreML 모든 ANE 기능을 자동 감지하여 최적 실행
version: 1.3.0
trigger_keywords:
  - apple neural engine
  - ANE
  - 뉴럴엔진
  - neural engine
  - apple ml
  - apple ai
  - 애플 ML
  - on-device ml
  - apple vision
  - apple ocr
  - apple 음성인식
  - apple 번역
  - apple 소리분석
  - coreml
  - core ml
  - vision framework
  - foundation models
  - apple intelligence
  - 온디바이스 AI
  - mlmodel
  - create ml
  - apple 텍스트분석
  - apple 감정분석
  - apple 이미지분류
  - apple 문서인식
  - apple 바코드
  - apple 포즈
  - 뉴럴엔진 스킬
category: apple-ml
platforms: [macOS, iOS, visionOS]
autoresearch: true
---

# Apple Neural Engine (ANE) 통합 스킬 v1.3

> Apple Silicon의 Neural Engine이 가속하는 **모든** 온디바이스 ML 프레임워크를 하나의 진입점으로 통합.
> `/apple` 슬래시 커맨드로 호출. 작업 의도를 자동 감지하여 최적 프레임워크와 API를 선택.

---

## 0. ANE 아키텍처 개요

### Neural Engine이란?
- Apple Silicon 내장 NPU (Neural Processing Unit)
- 전용 하드웨어로 행렬 곱셈, 합성곱 등 ML 연산 가속
- A11+ (iPhone), M1+ (Mac) 칩에 탑재
- M4: 38 TOPS, M3 Ultra: 32코어 ANE

### ANE가 가속하는 프레임워크 (8개)

| # | 프레임워크 | 주요 기능 | ANE 활용 |
|---|-----------|----------|---------|
| 1 | **Core ML** | ML 모델 추론/파인튜닝 | CPU/GPU/ANE 자동 하이브리드 실행 |
| 2 | **Vision** | 이미지/비디오 분석 (33+ 요청 타입) | 내장 모델 ANE 가속 |
| 3 | **NaturalLanguage** | 텍스트 분석/임베딩/감정분석 | 내장 NLP 모델 ANE 실행 |
| 4 | **Speech** | 음성→텍스트 변환 (STT) | 온디바이스 인식 ANE 가속 |
| 5 | **SoundAnalysis** | 오디오 분류 (300+ 카테고리) | 사운드 분류 모델 ANE |
| 6 | **Translation** | 온디바이스 번역 | 번역 모델 ANE 가속 |
| 7 | **Create ML** | 온디바이스 모델 훈련 | 훈련 시 GPU/ANE 활용 |
| 8 | **FoundationModels** | 온디바이스 LLM (3B, Apple Intelligence) | ANE+GPU 하이브리드 추론 |

### 핵심 원칙
- **모든 처리는 온디바이스** — 데이터가 기기를 떠나지 않음
- **프라이버시 기본** — 네트워크 불필요
- **무료 추론** — API 비용 없음
- **ANE 자동 활용** — Core ML이 최적 컴퓨트 디바이스 자동 선택

---

## 0.5 ANE CLI 도구

> `System/11_Modules/ane-cli/ane_tool` (144KB, JSON 출력)

```bash
ane_tool devices | ocr | classify | aesthetics | sentiment | language | ner | embedding | sound
```

> 9/9 E2E 검증 완료 (2026-03-22). 상세: `12_Research/ANE_Skill_AB_Test_2026/`

---

## 1. 의도 파악 + 자동 라우팅

### 1.0 의도 파악 플로우 (Intent Disambiguation)

`/apple` 호출 시 사용자 요청이 **애매하면 AskUserQuestion으로 확인**한 뒤 라우팅.

```
사용자: /apple "이 파일 분석해줘"
  ↓
[1단계] 파일 확장자/컨텍스트 자동 감지
  ├── .png/.jpg → Vision (OCR? 분류? 미적평가?)
  ├── .aiff/.wav → SoundAnalysis
  ├── .txt/.md → NaturalLanguage
  └── 판단 불가 → [2단계]

[2단계] AskUserQuestion (애매한 경우만)
  "어떤 분석을 원하시나요?"
  ├── (1) 텍스트 추출 (OCR)
  ├── (2) 이미지 분류/태깅
  ├── (3) 미적 평가 (품질 점수)
  ├── (4) 감정 분석
  ├── (5) 사운드 분류
  └── (6) 기타 (설명해주세요)

[3단계] 지원 여부 판단
  ├── ANE 지원 가능 → 해당 API 실행
  └── ANE 미지원 → "이 작업은 ANE가 지원하지 않습니다. [대안 제안]"
```

### ANE 지원 범위 (가능/불가능 명확화)

| 가능 (ANE 가속) | 불가능 (ANE 범위 밖) |
|----------------|-------------------|
| OCR (한/영/일/중 등) | 이미지 생성 (Stable Diffusion 등) |
| 이미지 분류/객체 감지 | 비디오 편집/렌더링 |
| 얼굴/포즈/손 감지 | 3D 모델링 |
| 감정/언어/NER 분석 | 클라우드 API 호출 |
| 사운드 분류 (303종) | 실시간 스트리밍 처리 |
| 온디바이스 LLM (3B) | 대형 LLM 추론 (70B+) |
| 온디바이스 번역 | 커스텀 모델 훈련 (GPU 권장) |
| 단어/문장 임베딩 | 고정밀 벡터 임베딩 (e5-large급) |

### 의도 판단 키워드 매핑

| 키워드 | 자동 라우팅 | 추가 질문 불필요 |
|--------|-----------|---------------|
| "OCR", "텍스트 인식", "글자 읽어" | Vision OCR | O |
| "감정", "긍정/부정" | NL Sentiment | O |
| "무슨 언어", "언어 감지" | NL Language | O |
| "분류해", "이게 뭐야" (이미지) | Vision Classify | O |
| "소리", "무슨 소리" | SoundAnalysis | O |
| "번역해" | Translation | O |
| "분석해" (대상 불명확) | — | **AskUserQuestion** |
| "처리해" (작업 불명확) | — | **AskUserQuestion** |
| "도와줘" (범위 불명확) | — | **AskUserQuestion** |

사용자 요청을 분석하여 최적 프레임워크로 자동 라우팅.

### 라우팅 테이블

| 작업 의도 | 프레임워크 | API | 섹션 |
|-----------|-----------|-----|------|
| OCR / 텍스트 인식 | Vision | `RecognizeTextRequest` | §2.1 |
| 문서 구조 파싱 (테이블, 리스트) | Vision | `RecognizeDocumentsRequest` | §2.2 |
| 바코드/QR 스캔 | Vision | `DetectBarcodesRequest` | §2.3 |
| 이미지 분류 | Vision | `ClassifyImageRequest` | §2.4 |
| 얼굴 감지 | Vision | `DetectFaceRectanglesRequest` | §2.5 |
| 얼굴 랜드마크 | Vision | `DetectFaceLandmarksRequest` | §2.5 |
| 사람 감지/세그먼테이션 | Vision | `GeneratePersonSegmentationRequest` | §2.6 |
| 사람 체형 포즈 (2D) | Vision | `DetectHumanBodyPoseRequest` | §2.7 |
| 사람 체형 포즈 (3D) | Vision | `DetectHumanBodyPose3DRequest` | §2.7 |
| 손 포즈 | Vision | `DetectHumanHandPoseRequest` | §2.7 |
| 동물 포즈 | Vision | `DetectAnimalBodyPoseRequest` | §2.7 |
| 객체 추적 | Vision | `TrackObjectRequest` | §2.8 |
| 사각형 감지 | Vision | `DetectRectanglesRequest` | §2.9 |
| 수평선 감지 | Vision | `DetectHorizonRequest` | §2.9 |
| 주목도 맵 | Vision | `GenerateAttentionBasedSaliencyImageRequest` | §2.10 |
| 객체 기반 주목도 | Vision | `GenerateObjectnessBasedSaliencyImageRequest` | §2.10 |
| 이미지 유사도 | Vision | `GenerateImageFeaturePrintRequest` | §2.11 |
| 이미지 품질 평가 | Vision | `CalculateImageAestheticsScoresRequest` | §2.11 |
| 윤곽 감지 | Vision | `DetectContoursRequest` | §2.9 |
| 카메라 렌즈 오염 | Vision | `DetectCameraLensSmudgeRequest` | §2.12 |
| 이미지 정합 | Vision | `TrackHomographicImageRegistrationRequest` | §2.8 |
| 커스텀 ML 모델 | Vision + Core ML | `CoreMLRequest` | §2.13 |
| 텍스트 감정 분석 | NaturalLanguage | `NLTagger(.sentimentScore)` | §3.1 |
| 품사 태깅 (POS) | NaturalLanguage | `NLTagger(.lexicalClass)` | §3.2 |
| 개체명 인식 (NER) | NaturalLanguage | `NLTagger(.nameType)` | §3.3 |
| 언어 감지 | NaturalLanguage | `NLLanguageRecognizer` | §3.4 |
| 텍스트 토크나이징 | NaturalLanguage | `NLTokenizer` | §3.5 |
| 단어/문장 임베딩 | NaturalLanguage | `NLEmbedding` | §3.6 |
| 음성→텍스트 (STT) | Speech | `SFSpeechRecognizer` | §4.1 |
| 소리 분류 (300+) | SoundAnalysis | `SNClassifySoundRequest` | §5.1 |
| 커스텀 소리 분류 | SoundAnalysis | `SNClassifySoundRequest(mlModel:)` | §5.2 |
| 온디바이스 번역 | Translation | `TranslationSession` | §6.1 |
| 번역 가용성 확인 | Translation | `LanguageAvailability` | §6.2 |
| 이미지 분류기 훈련 | Create ML | `MLImageClassifier` | §7.1 |
| 텍스트 분류기 훈련 | Create ML | `MLTextClassifier` | §7.2 |
| 사운드 분류기 훈련 | Create ML | `MLSoundClassifier` | §7.3 |
| 손/동작 분류기 훈련 | Create ML | Hand/Action Classifier | §7.4 |
| LLM 텍스트 생성 | FoundationModels | `LanguageModelSession` | §8.1 |
| 구조화 출력 (@Generable) | FoundationModels | `@Generable` + `@Guide` | §8.2 |
| 콘텐츠 태깅 | FoundationModels | `.contentTagging` adapter | §8.3 |
| 도구 호출 | FoundationModels | Tool calling | §8.4 |
| 모델 변환 (PyTorch→CoreML) | coremltools (Python) | `ct.convert()` | §9.1 |
| 모델 최적화/양자화 | coremltools (Python) | `ct.optimize` | §9.2 |

### 자동 라우팅 프로토콜

```
1. 사용자 요청 수신
2. 키워드 + 의도 분석 → 라우팅 테이블 매칭
3. 복합 작업 감지 시 → 파이프라인 구성 (예: OCR + 감정분석 = Vision → NaturalLanguage)
4. 해당 프레임워크 Swift 코드 생성 또는 실행
5. 결과 반환 + 다른 스킬과 통합 가능성 제안
```

---

## 2. Vision 프레임워크 (33+ 요청 타입)

> **모든** Vision API는 온디바이스 실행, ANE 자동 가속

### 공통 패턴 (Swift)

```swift
import Vision

// 1. 요청 생성
let request = RecognizeTextRequest()

// 2. 핸들러로 실행
let handler = ImageRequestHandler(cgImage)
let observations = try await handler.perform(request)

// 3. 결과 처리
for observation in observations {
    print(observation.topCandidates(1).first?.string ?? "")
}
```

### 2.1 텍스트 인식 (OCR)

```swift
import Vision

func recognizeText(in image: CGImage) async throws -> [String] {
    var request = RecognizeTextRequest()
    request.recognitionLevel = .accurate  // .fast도 가능
    request.recognitionLanguages = [
        Locale.Language(identifier: "ko-KR"),
        Locale.Language(identifier: "en-US"),
        Locale.Language(identifier: "ja-JP")
    ]
    request.usesLanguageCorrection = true

    let handler = ImageRequestHandler(image)
    let results = try await handler.perform(request)

    return results.compactMap { observation in
        observation.topCandidates(1).first?.string
    }
}
```

**지원 언어**: 한국어, 영어, 일본어, 중국어, 프랑스어, 독일어 등 20+ 언어
**인식 수준**: `.accurate` (정밀, ANE 집중 사용) / `.fast` (속도 우선)

### 2.2 문서 구조 인식 (WWDC25 신규)

```swift
import Vision

func recognizeDocument(in image: CGImage) async throws {
    let request = RecognizeDocumentsRequest()
    let handler = ImageRequestHandler(image)
    let results = try await handler.perform(request)

    for document in results {
        // 테이블, 리스트, 문단, QR 코드 등 구조화된 요소 접근
        for element in document.body {
            switch element {
            case .table(let table):
                for row in table.rows {
                    for cell in row.cells {
                        print(cell.text)
                    }
                }
            case .paragraph(let paragraph):
                print(paragraph.text)
            default: break
            }
        }
    }
}
```

**26개 언어** 지원, 테이블/리스트/문단/QR 코드 자동 구분

### 2.3 바코드/QR 스캔

```swift
import Vision

func detectBarcodes(in image: CGImage) async throws -> [String] {
    let request = DetectBarcodesRequest()
    // request.symbologies = [.qr, .ean13, .code128] // 특정 타입만

    let handler = ImageRequestHandler(image)
    let results = try await handler.perform(request)

    return results.compactMap { $0.payloadStringValue }
}
```

### 2.4 이미지 분류

```swift
import Vision

func classifyImage(_ image: CGImage) async throws -> [(String, Float)] {
    let request = ClassifyImageRequest()
    let handler = ImageRequestHandler(image)
    let results = try await handler.perform(request)

    return results.prefix(5).map { ($0.identifier, $0.confidence) }
}
```

### 2.5 얼굴 감지 + 랜드마크

```swift
import Vision

func detectFaces(in image: CGImage) async throws -> [VNFaceObservation] {
    let request = DetectFaceLandmarksRequest()
    let handler = ImageRequestHandler(image)
    return try await handler.perform(request)
}
```

### 2.6 사람 세그먼테이션

```swift
import Vision

func segmentPerson(in image: CGImage) async throws -> PixelBufferObservation {
    var request = GeneratePersonSegmentationRequest()
    request.qualityLevel = .accurate

    let handler = ImageRequestHandler(image)
    return try await handler.perform(request)
    // 반환값: PixelBufferObservation (단일 객체, 배열 아님)
    // .confidence로 신뢰도 확인
}
```

### 2.7 포즈 감지

```swift
// 사람 2D 포즈
let bodyPose = DetectHumanBodyPoseRequest()

// 사람 3D 포즈
let bodyPose3D = DetectHumanBodyPose3DRequest()

// 손 포즈
let handPose = DetectHumanHandPoseRequest()

// 동물 포즈
let animalPose = DetectAnimalBodyPoseRequest()
```

### 2.8 객체 추적

```swift
let trackRequest = TrackObjectRequest(detectedObject: initialObservation)
// VNSequenceRequestHandler로 프레임 단위 추적
```

### 2.9 기하학적 감지

```swift
let rectangles = DetectRectanglesRequest()
let contours = DetectContoursRequest()
let horizon = DetectHorizonRequest()
```

### 2.10 주목도 분석

```swift
let attention = GenerateAttentionBasedSaliencyImageRequest()
let objectness = GenerateObjectnessBasedSaliencyImageRequest()
```

### 2.11 이미지 품질/유사도

```swift
let aesthetics = CalculateImageAestheticsScoresRequest()
// handler.perform(aesthetics) → ImageAestheticsScoresObservation (단일 객체)
// .overallScore로 접근 (배열 아님)

let featurePrint = GenerateImageFeaturePrintRequest()
```

### 2.12 카메라 렌즈 오염 감지 (WWDC25 신규)

```swift
let smudge = DetectCameraLensSmudgeRequest()
```

### 2.13 커스텀 Core ML 모델 + Vision

```swift
import Vision
import CoreML

func runCustomModel(on image: CGImage, model: MLModel) async throws {
    let vnModel = try VNCoreMLModel(for: model)
    let request = CoreMLRequest(model: vnModel)

    let handler = ImageRequestHandler(image)
    let results = try await handler.perform(request)
    // 결과 타입: VNClassificationObservation, VNPixelBufferObservation, 또는 VNCoreMLFeatureValueObservation
}
```

---

## 3. NaturalLanguage 프레임워크

> 온디바이스 NLP — 감정분석, 품사 태깅, NER, 임베딩, 언어 감지

### 3.1 감정 분석

```swift
import NaturalLanguage

func analyzeSentiment(_ text: String) -> Double {
    let tagger = NLTagger(tagSchemes: [.sentimentScore])
    tagger.string = text

    var score = 0.0
    tagger.enumerateTags(in: text.startIndex..<text.endIndex,
                         unit: .paragraph,
                         scheme: .sentimentScore,
                         options: []) { tag, _ in
        if let s = tag?.rawValue, let d = Double(s) {
            score = d
        }
        return true
    }
    return score  // -1.0 (부정) ~ +1.0 (긍정)
}
```

### 3.2 품사 태깅 (Part-of-Speech)

```swift
func tagPartsOfSpeech(_ text: String) -> [(String, NLTag?)] {
    let tagger = NLTagger(tagSchemes: [.lexicalClass])
    tagger.string = text

    var results: [(String, NLTag?)] = []
    tagger.enumerateTags(in: text.startIndex..<text.endIndex,
                         unit: .word,
                         scheme: .lexicalClass,
                         options: [.omitPunctuation, .omitWhitespace]) { tag, range in
        results.append((String(text[range]), tag))
        return true
    }
    return results  // [("Apple", .noun), ("released", .verb), ...]
}
```

### 3.3 개체명 인식 (NER)

```swift
func extractEntities(_ text: String) -> [(String, NLTag?)] {
    let tagger = NLTagger(tagSchemes: [.nameType])
    tagger.string = text

    var entities: [(String, NLTag?)] = []
    tagger.enumerateTags(in: text.startIndex..<text.endIndex,
                         unit: .word,
                         scheme: .nameType,
                         options: [.joinNames, .omitWhitespace, .omitPunctuation]) { tag, range in
        if let tag = tag, tag != .otherWord {
            entities.append((String(text[range]), tag))
        }
        return true
    }
    return entities  // [("Apple", .organizationName), ("Seoul", .placeName), ...]
}
```

### 3.4 언어 감지

```swift
func detectLanguage(_ text: String) -> NLLanguage? {
    let recognizer = NLLanguageRecognizer()
    recognizer.processString(text)
    return recognizer.dominantLanguage  // .korean, .english, .japanese, etc.
}
```

### 3.5 토크나이징

```swift
func tokenize(_ text: String, unit: NLTokenUnit = .word) -> [String] {
    let tokenizer = NLTokenizer(unit: unit)
    tokenizer.string = text
    return tokenizer.tokens(for: text.startIndex..<text.endIndex).map {
        String(text[$0])
    }
}
```

### 3.6 텍스트 임베딩 (시맨틱 유사도)

```swift
func findSimilarWords(to word: String, language: NLLanguage = .english) -> [(String, Double)] {
    guard let embedding = NLEmbedding.wordEmbedding(for: language) else { return [] }

    var results: [(String, Double)] = []
    embedding.enumerateNeighbors(for: word, maximumCount: 5) { neighbor, distance in
        results.append((neighbor, distance))
        return true
    }
    return results
}

func sentenceSimilarity(_ a: String, _ b: String, language: NLLanguage = .english) -> Double? {
    guard let embedding = NLEmbedding.sentenceEmbedding(for: language) else { return nil }
    return embedding.distance(between: a, and: b)
}
```

---

## 4. Speech 프레임워크

> 온디바이스 음성 인식 (STT)

### 4.1 오디오 파일 → 텍스트

```swift
import Speech

func transcribeAudioFile(url: URL) async throws -> String {
    guard SFSpeechRecognizer.authorizationStatus() == .authorized else {
        SFSpeechRecognizer.requestAuthorization { _ in }
        throw NSError(domain: "auth", code: 1)
    }

    let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "ko-KR"))!
    guard recognizer.supportsOnDeviceRecognition else {
        throw NSError(domain: "ondevice", code: 2)
    }

    let request = SFSpeechURLRecognitionRequest(url: url)
    request.requiresOnDeviceRecognition = true

    // recognitionTask는 callback 기반 — async/await 래핑 필수
    return try await withCheckedThrowingContinuation { continuation in
        var hasResumed = false
        recognizer.recognitionTask(with: request) { result, error in
            guard !hasResumed else { return }
            if let error = error {
                hasResumed = true
                continuation.resume(throwing: error)
            } else if let result = result, result.isFinal {
                hasResumed = true
                continuation.resume(returning: result.bestTranscription.formattedString)
            }
        }
    }
}
```

### 4.2 실시간 마이크 → 텍스트

```swift
// SFSpeechAudioBufferRecognitionRequest + AVAudioEngine 조합
let request = SFSpeechAudioBufferRecognitionRequest()
request.requiresOnDeviceRecognition = true
// AVAudioEngine의 inputNode에서 버퍼를 request.append()로 전달
```

---

## 5. SoundAnalysis 프레임워크

> 300+ 사운드 카테고리 내장 분류기

### 5.1 내장 분류기 (300+ 카테고리)

```swift
import SoundAnalysis

func classifySoundsInFile(url: URL) async throws {
    let request = try SNClassifySoundRequest(classifierIdentifier: .version1)
    let analyzer = try SNAudioFileAnalyzer(url: url)

    // 지원되는 모든 사운드 카테고리 조회
    print(request.knownClassifications) // ["speech", "music", "laughter", "applause", ...]

    let observer = SoundObserver()
    try analyzer.add(request, withObserver: observer)
    await analyzer.analyze()  // async — 분석 완료까지 대기
}

class SoundObserver: NSObject, SNResultsObserving {
    func request(_ request: SNRequest, didProduce result: SNResult) {
        guard let result = result as? SNClassificationResult else { return }
        let top = result.classifications.prefix(3)
        for classification in top {
            print("\(classification.identifier): \(classification.confidence)")
        }
    }
}
```

### 5.2 커스텀 사운드 모델

```swift
let customModel: MLModel = try MLModel(contentsOf: modelURL)
let request = try SNClassifySoundRequest(mlModel: customModel)
```

### 5.3 실시간 오디오 스트림 분류

```swift
let streamAnalyzer = SNAudioStreamAnalyzer(format: audioFormat)
try streamAnalyzer.add(request, withObserver: observer)

// AVAudioEngine tap에서:
streamAnalyzer.analyze(buffer, atAudioFramePosition: time.sampleTime)
```

---

## 6. Translation 프레임워크

> 완전 온디바이스 번역 — Apple 서버에 콘텐츠 전송하지 않음

### 6.1 텍스트 번역

```swift
import Translation

func translate(_ text: String, from: Locale.Language, to: Locale.Language) async throws -> String {
    let session = try TranslationSession(installedSource: from, target: to)
    let response = try await session.translate(text)
    return response.targetText
}

// 배치 번역
func translateBatch(_ texts: [String], from: Locale.Language, to: Locale.Language) async throws -> [String] {
    let session = try TranslationSession(installedSource: from, target: to)
    let requests = texts.map { TranslationSession.Request(sourceText: $0) }
    var results: [String] = []
    for try await response in session.translate(batch: requests) {
        results.append(response.targetText)
    }
    return results
}
```

### 6.2 언어 가용성 확인

```swift
func checkTranslationSupport(from: Locale.Language, to: Locale.Language) async -> Bool {
    let availability = LanguageAvailability()
    let status = await availability.status(from: from, to: to)
    switch status {
    case .installed, .supported: return true
    case .unsupported: return false
    @unknown default: return false
    }
}
```

### 6.3 SwiftUI 통합

```swift
Text(sourceText)
    .translationTask(source: .init(identifier: "en"),
                     target: .init(identifier: "ko")) { session in
        targetText = try? await session.translate(sourceText).targetText
    }
```

---

## 7. Create ML 프레임워크

> 온디바이스 모델 훈련 — macOS, iOS/iPadOS에서 프로그래밍 가능

### 7.1 이미지 분류기 훈련

```swift
import CreateML

func trainImageClassifier(dataDir: URL) throws -> MLModel {
    let trainingData = MLImageClassifier.DataSource.labeledDirectories(at: dataDir)
    let classifier = try MLImageClassifier(trainingData: trainingData)

    let metadata = MLModelMetadata(author: "ANE Skill", description: "Custom classifier")
    try classifier.write(to: URL(fileURLWithPath: "/tmp/MyClassifier.mlmodel"), metadata: metadata)

    return classifier.model
}
```

### 7.2 텍스트 분류기 훈련

```swift
import CreateML
import TabularData

func trainTextClassifier(jsonFile: URL) throws -> MLModel {
    let data = try DataFrame(contentsOfJSONFile: jsonFile)
    let (trainingData, testData) = data.randomSplit(by: 0.8)

    let classifier = try MLTextClassifier(trainingData: DataFrame(trainingData),
                                          textColumn: "text",
                                          labelColumn: "label")

    let metrics = classifier.evaluation(on: DataFrame(testData),
                                         textColumn: "text",
                                         labelColumn: "label")
    print("Accuracy: \(metrics.classificationError)")

    return classifier.model
}
```

### 7.3 사운드 분류기 훈련

```swift
let classifier = try MLSoundClassifier(trainingData: .labeledDirectories(at: audioDir))
```

### 7.4 기타 훈련 가능 모델

| 모델 타입 | API | 입력 |
|-----------|-----|------|
| 이미지 분류 | `MLImageClassifier` | 폴더별 이미지 |
| 객체 감지 | `MLObjectDetector` | 주석된 이미지 |
| 텍스트 분류 | `MLTextClassifier` | 레이블된 텍스트 |
| 사운드 분류 | `MLSoundClassifier` | 폴더별 오디오 |
| 동작 분류 | `MLActionClassifier` | 동영상 |
| 손 포즈 분류 | `MLHandPoseClassifier` | 동영상 |
| 손 동작 분류 | `MLHandActionClassifier` | 동영상 |
| 스타일 전이 | `MLStyleTransfer` | 스타일 이미지 |
| 테이블 분류 | `MLClassifier` | CSV/JSON |
| 테이블 회귀 | `MLRegressor` | CSV/JSON |

---

## 8. Foundation Models 프레임워크 (macOS 26+)

> 온디바이스 3B LLM — Apple Intelligence 엔진 직접 접근

### 8.1 기본 텍스트 생성

```swift
import FoundationModels

func generateText(_ prompt: String) async throws -> String {
    let model = SystemLanguageModel.default
    guard case .available = model.availability else {
        throw NSError(domain: "FM", code: 1, userInfo: [NSLocalizedDescriptionKey: "Apple Intelligence 미활성"])
    }

    let session = LanguageModelSession()
    let response = try await session.respond(to: prompt)
    return response.content
}
```

### 8.2 구조화 출력 (Guided Generation)

```swift
import FoundationModels

@Generable
struct ReviewAnalysis {
    @Guide(description: "감정: positive, negative, neutral 중 하나")
    var sentiment: String

    @Guide(description: "핵심 키워드 3개")
    var keywords: [String]

    @Guide(description: "1-5 별점")
    var rating: Int
}

func analyzeReview(_ text: String) async throws -> ReviewAnalysis {
    let session = LanguageModelSession()
    let result: ReviewAnalysis = try await session.respond(
        to: "리뷰를 분석해줘: \(text)",
        generating: ReviewAnalysis.self
    ).content
    return result
}
```

### 8.3 콘텐츠 태깅

```swift
let taggingModel = SystemLanguageModel(useCase: .contentTagging)
let session = LanguageModelSession(model: taggingModel)
// 토픽 태그, 엔티티 추출, 토픽 감지
```

### 8.4 스트리밍 응답

```swift
let session = LanguageModelSession()
for try await partial in session.streamResponse(to: "설명해줘: \(topic)") {
    print(partial.content, terminator: "")
}
```

### 8.5 가용성 확인

```swift
let availability = SystemLanguageModel.default.availability
switch availability {
case .available: // 사용 가능
case .unavailable(.deviceNotEligible): // 디바이스 미지원
case .unavailable(.appleIntelligenceNotEnabled): // Apple Intelligence 미활성
case .unavailable(.modelNotReady): // 모델 다운로드 중
default: break
}
```

---

## 9. Core ML 모델 관리

### 9.1 Python에서 모델 변환 (coremltools)

```python
import coremltools as ct
import torch

# PyTorch → Core ML
model = torch.load("model.pt")
traced = torch.jit.trace(model, example_input)
mlmodel = ct.convert(traced,
                     inputs=[ct.TensorType(shape=example_input.shape)],
                     compute_units=ct.ComputeUnit.ALL)  # CPU+GPU+ANE
mlmodel.save("Model.mlpackage")
```

### 9.2 ANE 최적화

```python
# 양자화 (ANE는 16-bit 선호)
from coremltools.models.neural_network import quantization_utils
quantized = quantization_utils.quantize_weights(mlmodel, nbits=16)

# 또는 coremltools optimize API
from coremltools.optimize.coreml import OpPalettizerConfig, OptimizationConfig
config = OptimizationConfig(global_config=OpPalettizerConfig(nbits=4))
compressed = ct.optimize.coreml.palettize_weights(mlmodel, config)
```

### 9.3 컴퓨트 디바이스 지정 (Swift)

```swift
let config = MLModelConfiguration()
config.computeUnits = .all  // CPU+GPU+ANE (기본, 권장)
// config.computeUnits = .cpuAndNeuralEngine  // GPU 제외
// config.computeUnits = .cpuOnly  // ANE/GPU 제외

let model = try MLModel(contentsOf: modelURL, configuration: config)
```

### 9.4 ANE 호환성 팁

| 권장 | 비권장 |
|------|--------|
| Conv2D, Dense, LSTM | Custom layers |
| 16-bit 양자화 | 32-bit float |
| 배치 크기 1 | 동적 배치 |
| 표준 활성화 함수 | 비표준 연산 |
| Core ML 최적화 모델 | 변환 없는 원시 모델 |

---

## 10. 다른 스킬과의 통합 패턴

### 10.1 통합 인터페이스

이 스킬은 다른 스킬에서 호출할 때 다음 패턴을 따릅니다:

```
# 다른 스킬에서 호출 시:
# "이 작업에 Apple Neural Engine 기능이 필요함" → /apple 자동 트리거
# 또는 코드에서 직접 해당 프레임워크 API 사용
```

### 10.2 통합 시나리오 예시

| 호출 스킬 | ANE 기능 | 파이프라인 |
|-----------|---------|-----------|
| `pdf` (PDF 스킬) | OCR + 문서 구조 | Vision `RecognizeDocumentsRequest` → 텍스트 추출 |
| `doc-forge` | 이미지 내 텍스트 | Vision `RecognizeTextRequest` |
| `tts-forge` | STT (역방향) | Speech `SFSpeechRecognizer` |
| `ai-image-forge` | 이미지 분류/분석 | Vision `ClassifyImageRequest` |
| `rag-forge` | 텍스트 임베딩 | NaturalLanguage `NLEmbedding` |
| `search-orchestration` | 이미지 검색 | Vision `GenerateImageFeaturePrintRequest` |
| `data-analysis` | 감정 분석 | NaturalLanguage `NLTagger(.sentimentScore)` |
| `videogen` | 객체/포즈 감지 | Vision `DetectHumanBodyPoseRequest` |
| `quality-suite` | 코드 품질 + 문서 품질 | Vision (PDF 도형 검사) + NL (텍스트 품질) |

### 10.3 CLI 통합 (Python pyobjc)

macOS에서 Python으로도 Vision 프레임워크 접근 가능:

```python
import Quartz
from Foundation import NSURL
import Vision

def ocr_image(image_path):
    url = NSURL.fileURLWithPath_(image_path)
    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(1)  # accurate
    request.setRecognitionLanguages_(["ko-KR", "en-US"])

    handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(url, None)
    handler.performRequests_error_([request], None)

    results = []
    for obs in request.results():
        text = obs.topCandidates_(1)[0].string()
        results.append(text)
    return results
```

---

## 11. Autoresearch 자가개선 루프

> Karpathy autoresearch 패턴 적용 — 이 스킬 자체가 지속적으로 개선됨

### 11.1 자동 개선 트리거

| 트리거 | 행동 |
|--------|------|
| 새 WWDC ML 세션 발표 | Vision/CoreML/FM API 변경 확인 → SKILL.md 업데이트 |
| 새 ANE 칩 출시 (M5 등) | TOPS 수치 + 새 기능 업데이트 |
| 사용자 호출 실패 2회+ | 실패 패턴 분석 → 라우팅 테이블 보강 |
| 새 프레임워크 API 감지 | 해당 섹션 자동 추가 |
| Foundation Models 업데이트 | @Generable 패턴, 새 adapter 추가 |

### 11.2 개선 루프 절차

```
Iteration:
  1. Detect: 실패 로그 또는 새 API 감지
  2. Research: WebSearch + Apple docs 조사
  3. Modify: SKILL.md 해당 섹션 업데이트
  4. Verify: 수정된 API 코드 컴파일 테스트 (가능한 경우)
  5. Keep/Discard: 테스트 통과 → Keep / 실패 → Discard
```

### 11.3 품질 메트릭

| 메트릭 | 목표 |
|--------|------|
| 라우팅 정확도 | 95%+ (사용자 의도 → 올바른 프레임워크) |
| API 커버리지 | Vision 33/33, NL 6/6, Speech 2/2, SA 3/3, Translation 3/3, FM 5/5 |
| 코드 예시 정확도 | 100% (컴파일 가능한 Swift 코드) |
| 통합 스킬 수 | 10+ 스킬과 파이프라인 연결 |

---

## 12. 빠른 참조 카드

### 프레임워크별 import

```swift
import CoreML           // 모델 추론
import Vision           // 이미지/비디오 분석
import NaturalLanguage  // 텍스트 NLP
import Speech           // 음성 인식
import SoundAnalysis    // 소리 분류
import Translation      // 번역
import CreateML          // 모델 훈련
import FoundationModels // 온디바이스 LLM (macOS 26+)
```

### ANE 컴퓨트 디바이스

```swift
// Core ML에서 ANE 명시적 확인
let devices = MLComputeDevice.allComputeDevices
for device in devices {
    switch device {
    case .cpu: print("CPU")
    case .gpu: print("GPU")
    case .neuralEngine: print("Neural Engine 사용 가능!")
    @unknown default: break
    }
}
```

### 사용자 권한 요구사항

| 프레임워크 | 권한 | Info.plist 키 |
|-----------|------|--------------|
| Speech | 마이크 + 음성 인식 | `NSSpeechRecognitionUsageDescription`, `NSMicrophoneUsageDescription` |
| SoundAnalysis | 마이크 (실시간 시) | `NSMicrophoneUsageDescription` |
| Vision | 카메라 (실시간 시) | `NSCameraUsageDescription` |
| Translation | 없음 (온디바이스) | — |
| FoundationModels | Apple Intelligence 활성화 | — |

---

## 13. ANE 제약사항 (Orion 논문 2026-03)

> 출처: arxiv 2603.06728 — 20가지 ANE 제약 (14가지 신규 발견)

| 제약 | 설명 | 해결 방법 |
|------|------|-----------|
| FP16 전용 | ANE 연산은 Float16만 지원 | coremltools로 FP16 변환 |
| 최대 5D 텐서 | 6D+ 텐서 불가 | reshape로 5D 이하로 변환 |
| 고정 입력 형상 | 동적 shape 제한적 | EnumeratedShapes 사용 |
| nn.Linear 비효율 | ANE에서 느림 | nn.Conv2d 1x1로 교체 |
| Channels-first 필수 | (B,C,1,S) 형식 요구 | permute/reshape 적용 |
| INT8은 저장만 | 실제 연산은 FP16 dequantize | 진짜 INT8 가속 아님 |
| 컴파일 한도 | ~119회 컴파일 후 오류 가능 | 모델 캐싱 필수 |
| LLM 직접 실행 어려움 | CoreML 오버헤드 2-4x | 하이브리드 (ANE+GPU) 운용 |
| 커스텀 레이어 불가 | ANE 미지원 → CPU fallback | 표준 연산만 사용 |
| 배치 크기 제한 | 배치 1이 최적 | 개별 추론 권장 |

---

## 14. ANE 프로파일링 도구

### 14.1 MLComputePlan API (WWDC24)

```swift
import CoreML

func profileModel(at url: URL) async throws {
    let plan = try await MLComputePlan(contentsOf: url)

    // 각 operation의 preferred compute device 조회
    for operation in plan.modelStructure.neuralNetwork?.layers ?? [] {
        let deviceUsage = plan.estimatedCost(of: operation)
        print("\(operation.name): preferred=\(deviceUsage.preferredComputeDevice)")
    }
}
```

### 14.2 CLI 프로파일링

```bash
# 모델 컴파일
xcrun coremlcompiler compile MyModel.mlpackage ./output/

# 래퍼 클래스 생성
xcrun coremlcompiler generate MyModel.mlpackage ./output/ --language Swift

# 서드파티 CLI (Homebrew)
brew install coreml-cli
coreml-cli predict MyModel.mlpackage --device ane --input data.json
coreml-cli benchmark MyModel.mlpackage --device ane
```

### 14.3 Instruments ANE 추적

Instruments에서 다음을 확인:
- `H11ANE*` 스레드 활성 = ANE 실행 중
- `-[_ANEClient evaluateWithModel:]` 호출 = ANE 추론 수행
- Xcode Performance Report: operation별 시간 + 컴퓨트 유닛 분석

---

## 15. 백그라운드 처리

```swift
// ANE는 iOS 백그라운드에서 허용 (GPU/Metal은 불가!)
let config = MLModelConfiguration()
config.computeUnits = .cpuAndNeuralEngine  // 백그라운드 안전 설정

// BGProcessingTask에서 CoreML 추론 가능
import BackgroundTasks
BGTaskScheduler.shared.register(forTaskWithIdentifier: "com.app.ml",
                                 using: nil) { task in
    let mlTask = task as! BGProcessingTask
    // CoreML 추론 수행 (ANE 사용)
}
```

---

## 16. 이 프로젝트의 기존 ANE 구현 (재사용 가능)

> 이 워크스페이스에서 발견된 프로덕션 CoreML 코드

| 프로젝트 | 경로 | 모델 | ANE 활용 | 성능 |
|---------|------|------|---------|------|
| Lightning-SimulWhisper | `10_Projects/MacRE_Orchestrator/PromptlyRE/Lightning-SimulWhisper/` | Whisper Encoder | CoreML CPU+NE | 3-18x 속도 향상 |
| Claude History Viewer | `10_Projects/claude-history-viewer/` | BGE-M3 (1024d) | CoreML ALL | ~100ms/텍스트 |
| SwiftVoice | `10_Projects/SwiftVoice/Scripts/` | Wav2Vec2 XLS-R 1B | CoreML ALL | 동적 1-60초 |

### 재사용 가능 패턴

```
# BERT/임베딩 모델 변환
10_Projects/claude-history-viewer/scripts/convert_to_coreml.py

# 음성 모델 변환 (동적 시퀀스)
10_Projects/SwiftVoice/Scripts/convert_to_coreml.py

# Swift CoreML Actor 래퍼
10_Projects/claude-history-viewer/Sources/ClaudeHistory/Services/CoreMLEmbeddingProvider.swift

# ANE 기술 스택 문서
10_Projects/MacMini_RAG_Project/NEURAL_ENGINE_TECH_STACK.md
```

---

## 17. 파이프라인 통합 — 다른 스킬의 품질 보조

> 상세 코드: `references/pipeline-integration.md`

ANE는 **다른 스킬의 품질 보조 레이어**로 가장 강력. 0.01~0.6초로 오버헤드 제로.

| AI 작업 | ANE 기능 | 비용 | CLI |
|---------|---------|------|-----|
| PDF→MD | OCR 교차검증 | +2s | `ane_tool ocr` |
| 챕터/문서 작성 | 감정 일관성 + NER | +0.1s | `ane_tool sentiment` + `ner` |
| 이미지 생성 | 미적 평가 | +0.1s | `ane_tool aesthetics` |
| TTS | STT 역검증 | +실시간 | Speech framework |
| 번역 출력 | 언어 확인 | +0.01s | `ane_tool language` |
| 오디오 분석 | 사운드 분류 | +1s | `ane_tool sound` |

### 스킬 증강 (Skill Augmentation)

다른 스킬에 ANE 검증을 자동 부착하는 방법:

```bash
# 1. 스킬이 생성한 결과물에 ANE 검증 추가
ane_tool ocr generated_image.png       # 이미지 내 텍스트 정확도
ane_tool aesthetics output.png         # 품질 점수 (< 0.3 → 재생성)
ane_tool sentiment "생성된 텍스트"      # 감정 톤 일관성
ane_tool language "output text"        # 출력 언어 확인
```

**Python 래퍼** (다른 스킬에서 임포트):

```python
import subprocess, json
def ane(cmd, arg): return json.loads(subprocess.run(
    ["ane_tool", cmd, arg], capture_output=True, text=True, timeout=30).stdout)
```

---

*Last updated: 2026-03-22 | Apple Neural Engine Skill v1.3*
