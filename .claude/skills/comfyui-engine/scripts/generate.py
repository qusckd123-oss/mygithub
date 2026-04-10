#!/usr/bin/env python3.12
"""
ComfyUI 이미지/영상 생성 — 단일 프롬프트 실행 (v2.1).

v2 변경점:
- BRAND_BOOSTER 하드코딩 제거 → PromptComposer가 visual-identity.json 기반 SSOT 주입
- 섹션 타입별 프롬프트/네거티브/샘플러 자동 분기 (flat_sketch 컬러 충돌 버그 해결)
- WorkflowResolver가 section_type + channel + ref_image 유무로 워크플로우 자동 선택
- 채널 → SDXL 해상도 자동 매핑
- 메타데이터 JSON 동반 저장 (재현성)
- --from-meta 모드로 이전 생성 재현
- --dry-run 모드로 실제 생성 없이 프롬프트 미리보기

v2.1 추가 (2026-04-10 NotebookLM 리서치 기반):
- Foundation Formula 7슬롯 입력: --shot / --silhouette / --material / --details /
  --color-slot / --construction / --lighting-quality (값이 주어지면 --prompt 대신 7슬롯 모드)
- --style-lock <name>: 컬렉션 단위 seed + 샘플러 + photo_direction 고정 (일관성 제어).
  첫 호출 시 ~/.comfyui-engine/style-locks/<name>.json 생성, 이후 호출은 해당 값 재사용.
  brand-prompt-kit.json의 style_lock_presets 프리셋 이름도 직접 사용 가능.
- --iterate <prev_image>: BUG 벤치마크 반복 수정. 이전 이미지를 참조로 삼고
  --revise "수정 지시"와 결합해 img2img/IPAdapter 워크플로우로 재생성.
  출력 파일명에 _iter<N> 자동 suffix, 메타데이터에 parent_image/iteration 기록.

사용법:
    # 직접 실행
    python3.12 generate.py \
        --section-type lookbook \
        --channel musinsa_hero \
        --prompt "oversized hoodie with graphic print" \
        --output ./test.png

    # Foundation Formula 7슬롯
    python3.12 generate.py \
        --section-type lookbook \
        --shot three_quarter \
        --silhouette oversized_hoodie \
        --material french_terry_brushed \
        --details signature_stitching \
        --construction premium_manufacture \
        --lighting-quality golden_hour \
        --output ./ff.png

    # 컬렉션 스타일 락 (첫 호출)
    python3.12 generate.py --style-lock 26ss-lookbook \
        --section-type lookbook --prompt "..." --seed 12345 --output ./01.png

    # 컬렉션 스타일 락 (재사용 — seed/sampler 자동 로드)
    python3.12 generate.py --style-lock 26ss-lookbook \
        --section-type lookbook --prompt "다른 룩" --output ./02.png

    # BUG 반복 수정
    python3.12 generate.py --iterate ./01.png \
        --revise "change color to signature yellow, keep the silhouette" \
        --section-type lookbook --output ./01_iter.png

    # 플랫 스케치 (brand_booster 자동 OFF)
    python3.12 generate.py \
        --section-type flat_sketch \
        --prompt "technical front view of hoodie" \
        --output ./sketch.png

    # dry-run
    python3.12 generate.py --section-type lookbook --prompt "test" --dry-run

    # 재현
    python3.12 generate.py --from-meta ./test.meta.json --output ./test_repro.png
"""

import argparse
import json
import os
import random
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
WORKFLOWS_DIR = SCRIPT_DIR.parent / "workflows"
REFS_DIR = SCRIPT_DIR.parent / "references"
STYLE_LOCK_DIR = Path.home() / ".comfyui-engine" / "style-locks"
sys.path.insert(0, str(SCRIPT_DIR))

from comfyui_client import ComfyUIClient
from prompt_composer import PromptComposer
from workflow_resolver import WorkflowResolver
import metadata_store


