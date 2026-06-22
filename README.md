# ComfyUI-HttpRequestNodes

> **扩展版本** — 本仓库 fork 自 [felixszeto/ComfyUI-RequestNodes](https://github.com/felixszeto/ComfyUI-RequestNodes)（原项目仅支持图片上传），在此基础上新增了对音频（AUDIO）、视频（VIDEO）二进制数据的 HTTP 发送与接收能力，以及原始二进制 POST 请求和多媒体 Form 上传支持。
>
> 原项目节点完全兼容，所有新增节点均遵循原项目的设计模式。

[中文版本](README_zh.md)

## Introduction

ComfyUI-RequestNodes is a custom node plugin for ComfyUI that provides functionality for sending HTTP requests and related utilities. Currently, it includes the following nodes:

*   **Get Request Node**: Sends GET requests and retrieves responses.
*   **Post Request Node**: Sends POST requests and retrieves responses.
*   **Form Post Request Node**: Sends POST requests in `multipart/form-data` format, supporting file (image) uploads.
*   **Rest Api Node**: A versatile node for sending various HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS) with retry settings.
*   **Image to Base64 Node**: Converts an image to a Base64 encoded string.
*   **Image to Blob Node**: Converts an image to a Blob (Binary Large Object).
*   **Key/Value Node**: Creates key/value pairs for building request parameters, headers, or other dictionary-like structures.
*   **Chain Image Node**: Uploads an image and adds it to an image batch, allowing for chaining to build a batch from multiple images.
*   **String Replace Node**: Replaces placeholders in a string with provided values.
*   **Retry Settings Node**: Creates retry setting configurations for the Rest Api Node.

### New Nodes (Extended)

*   **Audio To Blob Node**: Converts ComfyUI AUDIO type to WAV binary bytes for HTTP transmission.
*   **Video To Blob Node**: Converts ComfyUI VIDEO type (VHS path or frame tensor) to MP4/GIF binary bytes.
*   **Binary Post Request Node**: Sends raw binary data (BYTES) via HTTP POST/PUT/PATCH with `application/octet-stream` content type.
*   **Media Form Post Node**: Sends multimedia data (IMAGE/AUDIO/VIDEO) via `multipart/form-data` in a single request.
*   **Blob To Image Node**: Decodes binary image data (PNG/JPEG/BMP/WebP bytes) to ComfyUI IMAGE type.
*   **Blob To Batch Image Node**: Decodes binary image data to IMAGE type, supporting multi-page TIFF.
*   **Blob To Audio Node**: Decodes binary audio data (WAV bytes) to ComfyUI AUDIO type.
*   **Blob To Video Node**: Decodes binary video data (MP4/GIF/WebM bytes) to ComfyUI VIDEO type.

---

## Node Details

### Audio To Blob Node

Converts ComfyUI `AUDIO` type to WAV binary bytes (`BYTES`). Uses `soundfile` for WAV encoding. Output is suitable for HTTP POST as `application/octet-stream`.

*   **Category**: RequestNode/Converters
*   **Inputs**:
    *   `audio` (AUDIO, required): The audio data to convert.
*   **Outputs**:
    *   `wav_bytes` (BYTES): The audio encoded as WAV binary data.

### Video To Blob Node

Converts ComfyUI `VIDEO` type to MP4 or GIF binary bytes. Supports both VHS-style path-based VIDEO and frame tensor VIDEO. Uses `imageio` for encoding.

*   **Category**: RequestNode/Converters
*   **Inputs**:
    *   `video` (VIDEO, required): The video data to convert.
    *   `format` (Dropdown, optional): Output format, `mp4` (default) or `gif`.
    *   `fps` (INT, optional): Frames per second (default: 24). Ignored for VHS-style VIDEO that already has metadata.
*   **Outputs**:
    *   `video_bytes` (BYTES): The video encoded as binary data.

### Binary Post Request Node

Sends raw binary data via HTTP POST/PUT/PATCH. The body is sent as `application/octet-stream`. This is the core node for transmitting audio/video binary data to external APIs (e.g., SVC voice conversion services).

*   **Category**: RequestNode/REST API
*   **Inputs**:
    *   `target_url` (STRING, required): The URL to send the request to.
    *   `body` (BYTES, required): The binary data to send. Connect output from Audio/Video/Image To Blob nodes.
    *   `method` (Dropdown, required): HTTP method — `POST` (default), `PUT`, or `PATCH`.
    *   `content_type` (STRING, optional): Content-Type header, default `application/octet-stream`.
    *   `headers` (KEY_VALUE, optional): Additional request headers (e.g., Authorization). From Key/Value Node.
