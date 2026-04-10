#!/bin/bash
# ─────────────────────────────────────────────────────────
# FPOF Team tmux Launcher
# 서브에이전트를 tmux 분할 화면에서 병렬 실행·모니터링
#
# Usage:
#   team-tmux.sh <preset>              # 프리셋 실행
#   team-tmux.sh custom "역할:프롬프트" "역할:프롬프트" ...
#   team-tmux.sh list                  # 프리셋 목록
#   team-tmux.sh kill                  # 세션 종료
#   team-tmux.sh status                # 실행 상태 확인
#
# Examples:
#   team-tmux.sh season-plan
#   team-tmux.sh custom "리서처:트렌드 분석해줘" "전략가:브랜드 전략 수립해줘"
# ─────────────────────────────────────────────────────────
set -euo pipefail

# ── Config ──────────────────────────────────────────────
SESSION="fpof-team"
PROJECT_DIR="/Users/sherman/07. FPOF V2.2 Claude"
RESULTS_DIR="${PROJECT_DIR}/workspace/team-results"
CLAUDE_BIN="claude"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RUN_DIR="${RESULTS_DIR}/${TIMESTAMP}"

# ── Colors ──────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ── Agents array (populated by presets) ─────────────────
AGENTS=()

# ── Presets ─────────────────────────────────────────────

preset_season_plan() {
  AGENTS=(
    "시장-리서처|/brief trend-brief 를 실행해서 트렌드 브리프를 작성해줘. 완료 후 결과 파일 경로를 알려줘."
    "브랜드-전략가|/brief brand-strategy 를 실행해서 브랜드 전략을 수립해줘. 완료 후 결과 파일 경로를 알려줘."
    "수석-MD|/brief md-planning 을 실행해서 MD 플래닝을 작성해줘. 카테고리 믹스, SKU 구성 포함. 완료 후 결과 파일 경로를 알려줘."
    "컬렉션-플래너|/brief line-sheet 를 실행해서 라인시트를 작성해줘. 완료 후 결과 파일 경로를 알려줘."
  )
}

preset_design_sprint() {
  AGENTS=(
    "크리에이티브-디렉터|/brief moodboard 를 실행해서 무드보드를 만들어줘. 완료 후 결과 파일 경로를 알려줘."
    "패션-디자이너|/brief design-spec 을 실행해서 디자인 스펙을 작성해줘. 완료 후 결과 파일 경로를 알려줘."
    "아트-디렉터|비주얼 에셋을 생성해줘. 시즌 테마에 맞는 룩북 컨셉 이미지. 완료 후 결과 파일 경로를 알려줘."
    "프로덕션-매니저|/brief costing-ve 를 실행해서 원가 분석을 해줘. 완료 후 결과 파일 경로를 알려줘."
  )
}

preset_marketing_blitz() {
  AGENTS=(
    "마케팅-디렉터|/brief imc-strategy 를 실행해서 IMC 전략을 수립해줘. 완료 후 결과 파일 경로를 알려줘."
    "패션-에디터|상품 카피를 작성해줘. 주력 아이템 3개의 PDP 카피. 완료 후 결과 파일 경로를 알려줘."
    "콘텐츠-디렉터|화보 촬영 기획안을 작성해줘. 시즌 룩북용. 완료 후 결과 파일 경로를 알려줘."
    "소셜-전략-디렉터|소셜 바이럴 전략을 수립해줘. 인스타/틱톡 채널별. 완료 후 결과 파일 경로를 알려줘."
  )
}

preset_data_review() {
  AGENTS=(
    "트렌드-애널리스트|매출 데이터를 분석해줘. 채널별, 카테고리별 실적 비교. 완료 후 결과 파일 경로를 알려줘."
    "인사이트-아키텍트|최근 실적에서 인사이트를 도출해줘. 히트/부진 상품 원인 분석. 완료 후 결과 파일 경로를 알려줘."
    "데이터-애널리스트|코호트 분석을 실행해줘. 고객 리텐션, 재구매 패턴. 완료 후 결과 파일 경로를 알려줘."
  )
}

preset_quality_gate() {
  AGENTS=(
    "품질-검증관|현재 단계 Quality Gate 검수를 실행해줘. 완료 후 결과를 알려줘."
    "갭-디텍터|기획 대비 실행 갭 분석을 해줘. 누락된 산출물이나 기준 미달 항목. 완료 후 결과를 알려줘."
    "리포트-제너레이터|완료 보고서를 작성해줘. 현재까지 진행 상황 종합. 완료 후 결과 파일 경로를 알려줘."
  )
}

# ── Functions ───────────────────────────────────────────

