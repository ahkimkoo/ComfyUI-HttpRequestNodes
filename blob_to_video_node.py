
from io import BytesIO
import torch
import numpy as np

try:
    import imageio
except ImportError:
    imageio = None


class BlobToVideoNode:
    """
    Decode binary video data (MP4/GIF/WebM bytes) to ComfyUI VIDEO type.
    Compatible with VideoHelperSuite format.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "bytes": ("BYTES",),
            },
        }

    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    FUNCTION = "decode"
    OUTPUT_NODE = False
    CATEGORY = "RequestNode/Utils"

    def decode(self, bytes: bytes):
        if imageio is None:
            raise ImportError("imageio is required. pip install imageio imageio-ffmpeg")

        reader = imageio.get_reader(BytesIO(bytes), format="ffmpeg")
        frames = []
        for frame in reader:
            frames.append(frame)
        reader.close()

        # frames: list of [H, W, 3] uint8
        arr = np.stack(frames, axis=0)  # [N, H, W, 3]
        tensor = torch.from_numpy(arr).float() / 255.0  # [N, H, W, 3] float

        video = {
            "frames": tensor,
            "frame_rate": reader.get_meta_data().get("fps", 24),
            "path": None,
        }
        return (video,)
