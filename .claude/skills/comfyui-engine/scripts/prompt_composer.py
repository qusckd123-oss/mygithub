#!/usr/bin/env python3.12
"""
프롬프트 조립기 (v2.1 — Foundation Formula 리팩토링).

brand-prompt-kit.json + section-profiles.json + material-intelligence.json 을 결합하여
섹션 타입별 positive / negative / 샘플러 파라미터를 생성한다.

v2 (Phase 1) 수정점:
- flat_sketch 섹션은 brand_booster OFF → "플랫 스케치에 컬러 부스터 주입" 버그 해결
- BRAND_BOOSTER 하드코딩 제거, visual-identity.json 기반 SSOT 복원
- 섹션별 네거티브 프롬프트 분기

v2.1 (Foundation Formula 리팩토링, 2026-04-10) 추가점:
- compose_foundation_formula() 신규 메서드 — 7슬롯 구조화 입력
  (shot_type / silhouette / material / details / color / construction / lighting_quality)
- material-intelligence.json 로드 → material 슬롯은 키워드 사전 자동 조회
- look_up_material() / resolve_slot() 헬퍼
- 리서치 출처: NotebookLM 패션하우스 AI 프롬프트 디자인 품질 리서치 (2026-04-10)
"""

import json
from pathlib import Path
from typing import Optional


SCRIPT_DIR = Path(__file__).parent
KIT_DIR = SCRIPT_DIR.parent / "references"