# ────────────────────────────────────────────────────────────
# v2.1: Style Lock 관리 (컬렉션 단위 일관성)
# ────────────────────────────────────────────────────────────
def load_style_lock(name: str) -> dict | None:
    """
    Style lock 로드 우선순위:
      1. ~/.comfyui-engine/style-locks/<name>.json (사용자 저장본)
      2. brand-prompt-kit.json의 style_lock_presets[<name>] (빌트인 프리셋)
    """
    user_path = STYLE_LOCK_DIR / f"{name}.json"
    if user_path.exists():
        with open(user_path, encoding="utf-8") as f:
            return json.load(f)

    # 빌트인 프리셋 fallback
    kit_path = REFS_DIR / "brand-prompt-kit.json"
    if kit_path.exists():
        with open(kit_path, encoding="utf-8") as f:
            kit = json.load(f)
        preset = kit.get("style_lock_presets", {}).get(name)
        if preset:
            return dict(preset)
    return None


def save_style_lock(name: str, payload: dict) -> Path:
    """사용자 style lock을 저장 (첫 호출 시)."""
    STYLE_LOCK_DIR.mkdir(parents=True, exist_ok=True)
    path = STYLE_LOCK_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def next_iteration_path(base_path: str) -> tuple[str, int]:
    """
    파일명에서 _iter<N> suffix를 찾아 다음 iteration 번호 반환.
    base_path = "./01.png"           → ("./01_iter1.png", 1)
    base_path = "./01_iter3.png"     → ("./01_iter4.png", 4)
    """
    p = Path(base_path)
    stem = p.stem
    match = re.match(r"^(.*)_iter(\d+)$", stem)
    if match:
        root, n = match.group(1), int(match.group(2))
        new_n = n + 1
    else:
        root, new_n = stem, 1
    return str(p.with_name(f"{root}_iter{new_n}{p.suffix}")), new_n


def inject_params(workflow: dict, params: dict) -> dict:
    """워크플로우 JSON에 파라미터를 주입한다."""
    wf = json.loads(json.dumps(workflow))  # deep copy

    for node_id, node in wf.items():
        inputs = node.setdefault("inputs", {})
        ct = node.get("class_type", "")

        # ── CLIPTextEncode: positive/negative 프롬프트 주입 ──
        if ct == "CLIPTextEncode":
            title = node.get("_meta", {}).get("title", "").lower()
            if "positive" in title:
                inputs["text"] = params.get("prompt", inputs.get("text", ""))
            elif "negative" in title:
                inputs["text"] = params.get("negative", inputs.get("text", ""))
            # _meta 없는 경우: text 필드의 placeholder로 판별
            elif inputs.get("text") == "POSITIVE_PROMPT":
                inputs["text"] = params.get("prompt", "")
            elif inputs.get("text") == "NEGATIVE_PROMPT":
                inputs["text"] = params.get("negative", "")

        # ── EmptyLatentImage: 해상도/배치 ──
        if ct == "EmptyLatentImage":
            if "width" in params:
                inputs["width"] = params["width"]
            if "height" in params:
                inputs["height"] = params["height"]
            if "batch_size" in params:
                inputs["batch_size"] = params["batch_size"]

        # ── KSampler: 시드/스텝/CFG/샘플러/스케줄러 ──
        if ct == "KSampler":
            if "seed" in params:
                inputs["seed"] = params["seed"]
            if "steps" in params:
                inputs["steps"] = params["steps"]
            if "cfg" in params:
                inputs["cfg"] = params["cfg"]
            if "sampler" in params:
                inputs["sampler_name"] = params["sampler"]
            if "scheduler" in params:
                inputs["scheduler"] = params["scheduler"]

        # ── SaveImage: 파일명 prefix ──
        if ct == "SaveImage":
            if "filename_prefix" in params:
                inputs["filename_prefix"] = params["filename_prefix"]

        # ── ControlNet 강도 ──
        if ct == "ControlNetApplyAdvanced":
            if "ref_strength" in params:
                inputs["strength"] = params["ref_strength"]

        # ── IP-Adapter 가중치 (v2 Advanced / legacy Apply 둘 다 지원) ──
        if "IPAdapter" in ct and "Loader" not in ct:
            if "ref_strength" in params:
                inputs["weight"] = params["ref_strength"]

        # ── 참조 이미지 (LoadImage 노드) ──
        if ct == "LoadImage":
            if params.get("ref_image_name"):
                inputs["image"] = params["ref_image_name"]

    return wf


