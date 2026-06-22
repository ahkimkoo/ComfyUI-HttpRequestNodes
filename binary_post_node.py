import requests
import json
import io


class BinaryPostRequestNode:
    """Send raw binary data via HTTP POST/PUT/PATCH.

    Content-Type defaults to application/octet-stream.
    Designed for sending audio/video blobs to REST APIs.
    Accepts BYTES input (from AudioToBlob, VideoToBlob, ImageToBlob nodes).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "target_url": ("STRING", {"default": "http://127.0.0.1:8000/rvc/default"}),
                "body": ("BYTES",),
            },
            "optional": {
                "method": (["POST", "PUT", "PATCH"], {"default": "POST"}),
                "content_type": ("STRING", {"default": "application/octet-stream"}),
                "headers": ("KEY_VALUE", {"default": None}),
                "RETRY_SETTING": ("RETRY_SETTING", {"default": None}),
            },
        }

    RETURN_TYPES = ("STRING", "BYTES", "JSON", "INT", "DICT")
    RETURN_NAMES = ("text", "response_bytes", "json", "status_code", "response_headers")
    FUNCTION = "send_request"
    OUTPUT_NODE = True
    CATEGORY = "RequestNode/REST API"

    def send_request(self, target_url, body, method="POST", content_type="application/octet-stream",
                     headers=None, RETRY_SETTING=None):
        # Build headers
        request_headers = {"Content-Type": content_type}
        if headers:
            request_headers.update(headers)

        # Retry settings
        max_retry = 3
        retry_interval = 1000
        if RETRY_SETTING is not None:
            max_retry = RETRY_SETTING.get("max_retry", 3)
            retry_interval = RETRY_SETTING.get("retry_interval", 1000)

        # Ensure body is bytes
        if isinstance(body, io.BytesIO):
            body_bytes = body.getvalue()
        elif isinstance(body, (bytes, bytearray)):
            body_bytes = bytes(body)
        else:
            body_bytes = str(body).encode("utf-8")

        method_fn = {
            "POST": requests.post,
            "PUT": requests.put,
            "PATCH": requests.patch,
        }[method]

        last_err = None
        for attempt in range(max_retry + 1):
            try:
                resp = method_fn(
                    target_url,
                    data=body_bytes,
                    headers=request_headers,
                    timeout=300,
                    proxies={"http": None, "https": None},
                )
                resp_headers = dict(resp.headers)
                try:
                    resp_json = resp.json()
                except (json.JSONDecodeError, ValueError):
                    resp_json = {"raw": resp.text[:2000]}
                return (resp.text, resp.content, resp_json, resp.status_code, resp_headers)
            except Exception as e:
                last_err = e
                if attempt < max_retry:
                    import time
                    time.sleep(retry_interval / 1000.0)

        # All retries failed
        err_msg = str(last_err)
        return (err_msg, b"", {"error": err_msg}, 0, {})


NODE_CLASS_MAPPINGS = {
    "BinaryPostRequestNode": BinaryPostRequestNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BinaryPostRequestNode": "Binary POST Request",
}
