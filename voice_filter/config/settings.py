import os
from typing import Literal, Union
default_ffmpeg_settings = {
    "video_codec": "libx264",
    "audio_codec": "aac",
    "audio_bitrate": "128k",
    "video_quality": "23"  # CRF值，越小质量越好
}

video_codec = os.environ.get("VIDEO_CODEC", default_ffmpeg_settings["video_codec"])
audio_codec = os.environ.get("AUDIO_CODEC", default_ffmpeg_settings["audio_codec"])
audio_bitrate = os.environ.get("AUDIO_BITRATE", default_ffmpeg_settings["audio_bitrate"])
video_quality = os.environ.get("VIDEO_QUALITY", default_ffmpeg_settings["video_quality"])

FFMPEG_SETTINGS = {
    "video_codec": video_codec,
    "audio_codec": audio_codec,
    "audio_bitrate": audio_bitrate,
    "video_quality": video_quality
}


LOG_LEVEL: Union[Literal["INFO", "DEBUG"], str] = os.environ.get("LOG_LEVEL", "INFO")

if LOG_LEVEL not in ["INFO", "DEBUG"]:
    LOG_LEVEL = "INFO"

MODEL_DIR = os.environ.get("MODEL_DIR", "./data/audio-separator-models/")