usage() {
  echo -e "${BOLD}FPOF Team tmux Launcher${NC}"
  echo ""
  echo -e "Usage:"
  echo -e "  ${CYAN}team-tmux.sh <preset>${NC}              프리셋 실행"
  echo -e "  ${CYAN}team-tmux.sh custom \"역할:프롬프트\" ...${NC}  커스텀 실행"
  echo -e "  ${CYAN}team-tmux.sh list${NC}                  프리셋 목록"
  echo -e "  ${CYAN}team-tmux.sh kill${NC}                  세션 종료"
  echo -e "  ${CYAN}team-tmux.sh status${NC}                실행 상태 확인"
  echo ""
  echo -e "Presets:"
  echo -e "  ${GREEN}season-plan${NC}      — 시즌 전략 수립 (리서처·전략가·MD·플래너)"
  echo -e "  ${GREEN}design-sprint${NC}    — 디자인 스프린트 (무드보드·디자인스펙·비주얼·원가)"
  echo -e "  ${GREEN}marketing-blitz${NC}  — 마케팅 블리츠 (IMC·카피·비주얼·소셜)"
  echo -e "  ${GREEN}data-review${NC}      — 데이터 리뷰 (매출분석·인사이트·코호트)"
  echo -e "  ${GREEN}quality-gate${NC}     — 품질 검수 (QG·갭분석·리포트)"
}

kill_session() {
  if tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux kill-session -t "$SESSION"
    echo -e "${GREEN}세션 '${SESSION}' 종료됨${NC}"
  else
    echo -e "${YELLOW}세션 '${SESSION}'이 없습니다${NC}"
  fi
}

