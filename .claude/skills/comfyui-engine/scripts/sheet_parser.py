#!/usr/bin/env python3.12
"""
마크다운 AST 기반 프롬프트 시트 파서 (v2).

개선점 (v1 정규식 대비):
- 헤더 계층 이해 (H2/H3/H4 stack)
- 한 섹션 아래의 복수 코드블록 전부 추출 (Front/Back/Detail 3뷰 모두 잡음)
- 인라인 메타 주석 지원: <!-- workflow: ... --> , <!-- seed: 12345 --> , <!-- ref: path.png -->
- YAML front-matter 지원 (시트 상단 공통 설정)
- 섹션 타입 정확 추론 (flat_sketch, lookbook, graphic, moodboard, colorway)
- 인코딩 깨진 패턴 ('��래픽') 제거
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# 런타임 의존성 부트스트랩 — 시스템 python 에서 실행 시 ~/ComfyUI/venv 로 자동 전환
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap  # noqa: E402
_bootstrap.ensure_venv("mistune")

import mistune  # noqa: E402


META_COMMENT_PATTERN = re.compile(
    r"<!--\s*([a-z_]+)\s*:\s*(.+?)\s*-->",
    re.IGNORECASE,
)

YAML_FRONT_MATTER_PATTERN = re.compile(
    r"^---\n([\s\S]*?)\n---\n",
    re.MULTILINE,
)


class SheetParser:
    def __init__(self):
        # _bootstrap.ensure_venv("mistune") 이 위에서 실행되어 여기 도달 시 mistune 은 항상 import 가능
        self.md = mistune.create_markdown(renderer=None)

    def parse(self, md_path: str) -> list[dict]:
        """
        시트 파일을 파싱하여 엔트리 리스트를 반환한다.

        엔트리 스키마:
        {
          "header": str,               # 가장 가까운 헤더 텍스트
          "parent_headers": str,       # "H2 > H3" 형식
          "prompt": str,               # 코드블록 내용
          "section_type": str,         # flat_sketch|lookbook|graphic|moodboard|colorway
          "front_matter": dict,        # 시트 최상단 --- --- 블록
          "workflow": str | None,      # <!-- workflow: ... --> 지정
          "seed": str | None,          # <!-- seed: 12345 -->
          "ref": str | None,           # <!-- ref: path.png -->
          ...  # 기타 메타 주석 key:value
        }
        """
        with open(md_path, encoding="utf-8") as f:
            content = f.read()

        # 1. YAML front-matter 분리
        front = self._parse_front_matter(content)
        content_body = YAML_FRONT_MATTER_PATTERN.sub("", content, count=1)

        # 2. mistune AST 파싱
        ast = self.md(content_body)

        # 3. 노드 순회
        entries: list[dict] = []
        header_stack: list[tuple[int, str]] = []
        pending_meta: dict = {}

        for node in ast:
            node_type = node.get("type")

            if node_type == "heading":
                level = node.get("attrs", {}).get("level", 1)
                text = self._text_of(node)
                # level 이상의 헤더 제거 후 push (계층 유지)
                header_stack = [(l, t) for l, t in header_stack if l < level]
                header_stack.append((level, text))

            elif node_type == "block_html":
                raw = node.get("raw", "")
                pending_meta.update(self._parse_meta_comments(raw))

            elif node_type == "block_code":
                code = (node.get("raw") or "").strip()
                if not self._is_valid_prompt(code):
                    continue

                header = header_stack[-1][1] if header_stack else "unnamed"
                parent_headers = " > ".join(t for _, t in header_stack[:-1])

                section_type = (
                    pending_meta.get("section_type")
                    or self._infer_section_type(header_stack)
                )

                entry = {
                    "header": header,
                    "parent_headers": parent_headers,
                    "prompt": code,
                    "section_type": section_type,
                    "front_matter": front,
                    # 에셋 매트릭스 테이블 매칭용 키 후보 (우선순위 순)
                    "table_keys": self._build_table_keys(header, header_stack),
                }
                # 메타 주석 병합 (workflow/seed/ref/channel 등)
                entry.update(pending_meta)
                entries.append(entry)
                pending_meta = {}

        return entries

    @staticmethod
    def _text_of(node: dict) -> str:
        """heading 노드의 children에서 텍스트 추출."""
        children = node.get("children", [])
        parts = []
        for c in children:
            # mistune 3.x: text 노드는 raw 필드 사용
            if "raw" in c:
                parts.append(c["raw"])
            elif "children" in c:
                parts.append(SheetParser._text_of(c))
        return "".join(parts).strip()

    @staticmethod
    def _parse_front_matter(content: str) -> dict:
        """YAML front-matter 간이 파서 (의존성 회피)."""
        m = YAML_FRONT_MATTER_PATTERN.match(content)
        if not m:
            return {}
        out: dict = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip().strip("\"'")
        return out

    @staticmethod
    def _parse_meta_comments(raw: str) -> dict:
        """<!-- key: value --> 형식의 메타 주석 파싱."""
        out = {}
        for k, v in META_COMMENT_PATTERN.findall(raw):
            out[k.lower()] = v.strip()
        return out

    @staticmethod
    def _is_valid_prompt(code: str) -> bool:
        """프롬프트로 간주할 만한 코드블록인지 판별."""
        if not code:
            return False
        if len(code) < 20:
            return False
        # 테이블/JSON/목록/체크리스트/헤더는 프롬프트가 아님
        stripped = code.lstrip()
        if stripped.startswith(("|", "{", "- [", "#", "```")):
            return False
        # JSON 블록은 제외
        try:
            json.loads(code)
            return False
        except (json.JSONDecodeError, ValueError):
            pass
        return True

    @staticmethod
    def _build_table_keys(header: str, header_stack: list[tuple[int, str]]) -> list[str]:
        """
        에셋 매트릭스 테이블 행을 찾기 위한 매칭 키 후보 리스트.
        우선순위 순으로 시도되며, 첫 매칭이 성공하면 상태 갱신.

        예: header="V1 정면 (Front)", stack=[H2,H3("V1 키키 그래픽")]
            → ["V1 정면 (Front)", "정면 (Front)", "V1 키키 그래픽", "V1"]
        """
        keys: list[str] = []
        keys.append(header)

        # 선행 배리에이션 코드 (V1, V 2, v10 등) 스트립
        m = re.match(r"^[Vv]\s*\d+\s+(.+)$", header)
        if m:
            keys.append(m.group(1).strip())

        # 선행 배리에이션 코드만 (V1, V2 등) — 테이블에 'V1 키키 그래픽' 식으로 들어있을 수 있음
        m2 = re.match(r"^([Vv]\s*\d+)\b", header)
        if m2:
            keys.append(m2.group(1).strip())

        # 부모 헤더 (H3 = 배리에이션 이름, H2 = 섹션 이름)
        for level, text in reversed(header_stack[:-1]):
            if level >= 3 and text and text not in keys:
                keys.append(text)

        # 중복 제거 (순서 보존)
        seen: set[str] = set()
        unique: list[str] = []
        for k in keys:
            k = k.strip()
            if k and k not in seen:
                seen.add(k)
                unique.append(k)
        return unique

    @staticmethod
    def _infer_section_type(header_stack: list[tuple[int, str]]) -> str:
        """헤더 스택의 텍스트를 기반으로 섹션 타입을 추론."""
        text = " ".join(t.lower() for _, t in header_stack)

        if any(kw in text for kw in ["플랫", "flat", "스케치", "sketch", "도식", "technical"]):
            return "flat_sketch"
        if any(kw in text for kw in ["그래픽", "graphic", "프린트", "print", "자수", "벡터"]):
            return "graphic"
        if any(kw in text for kw in ["컬러웨이", "colorway", "컬러 배리에이션", "컬러웨어"]):
            return "colorway"
        if any(kw in text for kw in ["무드", "mood", "레퍼런스"]):
            return "moodboard"
        if any(kw in text for kw in ["착장", "룩", "look", "model", "모델", "무신사", "에디토리얼", "pdp", "룩북"]):
            return "lookbook"
        return "lookbook"  # 안전한 기본값


# ── CLI 디버그 모드 ──
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법: python3.12 sheet_parser.py <sheet.md>")
        sys.exit(1)

    parser = SheetParser()
    entries = parser.parse(sys.argv[1])
    print(f"추출된 엔트리: {len(entries)}개")
    for i, e in enumerate(entries):
        print(f"\n[{i}] {e['section_type']} | {e['parent_headers']} > {e['header']}")
        print(f"    프롬프트 길이: {len(e['prompt'])}자")
        extras = {k: v for k, v in e.items() if k not in ("header", "parent_headers", "prompt", "section_type", "front_matter")}
        if extras:
            print(f"    메타: {extras}")
