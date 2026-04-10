"""
Brand Fit Filter — Claude Vision 기반 브랜드 적합성 필터링
==========================================================
크롤링된 이미지를 Claude Vision API로 평가하여
와키윌리 브랜드 무드에 맞는 이미지만 선별합니다.

사용법:
  python filter.py ./pinterest_20260320                     # 전체 폴더 필터 (브랜드 적합성)
  python filter.py ./pinterest_20260320/brand_mood          # 특정 카테고리만
  python filter.py ./pinterest_20260320 --threshold 8       # 8점 이상만 유지
  python filter.py ./pinterest_20260320 --dry-run           # 미리보기 (이동 안 함)
  python filter.py ./soccer-jersey-street --keyword "soccer jersey street outfit" # 키워드 적합성 필터
"""

import os
import sys
import json
import glob
import base64
import argparse
from datetime import datetime

try:
    from anthropic import Anthropic
except ImportError:
    print("anthropic 패키지가 필요합니다: pip install anthropic")
    sys.exit(1)


# ──────────────────────────────────────────────
# 브랜드 프로필 (프리셋 기반)
# ──────────────────────────────────────────────

KEYWORD_EVAL_PROMPT = """이 이미지가 아래 검색 키워드의 의도에 부합하는지 판단해주세요.

## 검색 키워드: {keyword}

## 판단 기준
- 이미지가 해당 키워드로 검색했을 때 **기대되는 결과**인가?
- 키워드의 핵심 아이템/스타일이 이미지에 실제로 **포함되어 있는가?**
- Pinterest 검색 알고리즘이 개별 단어에 매칭하여 가져온 **노이즈 이미지**가 아닌가?

## 응답 형식 (JSON)
다음 JSON 형식으로만 답해주세요. 다른 텍스트 없이 JSON만:
{{
  "relevant": true,
  "confidence": 8,
  "reason": "한 줄 이유"
}}

- relevant: 키워드 의도에 부합하면 true, 아니면 false
- confidence: 확신도 1~10 (7 이상이면 적합)
- reason: 판단 근거 한 줄
"""

BRAND_EVAL_PROMPT = """이 이미지가 아래 패션 브랜드의 무드보드 레퍼런스로 적합한지 평가해주세요.

## 브랜드: Wacky Willy (와키윌리)

**디자인 컨셉**: Kitsch Street & IP Universe
**코어 타겟**: 18~25세 자유로운 트렌드리더
**비전**: K-컬처 기반 Youth Culture를 IP로 확장하는 글로벌 문화 브랜드
**뮤즈**: 지젤

**비주얼 키워드**: Doodle, Graffiti, Pop Art, Bold Lines, Vivid Colors
**컬러**: 시그니처 옐로우(#FEF200) + 블랙 + 비비드 악센트
**그래픽**: Bold outline + flat color fill, doodle/graffiti aesthetic
**사진 방향**: Street context, 자연광, 움직임이 있는 포즈
**레이아웃**: asymmetric, bold-crop, white-space-minimal

**적합한 무드**:
- 키치하고 컬러풀한 스트릿 패션
- 캐릭터/그래픽 프린트가 있는 스트릿웨어
- Y2K / 팝아트 / 하라주쿠 감성
- 과감한 컬러 블로킹
- 자유롭고 유쾌한 에너지

**부적합한 무드**:
- 미니멀 / 모노톤 / 클래식
- 포멀 / 비즈니스 웨어
- 무채색 위주 / 차분한 톤
- 럭셔리 하이패션 (브랜드 포지셔닝과 다름)
- 어둡고 무거운 무드

## 평가 기준
1. **컬러 매치** (비비드/키치 컬러 vs 무채색)
2. **스타일 매치** (스트릿/캐주얼 vs 포멀/미니멀)
3. **에너지 매치** (유쾌/자유 vs 차분/무거움)
4. **타겟 매치** (18~25세 트렌드리더가 좋아할 이미지인가)
5. **레퍼런스 가치** (무드보드에 놓았을 때 브랜드 방향을 강화하는가)

## 응답 형식 (JSON)
다음 JSON 형식으로만 답해주세요. 다른 텍스트 없이 JSON만:
{
  "score": 7,
  "color_match": 8,
  "style_match": 7,
  "energy_match": 6,
  "tags": ["kitsch", "colorful", "street"],
  "reason": "한 줄 이유"
}
"""


# ──────────────────────────────────────────────
# 필터 클래스
# ──────────────────────────────────────────────

