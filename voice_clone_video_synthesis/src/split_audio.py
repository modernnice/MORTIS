from pathlib import Path
import pandas as pd
import torchaudio
from loguru import logger
from src import _time_to_seconds


def splitter(audio_path: str | Path, structure_path: str | Path, tmp_dir: str | Path):
    if isinstance(audio_path, str):
        audio_path = Path(audio_path)
    if isinstance(structure_path, str):
        structure_path = Path(structure_path)
    if isinstance(tmp_dir, str):
        tmp_dir = Path(tmp_dir)
    # 读取音频与采样率
    audio, sr = torchaudio.load(audio_path)

    # 输出目录
    audio_dir = tmp_dir / "original"
    audio_dir.mkdir(parents=True, exist_ok=True)

    # 读取切分结构
    structure = pd.read_json(structure_path)
    ids = []

    for i, row in structure.iterrows():
        start_sec = _time_to_seconds(row["start_time"])
        end_sec = _time_to_seconds(row["end_time"])
        start_sample = int(start_sec * sr)
        end_sample = int(end_sec * sr)
        segment = audio[:, start_sample:end_sample]
        seg_name = f"{i:04d}.wav"

        output_path = audio_dir / seg_name
        torchaudio.save(output_path, segment, sr)
        ids.append(seg_name)

        logger.info(
            "Saved segment {}: {} - {} -> {}",
            i,
            start_sec,
            end_sec,
            output_path,
        )
    structure["id"] = ids
    structure.to_json(
        tmp_dir / "structure.json", orient="records", force_ascii=False, indent=2
    )
