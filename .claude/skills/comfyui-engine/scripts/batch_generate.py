#!/usr/bin/env python3.12
"""
프롬프트 시트 배치 생성기 (v2).

v2 변경점:
- 정규식 파서 → SheetParser (마크다운 AST 기반, 복수 코드블록 전부 추출)
- 섹션 타입별 자동 분기 (flat_sketch / lookbook / graphic / moodboard / colorway)
- WorkflowResolver가 엔트리별 워크플로우 선택
- PromptComposer가 엔트리별 브랜드 부스터 on/off 제어
- 배치 완료 후 시트 상태 머신 자동 갱신 (PROMPT → GENERATED)
- report.md 자동 생성 (generated/report.md)

사용법:
    python3.12 batch_generate.py \
        --sheet workspace/26SS/proj/design_generator-sheet.md \
        --output-dir workspace/26SS/proj/generated/

    # 채널 지정 (엔트리에 <!-- channel: ... --> 없을 때 기본값)
    python3.12 batch_generate.py \
        --sheet sheet.md --output-dir ./out/ \
        --default-channel musinsa_hero

    # phase 제한 (Phase 2 활성화 시 --phase-limit 2)
    python3.12 batch_generate.py ... --phase-limit 2
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from sheet_parser import SheetParser
import sheet_state
from generate import generate as generate_one


def run_batch(args) -> list[dict]:
    """배치 생성 실행."""
    parser = SheetParser()
    entries = parser.parse(args.sheet)

    if not entries:
        print(f"프롬프트를 찾을 수 없습니다: {args.sheet}")
        print("시트에 ## / ### 헤더 + ``` 코드블록 형식의 프롬프트가 있는지 확인하세요.")
        sys.exit(1)

    # 섹션 타입별 집계
    counts: dict[str, int] = {}
    for e in entries:
        counts[e["section_type"]] = counts.get(e["section_type"], 0) + 1

    print(f"시트: {args.sheet}")
    print(f"추출된 엔트리: {len(entries)}개")
    print(f"  섹션 분포: {counts}")
    print(f"출력: {args.output_dir}")
    print("=" * 60)

    os.makedirs(args.output_dir, exist_ok=True)
    results: list[dict] = []

    for i, entry in enumerate(entries):
        header = entry["header"]
        section_type = entry["section_type"]
        parent = entry.get("parent_headers", "")

        print(f"\n[{i+1}/{len(entries)}] {parent} > {header}")
        print(f"  섹션: {section_type}")

        # 파일명 생성
        safe_header = _sanitize_filename(header)
        output_name = f"{i:03d}_{safe_header}.png"
        output_path = os.path.join(args.output_dir, output_name)

        # 엔트리 메타 주석의 channel > CLI default-channel
        channel = entry.get("channel") or args.default_channel
        ref_image = entry.get("ref")
        explicit_workflow = entry.get("workflow")
        seed_override = entry.get("seed")

        # generate 인자 구성
        gen_args = argparse.Namespace(
            prompt=entry["prompt"],
            negative=None,  # Composer가 채움
            section_type=section_type,
            channel=channel,
            model_family=args.model_family,
            phase_limit=args.phase_limit,
            speed=args.speed,
            workflow_rel=explicit_workflow,
            width=None,
            height=None,
            seed=int(seed_override) if seed_override else None,
            steps=None,
            cfg=None,
            batch=1,
            ref_image=ref_image,
            ref_strength=args.ref_strength,
            output=output_path,
            timeout=args.timeout,
            from_meta=None,
            source_sheet=args.sheet,
            source_header=header,
            dry_run=args.dry_run,
        )

        try:
            saved = generate_one(gen_args)
            results.append({
                "index": i,
                "header": header,
                "parent": parent,
                "section_type": section_type,
                "status": "OK",
                "files": saved,
                "output": output_path,
            })
            print(f"  -> 완료: {saved if saved else '(dry-run)'}")
        except Exception as e:
            results.append({
                "index": i,
                "header": header,
                "parent": parent,
                "section_type": section_type,
                "status": "ERROR",
                "error": str(e),
            })
            print(f"  -> 에러: {e}")

        # 연속 생성 사이 짧은 대기 (GPU 메모리 안정화)
        if i < len(entries) - 1 and not args.dry_run:
            time.sleep(2)

    # ── 결과 요약 ──
    print("\n" + "=" * 60)
    print("배치 생성 완료")
    ok = sum(1 for r in results if r["status"] == "OK")
    err = sum(1 for r in results if r["status"] == "ERROR")
    print(f"  성공: {ok}/{len(entries)}")
    if err:
        print(f"  실패: {err}/{len(entries)}")
        for r in results:
            if r["status"] == "ERROR":
                print(f"    - [{r['index']}] {r['header']}: {r['error']}")

    # ── 시트 상태 업데이트 ──
    if not args.dry_run and not args.no_sheet_update:
        ok_entries = [r for r in results if r["status"] == "OK"]
        state_result = sheet_state.update_many(
            args.sheet, ok_entries, new_state="GENERATED"
        )
        print(f"\n시트 상태 갱신: {state_result['updated']}개 PROMPT → GENERATED")
        if state_result["missed"]:
            print(f"  (매칭 실패: {len(state_result['missed'])}개 — 테이블 포맷 확인 필요)")

    # ── report.md 생성 ──
    if not args.dry_run:
        _write_report(args, entries, results)

    return results


def _sanitize_filename(header: str) -> str:
    """헤더를 안전한 파일명으로 변환."""
    import re
    name = re.sub(r"[^\w가-힣\s-]", "", header)
    name = re.sub(r"\s+", "-", name.strip())
    name = name.lower()[:60]
    return name or "unnamed"


def _write_report(args, entries: list[dict], results: list[dict]):
    """generated/report.md 작성."""
    report_path = os.path.join(args.output_dir, "report.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    counts: dict[str, dict] = {}
    for r in results:
        st = r["section_type"]
        if st not in counts:
            counts[st] = {"ok": 0, "err": 0}
        counts[st]["ok" if r["status"] == "OK" else "err"] += 1

    lines = []
    lines.append(f"# 배치 생성 리포트")
    lines.append("")
    lines.append(f"- 생성 시각: {now}")
    lines.append(f"- 시트: `{args.sheet}`")
    lines.append(f"- 출력 디렉토리: `{args.output_dir}`")
    lines.append(f"- 모델 패밀리: {args.model_family} (phase ≤ {args.phase_limit})")
    lines.append(f"- 기본 채널: {args.default_channel or '(없음)'}")
    lines.append("")
    lines.append("## 요약")
    lines.append("")
    ok = sum(1 for r in results if r["status"] == "OK")
    err = sum(1 for r in results if r["status"] == "ERROR")
    lines.append(f"- 총 엔트리: {len(entries)}")
    lines.append(f"- 성공: {ok}")
    lines.append(f"- 실패: {err}")
    lines.append("")
    lines.append("### 섹션 타입별")
    lines.append("")
    lines.append("| 섹션 | 성공 | 실패 |")
    lines.append("|------|------|------|")
    for st, c in counts.items():
        lines.append(f"| {st} | {c['ok']} | {c['err']} |")
    lines.append("")
    lines.append("## 상세")
    lines.append("")
    lines.append("| # | 섹션 | 헤더 | 상태 | 파일 |")
    lines.append("|---|------|------|------|------|")
    for r in results:
        file_info = Path(r["files"][0]).name if r.get("files") else (r.get("error", ""))[:50]
        lines.append(
            f"| {r['index']} | {r['section_type']} | {r['header']} | {r['status']} | {file_info} |"
        )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"리포트: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="프롬프트 시트 배치 생성 (v2)")
    parser.add_argument("--sheet", required=True, help="프롬프트 시트 경로 (.md)")
    parser.add_argument("--output-dir", required=True, help="출력 디렉토리")
    parser.add_argument(
        "--default-channel",
        default=None,
        help="엔트리에 채널 지정이 없을 때 기본값 (예: musinsa_hero)",
    )
    parser.add_argument(
        "--model-family",
        default="sdxl",
        choices=["sdxl", "flux"],
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
    parser.add_argument("--ref-strength", type=float, default=0.7)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--dry-run", action="store_true", help="실제 생성 없이 프롬프트 미리보기")
    parser.add_argument(
        "--no-sheet-update",
        action="store_true",
        help="시트 상태 자동 업데이트 비활성화",
    )

    args = parser.parse_args()
    run_batch(args)


if __name__ == "__main__":
    main()