class BrandFitFilter:
    """Claude Vision 기반 브랜드 적합성 필터"""

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    def __init__(self, api_key: str = None, model: str = "claude-sonnet-4-6"):
        self.client = Anthropic(api_key=api_key) if api_key else Anthropic()
        self.model = model
        self.results = []

    def evaluate_image(self, filepath: str) -> dict:
        """단일 이미지 브랜드 적합성 평가"""
        with open(filepath, "rb") as f:
            img_data = base64.standard_b64encode(f.read()).decode()

        ext = os.path.splitext(filepath)[1].lower()
        media_type_map = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".webp": "image/webp",
        }
        media_type = media_type_map.get(ext, "image/jpeg")

        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": img_data,
                            },
                        },
                        {"type": "text", "text": BRAND_EVAL_PROMPT},
                    ],
                }],
            )

            text = resp.content[0].text.strip()
            # JSON 파싱 (```json ... ``` 래핑 대응)
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            result = json.loads(text)
            result["filepath"] = filepath
            result["filename"] = os.path.basename(filepath)
            return result

        except json.JSONDecodeError:
            # 숫자만 반환한 경우 대응
            try:
                score = int(text.strip())
                return {
                    "score": score,
                    "filepath": filepath,
                    "filename": os.path.basename(filepath),
                    "tags": [],
                    "reason": "score-only response",
                }
            except ValueError:
                return {
                    "score": 5,
                    "filepath": filepath,
                    "filename": os.path.basename(filepath),
                    "tags": [],
                    "reason": f"parse error: {text[:100]}",
                }
        except Exception as e:
            return {
                "score": -1,
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "tags": [],
                "reason": f"API error: {str(e)}",
            }

    def evaluate_keyword_relevance(self, filepath: str, keyword: str) -> dict:
        """단일 이미지 키워드 적합성 평가"""
        with open(filepath, "rb") as f:
            img_data = base64.standard_b64encode(f.read()).decode()

        ext = os.path.splitext(filepath)[1].lower()
        media_type_map = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".webp": "image/webp",
        }
        media_type = media_type_map.get(ext, "image/jpeg")

        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": img_data,
                            },
                        },
                        {"type": "text", "text": KEYWORD_EVAL_PROMPT.format(keyword=keyword)},
                    ],
                }],
            )

            text = resp.content[0].text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            result = json.loads(text)
            result["filepath"] = filepath
            result["filename"] = os.path.basename(filepath)
            return result

        except (json.JSONDecodeError, Exception) as e:
            return {
                "relevant": True,  # 에러 시 보수적으로 유지
                "confidence": 5,
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "reason": f"parse/API error: {str(e)!s:.80s}",
            }

    def filter_by_keyword(self, directory: str, keyword: str,
                          threshold: int = 7, dry_run: bool = False) -> dict:
        """키워드 적합성 기준으로 이미지 필터링"""
        image_files = []
        for ext in self.IMAGE_EXTENSIONS:
            image_files.extend(glob.glob(os.path.join(directory, f"*{ext}")))
        image_files.sort()

        if not image_files:
            print(f"  이미지 없음: {directory}")
            return {"keep": [], "filtered": [], "errors": []}

        print(f"  키워드 적합성 검사: {len(image_files)}장 (keyword: {keyword}, threshold: {threshold})")

        keep, filtered, errors = [], [], []

        for i, filepath in enumerate(image_files):
            result = self.evaluate_keyword_relevance(filepath, keyword)

            relevant = result.get("relevant", True)
            confidence = result.get("confidence", 5)
            reason = result.get("reason", "")

            if confidence < 0:
                errors.append(result)
                status = "ERR"
            elif relevant and confidence >= threshold:
                keep.append(result)
                status = "OK "
            else:
                filtered.append(result)
                status = "OUT"

            print(f"  [{status}] {confidence:2d}점 | {result['filename']} | {reason}")

            if not dry_run and status == "OUT":
                filtered_dir = os.path.join(directory, "_irrelevant")
                os.makedirs(filtered_dir, exist_ok=True)
                dest = os.path.join(filtered_dir, result["filename"])
                os.rename(filepath, dest)

            if (i + 1) % 10 == 0:
                print(f"  --- 진행: {i + 1}/{len(image_files)} ---")

        return {"keep": keep, "filtered": filtered, "errors": errors}

    def filter_directory(self, directory: str, threshold: int = 7,
                         dry_run: bool = False) -> dict:
        """디렉토리 내 모든 이미지 필터링"""
        # 이미지 파일 목록
        image_files = []
        for ext in self.IMAGE_EXTENSIONS:
            image_files.extend(glob.glob(os.path.join(directory, f"*{ext}")))
        image_files.sort()

        if not image_files:
            print(f"  이미지 없음: {directory}")
            return {"keep": [], "filtered": [], "errors": []}

        print(f"  평가 대상: {len(image_files)}장 (threshold: {threshold}점)")

        keep, filtered, errors = [], [], []

        for i, filepath in enumerate(image_files):
            result = self.evaluate_image(filepath)
            self.results.append(result)

            score = result.get("score", -1)
            tags = ", ".join(result.get("tags", []))
            reason = result.get("reason", "")

            if score < 0:
                errors.append(result)
                status = "ERR"
            elif score >= threshold:
                keep.append(result)
                status = "OK "
            else:
                filtered.append(result)
                status = "OUT"

            print(f"  [{status}] {score:2d}점 | {result['filename']} | {tags} | {reason}")

            # 부적합 이미지 이동
            if not dry_run and status == "OUT":
                filtered_dir = os.path.join(directory, "_filtered")
                os.makedirs(filtered_dir, exist_ok=True)
                dest = os.path.join(filtered_dir, result["filename"])
                os.rename(filepath, dest)

            if (i + 1) % 10 == 0:
                print(f"  --- 진행: {i + 1}/{len(image_files)} ---")

        return {"keep": keep, "filtered": filtered, "errors": errors}

    def save_report(self, output_dir: str, results: dict):
        """필터링 리포트 저장"""
        report = {
            "brand": "Wacky Willy",
            "filtered_at": datetime.now().isoformat(),
            "summary": {
                "keep": len(results["keep"]),
                "filtered": len(results["filtered"]),
                "errors": len(results["errors"]),
                "keep_rate": (
                    f"{len(results['keep']) / max(1, len(results['keep']) + len(results['filtered'])) * 100:.1f}%"
                ),
            },
            "keep": results["keep"],
            "filtered": results["filtered"],
            "errors": results["errors"],
        }

        report_path = os.path.join(output_dir, "_filter_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n  리포트 저장: {report_path}")
        return report_path


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Wacky Willy Brand Fit Filter — Claude Vision"
    )
    parser.add_argument("directory", help="필터링할 이미지 디렉토리")
    parser.add_argument("--threshold", "-t", type=int, default=7,
                        help="적합 판정 최소 점수 (기본: 7)")
    parser.add_argument("--model", default="claude-sonnet-4-6",
                        help="사용할 Claude 모델 (기본: claude-sonnet-4-6)")
    parser.add_argument("--api-key", help="Anthropic API 키 (없으면 ANTHROPIC_API_KEY 환경변수)")
    parser.add_argument("--keyword", "-k",
                        help="키워드 적합성 필터 모드 (브랜드 필터 대신 키워드 매칭)")
    parser.add_argument("--dry-run", action="store_true",
                        help="미리보기만 (파일 이동 안 함)")
    parser.add_argument("--recursive", "-r", action="store_true",
                        help="하위 폴더도 재귀 필터링")

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"디렉토리를 찾을 수 없음: {args.directory}")
        sys.exit(1)

    mode_label = "Keyword Relevance" if args.keyword else "Brand Fit"
    print("=" * 60)
    print(f"  Wacky Willy {mode_label} Filter")
    print(f"  대상: {args.directory}")
    if args.keyword:
        print(f"  키워드: {args.keyword}")
    print(f"  기준: {args.threshold}점 이상")
    print(f"  모드: {'미리보기' if args.dry_run else '실행'}")
    print("=" * 60)

    filt = BrandFitFilter(api_key=args.api_key, model=args.model)

    all_results = {"keep": [], "filtered": [], "errors": []}

    if args.keyword:
        # 키워드 적합성 필터 모드
        all_results = filt.filter_by_keyword(
            args.directory, args.keyword, args.threshold, args.dry_run
        )
    elif args.recursive:
        # 브랜드 필터 - 하위 폴더 순회
        for subdir in sorted(os.listdir(args.directory)):
            full = os.path.join(args.directory, subdir)
            if os.path.isdir(full) and not subdir.startswith("_"):
                print(f"\n── {subdir} ──")
                res = filt.filter_directory(full, args.threshold, args.dry_run)
                for k in all_results:
                    all_results[k].extend(res[k])
    else:
        all_results = filt.filter_directory(
            args.directory, args.threshold, args.dry_run
        )

    # 리포트
    filt.save_report(args.directory, all_results)

    # 요약
    total = len(all_results["keep"]) + len(all_results["filtered"])
    print("\n" + "=" * 60)
    print(f"  적합: {len(all_results['keep'])}장")
    dest_folder = "_irrelevant/" if args.keyword else "_filtered/"
    print(f"  부적합: {len(all_results['filtered'])}장 → {dest_folder} 이동{'(미리보기)' if args.dry_run else ''}")
    print(f"  에러: {len(all_results['errors'])}장")
    print(f"  적합률: {len(all_results['keep']) / max(1, total) * 100:.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    main()