*   **Outputs**:
    *   `text` (STRING): Response body as text.
    *   `response_bytes` (BYTES): Response body as raw bytes. Connect to Blob To Audio/Image/Video nodes to decode.
    *   `json` (JSON): Response parsed as JSON (if valid).
    *   `status_code` (INT): HTTP status code.
    *   `response_headers` (DICT): Response headers as dictionary.

### Media Form Post Node

Sends multimedia data via `multipart/form-data`. Can attach IMAGE, AUDIO, and VIDEO in a single request, along with additional form fields and headers. Supports binary data from Image/Audio/Video To Blob nodes.

*   **Category**: RequestNode/Post Request
*   **Inputs**:
    *   `target_url` (STRING, required): The URL to send the request to.
    *   `form_fields` (KEY_VALUE, optional): Additional form fields. From Key/Value Node.
    *   `headers` (KEY_VALUE, optional): Request headers (e.g., Authorization). From Key/Value Node.
    *   `image` (IMAGE, optional): Image data to attach.
    *   `image_field_name` (STRING, optional): Form field name for image, default `image`.
    *   `image_bytes` (BYTES, optional): Pre-encoded image binary data (alternative to IMAGE input).
    *   `audio_bytes` (BYTES, optional): Audio binary data to attach. From Audio To Blob Node.
    *   `audio_field_name` (STRING, optional): Form field name for audio, default `audio`.
    *   `video_bytes` (BYTES, optional): Video binary data to attach. From Video To Blob Node.
    *   `video_field_name` (STRING, optional): Form field name for video, default `video`.
*   **Outputs**:
    *   `text` (STRING): Response body as text.
    *   `json` (JSON): Response parsed as JSON (if valid).
    *   `status_code` (INT): HTTP status code.
    *   `response_bytes` (BYTES): Response body as raw bytes.
    *   `response_headers` (DICT): Response headers as dictionary.

### Blob To Image Node

Decodes binary image data (PNG/JPEG/BMP/WebP bytes) to ComfyUI `IMAGE` type. Useful for converting HTTP response bytes back to images.

*   **Category**: RequestNode/Utils
*   **Inputs**:
    *   `bytes` (BYTES, required): The binary image data to decode.
*   **Outputs**:
    *   `image` (IMAGE): Decoded image as ComfyUI IMAGE tensor `[batch, height, width, channels]`.

### Blob To Batch Image Node

Decodes binary image data to ComfyUI `IMAGE` type. Supports multi-page TIFF files, returning all pages as a batch. Single-page images return batch size 1.

*   **Category**: RequestNode/Utils
*   **Inputs**:
    *   `bytes` (BYTES, required): The binary image data to decode.
*   **Outputs**:
    *   `image` (IMAGE): Decoded image(s) as IMAGE tensor. Multi-page TIFF returns all pages as batch.

### Blob To Audio Node

Decodes binary audio data (WAV bytes) to ComfyUI `AUDIO` type. Output is compatible with PreviewAudio, SaveAudio, and other audio nodes.

*   **Category**: RequestNode/Utils
*   **Inputs**:
    *   `bytes` (BYTES, required): The binary WAV data to decode.
*   **Outputs**:
    *   `audio` (AUDIO): Decoded audio as `{"waveform": Tensor [batch, channels, samples], "sample_rate": int}`.

### Blob To Video Node

Decodes binary video data (MP4/GIF/WebM bytes) to ComfyUI `VIDEO` type. Output is compatible with VHS (Video Helper Suite) nodes for preview and further processing.

*   **Category**: RequestNode/Utils
*   **Inputs**:
    *   `bytes` (BYTES, required): The binary video data to decode.
*   **Outputs**:
    *   `video` (VIDEO): Decoded video as ComfyUI VIDEO type (path-based).

---

## Example Workflows

The following workflow templates are included in ComfyUI's workflow list:

*   **svc-all-endpoints** — SVC voice conversion service integration with 4 groups:
    *   ① List Roles (GET /roles)
    *   ② Train Voice (POST /train/{name}) — disabled by default
    *   ③ Voice Conversion (POST /rvc/{name}) — enabled by default
    *   ④ Clone Role (POST /role/{name}) — disabled by default

---

## Test Resources

The plugin includes the following test resources:
* `base_flask_server.py` - Python Flask server for testing
* `get_node.json` - GET request workflow template
![rest_node](workflows/get_node.png)
* `post_node.json` - POST request workflow template
![rest_node](workflows/post_node.png)
* `form_post_request_node.json` - FORM POST request workflow template
![rest_node](workflows/form_post_request_node.png)
* `workflows/rest_node.json` - REST API request workflow template
![rest_node](workflows/rest_node.png)

## Installation

To install ComfyUI-RequestNodes, follow these steps:

