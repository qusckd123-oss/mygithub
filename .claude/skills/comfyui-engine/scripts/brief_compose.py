#!/usr/bin/env python3.12
"""
디자인 디스커버리 브리프 → generate.py 실행기.

design-discovery-flow.json 의 steps 를 AskUserQuestion 으로 순회한 Claude 가
수집한 brief.json 을 받아 generate.py 의 Foundation Formula 7슬롯 모드로
변환해 호출한다. 스키마 검증과 CLI 인자 매핑만 담당, 프롬프트 합성이나
워크플로우 선택은 모두 generate.py 로 위임한다.

Brief JSON 스키마 (design-discovery-flow.json 의 brief_schema 와 동기):
{
  "section_type": "lookbook",              # 필수 — 5종 중 하나
  "category": "unisex_tops",               # 선택 — 시트/리포트 기록용
  "silhouette": "oversized_hoodie",        # foundation_formula 키
  "material": "french_terry_brushed",      # material-intelligence 키
  "details": "signature_stitching",        # foundation_formula 키 (또는 [list])
  "color": "signature canary yellow...",   # 자유 텍스트 또는 foundation_formula 키
  "construction": "premium_manufacture",   # 선택
  "shot": "three_quarter",                 # 선택
  "lighting_quality": "golden_hour",       # 선택
  "channel": "musinsa_hero",               # 선택 — 해상도 결정
  "extra_raw": "graffiti alley backdrop",  # 선택 — 추가 디렉션
  "ref_image": "/path/to/ref.jpg",         # moodboard 전용 필수
  "style_lock": "wacky_street_26ss",       # 선택 — 컬렉션 일관성
  "seed": 12345,                            # 선택 — 재현
  "output": "./out.png"                     # 선택 — 기본 ./discovery_out.png
}

사용법:
  # 파일에서 brief 로드 → 생성 실행
  python3.12 brief_compose.py --brief ./brief.json

  # stdin 으로 brief 전달
  echo '{"section_type":"lookbook",...}' | python3.12 brief_compose.py --stdin

  # 실제 실행 없이 generate.py 에 --dry-run 전달
  python3.12 brief_compose.py --brief ./brief.json --dry-run

  # 실행할 명령어만 출력 (디버그)
  python3.12 brief_compose.py --brief ./brief.json --print-cmd

  # brief 유효성만 검사
  python3.12 brief_compose.py --brief ./brief.json --validate-only
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
GENERATE_PY = SCRIPT_DIR / "generate.py"

VALID_SECTION_TYPES = {
    "flat_sketch",
    "lookbook",
    "graphic",
    "moodboard",
    "colorway",
}

# 섹션별 필수 필드 — brief_schema 와 동기
REQUIRED_FIELDS = {
    "flat_sketch": {"section_type", "silhouette"},
    "lookbook": {"section_type", "silhouette", "material"},
    "graphic": {"section_type", "color"},
    "moodboard": {"section_type", "ref_image"},
    "colorway": {"section_type", "silhouette", "color"},
}

# brief 필드 → generate.py CLI 플래그
SLOT_FLAGS = [
    ("shot", "--shot"),
    ("silhouette", "--silhouette"),
    ("material", "--material"),
    ("construction", "--construction"),
    ("lighting_quality", "--lighting-quality"),
]

PASSTHROUGH_FLAGS = [
    ("channel", "--channel"),
    ("style_lock", "--style-lock"),
    ("ref_image", "--ref-image"),
]


def load_brief(args) -> dict:
    if args.stdin:
        return json.load(sys.stdin)
    if args.brief:
        path = Path(args.brief).expanduser()
        if not path.exists():
            raise SystemExit(f"ERROR: brief 파일을 찾을 수 없습니다: {path}")
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    raise SystemExit("ERROR: --brief <path> 또는 --stdin 중 하나 필수")


def validate(brief: dict) -> list[str]:
    """brief 를 검증해 에러 메시지 리스트를 반환. 빈 리스트면 OK."""
    errors: list[str] = []

    section_type = brief.get("section_type")
    if section_type not in VALID_SECTION_TYPES:
        errors.append(
            f"section_type={section_type!r} 가 유효하지 않습니다. "
            f"허용값: {sorted(VALID_SECTION_TYPES)}"
        )
        return errors  # 이후 검증이 의미 없음

    required = REQUIRED_FIELDS[section_type]
    missing = [f for f in required if not brief.get(f)]
    if missing:
        errors.append(
            f"섹션 '{section_type}' 필수 필드 누락: {missing}. "
            f"(필수: {sorted(required)})"
        )

    # details 는 string 또는 list 허용 — 그 외 타입 거부
    details = brief.get("details")
    if details is not None and not isinstance(details, (str, list)):
        errors.append(f"details 는 string 또는 list 여야 합니다. 현재: {type(details).__name__}")

    seed = brief.get("seed")
    if seed is not None and not isinstance(seed, int):
        errors.append(f"seed 는 정수여야 합니다. 현재: {seed!r}")

    # moodboard → ref_image 가 존재하는 파일인지 확인
    if section_type == "moodboard" and brief.get("ref_image"):
        ref_path = Path(brief["ref_image"]).expanduser()
        if not ref_path.exists():
            errors.append(f"ref_image 경로가 존재하지 않습니다: {ref_path}")

    return errors


def first(v):
    """details 가 list 인 경우 첫 원소만 반환 (generate.py --details 는 단일 키)."""
    if isinstance(v, list):
        return v[0] if v else None
    return v


def build_cli_args(brief: dict) -> list[str]:
    """brief → generate.py CLI 인자 리스트."""
    args: list[str] = ["--section-type", brief["section_type"]]

    for key, flag in SLOT_FLAGS:
        val = brief.get(key)
        if val:
            args += [flag, str(val)]

    # details: list 수용
    details = first(brief.get("details"))
    if details:
        args += ["--details", str(details)]

    # color 슬롯 — generate.py 는 --color-slot 로 받는다 (brand-prompt-kit.json 주석 참조)
    color = brief.get("color")
    if color:
        args += ["--color-slot", str(color)]

    # extra_raw — 자유 텍스트. generate.py 는 --prompt 로 받아서 extra_raw 로 활용
    # (7슬롯 모드에서 raw_prompt 도 추가 가능)
    extra = brief.get("extra_raw")
    if extra:
        args += ["--prompt", str(extra)]

    for key, flag in PASSTHROUGH_FLAGS:
        val = brief.get(key)
        if val:
            args += [flag, str(val)]

    seed = brief.get("seed")
    if seed is not None:
        args += ["--seed", str(int(seed))]

    output = brief.get("output") or "./discovery_out.png"
    args += ["--output", output]

    return args


def summarize(brief: dict) -> str:
    """사용자/로그용 브리프 요약 문자열."""
    lines = ["── Discovery Brief ──"]
    for k in (
        "section_type",
        "category",
        "silhouette",
        "material",
        "details",
        "color",
        "construction",
        "shot",
        "lighting_quality",
        "channel",
        "extra_raw",
        "ref_image",
        "style_lock",
        "seed",
        "output",
    ):
        v = brief.get(k)
        if v is not None and v != "":
            lines.append(f"  {k:17s} = {v}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="디자인 디스커버리 브리프 → generate.py 실행기"
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--brief", help="brief.json 파일 경로")
    src.add_argument("--stdin", action="store_true", help="stdin 에서 brief JSON 읽기")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="generate.py 에 --dry-run 전달 (실제 생성 없이 프롬프트 미리보기)",
    )
    parser.add_argument(
        "--print-cmd",
        action="store_true",
        help="실행할 generate.py 명령어만 출력하고 종료",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="brief 유효성만 검사하고 종료",
    )

    args = parser.parse_args()

    brief = load_brief(args)

    errors = validate(brief)
    if errors:
        print("brief 검증 실패:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 2

    print(summarize(brief))

    if args.validate_only:
        print("\n검증 통과.")
        return 0

    if not GENERATE_PY.exists():
        print(f"ERROR: generate.py 를 찾을 수 없습니다: {GENERATE_PY}", file=sys.stderr)
        return 1

    cli = build_cli_args(brief)
    if args.dry_run:
        cli.append("--dry-run")

    cmd = [sys.executable, str(GENERATE_PY)] + cli

    if args.print_cmd:
        # shell-quote 안 한 raw 출력 — 복사 붙여넣기용
        print("\n실행 명령어:")
        print("  " + " ".join(cmd))
        return 0

    print(f"\n실행: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
