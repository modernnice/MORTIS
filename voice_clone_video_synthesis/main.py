from huggingface_hub import constants
import sys
from loguru import logger
import warnings
import shutil
import time
from pathlib import Path
import argparse

warnings.filterwarnings("ignore")
logger.remove()
logger.add(sys.stderr, level="INFO")
constants.HF_HUB_CACHE


def tts2(cfg_path: str, model_dir: str, tmp_dir: str):
    from indextts.infer_v2 import IndexTTS2
    from src.voice_clone import get_tasks

    logger.info("loading tts2...")
    agent = IndexTTS2(
        cfg_path,
        model_dir,
        use_fp16=False,
        use_cuda_kernel=False,
        use_deepspeed=False,
    )
    tasks = get_tasks(tmp_dir)
    total = len(tasks)
    for task in tasks:
        id = task.pop("id")
        t0 = time.time()
        agent.infer(**task)
        t1 = time.time()
        logger.info(
            '[{}/{}] "{}" Using {:.3f} seconds', id + 1, total, task["text"], t1 - t0
        )


def cli(
    cleaned_voice: str,
    subtitle_structure: str,
    background_sound: str,
    output: str,
    tmp_dir: str,
    cfg_path: str = "/checkpoints/config.yaml",  
    model_dir: str = "/checkpoints",  
):
    from src.split_audio import splitter
    from src.mixer import voice_background_mixer
    def remove_check():
        logger.info("Do you want to remove tmp files? [y/n]")
        remove = input()
        if remove.lower() == "y":
            shutil.rmtree(tmp_dir)
            logger.info("removed")
    try:
        splitter(cleaned_voice, subtitle_structure, tmp_dir)
        tts2(cfg_path, model_dir, tmp_dir)
        tmp_dir_path = Path(tmp_dir)
        voice_background_mixer(
            tmp_dir_path / "structure.json", background_sound, output
        )
        logger.info("finish")
        remove_check()
    except KeyboardInterrupt:
        logger.info("interrupted, removing tmp files...")
        remove_check()
    except Exception as e:
        logger.error(e)
        remove_check()


def main():
    parser = argparse.ArgumentParser(
        description="Process voice and subtitles with background sound."
    )

    # 添加带有缩写的命令行参数
    parser.add_argument(
        "-v",
        "--cleaned_voice",
        type=str,
        required=True,
        help="Path to the cleaned voice file",
    )
    parser.add_argument(
        "-s",
        "--subtitle_structure",
        type=str,
        required=True,
        help="Path to the subtitle structure file",
    )
    parser.add_argument(
        "-b",
        "--background_sound",
        type=str,
        required=True,
        help="Path to the background sound file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Path where the output should be saved",
    )
    parser.add_argument(
        "-t",
        "--tmp_dir",
        type=str,
        required=True,
        help="Temporary directory for processing",
    )

    # 可选参数，使用默认值
    parser.add_argument(
        "-c",
        "--cfg_path",
        type=str,
        help="Path to the config file",
    )
    parser.add_argument(
        "-m",
        "--model_dir",
        type=str,
        help="Path to the model directory",
    )

    # 解析命令行参数
    args = parser.parse_args()

    # 调用函数并传入命令行参数
    cli(
        cleaned_voice=args.cleaned_voice,
        subtitle_structure=args.subtitle_structure,
        background_sound=args.background_sound,
        output=args.output,
        tmp_dir=args.tmp_dir,
        cfg_path=args.cfg_path,
        model_dir=args.model_dir,
    )


if __name__ == "__main__":
    main()