check_status() {
  if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    echo -e "${YELLOW}실행 중인 팀 세션이 없습니다${NC}"
    return
  fi

  echo -e "${BOLD}── FPOF Team Status ──${NC}"
  local pane_count
  pane_count=$(tmux list-panes -t "$SESSION" 2>/dev/null | wc -l | tr -d ' ')
  echo -e "세션: ${CYAN}${SESSION}${NC} | 패인: ${pane_count}개"
  echo ""

  local i=0
  tmux list-panes -t "$SESSION" -F '#{pane_index}' 2>/dev/null | while read -r idx; do
    local pane_title
    pane_title=$(tmux display-message -t "${SESSION}:0.${idx}" -p '#{pane_title}' 2>/dev/null || echo "pane-${idx}")
    local last_line
    last_line=$(tmux capture-pane -t "${SESSION}:0.${idx}" -p 2>/dev/null | grep -v '^$' | tail -1)
    echo -e "  [${GREEN}${pane_title}${NC}] ${last_line}"
  done

  echo ""

  # 결과 파일 확인
  local latest_run
  latest_run=$(ls -1td "${RESULTS_DIR}"/*/ 2>/dev/null | head -1)
  if [ -n "$latest_run" ]; then
    echo -e "결과 디렉토리: ${CYAN}${latest_run}${NC}"
    local result_count
    result_count=$(find "$latest_run" -name "*.md" -not -name ".*" 2>/dev/null | wc -l | tr -d ' ')
    echo -e "완료된 결과: ${GREEN}${result_count}개${NC}"
  fi
}

build_wrapper_script() {
  local role="$1"
  local prompt="$2"
  local output_file="${RUN_DIR}/${role}.md"
  local wrapper="${RUN_DIR}/.run-${role}.sh"

  cat > "$wrapper" << WRAPPER_EOF
#!/bin/bash
set -euo pipefail

ROLE="${role}"
OUTPUT_FILE="${output_file}"
PROJECT_DIR="${PROJECT_DIR}"
CLAUDE_BIN="${CLAUDE_BIN}"

# 타이틀 설정
printf '\033]2;%s\033\\' "\${ROLE}"

echo ""
echo -e "\033[1;36m┌────────────────────────────────────────┐\033[0m"
echo -e "\033[1;36m│  \${ROLE}\033[0m"
echo -e "\033[1;36m│  \$(date '+%H:%M:%S') 시작\033[0m"
echo -e "\033[1;36m└────────────────────────────────────────┘\033[0m"
echo ""

cd "\${PROJECT_DIR}"

# Claude 실행 — print 모드로 스트리밍 출력 + 결과 파일 저장
\${CLAUDE_BIN} -p '${prompt}

작업 완료 후 결과를 정리해서 보여줘.' 2>&1 | tee "\${OUTPUT_FILE}"

# 완료 시그널
echo ""
echo -e "\033[1;32m\${ROLE} 작업 완료 — \$(date '+%H:%M:%S')\033[0m"
echo -e "\033[0;33m결과: \${OUTPUT_FILE}\033[0m"
echo ""
echo "아무 키나 누르면 패인을 닫습니다..."
read -r -n 1
WRAPPER_EOF

  chmod +x "$wrapper"
  echo "$wrapper"
}

launch_team() {
  local agent_count=${#AGENTS[@]}

  if [ "$agent_count" -eq 0 ]; then
    echo -e "${RED}에이전트가 없습니다${NC}"
    exit 1
  fi

  if [ "$agent_count" -gt 6 ]; then
    echo -e "${RED}최대 6개 패인까지 지원합니다 (현재: ${agent_count})${NC}"
    exit 1
  fi

  # 이전 세션 정리
  tmux kill-session -t "$SESSION" 2>/dev/null || true

  # 결과 디렉토리 생성
  mkdir -p "$RUN_DIR"

  echo -e "${BOLD}── FPOF Team Launch ──${NC}"
  echo -e "세션: ${CYAN}${SESSION}${NC}"
  echo -e "에이전트: ${GREEN}${agent_count}명${NC}"
  echo -e "결과: ${CYAN}${RUN_DIR}${NC}"
  echo ""

  # 첫 번째 에이전트로 세션 생성
  local first_entry="${AGENTS[0]}"
  local first_role="${first_entry%%|*}"
  local first_prompt="${first_entry#*|}"
  local first_wrapper
  first_wrapper=$(build_wrapper_script "$first_role" "$first_prompt")

  tmux new-session -d -s "$SESSION" -x 200 -y 50
  tmux send-keys -t "${SESSION}:0.0" "bash '${first_wrapper}'" Enter
  tmux select-pane -t "${SESSION}:0.0" -T "$first_role"
  echo -e "  [${GREEN}${first_role}${NC}] 시작"

  # 나머지 에이전트 추가
  local i=1
  while [ $i -lt $agent_count ]; do
    local entry="${AGENTS[$i]}"
    local role="${entry%%|*}"
    local prompt="${entry#*|}"
    local wrapper
    wrapper=$(build_wrapper_script "$role" "$prompt")

    # 분할 방향 결정 (타일 레이아웃)
    if [ $((i % 2)) -eq 1 ]; then
      tmux split-window -h -t "${SESSION}:0"
    else
      tmux split-window -v -t "${SESSION}:0"
    fi

    tmux send-keys -t "${SESSION}:0.${i}" "bash '${wrapper}'" Enter
    tmux select-pane -t "${SESSION}:0.${i}" -T "$role"
    echo -e "  [${GREEN}${role}${NC}] 시작"

    i=$((i + 1))
  done

  # 레이아웃 정리
  tmux select-layout -t "$SESSION" tiled

  # 패인 보더에 역할명 표시
  tmux set-option -t "$SESSION" pane-border-status top
  tmux set-option -t "$SESSION" pane-border-format " #{pane_title} "
  tmux set-option -t "$SESSION" pane-active-border-style "fg=cyan"
  tmux set-option -t "$SESSION" pane-border-style "fg=white"

  echo ""
  echo -e "${BOLD}── 실행 완료 ──${NC}"
  echo -e "모니터링: ${CYAN}tmux attach -t ${SESSION}${NC}"
  echo -e "상태 확인: ${CYAN}team-tmux.sh status${NC}"
  echo -e "종료:     ${CYAN}team-tmux.sh kill${NC}"
  echo ""

  # 자동 어태치 (인터랙티브 터미널인 경우)
  if [ -t 0 ]; then
    echo -e "${YELLOW}3초 후 tmux 세션에 연결합니다... (Ctrl+B, D로 빠져나오기)${NC}"
    sleep 3
    tmux attach -t "$SESSION"
  fi
}

# ── Main ────────────────────────────────────────────────
if [ $# -eq 0 ]; then
  usage
  exit 0
fi

case "$1" in
  list)
    echo -e "${BOLD}사용 가능한 프리셋:${NC}"
    echo ""
    echo -e "  ${GREEN}season-plan${NC}      — 시즌 전략 수립 (리서처·전략가·MD·플래너)"
    echo -e "  ${GREEN}design-sprint${NC}    — 디자인 스프린트 (무드보드·디자인스펙·비주얼·원가)"
    echo -e "  ${GREEN}marketing-blitz${NC}  — 마케팅 블리츠 (IMC·카피·비주얼·소셜)"
    echo -e "  ${GREEN}data-review${NC}      — 데이터 리뷰 (매출분석·인사이트·코호트)"
    echo -e "  ${GREEN}quality-gate${NC}     — 품질 검수 (QG·갭분석·리포트)"
    ;;

  kill)
    kill_session
    ;;

  status)
    check_status
    ;;

  season-plan)
    preset_season_plan
    launch_team
    ;;

  design-sprint)
    preset_design_sprint
    launch_team
    ;;

  marketing-blitz)
    preset_marketing_blitz
    launch_team
    ;;

  data-review)
    preset_data_review
    launch_team
    ;;

  quality-gate)
    preset_quality_gate
    launch_team
    ;;

  custom)
    shift
    AGENTS=()
    for arg in "$@"; do
      # "역할:프롬프트" → "역할|프롬프트"
      role="${arg%%:*}"
      prompt="${arg#*:}"
      AGENTS+=("${role}|${prompt}")
    done
    launch_team
    ;;

  *)
    echo -e "${RED}알 수 없는 명령: $1${NC}"
    echo ""
    usage
    exit 1
    ;;
esac
