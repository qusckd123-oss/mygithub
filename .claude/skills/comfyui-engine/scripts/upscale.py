#!/usr/bin/env python3.12
"""
4xUltraSharp ESRGAN 업스케일러 래퍼 (Phase 2).

ComfyUI API로 입력 이미지를 4배 업스케일한다.
- 룩북 2000×3000 요구 시 832×1216 → 4배 업스케일 → 3328×4864 → 크롭
- 자사몰 히어로 1920×800 → 1344×768 → 4배 → 5376×3072 → 리사이즈

사용법:
    python3.12 upscale.py --input ./source.png --output ./upscaled.png
    python3.12 upscale.py --input-dir ./generated/ --output-dir ./upscaled/
"""

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from comfyui_client import ComfyUIClient


DEFAULT_MODEL = "4x-UltraSharp.pth"


def build_workflow(image_name: str, filename_prefix: str, model: str = DEFAULT_MODEL) -> dict:
    """ESRGAN 업스케일 워크플로우 JSON 생성."""
    return {
        "1": {
            "class_type": "LoadImage",
            "_meta": {"title": "Load Source"},
            "inputs": {"image": image_name},
        },
        "2": {
            "class_type": "UpscaleModelLoader",
            "_meta": {"title": "Load 4xUltraSharp"},
            "inputs": {"model_name": model},
        },
        "3": {
            "class_type": "ImageUpscaleWithModel",
            "_meta": {"title": "Apply ESRGAN"},
            "inputs": {
                "upscale_model": ["2", 0],
                "image": ["1", 0],
            },
        },
        "4": {
            "class_type": "SaveImage",
            "_meta": {"title": "Save Upscaled"},
            "inputs": {
                "images": ["3", 0],
                "filename_prefix": filename_prefix,
            },
        },
    }


def upscale_one(
    input_path: str,
    output_path: str,
    model: str = DEFAULT_MODEL,
    timeout: int = 300,
) -> str:
    """단일 이미지 업스케일."""
    client = ComfyUIClient()
    if not client.is_alive():
        raise RuntimeError(
            "ComfyUI 서버가 응답하지 않습니다. bash server_ctl.sh start"
        )

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"입력 이미지 없음: {input_path}")

    # ComfyUI input 폴더에 업로드
    upload = client.upload_image(input_path)
    img_name = upload.get("name", os.path.basename(input_path))

    # 워크플로우 구성
    filename_prefix = Path(output_path).stem
    workflow = build_workflow(img_name, filename_prefix, model=model)

    print(f"업스케일 중: {input_path} → {output_path}")
    prompt_id = client.queue_prompt(workflow)

    output_dir = os.path.dirname(output_path) or "."
    os.makedirs(output_dir, exist_ok=True)

    saved = client.wait_and_download(
        prompt_id,
        output_dir=output_dir,
        filename_prefix=filename_prefix,
        timeout=timeout,
    )

    if len(saved) == 1 and saved[0] != output_path:
        os.rename(saved[0], output_path)
        saved = [output_path]

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"완료: {output_path} ({size_mb:.1f}MB)")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="4xUltraSharp ESRGAN 업스케일러")
    parser.add_argument("--input", default=None, help="입력 이미지 경로")
    parser.add_argument("--input-dir", dest="input_dir", default=None, help="입력 디렉토리 (일괄)")
    parser.add_argument("--output", default=None, help="출력 이미지 경로")
    parser.add_argument("--output-dir", dest="output_dir", default=None, help="출력 디렉토리")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="업스케일 모델 (기본 4x-UltraSharp.pth)")
    parser.add_argument("--timeout", type=int, default=300)

    args = parser.parse_args()

    if args.input and args.output:
        upscale_one(args.input, args.output, model=args.model, timeout=args.timeout)
    elif args.input_dir and args.output_dir:
        exts = {".png", ".jpg", ".jpeg", ".webp"}
        files = sorted(
            str(p) for p in Path(args.input_dir).iterdir()
            if p.suffix.lower() in exts
        )
        os.makedirs(args.output_dir, exist_ok=True)
        for fp in files:
            out = os.path.join(args.output_dir, Path(fp).name)
            upscale_one(fp, out, model=args.model, timeout=args.timeout)
    else:
        parser.error("--input/--output 또는 --input-dir/--output-dir 조합 필요")


if __name__ == "__main__":
    main()
