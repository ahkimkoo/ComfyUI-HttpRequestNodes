import requests
import json
import io
import torch
import numpy as np


class MediaFormPostNode:
    """Send media (IMAGE / AUDIO / VIDEO) via multipart/form-data POST.

    Unified node that accepts any combination of IMAGE, AUDIO, VIDEO inputs
    and sends them as multipart form data files. Designed for APIs that accept
    file uploads (e.g., TTS, SVC, video processing services).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "target_url": ("STRING", {"default": "http://127.0.0.1:8000/api/upload"}),
            },
            "optional": {
                "image": ("IMAGE",),
                "audio": ("AUDIO",),
                "video": ("VIDEO",),
                "image_field": ("STRING", {"default": "image"}),
                "audio_field": ("STRING", {"default": "audio"}),
                "video_field": ("STRING", {"default": "video"}),
                "form_fields": ("KEY_VALUE", {"default": None}),
                "headers": ("KEY_VALUE", {"default": None}),
            },
        }

    RETURN_TYPES = ("STRING", "BYTES", "JSON", "INT", "DICT")
    RETURN_NAMES = ("text", "response_bytes", "json", "status_code", "response_headers")
    FUNCTION = "send"
    CATEGORY = "RequestNode/Post Request"
    DESCRIPTION = "Upload IMAGE/AUDIO/VIDEO as multipart/form-data. At least one media input required."

    def send(self, target_url, image=None, audio=None, video=None,
             image_field="image", audio_field="audio", video_field="video",
             form_fields=None, headers=None):

        files = []

        # --- IMAGE ---
        if image is not None:
            from PIL import Image as PILImage
            for i, single_image in enumerate(image):
                img_np = 255.0 * single_image.cpu().numpy()
                img = PILImage.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                files.append((image_field, (f"image_{i}.png", buf, "image/png")))

        # --- AUDIO ---
        if audio is not None:
            import soundfile as sf
            waveform = audio["waveform"]
            sr = audio["sample_rate"]
            w = waveform
            if w.dim() == 3:
                w = w.squeeze(0)
            if w.dim() == 2 and w.shape[0] < w.shape[1]:
                w = w.T
            w_np = w.cpu().float().numpy()
            w_np = np.clip(w_np, -1.0, 1.0)
            w_int16 = (w_np * 32767).astype(np.int16)
            buf = io.BytesIO()
            sf.write(buf, w_int16, sr, format="WAV")
            buf.seek(0)
            files.append((audio_field, ("audio.wav", buf, "audio/wav")))

        # --- VIDEO ---
        if video is not None:
            import imageio
            frames = None
            fps = 24.0
            if isinstance(video, dict):
                frames = video.get("frames")
                if "frame_rate" in video:
                    fps = float(video["frame_rate"])
                elif "video_info" in video and isinstance(video["video_info"], dict):
                    fps = float(video["video_info"].get("fps", 24.0))
            elif isinstance(video, torch.Tensor):
                frames = video

            if frames is not None:
                if frames.dim() == 4:
                    frames = frames.squeeze(0)
                f_np = (frames.cpu().float().numpy() * 255).clip(0, 255).astype(np.uint8)
                buf = io.BytesIO()
                writer = imageio.get_writer(buf, format="mp4", fps=fps)
                for i in range(f_np.shape[0]):
                    writer.append_data(f_np[i])
                writer.close()
                buf.seek(0)
                files.append((video_field, ("video.mp4", buf, "video/mp4")))

        if not files:
            return ("No media input provided", b"", {"error": "No media input"}, 0, {})

        data = form_fields if form_fields else {}
        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            resp = requests.post(target_url, files=files, data=data, headers=request_headers, timeout=300)
            resp_headers = dict(resp.headers)
            try:
                resp_json = resp.json()
            except (json.JSONDecodeError, ValueError):
                resp_json = {"raw": resp.text[:2000]}
            return (resp.text, resp.content, resp_json, resp.status_code, resp_headers)
        except Exception as e:
            err = str(e)
            return (err, b"", {"error": err}, 0, {})


NODE_CLASS_MAPPINGS = {
    "MediaFormPostNode": MediaFormPostNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "MediaFormPostNode": "Media Form POST (Image/Audio/Video)",
}
