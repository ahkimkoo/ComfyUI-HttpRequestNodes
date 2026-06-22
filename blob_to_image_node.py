
from PIL import Image
from io import BytesIO
import torch
import numpy as np


class BlobToImageNode:
    """
    Decode binary image data (PNG/JPEG/BMP/WebP bytes) to ComfyUI IMAGE type.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "bytes": ("BYTES",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "decode"
    OUTPUT_NODE = False
    CATEGORY = "RequestNode/Utils"

    def decode(self, bytes: bytes):
        img = Image.open(BytesIO(bytes))

        # Handle alpha channel: composite onto white background
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode == "L":
            img = img.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        arr = np.array(img, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(arr).unsqueeze(0)  # [1, H, W, 3]
        return (tensor,)
