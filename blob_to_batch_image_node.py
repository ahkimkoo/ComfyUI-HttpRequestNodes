
from PIL import Image
from io import BytesIO
import torch
import numpy as np


class BlobToBatchImageNode:
    """
    Decode binary image data (PNG/JPEG/BMP/WebP/TIFF bytes) to ComfyUI IMAGE type.
    Supports multi-page TIFF as batch.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "bytes": ("BYTES",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "decode"
    OUTPUT_NODE = False
    CATEGORY = "RequestNode/Utils"

    def decode(self, bytes: bytes):
        img = Image.open(BytesIO(bytes))
        frames = []

        try:
            i = 0
            while True:
                img.seek(i)
                frames.append(self._frame_to_array(img))
                i += 1
        except EOFError:
            pass

        if not frames:
            frames.append(self._frame_to_array(img))

        batch = np.stack(frames, axis=0)
        tensor = torch.from_numpy(batch).float()
        return (tensor,)

    def _frame_to_array(self, img):
        frame = img.copy()
        if frame.mode == "RGBA":
            bg = Image.new("RGB", frame.size, (255, 255, 255))
            bg.paste(frame, mask=frame.split()[3])
            frame = bg
        elif frame.mode == "L":
            frame = frame.convert("RGB")
        elif frame.mode != "RGB":
            frame = frame.convert("RGB")
        return np.array(frame, dtype=np.float32) / 255.0
