"""
venv 자동 전환 부트스트랩.

시스템 python3.12 에서 스킬 스크립트가 직접 실행될 때 ~/ComfyUI/venv 안의
mistune, Pillow 등 런타임 의존성을 찾지 못해 ImportError 가 발생하는 문제를 해결한다.

ensure_venv(module)을 호출하면:
  1. 해당 모듈이 현재 인터프리터에 import 가능하면 즉시 리턴
  2. 불가능하면 ~/ComfyUI/venv/bin/python 으로 os.execv 재실행
  3. venv python 에도 없으면 명확한 에러 메시지와 함께 종료

무한 루프 방지: FPOF_IN_VENV=1 환경변수로 가드.
"""

import importlib
import os
import sys


VENV_PY = os.path.expanduser("~/ComfyUI/venv/bin/python")


def ensure_venv(required_module: str) -> None:
    """required_module 을 probe 하고 실패 시 venv python 으로 재실행."""
    # 현재 인터프리터에 이미 있으면 패스
    try:
        importlib.import_module(required_module)
        return
    except ImportError:
        pass

    # 이미 venv 안에서 재실행된 상태인데도 실패 → 진짜로 없음
    if os.environ.get("FPOF_IN_VENV") == "1":
        sys.stderr.write(
            f"ERROR: ~/ComfyUI/venv 에서도 '{required_module}' 를 찾을 수 없습니다.\n"
            f"  cd ~/ComfyUI && source venv/bin/activate && pip install {required_module}\n"
        )
        sys.exit(1)

    if not os.path.exists(VENV_PY):
        sys.stderr.write(
            f"ERROR: '{required_module}' 모듈이 없고 ~/ComfyUI/venv 도 없습니다.\n"
            f"  bash scripts/setup.sh 를 먼저 실행하세요.\n"
        )
        sys.exit(1)

    # python -c "..." 인라인 모드 감지:
    # 이 경우 sys.argv = ['-c'] 로 스크립트 본문이 argv 에 보존되지 않으므로
    # os.execv 로 재실행하면 -c 뒤 인자가 사라져 "Argument expected for the -c option" 에러.
    # 인라인 모드에서는 사용자가 venv python 을 직접 쓰도록 안내하고 종료.
    if sys.argv and sys.argv[0] == "-c":
        sys.stderr.write(
            f"ERROR: '{required_module}' 모듈이 현재 인터프리터에 없습니다.\n"
            f"  'python -c' 인라인 모드는 자동 venv 전환이 불가능합니다.\n"
            f"  venv python 을 직접 사용하세요:\n"
            f"    {VENV_PY} -c \"...\"\n"
        )
        sys.exit(1)

    # venv python 으로 자기 자신 재실행
    os.environ["FPOF_IN_VENV"] = "1"
    os.execv(VENV_PY, [VENV_PY] + sys.argv)
