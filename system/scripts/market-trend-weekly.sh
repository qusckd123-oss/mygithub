#!/bin/bash
# ==============================================================
# market-trend-weekly.sh
# 매주 일요일 밤 자동 실행 — 무신사 마켓 동향 크롤링 + 대시보드 갱신
#
# 수동 실행: bash system/scripts/market-trend-weekly.sh
# 자동 실행: launchd plist 등록 (아래 install 옵션)
# ==============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON="python3"
LOG_DIR="$PROJECT_ROOT/workspace/musinsa-trend/logs"
LOG_FILE="$LOG_DIR/crawl_$(date +%Y%m%d_%H%M).log"
PLIST_NAME="com.fpof.market-trend-weekly"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

mkdir -p "$LOG_DIR"

# ----------------------------------------------------------
# install / uninstall 명령
# ----------------------------------------------------------
if [[ "${1:-}" == "install" ]]; then
  HOUR="${2:-22}"
  MINUTE="${3:-30}"
  echo "launchd 등록: 매주 일요일 ${HOUR}:${MINUTE} 실행"

  cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_NAME}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${SCRIPT_DIR}/market-trend-weekly.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key>
    <integer>0</integer>
    <key>Hour</key>
    <integer>${HOUR}</integer>
    <key>Minute</key>
    <integer>${MINUTE}</integer>
  </dict>
  <key>WorkingDirectory</key>
  <string>${PROJECT_ROOT}</string>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/launchd_stdout.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/launchd_stderr.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
  </dict>
</dict>
</plist>
PLIST

  launchctl unload "$PLIST_PATH" 2>/dev/null || true
  launchctl load "$PLIST_PATH"
  echo "등록 완료: $PLIST_PATH"
  echo "확인: launchctl list | grep $PLIST_NAME"
  exit 0
fi

if [[ "${1:-}" == "uninstall" ]]; then
  launchctl unload "$PLIST_PATH" 2>/dev/null || true
  rm -f "$PLIST_PATH"
  echo "제거 완료"
  exit 0
fi

if [[ "${1:-}" == "status" ]]; then
  if launchctl list | grep -q "$PLIST_NAME"; then
    echo "상태: 등록됨"
    launchctl list | grep "$PLIST_NAME"
  else
    echo "상태: 미등록"
  fi
  echo "최근 로그:"
  ls -lt "$LOG_DIR"/*.log 2>/dev/null | head -3
  exit 0
fi

# ----------------------------------------------------------
# 크롤링 실행
# ----------------------------------------------------------
exec > >(tee -a "$LOG_FILE") 2>&1
echo "=========================================="
echo "마켓 동향 크롤링 시작: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

cd "$PROJECT_ROOT"

# Step 1: 상품 랭킹 (유니 + 우먼스, 코어타겟 20-24세, 주간)
echo ""
echo "[1/4] 상품 랭킹 크롤링..."
$PYTHON system/scripts/musinsa-crawler/crawler.py \
  --category 001,002,003,004,103 \
  --period WEEKLY --gender M --age AGE_BAND_20 \
  --format json --no-images &
PID_RANK_M=$!

$PYTHON system/scripts/musinsa-crawler/crawler.py \
  --category 001,002,003,004,103 \
  --period WEEKLY --gender F --age AGE_BAND_20 \
  --format json --no-images &
PID_RANK_F=$!

# Step 2: 발매 정보 (예정 + NOW)
echo "[2/4] 발매 정보 크롤링..."
$PYTHON system/scripts/musinsa-release-crawler/crawler.py \
  --tab upcoming --gender A --sort latest \
  --format json --no-images &
PID_REL_UP=$!

$PYTHON system/scripts/musinsa-release-crawler/crawler.py \
  --tab now --gender A --sort popular \
  --format json --no-images &
PID_REL_NOW=$!

# Step 3: 검색어 + 브랜드 트렌드
echo "[3/4] 검색어/브랜드 트렌드 크롤링..."
$PYTHON system/scripts/musinsa-trend-crawler/crawler.py \
  --format json &
PID_TREND=$!

# 모든 크롤러 완료 대기
echo ""
echo "크롤러 5개 병렬 실행 중... 완료 대기"
FAIL=0
for PID in $PID_RANK_M $PID_RANK_F $PID_REL_UP $PID_REL_NOW $PID_TREND; do
  wait $PID || { echo "  크롤러 PID $PID 실패"; FAIL=$((FAIL+1)); }
done

if [ $FAIL -gt 0 ]; then
  echo "경고: ${FAIL}개 크롤러 실패"
else
  echo "크롤러 전체 완료"
fi

# Step 4: 대시보드 데이터 빌드
echo ""
echo "[4/4] 대시보드 데이터 빌드..."
$PYTHON system/scripts/market-trend-builder.py

echo ""
echo "=========================================="
echo "완료: $(date '+%Y-%m-%d %H:%M:%S')"
echo "로그: $LOG_FILE"
echo "=========================================="
