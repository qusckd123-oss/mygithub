#!/usr/bin/env python3
"""
Musinsa MCP Server — 무신사 크롤러 통합 MCP 서버
==================================================
기존 musinsa-crawler, musinsa-release-crawler, musinsa-trend-crawler를
MCP stdio 프로토콜로 래핑하여 Claude Code에서 도구 호출로 직접 사용.

지원 도구:
  - musinsa_ranking: 카테고리별/기간별/성별/연령별 랭킹 수집
  - musinsa_release: 발매판 수집 (예정/진행/종료)
  - musinsa_trend: 검색어/브랜드 랭킹 수집
"""

import json
import sys
import subprocess
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)


def read_message():
    """Read a JSON-RPC message from stdin (Content-Length header framing)."""
    headers = {}
    while True:
        line = sys.stdin.readline()
        if not line or line.strip() == "":
            break
        if ":" in line:
            key, val = line.split(":", 1)
            headers[key.strip()] = val.strip()
    content_length = int(headers.get("Content-Length", 0))
    if content_length == 0:
        return None
    body = sys.stdin.read(content_length)
    return json.loads(body)


def write_message(msg):
    """Write a JSON-RPC message to stdout."""
    body = json.dumps(msg)
    header = f"Content-Length: {len(body.encode('utf-8'))}\r\n\r\n"
    sys.stdout.write(header)
    sys.stdout.write(body)
    sys.stdout.flush()


def handle_initialize(msg):
    return {
        "jsonrpc": "2.0",
        "id": msg["id"],
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": False}
            },
            "serverInfo": {
                "name": "musinsa-mcp-server",
                "version": "1.0.0"
            }
        }
    }


def handle_tools_list(msg):
    return {
        "jsonrpc": "2.0",
        "id": msg["id"],
        "result": {
            "tools": [
                {
                    "name": "musinsa_ranking",
                    "description": "무신사 랭킹 수집 — 카테고리별/기간별/성별/연령별 상품 랭킹 데이터를 수집합니다. 엑셀 파일로 저장됩니다.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "카테고리 코드 (000=전체, 001=상의, 002=아우터, 003=바지, 004=가방, 100=원피스/스커트, 101=소품, 103=신발). 복수: 001,002,003",
                                "default": "000"
                            },
                            "sub_category": {
                                "type": "string",
                                "description": "2depth 서브카테고리 코드 (예: 001005=맨투맨/스웨트셔츠, 001006=후드 티셔츠). 생략 시 전체",
                                "default": ""
                            },
                            "period": {
                                "type": "string",
                                "enum": ["REALTIME", "DAILY", "WEEKLY"],
                                "description": "기간 (REALTIME=실시간, DAILY=일간, WEEKLY=주간)",
                                "default": "WEEKLY"
                            },
                            "gender": {
                                "type": "string",
                                "enum": ["A", "M", "F"],
                                "description": "성별 (A=전체, M=남성, F=여성)",
                                "default": "A"
                            },
                            "age": {
                                "type": "string",
                                "enum": ["AGE_BAND_ALL", "AGE_BAND_10", "AGE_BAND_20", "AGE_BAND_30"],
                                "description": "연령대 (AGE_BAND_ALL=전체, AGE_BAND_10=10대, AGE_BAND_20=20대, AGE_BAND_30=30대)",
                                "default": "AGE_BAND_ALL"
                            }
                        }
                    }
                },
                {
                    "name": "musinsa_release",
                    "description": "무신사 발매판 수집 — 발매 예정/진행 중/종료 상품의 브랜드, 상품명, 발매일시, D-Day, 가격 정보를 수집합니다.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab": {
                                "type": "string",
                                "enum": ["now", "upcoming", "end"],
                                "description": "탭 (now=진행 중, upcoming=발매 예정, end=종료)",
                                "default": "now"
                            },
                            "gender": {
                                "type": "string",
                                "enum": ["A", "M", "F"],
                                "description": "성별 (A=전체, M=남성, F=여성)",
                                "default": "A"
                            },
                            "sort": {
                                "type": "string",
                                "enum": ["latest", "popular"],
                                "description": "정렬 (latest=최신순, popular=인기순)",
                                "default": "latest"
                            }
                        }
                    }
                },
                {
                    "name": "musinsa_trend",
                    "description": "무신사 트렌드 수집 — 검색어 랭킹과 브랜드 랭킹(스타일별)을 수집합니다. 코어타겟 분석용.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "format": {
                                "type": "string",
                                "enum": ["json", "xlsx", "both"],
                                "description": "출력 포맷",
                                "default": "json"
                            }
                        }
                    }
                },
                {
                    "name": "musinsa_categories",
                    "description": "무신사 카테고리 목록 조회 — 사용 가능한 카테고리 코드와 이름을 반환합니다.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    }


def run_crawler(script_path, args):
    """Run a crawler script and capture output."""
    cmd = [sys.executable, script_path] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.join(SCRIPT_DIR, "..")
        )
        output = result.stdout
        if result.returncode != 0:
            output += f"\n[STDERR]: {result.stderr}" if result.stderr else ""
        return output if output.strip() else f"완료 (exit code: {result.returncode})"
    except subprocess.TimeoutExpired:
        return "오류: 크롤링 시간 초과 (120초)"
    except Exception as e:
        return f"오류: {str(e)}"


