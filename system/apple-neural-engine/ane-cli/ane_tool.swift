#!/usr/bin/env swift
// ANE CLI Tool — 만능 Apple Neural Engine 도구
// 컴파일: swiftc -O -o ane_tool ane_tool.swift
// 사용: ./ane_tool ocr /path/to/image.png
//       ./ane_tool sentiment "텍스트"
//       ./ane_tool language "텍스트"
//       ./ane_tool classify /path/to/image.png
//       ./ane_tool ner "Tim Cook announced Apple in Seoul"
//       ./ane_tool embedding "word"
//       ./ane_tool sound /path/to/audio.aiff
//       ./ane_tool devices
//       ./ane_tool aesthetics /path/to/image.png

import Foundation
import Vision
import NaturalLanguage
import CoreML
import SoundAnalysis

// MARK: - JSON Output Helper

func jsonOutput(_ dict: [String: Any]) {
    if let data = try? JSONSerialization.data(withJSONObject: dict, options: .prettyPrinted),
       let str = String(data: data, encoding: .utf8) {
        print(str)
    }
}

// MARK: - Image Loading

func loadCGImage(from path: String) -> CGImage? {
    let url = URL(fileURLWithPath: path)
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else { return nil }
    return CGImageSourceCreateImageAtIndex(source, 0, nil)
}

// MARK: - Commands

func cmdOCR(_ imagePath: String) async {
    guard let image = loadCGImage(from: imagePath) else {
        jsonOutput(["error": "이미지 로드 실패: \(imagePath)"])
        return
    }
    var request = RecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = [
        Locale.Language(identifier: "ko-KR"),
        Locale.Language(identifier: "en-US"),
        Locale.Language(identifier: "ja-JP")
    ]

    let handler = ImageRequestHandler(image)
    do {
        let observations = try await handler.perform(request)
        let texts = observations.compactMap { $0.topCandidates(1).first?.string }
        jsonOutput([
            "command": "ocr",
            "file": imagePath,
            "lines": texts.count,
            "text": texts.joined(separator: "\n"),
            "texts": texts
        ])
    } catch {
        jsonOutput(["error": "OCR 실패: \(error.localizedDescription)"])
    }
}

func cmdClassify(_ imagePath: String) async {
    guard let image = loadCGImage(from: imagePath) else {
        jsonOutput(["error": "이미지 로드 실패: \(imagePath)"])
        return
    }
    let request = ClassifyImageRequest()
    let handler = ImageRequestHandler(image)
    do {
        let observations = try await handler.perform(request)
        let results = observations.prefix(5).map {
            ["label": $0.identifier, "confidence": String(format: "%.3f", $0.confidence)]
        }
        jsonOutput([
            "command": "classify",
            "file": imagePath,
            "results": results
        ])
    } catch {
        jsonOutput(["error": "분류 실패: \(error.localizedDescription)"])
    }
}

func cmdAesthetics(_ imagePath: String) async {
    guard let image = loadCGImage(from: imagePath) else {
        jsonOutput(["error": "이미지 로드 실패: \(imagePath)"])
        return
    }
    let request = CalculateImageAestheticsScoresRequest()
    let handler = ImageRequestHandler(image)
    do {
        let score = try await handler.perform(request)
        jsonOutput([
            "command": "aesthetics",
            "file": imagePath,
            "overall_score": String(format: "%.3f", score.overallScore)
        ])
    } catch {
        jsonOutput(["error": "미적 평가 실패: \(error.localizedDescription)"])
    }
}

func cmdSentiment(_ text: String) {
    let tagger = NLTagger(tagSchemes: [.sentimentScore])
    tagger.string = text

    var score = 0.0
    tagger.enumerateTags(in: text.startIndex..<text.endIndex,
                         unit: .paragraph,
                         scheme: .sentimentScore,
                         options: []) { tag, _ in
        if let s = tag?.rawValue, let d = Double(s) { score = d }
        return true
    }
    jsonOutput([
        "command": "sentiment",
        "text": String(text.prefix(100)),
        "score": String(format: "%.3f", score),
        "label": score > 0.1 ? "positive" : (score < -0.1 ? "negative" : "neutral")
    ])
}

func cmdLanguage(_ text: String) {
    let recognizer = NLLanguageRecognizer()
    recognizer.processString(text)
    let dominant = recognizer.dominantLanguage?.rawValue ?? "unknown"
    let hypotheses = recognizer.languageHypotheses(withMaximum: 5)
    let langs = hypotheses.sorted { $0.value > $1.value }.map {
        ["language": $0.key.rawValue, "confidence": String(format: "%.3f", $0.value)]
    }
    jsonOutput([
        "command": "language",
        "text": String(text.prefix(100)),
        "dominant": dominant,
        "hypotheses": langs
    ])
}

func cmdNER(_ text: String) {
    let tagger = NLTagger(tagSchemes: [.nameType])
    tagger.string = text

    var entities: [[String: String]] = []
    tagger.enumerateTags(in: text.startIndex..<text.endIndex,
                         unit: .word,
                         scheme: .nameType,
                         options: [.joinNames, .omitWhitespace, .omitPunctuation]) { tag, range in
        if let tag = tag, tag != .otherWord {
            entities.append([
                "text": String(text[range]),
                "type": tag.rawValue
            ])
        }
        return true
    }
    jsonOutput([
        "command": "ner",
        "text": String(text.prefix(100)),
        "entities": entities,
        "count": entities.count
    ])
}

