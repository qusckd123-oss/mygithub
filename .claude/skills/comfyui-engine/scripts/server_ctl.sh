#!/bin/bash
# ComfyUI 서버 제어 — start | stop | status
# 사용법: bash server_ctl.sh [start|stop|status]

COMFYUI_DIR="$HOME/ComfyUI"
PIDFILE="$COMFYUI_DIR/.comfyui.pid"
LOGFILE="$COMFYUI_DIR/.comfyui.log"
PORT=8188

case "${1:-status}" in
    start)
        # 이미 실행 중인지 확인
        if curl -s "http://127.0.0.1:$PORT/system_stats" > /dev/null 2>&1; then
            echo "ComfyUI 이미 실행 중 (port $PORT)"
            exit 0
        fi

        if [[ ! -d "$COMFYUI_DIR" ]]; then
            echo "ERROR: ComfyUI가 설치되지 않았습니다. setup.sh를 먼저 실행하세요."
            exit 1
        fi

        echo "ComfyUI 서버 시작 중..."
        cd "$COMFYUI_DIR"
        source venv/bin/activate

        # --force-fp16: Apple Silicon MPS 최적화
        # --listen: 로컬 접근 허용
        nohup python main.py --force-fp16 --port $PORT > "$LOGFILE" 2>&1 &
        echo $! > "$PIDFILE"

        echo "PID: $(cat $PIDFILE)"
        echo "로그: $LOGFILE"

        # 서버 시작 대기 (최대 60초)
        echo -n "서버 준비 대기 중"
        for i in $(seq 1 60); do
            if curl -s "http://127.0.0.1:$PORT/system_stats" > /dev/null 2>&1; then
                echo ""
                echo "ComfyUI 준비 완료! → http://127.0.0.1:$PORT"
                exit 0
            fi
            echo -n "."
            sleep 1
        done
        echo ""
        echo "WARNING: 60초 내에 서버가 준비되지 않았습니다."
        echo "로그 확인: tail -f $LOGFILE"
        ;;

    stop)
        if [[ -f "$PIDFILE" ]]; then
            PID=$(cat "$PIDFILE")
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                rm -f "$PIDFILE"
                echo "ComfyUI 서버 중지됨 (PID: $PID)"
            else
                rm -f "$PIDFILE"
                echo "프로세스가 이미 종료되었습니다."
            fi
        else
            # PID 파일 없으면 포트로 찾기
            PID=$(lsof -ti :$PORT 2>/dev/null)
            if [[ -n "$PID" ]]; then
                kill "$PID"
                echo "ComfyUI 서버 중지됨 (PID: $PID)"
            else
                echo "실행 중인 ComfyUI 서버가 없습니다."
            fi
        fi
        ;;

    status)
        if curl -s "http://127.0.0.1:$PORT/system_stats" > /dev/null 2>&1; then
            STATS=$(curl -s "http://127.0.0.1:$PORT/system_stats")
            echo "ComfyUI 서버: 실행 중 (port $PORT)"
            echo "시스템 정보:"
            echo "$STATS" | python3 -m json.tool 2>/dev/null || echo "$STATS"
        else
            echo "ComfyUI 서버: 중지됨"
            if [[ -d "$COMFYUI_DIR" ]]; then
                echo "설치 경로: $COMFYUI_DIR (설치됨)"
                echo "시작하려면: bash server_ctl.sh start"
            else
                echo "ComfyUI 미설치. setup.sh를 먼저 실행하세요."
            fi
        fi
        ;;

    *)
        echo "사용법: bash server_ctl.sh [start|stop|status]"
        exit 1
        ;;
esac