def handle_tool_call(msg):
    params = msg.get("params", {})
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})

    if tool_name == "musinsa_ranking":
        args = []
        args += ["--category", arguments.get("category", "000")]
        if arguments.get("sub_category"):
            args += ["--sub-category", arguments["sub_category"]]
        args += ["--period", arguments.get("period", "WEEKLY")]
        args += ["--gender", arguments.get("gender", "A")]
        args += ["--age", arguments.get("age", "AGE_BAND_ALL")]
        output = run_crawler(
            os.path.join(PARENT_DIR, "musinsa-crawler", "crawler.py"),
            args
        )

    elif tool_name == "musinsa_release":
        args = []
        args += ["--tab", arguments.get("tab", "now")]
        args += ["--gender", arguments.get("gender", "A")]
        args += ["--sort", arguments.get("sort", "latest")]
        output = run_crawler(
            os.path.join(PARENT_DIR, "musinsa-release-crawler", "crawler.py"),
            args
        )

    elif tool_name == "musinsa_trend":
        args = []
        args += ["--format", arguments.get("format", "json")]
        args += ["--no-images"]
        output = run_crawler(
            os.path.join(PARENT_DIR, "musinsa-trend-crawler", "crawler.py"),
            args
        )

    elif tool_name == "musinsa_categories":
        categories = {
            "000": "전체", "001": "상의", "002": "아우터", "003": "바지",
            "004": "가방", "100": "원피스/스커트", "101": "소품",
            "103": "신발", "104": "뷰티", "026": "속옷/홈웨어", "017": "스포츠/키즈"
        }
        sub_categories = {
            "001": {"001005": "맨투맨/스웨트셔츠", "001006": "후드 티셔츠", "001001": "반소매 티셔츠", "001002": "긴소매 티셔츠", "001003": "셔츠/블라우스", "001004": "피케/카라", "001010": "니트/스웨터"},
            "002": {"002001": "후드 집업", "002002": "블루종/MA-1", "002006": "코트", "002017": "나일론/코치 재킷"},
            "003": {"003002": "데님 팬츠", "003004": "코튼 팬츠", "003007": "트레이닝/조거", "003008": "숏 팬츠"},
        }
        output = json.dumps({"categories": categories, "sub_categories": sub_categories}, ensure_ascii=False, indent=2)

    else:
        output = f"알 수 없는 도구: {tool_name}"

    return {
        "jsonrpc": "2.0",
        "id": msg["id"],
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": output
                }
            ]
        }
    }


def main():
    while True:
        msg = read_message()
        if msg is None:
            break

        method = msg.get("method", "")

        if method == "initialize":
            write_message(handle_initialize(msg))
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            write_message(handle_tools_list(msg))
        elif method == "tools/call":
            write_message(handle_tool_call(msg))
        elif method == "ping":
            write_message({"jsonrpc": "2.0", "id": msg["id"], "result": {}})
        else:
            if "id" in msg:
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg["id"],
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                })


if __name__ == "__main__":
    main()
