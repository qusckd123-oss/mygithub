#!/bin/bash
# ComfyUI 설치 스크립트 — macOS Apple Silicon (M4 Pro)
# 사용법: bash setup.sh [--tier 1|2|3]

set -euo pipefail

COMFYUI_DIR="$HOME/ComfyUI"
PYTHON="python3.12"
TIER="${1:---tier}"
TIER_NUM="${2:-2}"

# Parse --tier argument (지원: 1, 2, 3, slim)
if [[ "$TIER" == "--tier" ]]; then
    TIER_NUM="${TIER_NUM}"
else
    TIER_NUM="2"
fi

# slim 플래그: 기본 Tier 1 + RealVisXL + Lightning LoRA + UltraSharp
SLIM=0
if [[ "$TIER_NUM" == "slim" ]]; then
    SLIM=1
    TIER_NUM=1  # Tier 1 (SDXL Base)은 여전히 설치
fi

echo "============================================"
echo "  ComfyUI 설치 — FPOF Fashion Engine"
echo "  대상: macOS Apple Silicon (MPS)"
echo "  설치 경로: $COMFYUI_DIR"
echo "  모델 티어: $TIER_NUM"
echo "============================================"
echo ""

# ----- 1. 사전 확인 -----
echo "[1/6] 사전 확인..."

if ! command -v $PYTHON &> /dev/null; then
    echo "ERROR: $PYTHON 이 없습니다. 'brew install python@3.12' 를 먼저 실행해주세요."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "ERROR: git이 없습니다."
    exit 1
fi

ARCH=$(uname -m)
if [[ "$ARCH" != "arm64" ]]; then
    echo "WARNING: Apple Silicon이 아닙니다 ($ARCH). MPS 가속이 불가할 수 있습니다."
fi

DISK_FREE=$(df -g "$HOME" | tail -1 | awk '{print $4}')
echo "  디스크 여유: ${DISK_FREE}GB"
if [[ "$DISK_FREE" -lt 15 ]]; then
    echo "WARNING: 디스크 여유가 15GB 미만입니다. 모델 다운로드에 공간이 부족할 수 있습니다."
fi

echo "  Python: $($PYTHON --version)"
echo "  Git: $(git --version | head -1)"
echo "  아키텍처: $ARCH"
echo ""

# ----- 2. ComfyUI 클론 -----
echo "[2/6] ComfyUI 설치..."

if [[ -d "$COMFYUI_DIR" ]]; then
    echo "  이미 설치됨: $COMFYUI_DIR"
    echo "  최신 업데이트 적용..."
    cd "$COMFYUI_DIR" && git pull --ff-only 2>/dev/null || true
else
    git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFYUI_DIR"
fi

cd "$COMFYUI_DIR"

# ----- 3. 가상환경 + 의존성 -----
echo "[3/6] Python 가상환경 및 의존성 설치..."

if [[ ! -d "$COMFYUI_DIR/venv" ]]; then
    $PYTHON -m venv venv
fi

source venv/bin/activate

# PyTorch (MPS 지원 nightly 또는 stable)
pip install --upgrade pip
pip install torch torchvision torchaudio

# ComfyUI 의존성
pip install -r requirements.txt

# 추가 유틸리티 (리사이즈용 + v2 시트 파서)
pip install Pillow
pip install mistune

echo "  PyTorch MPS 사용 가능 여부 확인..."
$PYTHON -c "import torch; print(f'  MPS available: {torch.backends.mps.is_available()}')"

# ----- 4. 커스텀 노드 설치 -----
echo "[4/6] 커스텀 노드 설치..."

CUSTOM_DIR="$COMFYUI_DIR/custom_nodes"

# ComfyUI-Manager (필수 — 노드 관리)
if [[ ! -d "$CUSTOM_DIR/ComfyUI-Manager" ]]; then
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git "$CUSTOM_DIR/ComfyUI-Manager"
    echo "  + ComfyUI-Manager"
else
    echo "  = ComfyUI-Manager (이미 설치)"
fi

if [[ "$TIER_NUM" -ge 2 ]]; then
    # ControlNet Auxiliary Preprocessors
    if [[ ! -d "$CUSTOM_DIR/comfyui_controlnet_aux" ]]; then
        git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git "$CUSTOM_DIR/comfyui_controlnet_aux"
        pip install -r "$CUSTOM_DIR/comfyui_controlnet_aux/requirements.txt" 2>/dev/null || true
        echo "  + ControlNet Auxiliary Preprocessors"
    else
        echo "  = ControlNet Aux (이미 설치)"
    fi

    # IP-Adapter Plus
    if [[ ! -d "$CUSTOM_DIR/ComfyUI_IPAdapter_plus" ]]; then
        git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git "$CUSTOM_DIR/ComfyUI_IPAdapter_plus"
        echo "  + IP-Adapter Plus"
    else
        echo "  = IP-Adapter Plus (이미 설치)"
    fi
