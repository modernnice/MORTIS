from audio_separator.separator import Separator
from loguru import logger
import os
import shutil
from config.settings import MODEL_DIR
class VoiceFilter:
    VOCAL_KEYWORDS = ("vocals", "vocal", "voice", "voices", "soprano", "lead")
    BACKGROUND_KEYWORDS = ("accompaniment", "accomp", "background", "inst", "instrumental", "music")
    def __init__(self):
        self.separator = Separator(model_file_dir=MODEL_DIR)
        self.model_loaded = False
    def filt(self, mixed_audio_in, vocal_audio_out, background_audio_out):
        separated_audios = self._separate(mixed_audio_in)
        vocals_src, background_src = self._resolve_audio(separated_audios)
        self._move_and_rename(vocals_src, vocal_audio_out)
        self._move_and_rename(background_src, background_audio_out)
        logger.info("done")
    def _ensure_model_loaded(self):
        if not self.model_loaded:
            logger.info("loading model")
            self.separator.load_model()
            self.model_loaded = True
    def _separate(self, audio_file_path):
        self._ensure_model_loaded()
        logger.info("separating")
        separated_audios = self.separator.separate(audio_file_path)
        return separated_audios
    def _resolve_audio(self, separated_audios):
        separated_paths = self._flatten_paths(separated_audios)
        vocals_src = self._find_file_by_keywords(separated_paths, self.VOCAL_KEYWORDS)
        background_src = self._find_file_by_keywords(separated_paths, self.BACKGROUND_KEYWORDS)

        if background_src is None and vocals_src is not None:
            others = [p for p in separated_paths if p != vocals_src]
            if others:
                background_src = others[0]

        if vocals_src is None and separated_paths:
            vocals_src = separated_paths[0]
        return vocals_src, background_src
    def _find_file_by_keywords(self, paths, keywords):
        """从字符串路径列表里通过关键词匹配找到最可能的文件（返回第一个匹配）"""
        if not paths:
            return None
        for p in paths:
            lower = os.path.basename(p).lower()
            for kw in keywords:
                if kw in lower:
                    return p
        return None
    def _move_and_rename(self, src, dst):
        """把 src 移动到 dst（保证目标目录存在，覆盖已存在文件）"""
        if src is None:
            return None
        src = str(src)
        dst = str(dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            os.remove(dst)
        shutil.move(src, dst)
        return dst
    def _flatten_paths(self, items):
        """把可能的嵌套结构扁平化，只保留字符串路径"""
        flattened = []
        if items is None:
            return flattened
        if isinstance(items, dict):
            items = list(items.values())
        stack = [items]
        while stack:
            cur = stack.pop()
            if cur is None:
                continue
            if isinstance(cur, (list, tuple, set)):
                for elem in cur:
                    stack.append(elem)
            else:
                if isinstance(cur, (str, bytes)) or hasattr(cur, "__fspath__"):
                    flattened.append(str(cur))
                else:
                    continue
        seen = set()
        res = []
        for p in flattened:
            if p not in seen:
                seen.add(p)
                res.append(p)
        return res
    