# ComfyUI-HttpRequestNodes

Extended HTTP request nodes for ComfyUI — supports image, audio, video binary data, form-data upload, and raw binary I/O.

Fork of [felixszeto/ComfyUI-RequestNodes](https://github.com/felixszeto/ComfyUI-RequestNodes)（原项目仅支持图片上传），在此基础上新增了对音频（AUDIO）、视频（VIDEO）二进制数据的 HTTP 发送与接收能力，以及原始二进制 POST 请求和多媒体 Form 上传支持。

## Installation

### 方法一：通过 ComfyUI Manager 安装（推荐）

在 ComfyUI 中打开 **Manager** → **Install Custom Nodes** → 搜索 `ComfyUI-HttpRequestNodes` → 点击 Install。

### 方法二：通过 comfy CLI 安装

```bash
comfy node install ComfyUI-HttpRequestNodes
```

### 方法三：手动安装

```bash
cd ComfyUI/custom_nodes
git clone git@github.com:ahkimkoo/ComfyUI-HttpRequestNodes.git
cd ComfyUI-HttpRequestNodes
pip install soundfile imageio imageio-ffmpeg
```

重启 ComfyUI 即可。

---

## Nodes

### 原有节点

*   **Get Request Node** — GET 请求
*   **Post Request Node** — POST 请求
*   **Form Post Request Node** — multipart/form-data POST（支持图片上传）
*   **Rest Api Node** — 通用 HTTP 方法（GET/POST/PUT/DELETE/PATCH/HEAD/OPTIONS），支持重试
*   **Image to Base64 Node** — 图片转 Base64
*   **Image to Blob Node** — 图片转二进制
*   **Key/Value Node** — 键值对构建
*   **Chain Image Node** — 图片拼接为 batch
*   **String Replace Node** — 字符串占位符替换
*   **Retry Settings Node** — 重试配置

### 新增节点

#### Audio To Blob Node
ComfyUI AUDIO 类型 → WAV 二进制（BYTES）。使用 soundfile 编码。
- Category: RequestNode/Converters
- Input: `audio` (AUDIO)
- Output: `wav_bytes` (BYTES)

#### Video To Blob Node
ComfyUI VIDEO 类型 → MP4/GIF 二进制（BYTES）。支持 VHS 路径和帧张量。使用 imageio 编码。
- Category: RequestNode/Converters
- Input: `video` (VIDEO), `format` (mp4/gif), `fps` (INT, default 24)
- Output: `video_bytes` (BYTES)

#### Binary Post Request Node
发送原始二进制数据（application/octet-stream）。用于音频/视频等二进制数据的 HTTP 传输。
- Category: RequestNode/REST API
- Input: `target_url` (STRING), `body` (BYTES), `method` (POST/PUT/PATCH), `content_type` (STRING), `headers` (KEY_VALUE)
- Output: `text` (STRING), `response_bytes` (BYTES), `json` (JSON), `status_code` (INT), `response_headers` (DICT)

#### Media Form Post Node
通过 multipart/form-data 发送多媒体数据（IMAGE/AUDIO/VIDEO），支持附加表单字段。
- Category: RequestNode/Post Request
- Input: `target_url`, `form_fields` (KEY_VALUE), `headers` (KEY_VALUE), `image` (IMAGE), `image_bytes` (BYTES), `audio_bytes` (BYTES), `video_bytes` (BYTES), 各 field_name
- Output: `text`, `json`, `status_code`, `response_bytes`, `response_headers`

#### Blob To Image Node
二进制图片（PNG/JPEG/BMP/WebP）→ ComfyUI IMAGE 类型。
- Category: RequestNode/Utils
- Input: `bytes` (BYTES)
- Output: `image` (IMAGE) `[batch, height, width, channels]`

#### Blob To Batch Image Node
二进制图片 → IMAGE 类型，支持多页 TIFF 返回完整 batch。
- Category: RequestNode/Utils
- Input: `bytes` (BYTES)
- Output: `image` (IMAGE)

#### Blob To Audio Node
二进制 WAV → ComfyUI AUDIO 类型。输出兼容 PreviewAudio、SaveAudio 等节点。
- Category: RequestNode/Utils
- Input: `bytes` (BYTES)
- Output: `audio` (AUDIO) `{"waveform": [batch, channels, samples], "sample_rate": int}`

#### Blob To Video Node
二进制视频（MP4/GIF/WebM）→ ComfyUI VIDEO 类型。输出兼容 VHS 节点。
- Category: RequestNode/Utils
- Input: `bytes` (BYTES)
- Output: `video` (VIDEO)

---

## Example Workflows

插件自带工作流模板，在 ComfyUI 工作流列表中可直接加载：

*   **svc-all-endpoints** — SVC 变声服务集成，包含 4 个分组：
    *   ① List Roles — GET /roles
    *   ② Train Voice — POST /train/{name}（默认禁用）
    *   ③ Voice Conversion — POST /rvc/{name}（默认启用）
    *   ④ Clone Role — POST /role/{name}（默认禁用）

---

## Usage（原有节点）

*   **Get Request Node**:
    *   **Category**: RequestNode/Get Request
    *   **Inputs**: `target_url` (STRING), `headers` (KEY_VALUE), `query_list` (KEY_VALUE)
    *   **Outputs**: `text` (STRING), `file` (BYTES), `json` (JSON), `any` (ANY)

*   **Post Request Node**:
    *   **Category**: RequestNode/Post Request
    *   **Inputs**: `target_url` (STRING), `request_body` (STRING, multiline), `headers` (KEY_VALUE), `str0`~`str9` (STRING)
    *   **Outputs**: `text` (STRING), `file` (BYTES), `json` (JSON), `any` (ANY)

*   **Form Post Request Node**:
    *   **Category**: RequestNode/Post Request
    *   **Inputs**: `target_url` (STRING), `image` (IMAGE), `image_field_name` (STRING), `form_fields` (KEY_VALUE), `headers` (KEY_VALUE)
    *   **Outputs**: `text` (STRING), `json` (JSON), `any` (ANY)

*   **Rest Api Node**:
    *   **Category**: RequestNode/REST API
    *   **Inputs**: `target_url` (STRING), `method` (Dropdown), `request_body` (STRING), `headers` (KEY_VALUE), `RETRY_SETTING` (RETRY_SETTING)
    *   **Outputs**: `text` (STRING), `file` (BYTES), `json` (JSON), `headers` (DICT), `status_code` (INT), `any` (ANY)

*   **Image to Base64 Node**:
    *   **Category**: RequestNode/Converters
    *   **Input**: `image` (IMAGE)
    *   **Output**: Base64 encoded string

*   **Image to Blob Node**:
    *   **Category**: RequestNode/Converters
    *   **Input**: `image` (IMAGE)
    *   **Output**: BYTES (raw binary)

*   **Key/Value Node**:
    *   **Category**: RequestNode/KeyValue
    *   **Inputs**: `key` (STRING), `value` (STRING), `KEY_VALUE` (KEY_VALUE, optional merge)
    *   **Output**: `KEY_VALUE` (KEY_VALUE)

*   **Chain Image Node**:
    *   **Category**: RequestNode/Utils
    *   **Inputs**: `image` (IMAGE, upload), `image_batch_in` (IMAGE, optional)
    *   **Output**: `image_batch_out` (IMAGE)

*   **String Replace Node**:
    *   **Category**: RequestNode/Utils
    *   **Inputs**: `input_string` (STRING, multiline), `placeholders` (KEY_VALUE)
    *   **Output**: `output_string` (STRING)

*   **Retry Settings Node**:
    *   **Category**: RequestNode/KeyValue
    *   **Inputs**: `key` (Dropdown: max_retry/retry_interval/retry_until_status_code/retry_until_not_status_code), `value` (INT), `RETRY_SETTING` (RETRY_SETTING)
    *   **Output**: `RETRY_SETTING` (RETRY_SETTING)
    *   **Retry Logic**: `max_retry` 最大重试次数（默认 3），`retry_interval` 重试间隔 ms（默认 1000），`retry_until_status_code` 等到指定状态码停止，`retry_until_not_status_code` 等到状态码不匹配停止。未指定条件时，非 2xx 自动重试。

---

## License

See [LICENSE](LICENSE) file.
