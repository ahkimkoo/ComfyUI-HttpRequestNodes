import io
import torch
import numpy as np


class VideoToBlobNode:
    """Convert ComfyUI VIDEO type to MP4 binary (BYTES).

    Supports two common VIDEO representations:
    1. VideoHelperSuite: {"video_info": {...}, "frames": Tensor [batch, H, W, C] 0-1 float}
    2. ComfyUI native:   {"frames": Tensor [batch, H, W, C] 0-1 float, "frame_rate": float}

    Output: MP4 bytes via imageio.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
            },
            "optional": {
                "frame_rate": ("INT", {"default": 0, "min": 0, "max": 120, "tooltip": "0 = auto-detect from VIDEO type"}),
                "output_format": (["mp4", "gif", "webp"], {"default": "mp4"}),
            },
        }

    RETURN_TYPES = ("BYTES", "INT")
    RETURN_NAMES = ("video_bytes", "frame_count")
    FUNCTION = "convert"
    CATEGORY = "RequestNode/Converters"

    def convert(self, video, frame_rate=0, output_format="mp4"):
        import imageio

        # Extract frames tensor
        frames = None
        detected_fps = 24.0  # fallback

        if isinstance(video, dict):
            # VideoHelperSuite format
            if "frames" in video:
                frames = video["frames"]
            # Try to detect fps
            if frame_rate > 0:
                detected_fps = float(frame_rate)
            elif "frame_rate" in video:
                detected_fps = float(video["frame_rate"])
            elif "video_info" in video:
                vi = video["video_info"]
                if isinstance(vi, dict) and "fps" in vi:
                    detected_fps = float(vi["fps"])
        elif isinstance(video, torch.Tensor):
            frames = video
        else:
            raise ValueError(f"Unsupported VIDEO type: {type(video)}")

        if frames is None:
            raise ValueError("Could not extract frames from VIDEO input")

        # frames: [batch, H, W, C] 0-1 float
        if frames.dim() == 4:
            frames = frames.squeeze(0)  # [H, W, C] per frame → stack of frames

        # Convert to uint8 numpy [N, H, W, C]
        f_np = (frames.cpu().float().numpy() * 255).clip(0, 255).astype(np.uint8)

        buffer = io.BytesIO()
        writer = imageio.get_writer(buffer, format=output_format, fps=detected_fps)
        for i in range(f_np.shape[0]):
            writer.append_data(f_np[i])
        writer.close()
        buffer.seek(0)

        return (buffer.getvalue(), f_np.shape[0])


NODE_CLASS_MAPPINGS = {
    "VideoToBlobNode": VideoToBlobNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoToBlobNode": "Video to Blob (MP4/GIF)",
}
