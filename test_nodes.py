#!/usr/bin/env python3
"""Direct test of AudioToBlobNode + BinaryPostRequestNode against SVC API."""
import sys, os, io, wave
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import torch

# Load a real WAV file
wav_path = '/Users/cherokee/Downloads/sing_dj_nightqueen.wav'
with wave.open(wav_path, 'rb') as w:
    n_channels = w.getnchannels()
    sampwidth = w.getsampwidth()
    framerate = w.getframerate()
    n_frames = w.getnframes()
    raw = w.readframes(n_frames)

print(f"Input: ch={n_channels}, rate={framerate}, dur={n_frames/framerate:.2f}s")

if sampwidth == 2:
    audio_np = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32767.0
elif sampwidth == 4:
    audio_np = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483647.0

if n_channels > 1:
    audio_np = audio_np.reshape(-1, n_channels)
else:
    audio_np = audio_np.reshape(-1, 1)

waveform = torch.from_numpy(audio_np).unsqueeze(0)
print(f"Tensor shape: {waveform.shape}")

# Test AudioToBlobNode
from audio_to_blob_node import AudioToBlobNode
audio_input = {"waveform": waveform, "sample_rate": framerate}
node = AudioToBlobNode()
wav_bytes = node.convert(audio_input)[0]
print(f"Encoded WAV bytes: {len(wav_bytes)}")

w = wave.open(io.BytesIO(wav_bytes), 'rb')
print(f"Encoded WAV: ch={w.getnchannels()}, rate={w.getframerate()}, dur={w.getnframes()/w.getframerate():.2f}s")
w.close()

# Test BinaryPostRequestNode against SVC
from binary_post_node import BinaryPostRequestNode
post_node = BinaryPostRequestNode()
token = "admin-key-1"
headers = {"Authorization": "Bearer " + token}

text, resp_bytes, resp_json, status_code, resp_headers = post_node.send_request(
    target_url="http://10.9.8.4:8080/rvc/houv",
    body=wav_bytes,
    method="POST",
    content_type="application/octet-stream",
    headers=headers
)

print(f"\n--- SVC Response ---")
print(f"Status: {status_code}")
print(f"Response size: {len(resp_bytes)} bytes")
print(f"RTF: {resp_headers.get('X-RTF', 'N/A')}")
print(f"Processing time: {resp_headers.get('X-Processing-Time-MS', 'N/A')}ms")
print(f"Input duration: {resp_headers.get('X-Input-Duration-MS', 'N/A')}ms")

out_path = '/tmp/svc_comfytest_output.wav'
with open(out_path, 'wb') as f:
    f.write(resp_bytes)

w2 = wave.open(io.BytesIO(resp_bytes), 'rb')
print(f"Output: ch={w2.getnchannels()}, rate={w2.getframerate()}, dur={w2.getnframes()/w2.getframerate():.2f}s")
w2.close()

print(f"\nOutput saved to {out_path}")
print("\n=== ALL NODE TESTS PASSED ===")
