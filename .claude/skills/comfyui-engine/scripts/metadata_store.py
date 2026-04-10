#!/usr/bin/env python3.12
"""
생성 이미지별 메타데이터 JSON 저장/로드.
재현성을 위해 seed, prompt, workflow, model, LoRA, 시간 등을 기록한다.

사용 예:
    from metadata_store import save, load

    save(
        "/path/to/image.png",
        workflow_rel="lookbook/sdxl_street_hires.json",
        positive_prompt="...",
        negative_prompt="...",
        seed=12345,
        ...
    )
    # → /path/to/image.meta.json 생성

    meta = load("/path/to/image.meta.json")
    # 동일 파라미터로 재생성 가능
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


SCHEMA_VERSION = "1.0"


def save(
    image_path: str,
    *,
    workflow_rel: str,
    positive_prompt: str,
    negative_prompt: str,
    seed: int,
    steps: int,
    cfg: float,
    sampler: str,
    scheduler: str,
    width: int,
    height: int,
    section_type: str,
    source_sheet: Optional[str] = None,
    source_header: Optional[str] = None,
    model_family: str = "sdxl",
    checkpoint: Optional[str] = None,
    loras: Optional[list[str]] = None,
    ref_image: Optional[str] = None,
    hires_fix: bool = False,
    extra: Optional[dict] = None,
) -> str:
    """이미지 옆에 `<image>.meta.json`을 생성하고 경로를 반환."""
    meta_path = str(Path(image_path).with_suffix(".meta.json"))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "image": Path(image_path).name,
        "workflow": workflow_rel,
        "model_family": model_family,
        "checkpoint": checkpoint,
        "loras": loras or [],
        "section_type": section_type,
        "prompt": {
            "positive": positive_prompt,
            "negative": negative_prompt,
        },
        "params": {
            "seed": seed,
            "steps": steps,
            "cfg": cfg,
            "sampler": sampler,
            "scheduler": scheduler,
            "width": width,
            "height": height,
            "hires_fix": hires_fix,
        },
        "source": {
            "sheet": source_sheet,
            "header": source_header,
        },
        "ref_image": ref_image,
        "extra": extra or {},
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return meta_path


def load(meta_path: str) -> dict:
    """메타데이터 JSON을 로드한다."""
    with open(meta_path, encoding="utf-8") as f:
        return json.load(f)


def to_generate_args(meta: dict) -> dict:
    """메타데이터를 generate.py가 소비할 인자 dict로 변환."""
    return {
        "prompt": meta["prompt"]["positive"],
        "negative": meta["prompt"]["negative"],
        "seed": meta["params"]["seed"],
        "steps": meta["params"]["steps"],
        "cfg": meta["params"]["cfg"],
        "width": meta["params"]["width"],
        "height": meta["params"]["height"],
        "sampler": meta["params"]["sampler"],
        "scheduler": meta["params"]["scheduler"],
        "workflow_rel": meta["workflow"],
        "section_type": meta["section_type"],
        "ref_image": meta.get("ref_image"),
        "hires_fix": meta["params"].get("hires_fix", False),
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법: python3.12 metadata_store.py <image.meta.json>")
        sys.exit(1)

    meta = load(sys.argv[1])
    print(json.dumps(meta, ensure_ascii=False, indent=2))