def _has_foundation_slot(args) -> bool:
    """7슬롯 중 하나라도 지정되었는지 확인."""
    return any(
        getattr(args, slot, None)
        for slot in (
            "shot",
            "silhouette",
            "material",
            "details",
            "color_slot",
            "construction",
            "lighting_quality",
        )
    )


def _apply_style_lock_defaults(args, lock: dict) -> None:
    """
    Style lock 값을 args에 적용. 사용자가 CLI에서 명시한 값이 있으면 그것을 우선.
    적용되는 키: seed, sampler, scheduler, cfg, steps, ref_image, lighting_quality
    """
    def _fill(attr: str, value):
        if value is None:
            return
        if getattr(args, attr, None) is None:
            setattr(args, attr, value)

    _fill("seed", lock.get("seed"))
    _fill("_locked_sampler", lock.get("sampler"))
    _fill("_locked_scheduler", lock.get("scheduler"))
    _fill("_locked_cfg", lock.get("cfg"))
    _fill("_locked_steps", lock.get("steps"))
    _fill("ref_image", lock.get("ref_image"))
    _fill("lighting_quality", lock.get("lighting_quality"))


def generate(args) -> list[str]:
    """
    메인 생성 로직.
    Returns: 저장된 파일 경로 리스트.
    """
    # ── 0. --iterate: BUG 반복 수정 세팅 ──
    iteration_n = 0
    parent_image = None
    if getattr(args, "iterate", None):
        parent_image = args.iterate
        if not os.path.exists(parent_image):
            print(f"ERROR: --iterate 대상 파일 없음: {parent_image}")
            sys.exit(1)
        # 이전 이미지를 ref-image로 전환 (moodboard/IPAdapter 워크플로우 유도)
        if not args.ref_image:
            args.ref_image = parent_image
        # section_type이 iterable 성격이 아니면 moodboard로 강제
        if args.section_type not in ("moodboard", "lookbook"):
            print(f"[iterate] section_type={args.section_type} → moodboard 로 전환")
            args.section_type = "moodboard"
        elif args.section_type == "lookbook":
            print(f"[iterate] lookbook 섹션이지만 ref_image가 있으므로 moodboard 워크플로우 유도")
            args.section_type = "moodboard"
        # 이전 이미지 메타가 있으면 seed/params 로드 (style-lock 같은 효과)
        parent_meta_path = Path(parent_image).with_suffix(".meta.json")
        if parent_meta_path.exists():
            try:
                parent_meta = metadata_store.load(str(parent_meta_path))
                if args.seed is None and parent_meta.get("params", {}).get("seed") is not None:
                    args.seed = parent_meta["params"]["seed"]
                    print(f"[iterate] 부모 메타에서 seed={args.seed} 로드")
            except Exception as e:
                print(f"[iterate] 부모 메타 로드 실패 (무시): {e}")
        # 출력 파일명 자동 iteration suffix
        if args.output:
            new_out, iteration_n = next_iteration_path(args.output)
            args.output = new_out
            print(f"[iterate] 출력: {args.output} (iter {iteration_n})")
        # revise 지시를 프롬프트 앞에 prepend
        if getattr(args, "revise", None):
            prefix = f"REVISION DIRECTIVE: {args.revise}. "
            if args.prompt:
                args.prompt = prefix + args.prompt
            else:
                args.prompt = prefix + "same garment with requested revisions, keep silhouette and composition"

    # ── 0.5 --style-lock: lock 파일 로드 또는 빌트인 프리셋 적용 ──
    style_lock_name = getattr(args, "style_lock", None)
    if style_lock_name:
        # 임시 locked 필드 초기화
        for f in ("_locked_sampler", "_locked_scheduler", "_locked_cfg", "_locked_steps"):
            if not hasattr(args, f):
                setattr(args, f, None)
        lock = load_style_lock(style_lock_name)
        if lock:
            print(f"[style-lock] '{style_lock_name}' 로드됨")
            _apply_style_lock_defaults(args, lock)
        else:
            print(f"[style-lock] '{style_lock_name}' — 기존 lock 없음, 이번 실행 후 저장됩니다")
    else:
        # 기본값 보장
        for f in ("_locked_sampler", "_locked_scheduler", "_locked_cfg", "_locked_steps"):
            setattr(args, f, None)

    # ── 1. --from-meta: 재현 모드 ──
    if getattr(args, "from_meta", None):
        meta = metadata_store.load(args.from_meta)
        # 재현에 필요한 값을 args에 덮어쓰기
        args.prompt = meta["prompt"]["positive"]
        args.negative = meta["prompt"]["negative"]
        args.seed = meta["params"]["seed"]
        args.steps = meta["params"]["steps"]
        args.cfg = meta["params"]["cfg"]
        args.width = meta["params"]["width"]
        args.height = meta["params"]["height"]
        args.section_type = meta["section_type"]
        args.workflow_rel = meta["workflow"]
        args.ref_image = meta.get("ref_image")
        args._sampler_override = meta["params"].get("sampler")
        args._scheduler_override = meta["params"].get("scheduler")
        args._from_meta_mode = True
        args._raw_positive_override = True  # Composer 재합성 건너뛰기
    else:
        args._from_meta_mode = False
        args._raw_positive_override = False

    # ── 2. 프롬프트 합성 (Composer) ──
    composer = PromptComposer()

    if args._raw_positive_override:
        # 재현 모드: 이미 positive/negative가 완성되어 있음
        comp = {
            "positive": args.prompt,
            "negative": args.negative,
            "sampler": args._sampler_override or "dpmpp_2m",
            "scheduler": args._scheduler_override or "karras",
            "cfg": args.cfg,
            "steps": args.steps,
            "resolution": [args.width, args.height],
            "hires_fix": False,
            "workflow_intent": None,
            "requires_ref_image": False,
            "requires_fixed_seed": False,
        }
    elif _has_foundation_slot(args):
        # Foundation Formula 7슬롯 모드
        comp = composer.compose_foundation_formula(
            section_type=args.section_type,
            shot_type=args.shot,
            silhouette=args.silhouette,
            material=args.material,
            details=args.details,
            color=args.color_slot,
            construction=args.construction,
            lighting_quality=args.lighting_quality,
            extra_raw=args.prompt,  # --prompt 가 있으면 꼬리에 추가
        )
        if args.negative:
            comp["negative"] = args.negative
    else:
        comp = composer.compose(
            raw_prompt=args.prompt or "",
            section_type=args.section_type,
            channel=args.channel,
        )
        # 사용자가 --negative 명시 → 오버라이드
        if args.negative:
            comp["negative"] = args.negative

    # ── 2.5. style lock 샘플러 오버라이드 적용 ──
    if args._locked_sampler:
        comp["sampler"] = args._locked_sampler
    if args._locked_scheduler:
        comp["scheduler"] = args._locked_scheduler
    if args._locked_cfg is not None:
        comp["cfg"] = args._locked_cfg
    if args._locked_steps is not None:
        comp["steps"] = args._locked_steps

    # ── 3. 워크플로우 선택 (Resolver) ──
    resolver = WorkflowResolver()
    res = resolver.resolve(
        section_type=args.section_type,
        ref_image=args.ref_image,
        channel=args.channel,
        model_family=args.model_family,
        phase_limit=args.phase_limit,
        explicit_workflow=getattr(args, "workflow_rel", None),
        speed=getattr(args, "speed", "balanced"),
    )

    # ── 3.5. speed overrides (Lightning LoRA 등) ──
    overrides = res.get("overrides", {})
    if overrides:
        print(f"[speed={getattr(args, 'speed', 'balanced')}] 샘플러 오버라이드: {overrides}")
        for k in ("sampler", "scheduler", "steps", "cfg"):
            if k in overrides:
                comp[k] = overrides[k]

    # ── 4. 해상도 최종 결정 (CLI > from-meta > channel > profile 기본값) ──
    width = args.width or res["width"]
    height = args.height or res["height"]
    # from-meta 모드에서는 args.width/height가 이미 설정됨

    # ── 5. 시드 ──
    if args.seed is not None:
        seed = int(args.seed)
    else:
        seed = random.randint(0, 2**32 - 1)

    # ── 6. dry-run ──
    if getattr(args, "dry_run", False):
        preview = {
            "workflow": res["workflow_rel"],
            "section_type": args.section_type,
            "channel": args.channel,
            "resolution": [width, height],
            "sampler": comp["sampler"],
            "scheduler": comp["scheduler"],
            "cfg": comp["cfg"],
            "steps": comp["steps"],
            "seed": seed,
            "positive": comp["positive"],
            "negative": comp["negative"],
            "positive_tokens": composer.token_count(comp["positive"]),
            "negative_tokens": composer.token_count(comp["negative"]),
        }
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return []

    # ── 7. ComfyUI 서버 확인 ──
    client = ComfyUIClient()
    if not client.is_alive():
        print("ERROR: ComfyUI 서버가 응답하지 않습니다.")
        print("  시작: bash server_ctl.sh start")
        sys.exit(1)

    # ── 8. 워크플로우 JSON 로드 ──
    with open(res["workflow_path"], encoding="utf-8") as f:
        workflow = json.load(f)

    # ── 9. 참조 이미지 업로드 ──
    ref_image_name = None
    if args.ref_image:
        if not os.path.exists(args.ref_image):
            print(f"ERROR: 참조 이미지 없음: {args.ref_image}")
            sys.exit(1)
        print(f"참조 이미지 업로드: {args.ref_image}")
        upload_result = client.upload_image(args.ref_image)
        ref_image_name = upload_result.get("name", os.path.basename(args.ref_image))

    # ── 10. 파라미터 주입 ──
    params = {
        "prompt": comp["positive"],
        "negative": comp["negative"],
        "width": width,
        "height": height,
        "seed": seed,
        "steps": comp["steps"],
        "cfg": comp["cfg"],
        "sampler": comp["sampler"],
        "scheduler": comp["scheduler"],
        "batch_size": args.batch,
        "ref_image_name": ref_image_name,
        "ref_strength": args.ref_strength,
        "filename_prefix": Path(args.output).stem if args.output else "comfyui_output",
    }
    workflow = inject_params(workflow, params)

    # ── 11. 실행 로그 ──
    print(f"섹션: {args.section_type}")
    print(f"워크플로우: {res['workflow_rel']}")
    print(f"해상도: {width}x{height}")
    print(f"시드: {seed}")
    print(f"샘플러: {comp['sampler']}/{comp['scheduler']}, CFG: {comp['cfg']}, 스텝: {comp['steps']}")
    if args.channel:
        print(f"채널: {args.channel}")
    print("생성 중...")

    # ── 12. 큐 + 대기 + 다운로드 ──
    prompt_id = client.queue_prompt(workflow)

    output_dir = os.path.dirname(args.output) or "."
    os.makedirs(output_dir, exist_ok=True)

    saved = client.wait_and_download(
        prompt_id,
        output_dir=output_dir,
        filename_prefix=Path(args.output).stem,
        timeout=args.timeout,
    )

    # ── 13. 파일명 정리 (단일 출력) ──
    if len(saved) == 1 and args.output:
        if saved[0] != args.output:
            os.rename(saved[0], args.output)
            saved = [args.output]

    # ── 14. 메타데이터 저장 ──
    checkpoint = _extract_checkpoint(workflow)
    extra_meta = {}
    if parent_image:
        extra_meta["parent_image"] = parent_image
        extra_meta["iteration"] = iteration_n
        if getattr(args, "revise", None):
            extra_meta["revise_directive"] = args.revise
    if style_lock_name:
        extra_meta["style_lock"] = style_lock_name

    for fp in saved:
        metadata_store.save(
            fp,
            workflow_rel=res["workflow_rel"],
            positive_prompt=comp["positive"],
            negative_prompt=comp["negative"],
            seed=seed,
            steps=comp["steps"],
            cfg=comp["cfg"],
            sampler=comp["sampler"],
            scheduler=comp["scheduler"],
            width=width,
            height=height,
            section_type=args.section_type,
            source_sheet=getattr(args, "source_sheet", None),
            source_header=getattr(args, "source_header", None),
            model_family=args.model_family,
            checkpoint=checkpoint,
            ref_image=args.ref_image,
            hires_fix=comp.get("hires_fix", False),
            extra=extra_meta if extra_meta else None,
        )

    # ── 14.5. style-lock 저장 (첫 호출이고 user lock 파일이 없는 경우) ──
    if style_lock_name:
        user_lock_path = STYLE_LOCK_DIR / f"{style_lock_name}.json"
        if not user_lock_path.exists():
            payload = {
                "seed": seed,
                "sampler": comp["sampler"],
                "scheduler": comp["scheduler"],
                "cfg": comp["cfg"],
                "steps": comp["steps"],
                "ref_image": args.ref_image,
                "lighting_quality": getattr(args, "lighting_quality", None),
                "section_type": args.section_type,
                "created_at_image": saved[0] if saved else None,
            }
            path = save_style_lock(style_lock_name, payload)
            print(f"[style-lock] 저장됨: {path}")

    # ── 15. 완료 ──
    print(f"\n완료! 생성된 파일:")
    for f in saved:
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"  {f} ({size_mb:.1f}MB)")
        print(f"  → {Path(f).with_suffix('.meta.json').name}")

    return saved


