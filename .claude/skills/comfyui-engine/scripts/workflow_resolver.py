#!/usr/bin/env python3.12
"""
워크플로우 선택기 (Phase 1).

입력: section_type + ref_image 유무 + channel + model_family + phase_limit
출력: 최적 워크플로우 JSON 경로 + 해상도 + 메타

우선순위 (resolver_rules.priority_order):
  explicit_cli_resolution > entry_meta_resolution > channel_derived > profile_default
"""

import json
from pathlib import Path
from typing import Optional


SCRIPT_DIR = Path(__file__).parent
REFS_DIR = SCRIPT_DIR.parent / "references"
WORKFLOWS_DIR = SCRIPT_DIR.parent / "workflows"


class WorkflowResolver:
    def __init__(
        self,
        catalog_path: Optional[Path] = None,
        profiles_path: Optional[Path] = None,
    ):
        self.catalog_path = catalog_path or (REFS_DIR / "workflow-catalog.json")
        self.profiles_path = profiles_path or (REFS_DIR / "section-profiles.json")
        with open(self.catalog_path, encoding="utf-8") as f:
            self.catalog = json.load(f)
        with open(self.profiles_path, encoding="utf-8") as f:
            self.profiles = json.load(f)["profiles"]

    def resolve(
        self,
        section_type: str,
        ref_image: Optional[str] = None,
        channel: Optional[str] = None,
        model_family: str = "sdxl",
        phase_limit: int = 1,
        explicit_workflow: Optional[str] = None,
        speed: str = "balanced",
    ) -> dict:
        """
        Returns: {
          "workflow_rel": str,          # "lookbook/sdxl_street_hires.json" 형식
          "workflow_path": str,         # 절대 경로
          "width": int,
          "height": int,
          "meta": dict,                 # 카탈로그 엔트리 (phase, api_version 등 포함)
          "overrides": dict,            # sampler/scheduler/steps/cfg 오버라이드 (Lightning 등)
        }
        """
        # ── 1. explicit_workflow 우선 ──
        if explicit_workflow:
            meta = self.catalog["workflows"].get(explicit_workflow)
            if not meta:
                raise ValueError(
                    f"Unknown explicit workflow: {explicit_workflow}. "
                    f"Valid: {list(self.catalog['workflows'].keys())}"
                )
            wf_rel = explicit_workflow
        else:
            # ── 2. intent 매핑 ──
            intent = self._intent_of(section_type)

            # ── 3. 후보 필터링 ──
            candidates = []
            for path, meta in self.catalog["workflows"].items():
                if meta["intent"] != intent:
                    continue
                if meta["model_family"] != model_family:
                    continue
                if meta.get("phase", 1) > phase_limit:
                    continue
                # ref_image 요구사항 확인
                req = meta.get("requires_ref")
                if req is True and not ref_image:
                    continue
                # optional-scribble / optional-controlnet 은 ref 없어도 통과

                # speed 태그 필터링
                candidate_speed = meta.get("speed", "balanced")
                if speed == "fast" and candidate_speed != "fast":
                    continue
                if speed == "balanced" and candidate_speed == "fast":
                    continue

                candidates.append((path, meta))

            if not candidates:
                fallback = self.catalog.get("resolver_rules", {}).get(
                    "fallback_workflow", "lookbook/sdxl_street_hires.json"
                )
                print(
                    f"[workflow_resolver] WARNING: no candidate for "
                    f"{section_type}/{model_family}/phase<={phase_limit}/speed={speed}, "
                    f"using fallback {fallback}"
                )
                meta = self.catalog["workflows"][fallback]
                wf_rel = fallback
            else:
                # 가장 매칭도 높은 후보 — 현재는 정의 순서 첫 번째
                # Phase 3에서 우선순위 스코어링 도입
                wf_rel, meta = candidates[0]

        # ── 4. 해상도 결정 ──
        width, height = self._resolve_resolution(section_type, channel)

        workflow_abs = WORKFLOWS_DIR / wf_rel

        return {
            "workflow_rel": wf_rel,
            "workflow_path": str(workflow_abs),
            "width": width,
            "height": height,
            "meta": meta,
            "overrides": meta.get("overrides", {}),
        }

    def _intent_of(self, section_type: str) -> str:
        """섹션 타입 → 워크플로우 인텐트 매핑."""
        profile = self.profiles.get(section_type)
        if profile and "workflow_intent" in profile:
            return profile["workflow_intent"]
        mapping = {
            "flat_sketch": "flat-sketch",
            "lookbook": "lookbook",
            "graphic": "graphic",
            "moodboard": "moodboard",
            "colorway": "colorway",
        }
        return mapping.get(section_type, "lookbook")

    def _resolve_resolution(
        self, section_type: str, channel: Optional[str]
    ) -> tuple[int, int]:
        """
        우선순위:
          1. channel이 있으면 channel_to_ratio → resolution_presets
          2. 없으면 section profile의 default_resolution
        """
        if channel:
            ratio = self.catalog.get("channel_to_ratio", {}).get(channel)
            if ratio and ratio in self.catalog.get("resolution_presets", {}):
                w, h = self.catalog["resolution_presets"][ratio]
                return int(w), int(h)
        profile = self.profiles.get(section_type, {})
        default = profile.get("default_resolution", [1024, 1024])
        return int(default[0]), int(default[1])


# ── CLI 디버그 모드 ──
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "사용법: python3.12 workflow_resolver.py <section_type> "
            "[channel] [ref_image] [model_family] [phase_limit]"
        )
        sys.exit(1)

    resolver = WorkflowResolver()
    section = sys.argv[1]
    channel = sys.argv[2] if len(sys.argv) > 2 else None
    ref = sys.argv[3] if len(sys.argv) > 3 else None
    model = sys.argv[4] if len(sys.argv) > 4 else "sdxl"
    phase = int(sys.argv[5]) if len(sys.argv) > 5 else 1

    result = resolver.resolve(
        section_type=section,
        ref_image=ref,
        channel=channel,
        model_family=model,
        phase_limit=phase,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