1.  **Open the ComfyUI custom_nodes directory.**
    *   In your ComfyUI installation directory, find the `custom_nodes` folder.

2.  **Clone the ComfyUI-RequestNodes repository.**
    *   Open a terminal or command prompt in the `custom_nodes` directory.
    *   Run the following command to clone the repository:

    ```bash
    git clone https://github.com/ahkimkoo/ComfyUI-HttpRequestNodes.git
    ```

3.  **Install dependencies.**
    *   The extended nodes require `soundfile` and `imageio` for audio/video encoding. Install them in your ComfyUI Python environment:

    ```bash
    pip install soundfile imageio imageio-ffmpeg
    ```

4.  **Restart ComfyUI.**
    *   Close and restart ComfyUI to load the newly installed nodes.

## Usage

After installation, you can find the nodes under the "RequestNode" category in the ComfyUI node list, with subcategories like "Get Request", "Post Request", "REST API", "Converters", and "Utils".

*   **Get Request Node**:
    *   **Category**: RequestNode/Get Request
    *   **Inputs**:
        *   `target_url` (STRING, required): The URL to send the GET request to.
        *   `headers` (KEY_VALUE, optional): Request headers, typically from a Key/Value Node.
        *   `query_list` (KEY_VALUE, optional): Query parameters, typically from a Key/Value Node.
    *   **Outputs**:
        *   `text` (STRING): The response body as text.
        *   `file` (BYTES): The response body as bytes.
        *   `json` (JSON): The response body parsed as JSON (if valid).
        *   `any` (ANY): The raw response content.
    *   ![image](https://github.com/user-attachments/assets/cdb1938f-f8a9-4a4b-a787-90fa4d543523)

*   **Post Request Node**:
    *   **Category**: RequestNode/Post Request
    *   **Inputs**:
        *   `target_url` (STRING, required): The URL to send the POST request to.
        *   `request_body` (STRING, required, multiline): The request body, typically in JSON format. Placeholders like `__str0__`, `__str1__`, ..., `__str9__` can be used and will be replaced by the corresponding optional string inputs.
        *   `headers` (KEY_VALUE, optional): Request headers, typically from a Key/Value Node.
        *   `str0` to `str9` (STRING, optional): String inputs to replace placeholders in `request_body`.
    *   **Outputs**:
        *   `text` (STRING): The response body as text.
        *   `file` (BYTES): The response body as bytes.
        *   `json` (JSON): The response body parsed as JSON (if valid).
        *   `any` (ANY): The raw response content.
    *   ![image](https://github.com/user-attachments/assets/6eda9fef-48cf-478c-875e-6bd6d850bff2)

*   **Form Post Request Node**:
    *   **Category**: RequestNode/Post Request
    *   **Inputs**:
        *   `target_url` (STRING, required): The URL to send the POST request to.
        *   `image` (IMAGE, required): The image or image batch to upload. If an image batch is provided, all images will be sent in the same request.
        *   `image_field_name` (STRING, required): The field name for the image in the form.
        *   `form_fields` (KEY_VALUE, optional): Other form fields, typically from a Key/Value Node.
        *   `headers` (KEY_VALUE, optional): Request headers, typically from a Key/Value Node.
    *   **Outputs**:
        *   `text` (STRING): The response body as text.
        *   `json` (JSON): The response body parsed as JSON (if valid).
        *   `any` (ANY): The raw response content.

*   **Image to Base64 Node**:
    *   **Category**: RequestNode/Converters
    *   **Inputs**:
        *   `image` (IMAGE, required): The image to convert.
    *   **Outputs**:
        *   `STRING`: The Base64 encoded image string.

*   **Image to Blob Node**:
    *   **Category**: RequestNode/Converters
    *   **Inputs**:
        *   `image` (IMAGE, required): The image to convert.
    *   **Outputs**:
        *   `BYTES`: The raw binary data of the image.

*   **Rest Api Node**:
    *   **Category**: RequestNode/REST API
    *   **Inputs**:
        *   `target_url` (STRING, required): The URL for the request.
        *   `method` (Dropdown, required): The HTTP method to use (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS).
        *   `request_body` (STRING, required, multiline): The request body (hidden for HEAD, OPTIONS, DELETE methods).
        *   `headers` (KEY_VALUE, optional): Request headers, typically from a Key/Value Node.
        *   `RETRY_SETTING` (RETRY_SETTING, optional): Retry settings, typically from a Retry Settings Node.
    *   **Outputs**:
        *   `text` (STRING): The response body as text.
        *   `file` (BYTES): The response body as bytes.
        *   `json` (JSON): The response body parsed as JSON (if valid). For HEAD requests, this output contains the response headers.
        *   `headers` (DICT): The response headers as a dictionary.
        *   `status_code` (INT): The HTTP status code of the response.
        *   `any` (ANY): The raw response content.

*   **Key/Value Node**:
    *   **Category**: RequestNode/KeyValue
    *   **Inputs**:
        *   `key` (STRING, required): The key name.
        *   `value` (STRING, required): The key value.
        *   `KEY_VALUE` (KEY_VALUE, optional): Connect output from other Key/Value Nodes to merge pairs.
    *   **Outputs**:
        *   `KEY_VALUE` (KEY_VALUE): A dictionary containing the key/value pair(s).
    *   ![image](https://github.com/user-attachments/assets/dfe7dab0-2b1b-4f99-ac6f-89e01d03b7e0)

*   **Chain Image Node**:
    *   **Category**: RequestNode/Utils
    *   **Description**: This node allows you to upload an image and add it to an image batch. You can chain multiple nodes of this type together to create a batch of several images. If you upload images with different dimensions, this node will automatically resize subsequent images to match the dimensions of the first one in the batch.
    *   **Inputs**:
        *   `image` (IMAGE, required): The image to upload. Use the "choose file to upload" button.
        *   `image_batch_in` (IMAGE, optional): An existing image batch to append the newly uploaded image to. This can be connected from another `Chain Image Node` to build a batch.
    *   **Outputs**:
        *   `image_batch_out` (IMAGE): The combined image batch.
    *   **Example**:
    *   ![image](workflows/chainable_upload_image_node.png)

*   **String Replace Node**:
    *   **Category**: RequestNode/Utils
    *   **Inputs**:
        *   `input_string` (STRING, required, multiline): The string containing placeholders to be replaced.
        *   `placeholders` (KEY_VALUE, optional): Key/Value pairs where keys are placeholders (e.g., `__my_placeholder__`) and values are the replacement strings.
    *   **Outputs**:
        *   `output_string` (STRING): The string with placeholders replaced.

*   **Retry Settings Node**:
    *   **Category**: RequestNode/KeyValue
    *   **Inputs**:
        *   `key` (Dropdown, required): The retry setting key (`max_retry`, `retry_interval`, `retry_until_status_code`, `retry_until_not_status_code`).
        *   `value` (INT, required): The integer value for the retry setting.
        *   `RETRY_SETTING` (RETRY_SETTING, optional): Connect output from other Retry Settings Nodes to merge settings.
    *   **Outputs**:
        *   `RETRY_SETTING` (RETRY_SETTING): A dictionary containing the retry setting(s).

    **Retry Logic Explanation:**

    The `Retry Settings Node` allows you to configure automatic retries for the `Rest Api Node` when specific conditions are met. The retry logic works as follows:

    *   **`max_retry`**: Defines the maximum number of times to retry the request after the initial attempt fails. For example, `max_retry: 3` means a total of 1 (initial) + 3 (retries) = 4 attempts. If set to 0 *and* specific status code conditions are defined, it will retry indefinitely. If no retry settings are provided, the default is no retries. If the `RETRY_SETTING` input is connected but `max_retry` is not explicitly set, it defaults to 3 retries.
    *   **`retry_interval`**: Specifies the delay in milliseconds between retry attempts (default is 1000ms).
    *   **`retry_until_status_code`**: The node will keep retrying *as long as* the HTTP status code received is *not* equal to this value (and `max_retry` limit is not reached). Useful for waiting for a specific success code (e.g., 200).
    *   **`retry_until_not_status_code`**: The node will keep retrying *as long as* the HTTP status code received *is* equal to this value (and `max_retry` limit is not reached). Useful for retrying on specific temporary error codes (e.g., retrying while status is 202 Accepted).
    *   **Default Retry Condition (Non-2xx):** If `max_retry` is set (or defaults to 3) but *neither* `retry_until_status_code` nor `retry_until_not_status_code` are specified, the node will retry *only if* the status code is *not* in the 200-299 range (i.e., a non-successful response).
    *   **Exceptions:** Any network or request exception will also trigger a retry attempt, respecting the `max_retry` limit and `retry_interval`.
    *   **Priority:** If both `retry_until_status_code` and `retry_until_not_status_code` are set, both conditions must be met (or not met, respectively) to stop retrying based on status code. The default non-2xx condition is only checked if specific status code conditions are *not* set.


## Contribution

Welcome to submit issues and pull requests to improve ComfyUI-RequestNodes!

---

**Note:**

*   Please ensure that your ComfyUI environment has Git installed correctly.
*   If your ComfyUI installation directory is not in the default location, please adjust the path according to your actual situation.
*   If you encounter any problems, please check the issue page of the GitHub repository or submit a new issue.
