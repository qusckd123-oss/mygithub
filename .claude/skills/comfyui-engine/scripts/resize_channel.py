#!/usr/bin/env python3.12
"""
채널별 이미지 리사이즈 유틸리티.
생성된 이미지를 무신사/인스타/룩북 등 채널 규격에 맞게 변환한다.

사용법:
    # 단일 파일
    python3.12 resize_channel.py --input image.png --channel musinsa --output resized.png

    # 디렉토리 일괄
    python3.12 resize_channel.py --input-dir ./generated/ --channel instagram_feed --output-dir ./resized/

    # 여러 채널 동시
    python3.12 resize_channel.py --input image.png --channel musinsa,instagram_feed,lookbook --output-dir ./multi/
"""

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SPECS_PATH = SCRIPT_DIR.parent / "references" / "channel-specs.json"

# 런타임 의존성 부트스트랩 — 시스템 python 에서 실행 시 ~/ComfyUI/venv 로 자동 전환
sys.path.insert(0, str(SCRIPT_DIR))
import _bootstrap  # noqa: E402
_bootstrap.ensure_venv("PIL")


def load_channel_specs() -> dict:
    """채널 규격 로드."""
    with open(SPECS_PATH) as f:
        return json.load(f)


def resize_image(input_path: str, width: int, height: int, output_path: str, fit: str = "cover"):
    """
    이미지를 지정 크기로 리사이즈.
    fit 모드:
      - cover: 비율 유지하면서 전체 영역을 채움 (크롭 발생 가능)
      - contain: 비율 유지하면서 영역 안에 맞춤 (여백 발생 가능, 흰색 배경)
      - stretch: 비율 무시하고 정확한 크기로 (비추천)
    """
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: Pillow가 설치되지 않았습니다.")
        print("  pip install Pillow")
        sys.exit(1)

    img = Image.open(input_path)
    orig_w, orig_h = img.size

    if fit == "cover":
        # 비율 유지 + 크롭 (영역 채움)
        ratio_w = width / orig_w
        ratio_h = height / orig_h
        ratio = max(ratio_w, ratio_h)
        new_w = int(orig_w * ratio)
        new_h = int(orig_h * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        # 중앙 크롭
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        img = img.crop((left, top, left + width, top + height))

    elif fit == "contain":
        # 비율 유지 + 여백 (영역 안에 맞춤)
        ratio_w = width / orig_w
        ratio_h = height / orig_h
        ratio = min(ratio_w, ratio_h)
        new_w = int(orig_w * ratio)
        new_h = int(orig_h * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        # 흰색 캔버스에 중앙 배치
        canvas = Image.new("RGB", (width, height), (255, 255, 255))
        paste_x = (width - new_w) // 2
        paste_y = (height - new_h) // 2
        canvas.paste(img, (paste_x, paste_y))
        img = canvas

    elif fit == "stretch":
        img = img.resize((width, height), Image.LANCZOS)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, quality=95)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="채널별 이미지 ���사이즈")
    parser.add_argument("--input", default=None, help="입력 이미지 경로")
    parser.add_argument("--input-dir", default=None, help="입력 디렉토리 (일괄)")
    parser.add_argument(
        "--channel",
        required=True,
        help="채널명 (쉼표 구분 가능). 예: musinsa, instagram_feed, lookbook",
    )
    parser.add_argument("--output", default=None, help="출력 파일 경로 (단일)")
    parser.add_argument("--output-dir", default=None, help="출력 디렉토리")
    parser.add_argument(
        "--fit",
        choices=["cover", "contain", "stretch"],
        default="cover",
        help="리사이즈 모드 (기본: cover)",
    )
    parser.add_argument("--list-channels", action="store_true", help="사용 가능한 채널 목록")

    args = parser.parse_args()
    specs = load_channel_specs()

    # 채널 목록 출력
    if args.list_channels:
        print("사용 가능한 채널:")
        for ch_id, ch in specs["channels"].items():
            print(f"  {ch_id}: {ch['name']} ({ch['width']}x{ch['height']})")
        return

    channels = [c.strip() for c in args.channel.split(",")]

    # 입력 파일 수집
    input_files = []
    if args.input:
        input_files = [args.input]
    elif args.input_dir:
        exts = {".png", ".jpg", ".jpeg", ".webp"}
        input_files = sorted(
            str(p) for p in Path(args.input_dir).iterdir() if p.suffix.lower() in exts
        )
    else:
        parser.error("--input 또는 --input-dir 중 하나를 지정하세요.")

    if not input_files:
        print("입력 파일이 없습니다.")
        sys.exit(1)

    total = 0
    for channel_id in channels:
        if channel_id not in specs["channels"]:
            print(f"WARNING: 알 수 없는 채널 '{channel_id}'. --list-channels로 확인하세요.")
            continue

        ch = specs["channels"][channel_id]
        w, h = ch["width"], ch["height"]
        print(f"\n채널: {ch['name']} ({w}x{h})")

        for filepath in input_files:
            stem = Path(filepath).stem
            ext = Path(filepath).suffix

            if args.output and len(input_files) == 1 and len(channels) == 1:
                out_path = args.output
            elif args.output_dir:
                out_path = os.path.join(args.output_dir, channel_id, f"{stem}{ext}")
            else:
                out_dir = os.path.dirname(filepath)
                out_path = os.path.join(out_dir, f"{stem}_{channel_id}{ext}")

            resize_image(filepath, w, h, out_path, fit=args.fit)
            print(f"  {Path(filepath).name} -> {out_path}")
            total += 1

    print(f"\n완료: {total}개 리사이즈")


if __name__ == "__main__":
    main()
