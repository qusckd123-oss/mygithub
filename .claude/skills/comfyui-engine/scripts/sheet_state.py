#!/usr/bin/env python3.12
"""
프롬프트 시트의 에셋 매트릭스 상태 컬럼을 업데이트한다.

visual-factory-sheet의 상태 머신:
  PROMPT → GENERATED → APPROVED → REJECTED → UPLOADED

SKILL.md의 "6. 프롬프트 시트 상태 업데이트" 약속을 실제 코드로 구현.

한계:
- 현재는 단순 정규식 치환 (마크다운 테이블 포맷 변형에 취약)
- Phase 3에서 마크다운 테이블 파서로 교체 예정
- 업데이트 실패 시 경고만 출력하고 생성 자체는 성공 (비파괴)
"""

import re
from pathlib import Path


STATE_VALUES = ["PROMPT", "GENERATED", "APPROVED", "REJECTED", "UPLOADED"]


def update_entry_state(
    sheet_path: str,
    entry_header: str,
    new_state: str,
    from_state: str = "PROMPT",
) -> bool:
    """
    에셋 매트릭스 테이블에서 entry_header를 포함하는 행의 상태 컬럼을 교체.

    Args:
        sheet_path: 시트 .md 경로
        entry_header: 매칭할 헤더 텍스트 (컷 이름, 배리에이션명 등)
        new_state: 새 상태 (STATE_VALUES 중 하나)
        from_state: 이전 상태 (기본 PROMPT, 안전장치)

    Returns:
        치환 성공 시 True, 매칭 실패 시 False.
    """
    if new_state not in STATE_VALUES:
        raise ValueError(f"Invalid state: {new_state}. Must be one of {STATE_VALUES}")

    path = Path(sheet_path)
    if not path.exists():
        return False

    content = path.read_text(encoding="utf-8")

    # 같은 줄에 entry_header와 from_state가 동시에 있는 파이프 테이블 행을 찾는다.
    # 예: | 1 | 컷 이름 | ... | PROMPT | ... |
    #
    # 주의: 엔트리 헤더가 배리에이션 간에 중복될 수 있으므로 (예: "정면 (Front)" 가
    # V1/V2/V3/V4 전부에 존재), count=1 로 한 번에 첫 행만 교체한다. 이렇게 해야
    # update_many 가 엔트리별로 순차 호출하면서 각 행을 정확히 한 번씩 채운다.
    pattern = re.compile(
        r"(\|[^\n]*"
        + re.escape(entry_header)
        + r"[^\n]*\|\s*)"
        + re.escape(from_state)
        + r"(\s*\|)",
        re.IGNORECASE,
    )
    new_content, n = pattern.subn(rf"\1{new_state}\2", content, count=1)

    if n == 0:
        return False

    path.write_text(new_content, encoding="utf-8")
    return True


def update_many(
    sheet_path: str,
    entries: list[dict],
    new_state: str = "GENERATED",
) -> dict:
    """
    여러 엔트리의 상태를 일괄 업데이트한다.

    Args:
        sheet_path: 시트 경로
        entries: [{"header": "...", "table_keys": [...], ...}, ...] 형식 (sheet_parser 결과)
        new_state: 새 상태

    각 엔트리에 대해 table_keys (sheet_parser 가 생성한 매칭 후보 리스트) 를
    우선순위 순으로 시도하고, 첫 매칭이 성공하면 업데이트 후 다음 엔트리로 넘어간다.
    table_keys 가 없으면 header 만 시도.

    Returns:
        {"updated": n, "missed": [header, ...]}
    """
    updated = 0
    missed: list[str] = []
    for e in entries:
        header = e.get("header", "")
        if not header:
            continue
        # sheet_parser 가 table_keys 를 넣어준 경우 우선 사용
        candidates = e.get("table_keys") or [header]
        matched = False
        for key in candidates:
            if not key:
                continue
            if update_entry_state(sheet_path, key, new_state):
                matched = True
                break
        if matched:
            updated += 1
        else:
            missed.append(header)
    return {"updated": updated, "missed": missed}


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("사용법: python3.12 sheet_state.py <sheet.md> <entry_header> <new_state>")
        sys.exit(1)

    ok = update_entry_state(sys.argv[1], sys.argv[2], sys.argv[3])
    print("OK" if ok else "MISS")
