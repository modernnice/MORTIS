import ffmpeg
from config.settings import FFMPEG_SETTINGS,LOG_LEVEL
from loguru import logger
def splitter(video_path:str, video_output:str, audio_mixed:str):
    logger.info("FFMPEG settings:")
    for k,v in FFMPEG_SETTINGS.items():
        logger.info(f"{k}: {v}")
    logger.info("Cleaning video...")
    if LOG_LEVEL == "DEBUG":
        quiet = False
    else:
        quiet = True
        
    (
        ffmpeg
        .input(video_path)
        .output(video_output, vcodec=FFMPEG_SETTINGS["video_codec"],
                an=None, crf=FFMPEG_SETTINGS["video_quality"])
        .overwrite_output()
        .run(quiet=quiet)
    )
    logger.info("Extracting audio...")
    (
        ffmpeg
        .input(video_path)
        .output(audio_mixed, acodec="pcm_s16le", ac=1, ar=16000)
        .overwrite_output()
        .run(quiet=quiet)
    )
    logger.info("Video split successfully")