fi

# ----- 5. 모델 다운로드 -----
echo "[5/6] 모델 다운로드 (Tier $TIER_NUM)..."

MODELS_DIR="$COMFYUI_DIR/models"
mkdir -p "$MODELS_DIR/checkpoints" "$MODELS_DIR/vae" "$MODELS_DIR/controlnet" \
         "$MODELS_DIR/ipadapter" "$MODELS_DIR/clip_vision" "$MODELS_DIR/loras"

download_model() {
    local url="$1"
    local dest="$2"
    local name="$3"

    if [[ -f "$dest" ]]; then
        echo "  = $name (이미 존재)"
        return
    fi

    echo "  다운로드 중: $name..."
    curl -L --progress-bar -o "$dest" "$url"
    echo "  + $name 완료"
}

# Tier 1: 기본 (SDXL Base + VAE) ≈ 7.3GB
echo "  --- Tier 1: 기본 모델 ---"

download_model \
    "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
    "$MODELS_DIR/checkpoints/sd_xl_base_1.0.safetensors" \
    "SDXL Base 1.0 (~6.9GB)"

download_model \
    "https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl_vae.safetensors" \
    "$MODELS_DIR/vae/sdxl_vae_fp16_fix.safetensors" \
    "SDXL VAE fp16 fix (~335MB)"

# Tier 2: ControlNet + IP-Adapter ≈ +7.2GB
if [[ "$TIER_NUM" -ge 2 ]]; then
    echo "  --- Tier 2: ControlNet + IP-Adapter ---"

    download_model \
        "https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model.fp16.safetensors" \
        "$MODELS_DIR/controlnet/controlnet-canny-sdxl-1.0-fp16.safetensors" \
        "ControlNet Canny SDXL (~2.5GB)"

    download_model \
        "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors" \
        "$MODELS_DIR/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors" \
        "IP-Adapter Plus SDXL (~850MB)"

    download_model \
        "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors" \
        "$MODELS_DIR/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors" \
        "CLIP-ViT-H-14 (~3.9GB)"
fi

# Tier 3: Video (SVD) ≈ +9GB
if [[ "$TIER_NUM" -ge 3 ]]; then
    echo "  --- Tier 3: Video (SVD) ---"

    download_model \
        "https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/resolve/main/svd_xt.safetensors" \
        "$MODELS_DIR/checkpoints/svd_xt.safetensors" \
        "Stable Video Diffusion XT (~9GB)"
fi

# Phase 2-Slim: RealVisXL + SDXL Lightning LoRA + 4xUltraSharp ≈ +7.3GB
if [[ "$SLIM" -eq 1 ]]; then
    echo "  --- Phase 2-Slim: RealVisXL + Lightning LoRA + UltraSharp ---"

    mkdir -p "$MODELS_DIR/loras" "$MODELS_DIR/upscale_models"

    download_model \
        "https://huggingface.co/SG161222/RealVisXL_V5.0/resolve/main/RealVisXL_V5.0_fp16.safetensors" \
        "$MODELS_DIR/checkpoints/RealVisXL_V5.0_fp16.safetensors" \
        "RealVisXL V5.0 fp16 (~6.5GB, 한국인 인물 품질 향상)"

    download_model \
        "https://huggingface.co/ByteDance/SDXL-Lightning/resolve/main/sdxl_lightning_4step_lora.safetensors" \
        "$MODELS_DIR/loras/sdxl_lightning_4step_lora.safetensors" \
        "SDXL Lightning 4-step LoRA (~400MB, 생성 시간 1/5)"

    download_model \
        "https://huggingface.co/lokCX/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth" \
        "$MODELS_DIR/upscale_models/4x-UltraSharp.pth" \
        "4xUltraSharp ESRGAN (~65MB, 룩북 고해상도 업스케일)"
fi

# ----- 6. 완료 -----
echo ""
echo "[6/6] 설치 확인..."

echo ""
echo "============================================"
echo "  ComfyUI 설치 완료!"
echo "============================================"
echo ""
echo "  경로: $COMFYUI_DIR"
echo "  모델 티어: $TIER_NUM"
echo ""
echo "  설치된 모델:"
echo "  $(ls -1 $MODELS_DIR/checkpoints/ 2>/dev/null | head -5)"
echo ""
echo "  서버 시작:"
echo "    cd $COMFYUI_DIR && source venv/bin/activate && python main.py --force-fp16"
echo ""
echo "  또는 server_ctl.sh 사용:"
echo "    bash server_ctl.sh start"
echo ""
echo "  API 엔드포인트: http://127.0.0.1:8188"
echo "============================================"