func cmdEmbedding(_ word: String) {
    guard let embedding = NLEmbedding.wordEmbedding(for: .english) else {
        jsonOutput(["error": "영어 임베딩 로드 실패"])
        return
    }
    var neighbors: [[String: String]] = []
    embedding.enumerateNeighbors(for: word, maximumCount: 10) { neighbor, distance in
        neighbors.append(["word": neighbor, "distance": String(format: "%.4f", distance)])
        return true
    }
    jsonOutput([
        "command": "embedding",
        "word": word,
        "neighbors": neighbors
    ])
}

func cmdSound(_ audioPath: String) async {
    do {
        let request = try SNClassifySoundRequest(classifierIdentifier: .version1)
        let url = URL(fileURLWithPath: audioPath)
        let analyzer = try SNAudioFileAnalyzer(url: url)

        class Observer: NSObject, SNResultsObserving {
            nonisolated(unsafe) var results: [[String: String]] = []
            func request(_ request: SNRequest, didProduce result: SNResult) {
                guard let result = result as? SNClassificationResult else { return }
                for c in result.classifications.prefix(5) {
                    results.append([
                        "label": c.identifier,
                        "confidence": String(format: "%.3f", c.confidence)
                    ])
                }
            }
            func request(_ request: SNRequest, didFailWithError error: Error) {}
            func requestDidComplete(_ request: SNRequest) {}
        }

        let observer = Observer()
        try analyzer.add(request, withObserver: observer)
        await analyzer.analyze()

        // 중복 제거 및 최고 confidence 유지
        var best: [String: Double] = [:]
        for r in observer.results {
            let conf = Double(r["confidence"] ?? "0") ?? 0
            if conf > (best[r["label"] ?? ""] ?? 0) {
                best[r["label"] ?? ""] = conf
            }
        }
        let sorted = best.sorted { $0.value > $1.value }.prefix(5).map {
            ["label": $0.key, "confidence": String(format: "%.3f", $0.value)]
        }

        jsonOutput([
            "command": "sound",
            "file": audioPath,
            "classifications": sorted
        ])
    } catch {
        jsonOutput(["error": "사운드 분석 실패: \(error.localizedDescription)"])
    }
}

func cmdDevices() {
    let devices = MLComputeDevice.allComputeDevices
    var deviceNames: [String] = []
    for device in devices {
        switch device {
        case .cpu: deviceNames.append("CPU")
        case .gpu: deviceNames.append("GPU")
        case .neuralEngine: deviceNames.append("NeuralEngine")
        @unknown default: deviceNames.append("Unknown")
        }
    }
    jsonOutput([
        "command": "devices",
        "devices": deviceNames,
        "neural_engine": deviceNames.contains("NeuralEngine")
    ])
}

// MARK: - Main

let args = CommandLine.arguments
guard args.count >= 2 else {
    print("""
    ANE CLI Tool — Apple Neural Engine 만능 도구

    사용법:
      ane_tool ocr <이미지경로>          OCR 텍스트 인식 (한/영/일)
      ane_tool classify <이미지경로>     이미지 분류
      ane_tool aesthetics <이미지경로>   이미지 미적 평가
      ane_tool sentiment <텍스트>        감정 분석
      ane_tool language <텍스트>         언어 감지
      ane_tool ner <텍스트>              개체명 인식
      ane_tool embedding <단어>          유사 단어 검색
      ane_tool sound <오디오경로>         사운드 분류 (303개 카테고리)
      ane_tool devices                  ANE 디바이스 확인

    출력: JSON (파이프라인 연결 용이)
    """)
    exit(0)
}

let command = args[1].lowercased()
let argument = args.count > 2 ? args[2...].joined(separator: " ") : ""

switch command {
case "ocr":
    guard !argument.isEmpty else { print("{\"error\": \"이미지 경로 필요\"}"); exit(1) }
    await cmdOCR(argument)
case "classify":
    guard !argument.isEmpty else { print("{\"error\": \"이미지 경로 필요\"}"); exit(1) }
    await cmdClassify(argument)
case "aesthetics":
    guard !argument.isEmpty else { print("{\"error\": \"이미지 경로 필요\"}"); exit(1) }
    await cmdAesthetics(argument)
case "sentiment":
    guard !argument.isEmpty else { print("{\"error\": \"텍스트 필요\"}"); exit(1) }
    cmdSentiment(argument)
case "language", "lang":
    guard !argument.isEmpty else { print("{\"error\": \"텍스트 필요\"}"); exit(1) }
    cmdLanguage(argument)
case "ner", "entities":
    guard !argument.isEmpty else { print("{\"error\": \"텍스트 필요\"}"); exit(1) }
    cmdNER(argument)
case "embedding", "similar":
    guard !argument.isEmpty else { print("{\"error\": \"단어 필요\"}"); exit(1) }
    cmdEmbedding(argument)
case "sound", "audio":
    guard !argument.isEmpty else { print("{\"error\": \"오디오 경로 필요\"}"); exit(1) }
    await cmdSound(argument)
case "devices", "device":
    cmdDevices()
default:
    print("{\"error\": \"알 수 없는 명령: \(command)\"}")
    exit(1)
}
