

from .get_node import GetRequestNode
from .post_node import PostRequestNode
from .key_value_node import KeyValueNode
from .rest_api_node import RestApiNode
from .string_replace_node import StringReplaceNode
from .retry_setting_node import RetrySettingNode
from .form_post_node import FormPostRequestNode
from .image_to_base64_node import ImageToBase64Node
from .image_to_blob_node import ImageToBlobNode
from .image_list_combiner_node import ChainableUploadImage
from .audio_to_blob_node import AudioToBlobNode
from .video_to_blob_node import VideoToBlobNode
from .binary_post_node import BinaryPostRequestNode
from .media_form_post_node import MediaFormPostNode
from .blob_to_image_node import BlobToImageNode
from .blob_to_audio_node import BlobToAudioNode
from .blob_to_video_node import BlobToVideoNode
from .blob_to_batch_image_node import BlobToBatchImageNode



NODE_CLASS_MAPPINGS = {
    "Get Request Node": GetRequestNode,
    "Post Request Node": PostRequestNode,
    "Form Post Request Node": FormPostRequestNode,
    "Rest Api Node": RestApiNode,
    "Key/Value Node": KeyValueNode,
    "String Replace Node": StringReplaceNode,
    "Retry Settings Node": RetrySettingNode,
    "Image To Base64 Node": ImageToBase64Node,
    "Image To Blob Node": ImageToBlobNode,
    "Chainable Upload Image": ChainableUploadImage,
    "Audio To Blob Node": AudioToBlobNode,
    "Video To Blob Node": VideoToBlobNode,
    "Binary Post Request Node": BinaryPostRequestNode,
    "Media Form Post Node": MediaFormPostNode,
    "Blob To Image Node": BlobToImageNode,
    "Blob To Audio Node": BlobToAudioNode,
    "Blob To Video Node": BlobToVideoNode,
    "Blob To Batch Image Node": BlobToBatchImageNode,
}
