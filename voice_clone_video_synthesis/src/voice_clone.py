from pathlib import Path
import pandas as pd
from loguru import logger

emo_vector_keys = ["高兴", "愤怒", "悲伤", "害怕", "厌恶", "忧郁", "惊讶", "平静"]
emo_vector_dict = {k: 0.0 for k in emo_vector_keys}


def get_tasks(data_dir: str | Path) -> list[dict]:
    if isinstance(data_dir, str):
        data_dir = Path(data_dir)

    structure = pd.read_json(data_dir / "structure.json")
    output_dir = data_dir / "translated"
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks_def = []
    for i, row in structure.iterrows():
        spk_audio_prompt: Path = data_dir / "original" / row["id"]
        text = row["dialogue_content"]
        output_path: Path = output_dir / row["id"]
        emo_audio_prompt = spk_audio_prompt
        task = {
            "id": i,
            "spk_audio_prompt": spk_audio_prompt,
            "text": text,
            "output_path": output_path,
            "verbose": False,
            "emo_audio_prompt": emo_audio_prompt,
        }

        emo_vector = emo_vector_dict.copy()
        if row["emotion_label"] not in emo_vector_keys:
            emo_vector = None
            logger.warning(
                "Invalid emotion label: {}, content: {}", row["emotion_label"], text
            )
            logger.warning("Infer without emo vector")
        else:
            emo_vector[row["emotion_label"]] = (row["emotion_intensity"] - 1) / 4
            emo_vector = list(emo_vector.values())
            task["emo_vector"] = emo_vector
        logger.debug("emo_vector: {}", emo_vector)
        tasks_def.append(task)
    logger.info("=======Total tasks: {}=======", len(tasks_def))
    return tasks_def
