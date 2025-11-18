import sys
from src.voice_filter import VoiceFilter
from src.video_audio_split import splitter
from loguru import logger
import argparse
from config.settings import LOG_LEVEL
logger.remove()
logger.add(sys.stdout ,level=LOG_LEVEL)
logger.info("log level: {}",LOG_LEVEL)
def main():
    parser = argparse.ArgumentParser(description='Separate vocals and background from a mixed audio file.')
    parser.add_argument('--video_path', help='Path to the video file.')
    parser.add_argument('--video_output', help='Path to the output video file.')
    parser.add_argument('--audio_mixed', help='Path to the mixed audio file.')
    parser.add_argument('--vocal', help='Path to the output vocal audio file.')
    parser.add_argument('--background', help='Path to the output background audio file.')
    args = parser.parse_args()
    cli(args.video_path, args.video_output, args.audio_mixed, args.vocal, args.background)

def cli(video_path, video_output, audio_mixed, vocal, background):
    splitter(video_path, video_output, audio_mixed)
    VoiceFilter().filt(audio_mixed, vocal, background)


if __name__ == "__main__":
    main()
