#!/bin/bash
# FPOF PreToolUse Hook — 파일명 네이밍 규칙 검증
# Write/Edit 도구가 workspace/ 경로에 파일을 생성/수정할 때 파일명이 규칙을 준수하는지 검증
#
# 종료코드: 0=Allow, 2=Deny

# stdin에서 JSON 페이로드 읽기
INPUT=$(cat)

# 도구 이름 확인 (환경변수 또는 JSON에서)
TOOL_NAME="${HOOK_TOOL_NAME:-}"
if [ -z "$TOOL_NAME" ]; then
  TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)
fi

# Write/Edit 도구만 검증
case "$TOOL_NAME" in
  write_file|Write|edit_file|Edit) ;;
  *) exit 0 ;;
esac

# 파일 경로 추출
FILE_PATH="${HOOK_TOOL_INPUT:-}"
if [ -z "$FILE_PATH" ]; then
  FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
inp = data.get('tool_input', data.get('input', {}))
if isinstance(inp, str):
    import json as j
    inp = j.loads(inp)
print(inp.get('file_path', inp.get('path', '')))
" 2>/dev/null)
fi

# workspace/ 경로가 아니면 통과
if [[ "$FILE_PATH" != *"/workspace/"* ]]; then
  exit 0
fi

# 파일명만 추출
FILENAME=$(basename "$FILE_PATH")

# 디렉토리 경로에서 위치 판단 (weekly/dashboard vs 프로젝트)
IS_OPERATIONAL=0
if [[ "$FILE_PATH" == *"/weekly/"* ]] || [[ "$FILE_PATH" == *"/dashboard/"* ]]; then
  IS_OPERATIONAL=1
fi

# PDCA 접두사 패턴
PDCA_REGEX='^(plan|design|do|check|act)_[a-z0-9][a-z0-9-]*(_[0-9]{4}-[0-9]{2}-[0-9]{2})?(_v[0-9]+)?\.[a-z]+$'

# 운영 접두사 패턴
OPS_REGEX='^(review|meeting|deck|board|sheet|report|data)_[a-z0-9][a-z0-9-]*(_[0-9]{4}-[0-9]{2}-[0-9]{2}|_w[0-9]{2})?(_v[0-9]+)?\.[a-z]+$'

# 공백 포함 검사
if [[ "$FILENAME" == *" "* ]]; then
  echo "FPOF 파일명 규칙 위반: 공백 포함 불가 — '$FILENAME'"
  echo "규칙: 세그먼트 구분 '_', 단어 구분 '-'"
  exit 2
fi

# 대문자 검사 (시즌코드 26SS 등 예외)
FILENAME_NO_SEASON=$(echo "$FILENAME" | sed -E 's/[0-9]{2}(SS|FW|AW|RS)//g')
if echo "$FILENAME_NO_SEASON" | grep -q '[A-Z]'; then
  echo "FPOF 파일명 규칙 위반: 소문자만 사용 — '$FILENAME'"
  echo "예외: 시즌코드(26SS, 26FW)"
  exit 2
fi

# 운영 폴더에 PDCA 접두사 사용 검사
if [ "$IS_OPERATIONAL" -eq 1 ]; then
  if echo "$FILENAME" | grep -qE '^(plan|design|do|check|act)_'; then
    echo "FPOF 파일명 규칙 위반: 주간/대시보드에 PDCA 접두사 사용 금지 — '$FILENAME'"
    echo "운영 접두사 사용: review, meeting, deck, board, sheet, report, data"
    exit 2
  fi
  if echo "$FILENAME" | grep -qE "$OPS_REGEX"; then
    exit 0
  else
    echo "FPOF 파일명 경고: 운영 산출물 패턴 불일치 — '$FILENAME'"
    echo "패턴: [type]_[description][_YYYY-MM-DD][_vN].[ext]"
    echo "type: review|meeting|deck|board|sheet|report|data"
    # 경고만 (exit 0)
    exit 0
  fi
fi

# 프로젝트/시즌 폴더에서 접두사 검증
if echo "$FILENAME" | grep -qE "$PDCA_REGEX"; then
  exit 0
elif echo "$FILENAME" | grep -qE "$OPS_REGEX"; then
  exit 0
else
  # 접두사가 아예 없는 파일 (README 등)은 통과
  if ! echo "$FILENAME" | grep -qE '^(plan|design|do|check|act|review|meeting|deck|board|sheet|report|data)_'; then
    exit 0
  fi
  echo "FPOF 파일명 경고: 네이밍 패턴 불일치 — '$FILENAME'"
  echo "PDCA: [plan|design|do|check|act]_[description][_YYYY-MM-DD][_vN].[ext]"
  echo "운영: [review|meeting|deck|board|sheet|report|data]_[description][_YYYY-MM-DD][_vN].[ext]"
  # 경고만
  exit 0
fi