class PromptComposer:
    def __init__(
        self,
        brand_kit_path: Optional[Path] = None,
        section_profile_path: Optional[Path] = None,
        material_kit_path: Optional[Path] = None,
    ):
        self.kit_path = brand_kit_path or (KIT_DIR / "brand-prompt-kit.json")
        self.profiles_path = section_profile_path or (KIT_DIR / "section-profiles.json")
        self.materials_path = material_kit_path or (KIT_DIR / "material-intelligence.json")
        self.kit = self._load(self.kit_path)
        self.profiles = self._load(self.profiles_path)["profiles"]
        # v2.1: material-intelligence 로드 (존재 시)
        try:
            self.materials = self._load(self.materials_path)
        except FileNotFoundError:
            self.materials = {"materials": {}, "lookup_helpers": {}}

    @staticmethod
    def _load(path: Path) -> dict:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    # ────────────────────────────────────────────────────────────
    # v2 기존 compose() — 원본 프롬프트 + 섹션 프로파일 기반
    # ────────────────────────────────────────────────────────────
    def compose(
        self,
        raw_prompt: str,
        section_type: str,
        channel: Optional[str] = None,
        extra_tokens: Optional[list[str]] = None,
    ) -> dict:
        """
        섹션 타입에 맞는 프롬프트와 파라미터를 합성한다.

        Returns: {
          "positive": str,
          "negative": str,
          "sampler": str,
          "scheduler": str,
          "cfg": float,
          "steps": int,
          "resolution": [int, int],
          "hires_fix": bool,
          "workflow_intent": str,
          "requires_ref_image": bool,
          "requires_fixed_seed": bool,
        }
        """
        profile = self._require_profile(section_type)

        # ── Positive 조립 ──
        positive_parts: list[str] = []

        # 1. 섹션 기본 프롬프트 (flat_sketch의 경우 "technical flat lay..." 고정)
        positive_parts.append(profile["prompt_base"])

        # 2. 사용자 원본 프롬프트
        positive_parts.append(raw_prompt)

        # 3~6. 브랜드 SSOT 주입
        positive_parts.extend(self._brand_ssot_tokens(profile))

        # 7. 추가 토큰 (CLI에서 직접 지정)
        if extra_tokens:
            positive_parts.extend(extra_tokens)

        # ── Negative 조립 ──
        negative_parts = self._negative_parts(profile)

        return self._finalize(profile, positive_parts, negative_parts)

    # ────────────────────────────────────────────────────────────
    # v2.1 신규 compose_foundation_formula() — 7슬롯 구조화 입력
    # ────────────────────────────────────────────────────────────
    def compose_foundation_formula(
        self,
        section_type: str,
        shot_type: Optional[str] = None,
        silhouette: Optional[str] = None,
        material: Optional[str] = None,
        details: Optional[str] = None,
        color: Optional[str] = None,
        construction: Optional[str] = None,
        lighting_quality: Optional[str] = None,
        extra_raw: Optional[str] = None,
        extra_tokens: Optional[list[str]] = None,
    ) -> dict:
        """
        Foundation Formula 7슬롯 구조화 프롬프트 조립.

        각 슬롯은 brand-prompt-kit.json의 foundation_formula 섹션에서 키로 조회되거나,
        자유 텍스트로 직접 전달될 수 있다. material 슬롯은 추가로 material-intelligence.json
        에서 소재 키워드 사전을 조회한다.

        리서치 출처 (Foundation Formula):
            [샷]+[실루엣]+[소재]+[디테일]+[색상]+[제작방식]+[조명·품질]

        Returns: compose()와 동일 구조.
        """
        profile = self._require_profile(section_type)
        ff = self.kit.get("foundation_formula", {})

        # 각 슬롯 해석
        slot_outputs: list[str] = []

        shot_txt = self._resolve_slot(shot_type, ff.get("shot_type_options"))
        if shot_txt:
            slot_outputs.append(shot_txt)

        silh_txt = self._resolve_slot(silhouette, ff.get("silhouette_templates"))
        if silh_txt:
            slot_outputs.append(silh_txt)

        material_txt = self._resolve_material_slot(material)
        if material_txt:
            slot_outputs.append(material_txt)

        details_txt = self._resolve_slot(details, ff.get("details_options"))
        if details_txt:
            slot_outputs.append(details_txt)

        # color 슬롯: 키로 조회되지 않으면 자유 텍스트. 기본은 brand color_tokens.
        if color:
            slot_outputs.append(color)
        elif profile.get("color_tokens") == "on":
            slot_outputs.extend(self.kit["color_tokens"]["descriptors"])

        construction_txt = self._resolve_slot(
            construction, ff.get("construction_options")
        )
        if construction_txt:
            slot_outputs.append(construction_txt)

        lighting_txt = self._resolve_slot(
            lighting_quality, ff.get("lighting_quality_tags")
        )
        if lighting_txt:
            slot_outputs.append(lighting_txt)

        # ── Positive 조립 ──
        positive_parts: list[str] = []
        positive_parts.append(profile["prompt_base"])
        positive_parts.extend(slot_outputs)

        if extra_raw:
            positive_parts.append(extra_raw)

        # 브랜드 SSOT은 7슬롯 뒤에 후처리로 주입 (subject_priors + avoids)
        # color_tokens는 위에서 이미 주입했으므로 여기서는 제외
        positive_parts.extend(
            self._brand_ssot_tokens(profile, skip_color=True)
        )

        # 품질 태그 (Foundation Formula 공식 꼬리)
        positive_parts.extend(ff.get("quality_tags", []))

        if extra_tokens:
            positive_parts.extend(extra_tokens)

        # ── Negative 조립 ──
        negative_parts = self._negative_parts(profile)

        return self._finalize(profile, positive_parts, negative_parts)

    # ────────────────────────────────────────────────────────────
    # 내부 헬퍼
    # ────────────────────────────────────────────────────────────
    def _require_profile(self, section_type: str) -> dict:
        profile = self.profiles.get(section_type)
        if not profile:
            raise ValueError(
                f"Unknown section_type: {section_type}. "
                f"Valid: {list(self.profiles.keys())}"
            )
        return profile

    def _brand_ssot_tokens(
        self, profile: dict, skip_color: bool = False
    ) -> list[str]:
        """brand-prompt-kit SSOT 토큰을 섹션 프로파일에 따라 주입."""
        out: list[str] = []

        # 3. 브랜드 부스터 (섹션이 허용한 경우만) ← v2 버그 수정점
        if profile.get("brand_booster") == "on":
            out.extend(self.kit["style_tokens"]["required_for_lifestyle"])

        # 4. 컬러 토큰
        if not skip_color and profile.get("color_tokens") == "on":
            out.extend(self.kit["color_tokens"]["descriptors"])

        # 5. Subject priors (lookbook/moodboard만)
        if profile.get("subject_priors") == "on":
            out.append(self.kit["subject_priors"]["model_appearance"])
            out.append(self.kit["subject_priors"]["model_proportions"])

        # 6. Photo direction (setting/lighting/camera 각 첫 옵션)
        if profile.get("photo_direction") == "on":
            pd = self.kit["photo_direction"]
            if pd.get("setting_options"):
                out.append(pd["setting_options"][0])
            if pd.get("lighting_options"):
                out.append(pd["lighting_options"][0])
            if pd.get("camera_options"):
                out.append(pd["camera_options"][0])

        return out

    def _negative_parts(self, profile: dict) -> list[str]:
        parts: list[str] = [profile["negative_base"]]
        if profile.get("brand_booster") == "on":
            parts.extend(self.kit.get("brand_negative", []))
            parts.extend(self.kit["style_tokens"].get("avoid_styles", []))
            parts.extend(self.kit["color_tokens"].get("avoid_colors", []))
            parts.extend(self.kit["subject_priors"].get("avoid_model", []))
        # tone-manner never_use는 모든 섹션에 적용
        parts.extend(self.kit.get("never_use_words", []))
        return parts

    def _finalize(
        self,
        profile: dict,
        positive_parts: list[str],
        negative_parts: list[str],
    ) -> dict:
        resolution = profile.get("default_resolution", [1024, 1024])
        return {
            "positive": ", ".join(self._dedupe(positive_parts)),
            "negative": ", ".join(self._dedupe(negative_parts)),
            "sampler": profile.get("default_sampler", "dpmpp_2m"),
            "scheduler": profile.get("default_scheduler", "karras"),
            "cfg": profile.get("default_cfg", 7.0),
            "steps": profile.get("default_steps", 25),
            "resolution": list(resolution),
            "hires_fix": profile.get("hires_fix", False),
            "workflow_intent": profile.get("workflow_intent"),
            "requires_ref_image": profile.get("requires_ref_image", False),
            "requires_fixed_seed": profile.get("requires_fixed_seed", False),
        }

    @staticmethod
    def _resolve_slot(value: Optional[str], options: Optional[dict]) -> Optional[str]:
        """
        value가 options 딕셔너리의 키면 해당 값을 반환, 아니면 value 자체(자유 텍스트)를 반환.
        value가 None이면 None 반환.
        """
        if not value:
            return None
        if options and value in options:
            return options[value]
        return value  # 자유 텍스트 fallback

    def _resolve_material_slot(self, material: Optional[str]) -> Optional[str]:
        """
        material 이름이 material-intelligence.json의 키면 primary_keywords를 조합해 반환.
        아니면 자유 텍스트 fallback.
        """
        if not material:
            return None
        entry = self.materials.get("materials", {}).get(material)
        if not entry:
            return material  # 자유 텍스트 fallback
        parts = list(entry.get("primary_keywords", []))
        optical = entry.get("optical_properties")
        drape = entry.get("drape_behavior")
        if optical:
            parts.append(optical)
        if drape:
            parts.append(drape)
        return ", ".join(parts)

    def look_up_material(self, material: str) -> Optional[dict]:
        """공개 헬퍼: 소재 엔트리 전체 조회 (CLI 디버그/외부 스킬용)."""
        return self.materials.get("materials", {}).get(material)

    def list_materials(self) -> list[str]:
        """공개 헬퍼: 사용 가능한 소재 키 목록."""
        return sorted(self.materials.get("materials", {}).keys())

    @staticmethod
    def _dedupe(parts: list[str]) -> list[str]:
        """순서 보존 중복 제거 (소문자 기준)."""
        seen: set[str] = set()
        out = []
        for p in parts:
            if not p:
                continue
            p = p.strip()
            if not p:
                continue
            key = p.lower()
            if key not in seen:
                seen.add(key)
                out.append(p)
        return out

    @staticmethod
    def token_count(text: str) -> int:
        """SDXL CLIP tokenizer 근사 (실제 77 토큰 한도 판단용)."""
        return len(text.split())


