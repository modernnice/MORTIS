import ffmpeg
from pathlib import Path
import pandas as pd
from src import _time_to_seconds, __seconds_to_str

from loguru import logger


def convert_path(path: str | Path):
    if isinstance(path, str):
        return Path(path)
    return path


def voice_background_mixer(
    voice_structure_path: str | Path,
    background_path: str | Path,
    output_path: str | Path,
):
    voice_structure_path = convert_path(voice_structure_path)
    background_path = convert_path(background_path)
    output_path = convert_path(output_path)

    # 读取声音片段结构
    voice_structure = pd.read_json(voice_structure_path)

    # 创建音频混合的列表
    mixed_audio_parts = []
    tmp_path = voice_structure_path.parent / "tmp"
    tmp_path.mkdir(parents=True, exist_ok=True)
    # 处理每一行的音频片段
    logger.info("mixing")
    last_end = 0
    last_i = None
    for i, row in voice_structure.iterrows():
        start = row["start_time"]
        end = row["end_time"]

        # 将pandas Timestamp转换为秒
        start_seconds = _time_to_seconds(start)
        end_seconds = _time_to_seconds(end)
        # 连接无声片段
        if start_seconds > last_end:
            logger.info(
                "[{}:{}] bridge {}-{}",
                __seconds_to_str(last_end),
                __seconds_to_str(start_seconds),
                last_i,
                i,
            )
            silence_clip = ffmpeg.input(
                str(background_path), ss=last_end, to=start_seconds
            )
            temp_output = tmp_path / f"temp_output_{last_i}_{i}.wav"
            ffmpeg.run(
                silence_clip.output(str(temp_output)),
                quiet=True,
                overwrite_output=True,
            )
            mixed_audio_parts.append(temp_output)

        # 提取背景片段
        background_clip = ffmpeg.input(
            str(background_path), ss=start_seconds, to=end_seconds
        )

        # 提取语音片段
        voice_path = voice_structure_path.parent / "translated" / row["id"]
        voice_clip = ffmpeg.input(str(voice_path))

        # 处理语音时长
        voice_duration = float(ffmpeg.probe(str(voice_path))["format"]["duration"])
        target_duration = end_seconds - start_seconds
        speed = voice_duration / target_duration
        filters = []
        while speed < 0.5 or speed > 2:
            if speed > 2:
                filters.append(("atempo", 2.0))
                speed /= 2
            else:
                filters.append(("atempo", 0.5))
                speed /= 0.5
        filters.append(("atempo", speed))
        for f, v in filters:
            voice_clip = voice_clip.filter(f, v)

        # 合并语音和背景
        mixed_audio = ffmpeg.filter(
            [background_clip, voice_clip],
            "amix",
            inputs=2,
            duration="longest",
        )

        # 输出到临时文件

        logger.info(
            "[{}:{}] mixing segment {}",
            __seconds_to_str(start_seconds),
            __seconds_to_str(end_seconds),
            i,
        )
        temp_output = tmp_path / f"temp_output_{i}.wav"
        ffmpeg.run(
            mixed_audio.output(str(temp_output)), quiet=True, overwrite_output=True
        )
        # 添加到混合片段列表
        mixed_audio_parts.append(temp_output)

        last_end = end_seconds
        last_i = i

    # 补齐尾部
    total = float(ffmpeg.probe(str(background_path))["format"]["duration"])
    if last_end < total:
        logger.info(
            "[{}:{}] bridge {}-{}",
            __seconds_to_str(last_end),
            __seconds_to_str(total),
            last_i,
            "tail",
        )
        silence_clip = ffmpeg.input(str(background_path), ss=last_end, to=total)
        temp_output = tmp_path / f"temp_output_{last_i}_tail.wav"
        ffmpeg.run(
            silence_clip.output(str(temp_output)),
            quiet=True,
            overwrite_output=True,
        )
        mixed_audio_parts.append(temp_output)
    # 使用FFmpeg合并所有生成的临时文件
    inputs = [ffmpeg.input(file) for file in mixed_audio_parts]
    logger.info("concating")
    for path in mixed_audio_parts:
        logger.debug("concat {}", str(path.stem))
    ffmpeg.run(
        ffmpeg.concat(*inputs, v=0, a=1).output(str(output_path)),
        quiet=True,
        overwrite_output=True,
    )
    return mixed_audio_parts
