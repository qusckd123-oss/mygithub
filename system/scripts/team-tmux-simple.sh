#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
# FPOF Team tmux — 간편 실행 래퍼
# Claude Code 세션 내에서 ! 로 호출
#
# Usage (Claude Code 안에서):
#   ! ./system/scripts/team-tmux-simple.sh season-plan
#   ! ./system/scripts/team-tmux-simple.sh status
#   ! ./system/scripts/team-tmux-simple.sh kill
# ─────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec bash "${SCRIPT_DIR}/team-tmux.sh" "$@"
