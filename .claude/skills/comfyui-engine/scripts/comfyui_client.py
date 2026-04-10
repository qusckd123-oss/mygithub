"""
ComfyUI API 클라이언트 — 로컬 ComfyUI 서버와 HTTP로 통신.
ComfyUI가 localhost:8188에서 실행 중이어야 한다.

사용법:
    from comfyui_client import ComfyUIClient
    client = ComfyUIClient()
    prompt_id = client.queue_prompt(workflow_dict)
    outputs = client.wait_and_download(prompt_id, output_dir)
"""

import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


class ComfyUIClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8188):
        self.base_url = f"http://{host}:{port}"
        self.client_id = f"fpof-{random.randint(1000, 9999)}"

    # ── 상태 확인 ──

    def is_alive(self) -> bool:
        """ComfyUI 서버가 응답하는지 확인."""
        try:
            req = urllib.request.Request(f"{self.base_url}/system_stats")
            urllib.request.urlopen(req, timeout=5)
            return True
        except (urllib.error.URLError, ConnectionRefusedError, OSError):
            return False

    def get_system_stats(self) -> dict:
        """시스템 정보 조회."""
        data = self._get("/system_stats")
        return json.loads(data)

    # ── 프롬프트 큐잉 ──

    def queue_prompt(self, workflow: dict, extra_data: dict | None = None) -> str:
        """워크플로우를 실행 큐에 추가. prompt_id를 반환."""
        payload = {
            "prompt": workflow,
            "client_id": self.client_id,
        }
        if extra_data:
            payload["extra_data"] = extra_data

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/prompt",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())

        if "error" in result:
            err = result["error"]
            if isinstance(err, dict):
                detail = err.get("details", err.get("message", json.dumps(err, ensure_ascii=False)))
            else:
                detail = str(err)
            raise RuntimeError(f"ComfyUI 큐잉 에러: {detail}")
        if "node_errors" in result and result["node_errors"]:
            errs = result["node_errors"]
            summary_lines = []
            for nid, e in errs.items():
                ct = e.get("class_type", "?") if isinstance(e, dict) else "?"
                err_list = e.get("errors", e) if isinstance(e, dict) else e
                summary_lines.append(f"  노드 {nid} ({ct}): {err_list}")
            raise RuntimeError(
                "ComfyUI 노드 에러 (워크플로우에 문제가 있습니다):\n"
                + "\n".join(summary_lines)
                + "\n\n힌트: 최신 ComfyUI-Manager로 커스텀 노드를 업데이트하거나 "
                "IP-Adapter Plus 저장소를 git pull 해보세요."
            )

        return result["prompt_id"]

    # ── 진행 상태 폴링 ──

    def get_history(self, prompt_id: str) -> dict | None:
        """특정 prompt의 실행 기록 조회. 아직 완료 안 됐으면 None."""
        data = self._get(f"/history/{prompt_id}")
        history = json.loads(data)
        return history.get(prompt_id)

    def get_queue(self) -> dict:
        """현재 큐 상태 조회."""
        data = self._get("/queue")
        return json.loads(data)

    def wait_for_completion(
        self, prompt_id: str, timeout: int = 600, poll_interval: float = 2.0
    ) -> dict:
        """
        프롬프트 완료까지 대기 (폴링 방식).
        timeout: 최대 대기 시간(초).
        반환: history 결과 dict.
        """
        start = time.time()
        while time.time() - start < timeout:
            history = self.get_history(prompt_id)
            if history and "outputs" in history:
                return history
            time.sleep(poll_interval)

        raise TimeoutError(
            f"ComfyUI 생성 {timeout}초 초과. prompt_id={prompt_id}"
        )

    # ── 이미지 다운로드 ──

    def download_image(
        self, filename: str, subfolder: str, img_type: str, save_path: str
    ) -> str:
        """생성된 이미지를 로컬에 저장."""
        params = urllib.parse.urlencode({
            "filename": filename,
            "subfolder": subfolder,
            "type": img_type,
        })
        url = f"{self.base_url}/view?{params}"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req)

        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(resp.read())

        return save_path

    def wait_and_download(
        self,
        prompt_id: str,
        output_dir: str,
        filename_prefix: str = "output",
        timeout: int = 600,
    ) -> list[str]:
        """
        완료 대기 후 모든 출력 이미지를 다운로드.
        반환: 저장된 파일 경로 리스트.
        """
        history = self.wait_for_completion(prompt_id, timeout=timeout)
        saved_files = []
        idx = 0

        outputs = history.get("outputs", {})
        for node_id, node_output in outputs.items():
            images = node_output.get("images", [])
            for img_info in images:
                ext = Path(img_info["filename"]).suffix or ".png"
                save_name = f"{filename_prefix}_{idx:04d}{ext}"
                save_path = os.path.join(output_dir, save_name)
                self.download_image(
                    filename=img_info["filename"],
                    subfolder=img_info.get("subfolder", ""),
                    img_type=img_info.get("type", "output"),
                    save_path=save_path,
                )
                saved_files.append(save_path)
                idx += 1

            # 영상 출력 (gifs/videos)
            gifs = node_output.get("gifs", [])
            for gif_info in gifs:
                ext = Path(gif_info["filename"]).suffix or ".mp4"
                save_name = f"{filename_prefix}_{idx:04d}{ext}"
                save_path = os.path.join(output_dir, save_name)
                self.download_image(
                    filename=gif_info["filename"],
                    subfolder=gif_info.get("subfolder", ""),
                    img_type=gif_info.get("type", "output"),
                    save_path=save_path,
                )
                saved_files.append(save_path)
                idx += 1

        return saved_files

    # ── 이미지 업로드 (ControlNet/IP-Adapter 입력용) ──

    def upload_image(self, filepath: str, subfolder: str = "") -> dict:
        """ComfyUI input 폴더에 이미지 업로드."""
        import mimetypes

        filename = os.path.basename(filepath)
        mime_type = mimetypes.guess_type(filepath)[0] or "image/png"

        boundary = f"----FormBoundary{random.randint(100000, 999999)}"
        body = bytearray()

        # image 필드
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(
            f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode()
        )
        body.extend(f"Content-Type: {mime_type}\r\n\r\n".encode())
        with open(filepath, "rb") as f:
            body.extend(f.read())
        body.extend(b"\r\n")

        # subfolder 필드
        if subfolder:
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(
                f'Content-Disposition: form-data; name="subfolder"\r\n\r\n{subfolder}\r\n'.encode()
            )

        # overwrite 필드
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(
            b'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n'
        )

        body.extend(f"--{boundary}--\r\n".encode())

        req = urllib.request.Request(
            f"{self.base_url}/upload/image",
            data=bytes(body),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())

    # ── 내부 유틸 ──

    def _get(self, path: str) -> bytes:
        req = urllib.request.Request(f"{self.base_url}{path}")
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.read()


# CLI 모드: 서버 상태 확인
if __name__ == "__main__":
    client = ComfyUIClient()
    if client.is_alive():
        stats = client.get_system_stats()
        print("ComfyUI 서버: 실행 중")
        print(json.dumps(stats, indent=2))
    else:
        print("ComfyUI 서버: 응답 없음")
        sys.exit(1)
