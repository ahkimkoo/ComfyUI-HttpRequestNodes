import torch
import numpy as np
import soundfile as sf
import io
import base64


class Base64ToAudioNode:
    """Decodes a Base64-encoded WAV string to ComfyUI AUDIO type."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64_string": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "convert"
    CATEGORY = "RequestNode/Converters"

    def convert(self, base64_string: str):
        audio_bytes = base64.b64decode(base64_string)

        audio_buffer = io.BytesIO(audio_bytes)
        audio_np, samplerate = sf.read(audio_buffer, dtype='float32')

        if audio_np.ndim == 1:
            audio_np = audio_np[:, np.newaxis]

        # ComfyUI AUDIO format: [batch, channels, samples]
        waveform = torch.from_numpy(audio_np)  # [samples, channels]
        waveform = waveform.permute(1, 0).unsqueeze(0)  # [1, channels, samples]

        return ({"waveform": waveform, "sample_rate": samplerate},)
