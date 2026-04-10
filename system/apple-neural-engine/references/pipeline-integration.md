# ANE 파이프라인 통합 상세 코드

> 이 파일은 SKILL.md §17의 상세 코드 블록을 포함합니다.

## PDF 파이프라인 교차검증

```
pymupdf4llm (0.1s, 100%) → Apple Vision 교차검증 (3페이지 샘플, ~2s)
  ├── match → 품질 "good" → 그대로 진행
  └── 차이 감지 → 경고 로그 + 사용자에게 알림
```

**벤치마크 근거 (2026-03-22, 8종 비교)**:
- pymupdf4llm: 한글 100%, 마크다운 완벽, 0.096s/page (디지털 PDF 1위)
- Apple Vision: 한글 97%, 0.62s/page (OCR 속도 1위, Neural Engine)

**구현 위치**: `book-forge/scripts/source_ingest.py` → `_vision_cross_verify()`

## 콘텐츠 품질 검증

```swift
import NaturalLanguage

func verifyChapterQuality(text: String) -> [String: Any] {
    let tagger = NLTagger(tagSchemes: [.sentimentScore])
    tagger.string = text

    let recognizer = NLLanguageRecognizer()
    recognizer.processString(text)
    let langHypotheses = recognizer.languageHypotheses(withMaximum: 3)

    let nerTagger = NLTagger(tagSchemes: [.nameType])
    nerTagger.string = text

    return ["sentiment": sentimentScore,
            "languages": langHypotheses,
            "entities": extractedEntities]
}
```

## 이미지 품질 검증

```swift
let aesthetics = try await CalculateImageAestheticsScoresRequest().perform(on: image)
let score = aesthetics.overallScore
// score < 0.3 → 재생성 제안
// score > 0.7 → 품질 통과
```

## 문서 구조 검증 (RecognizeDocumentsRequest)

```swift
let docRequest = RecognizeDocumentsRequest()
let results = try await ImageRequestHandler(pageImage).perform(docRequest)

for doc in results {
    for element in doc.body {
        switch element {
        case .table(let table):
            let visionRows = table.rows.count
            let visionCols = table.rows.first?.cells.count ?? 0
            if abs(visionRows - mdTableRows) > 1 {
                log.warning("테이블 행 수 불일치: Vision \(visionRows) vs MD \(mdTableRows)")
            }
        case .list(let list):
            break
        default: break
        }
    }
}
```

## NLContextualEmbedding — 온디바이스 BERT (CJK 27언어)

```swift
import NaturalLanguage

func contextualEmbedding(for text: String) -> [Float]? {
    guard let embedding = NLContextualEmbedding(modelIdentifier: .wordEmbeddingCJK) else {
        return nil
    }
    try? embedding.load()

    if let result = try? embedding.embeddingResult(for: text, language: .korean) {
        var vectors: [[Float]] = []
        result.enumerateTokenVectors(in: text.startIndex..<text.endIndex) { vector, range in
            vectors.append(Array(vector))
            return true
        }
        guard !vectors.isEmpty else { return nil }
        let dim = vectors[0].count
        var avg = [Float](repeating: 0, count: dim)
        for v in vectors { for i in 0..<dim { avg[i] += v[i] } }
        for i in 0..<dim { avg[i] /= Float(vectors.count) }
        return avg
    }
    return nil
}
```

## Python 래퍼 (ane_tool 호출)

```python
import subprocess, json
from pathlib import Path

ANE = "ane_tool"  # System/11_Modules/ane-cli/ane_tool

def ane_ocr(img): return json.loads(subprocess.run([ANE,"ocr",img],capture_output=True,text=True,timeout=30).stdout)
def ane_lang(txt): return json.loads(subprocess.run([ANE,"lang",txt],capture_output=True,text=True,timeout=5).stdout).get("dominant","unknown")
def ane_sentiment(txt): return json.loads(subprocess.run([ANE,"sentiment",txt],capture_output=True,text=True,timeout=5).stdout).get("score",0.0)
def ane_ner(txt): return json.loads(subprocess.run([ANE,"ner",txt],capture_output=True,text=True,timeout=5).stdout).get("entities",[])
def ane_aesthetic(img): return json.loads(subprocess.run([ANE,"aesthetic",img],capture_output=True,text=True,timeout=10).stdout).get("overall_score",0.0)
```

## 통합 가능한 스킬 매핑

| 스킬 | Apple 프레임워크 | 품질 보조 역할 |
|------|----------------|-------------|
| **book-forge** | Vision OCR + NL 감정/NER | PDF 인제스트 교차검증 + 챕터 품질 |
| **source_ingest.py** | Vision OCR | pymupdf4llm 교차검증 (구현 완료) |
| **ai-image-forge** | Vision Aesthetics | 생성 이미지 품질 점수 |
| **tts-forge** | Speech STT | TTS 출력을 STT로 역검증 (WER) |
| **doc-forge** | Vision RecognizeDocuments | 생성 PDF 테이블 구조 검증 |
| **rag-forge** | NLContextualEmbedding | 오프라인 임베딩 fallback |
| **videogen** | Vision + SoundAnalysis | 자막 정확도 + BGM 분류 |
| **search MCP** | NLEmbedding | 오프라인 시맨틱 검색 fallback |