# ── CLI 디버그 모드 ──
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법:")
        print("  A. raw 프롬프트 모드:")
        print("     python3.12 prompt_composer.py compose <section_type> <raw_prompt> [channel]")
        print("  B. Foundation Formula 모드:")
        print("     python3.12 prompt_composer.py ff <section_type> <shot> <silhouette> <material> [details] [color] [construction] [lighting]")
        print("  C. 소재 목록:")
        print("     python3.12 prompt_composer.py materials")
        print("  D. 소재 상세:")
        print("     python3.12 prompt_composer.py material <material_key>")
        sys.exit(1)

    mode = sys.argv[1]
    composer = PromptComposer()

    if mode == "materials":
        for m in composer.list_materials():
            entry = composer.look_up_material(m)
            print(f"  {m:35s} — {entry.get('display_name', '')} ({entry.get('weight_gsm', '')}gsm)")
        sys.exit(0)

    if mode == "material":
        entry = composer.look_up_material(sys.argv[2])
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        sys.exit(0)

    if mode == "compose":
        section = sys.argv[2]
        raw = sys.argv[3]
        channel = sys.argv[4] if len(sys.argv) > 4 else None
        result = composer.compose(raw, section, channel=channel)
    elif mode == "ff":
        section = sys.argv[2]
        argv = sys.argv[3:]
        result = composer.compose_foundation_formula(
            section_type=section,
            shot_type=argv[0] if len(argv) > 0 else None,
            silhouette=argv[1] if len(argv) > 1 else None,
            material=argv[2] if len(argv) > 2 else None,
            details=argv[3] if len(argv) > 3 else None,
            color=argv[4] if len(argv) > 4 else None,
            construction=argv[5] if len(argv) > 5 else None,
            lighting_quality=argv[6] if len(argv) > 6 else None,
        )
    else:
        # 구버전 호환: 첫 인자가 섹션으로 간주
        section = sys.argv[1]
        raw = sys.argv[2] if len(sys.argv) > 2 else ""
        channel = sys.argv[3] if len(sys.argv) > 3 else None
        result = composer.compose(raw, section, channel=channel)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\npositive 토큰 수: {composer.token_count(result['positive'])}")
    print(f"negative 토큰 수: {composer.token_count(result['negative'])}")