def _extract_checkpoint(workflow: dict) -> str | None:
    """워크플로우에서 체크포인트 파일명 추출."""
    for node in workflow.values():
        if node.get("class_type") in ("CheckpointLoaderSimple", "ImageOnlyCheckpointLoader"):
            return node.get("inputs", {}).get("ckpt_name")
    return None


def main():
    parser = argparse.ArgumentParser(description="ComfyUI 이미지/영상 생성 (v2.1)")

    # 입력
    parser.add_argument("--prompt", default=None, help="이미지 생성 프롬프트 (영문)")
    parser.add_argument("--negative", default=None, help="네거티브 프롬프트 오버라이드")

    # v2.1: Foundation Formula 7슬롯 (brand-prompt-kit.json foundation_formula 참조)
    ff_group = parser.add_argument_group(
        "Foundation Formula (v2.1)",
        "7슬롯 구조화 입력 — 하나라도 지정되면 7슬롯 모드로 진입. --prompt는 꼬리에 추가됨.",
    )
    ff_group.add_argument("--shot", default=None, help="샷 유형 (macro_closeup | three_quarter | full_body_editorial | flat_lay | street_candid | product_hero) 또는 자유 텍스트")
    ff_group.add_argument("--silhouette", default=None, help="실루엣 키 (oversized_hoodie | fitted_sweatshirt | tailored_jacket 등) 또는 자유 텍스트")
    ff_group.add_argument("--material", default=None, help="소재 키 (material-intelligence.json 참조: french_terry_brushed | velvet | denim_raw_selvedge 등) 또는 자유 텍스트")
    ff_group.add_argument("--details", default=None, help="디테일 키 (signature_stitching | embroidered_logo | patch_pocket 등) 또는 자유 텍스트")
    ff_group.add_argument("--color-slot", default=None, help="색상 슬롯 — 비우면 브랜드 컬러 토큰 자동 주입")
    ff_group.add_argument("--construction", default=None, help="제작방식 키 (premium_manufacture | heritage_construction 등) 또는 자유 텍스트")
    ff_group.add_argument("--lighting-quality", default=None, help="조명 품질 키 (studio_softbox | golden_hour | editorial_dramatic 등) 또는 자유 텍스트")

    # v2.1: 컬렉션 일관성 제어
    lock_group = parser.add_argument_group(
        "Style Lock & Iterate (v2.1)",
        "컬렉션 단위 시드/샘플러 고정 및 BUG 벤치마크 반복 수정",
    )
    lock_group.add_argument(
        "--style-lock",
        default=None,
        help="컬렉션 스타일 락 이름. 최초 호출 시 현재 seed/sampler/cfg/steps 저장, 이후 호출은 값 재사용. "
             "~/.comfyui-engine/style-locks/<name>.json 또는 brand-prompt-kit.json의 style_lock_presets.",
    )
    lock_group.add_argument(
        "--iterate",
        default=None,
        help="BUG 벤치마크 반복 수정: 이전 이미지 경로. 해당 이미지를 ref-image로 사용하고 "
             "출력 파일명에 _iter<N> suffix 자동 적용, 부모 메타에서 seed 상속.",
    )
    lock_group.add_argument(
        "--revise",
        default=None,
        help="--iterate와 함께 사용: 수정 지시 프롬프트 (예: 'change color to yellow, keep silhouette')",
    )

    # 섹션/채널/모델
    parser.add_argument(
        "--section-type",
        default="lookbook",
        choices=["flat_sketch", "lookbook", "graphic", "moodboard", "colorway", "structure_control"],
        help="섹션 타입 (프롬프트 프로파일 및 워크플로우 선택 기준)",
    )
    parser.add_argument(
        "--channel",
        default=None,
        help="출력 채널 (musinsa_hero, instagram_feed 등) — 해상도 자동 결정",
    )
    parser.add_argument(
        "--model-family",
        default="sdxl",
        choices=["sdxl", "flux"],
        help="모델 패밀리 (기본 sdxl, flux는 Phase 2 이후)",
    )
    parser.add_argument(
        "--phase-limit",
        type=int,
        default=1,
        help="사용 가능한 워크플로우의 최대 phase (기본 1, Phase 2-Slim 이후 2)",
    )
    parser.add_argument(
        "--speed",
        default="balanced",
        choices=["fast", "balanced"],
        help="생성 속도 프로파일 (fast: Lightning LoRA 4-step, balanced: 기본 30-step)",
    )
    parser.add_argument(
        "--workflow-rel",
        default=None,
        help="카탈로그의 워크플로우 경로 직접 지정 (예: lookbook/sdxl_street_hires.json)",
    )

    # 해상도 (CLI가 최우선)
    parser.add_argument("--width", type=int, default=None, help="출력 너비 (기본 채널/프로파일 자동)")
    parser.add_argument("--height", type=int, default=None, help="출력 높이 (기본 채널/프로파일 자동)")

    # 샘플링
    parser.add_argument("--seed", type=int, default=None, help="시드 (기본 랜덤)")
    parser.add_argument("--steps", type=int, default=None, help="샘플링 스텝 (기본 프로파일)")
    parser.add_argument("--cfg", type=float, default=None, help="CFG 스케일 (기본 프로파일)")
    parser.add_argument("--batch", type=int, default=1, help="배치 사이즈 (기본 1)")

    # 참조 이미지
    parser.add_argument("--ref-image", default=None, help="참조 이미지 경로 (moodboard/controlnet)")
    parser.add_argument("--ref-strength", type=float, default=0.7, help="참조 이미지 강도 0.0~1.0")

    # 출력
    parser.add_argument("--output", default="./output.png", help="출력 파일 경로")
    parser.add_argument("--timeout", type=int, default=600, help="최대 대기 시간(초)")

    # 재현/배치 연동
    parser.add_argument("--from-meta", default=None, help="메타데이터 JSON으로 재현 생성")
    parser.add_argument("--source-sheet", default=None, help="(배치) 원본 시트 경로 기록용")
    parser.add_argument("--source-header", default=None, help="(배치) 엔트리 헤더 기록용")

    # 유틸
    parser.add_argument("--dry-run", action="store_true", help="실제 생성 없이 프롬프트 미리보기")

    args = parser.parse_args()

    # argparse가 --color-slot → args.color_slot, --lighting-quality → args.lighting_quality 로 변환
    # (dest 자동 변환). _has_foundation_slot() 에서 참조.

    # 유효성 검사 — Foundation Formula 슬롯이나 --iterate 가 있으면 --prompt 없어도 OK
    has_input = (
        args.prompt
        or args.from_meta
        or _has_foundation_slot(args)
        or args.iterate
    )
    if not has_input:
        parser.error("--prompt, --from-meta, Foundation Formula 슬롯(--shot/--silhouette/--material 등), 또는 --iterate 중 하나는 필수입니다.")

    # --revise 는 --iterate 와만 사용
    if args.revise and not args.iterate:
        parser.error("--revise는 --iterate와 함께 사용해야 합니다.")

    generate(args)


if __name__ == "__main__":
    main()
