"""基于 DFA（确定有限状态自动机）的敏感词检测。"""
from pathlib import Path

from .normalize import normalize_text

_END = '__end__'


class DFAFilter:
    def __init__(self):
        self._root: dict = {}

    def add_word(self, word: str, *, min_length: int = 2) -> None:
        word = normalize_text(word)
        if not word or len(word) < min_length:
            return
        node = self._root
        for ch in word:
            node = node.setdefault(ch, {})
        node[_END] = True

    def load_file(self, path: Path) -> int:
        if not path.is_file():
            return 0
        count = 0
        with path.open(encoding='utf-8', errors='ignore') as fp:
            for line in fp:
                word = line.strip()
                if not word or word.startswith('#'):
                    continue
                normalized = normalize_text(word)
                if not normalized or len(normalized) < 2:
                    continue
                self.add_word(word)
                count += 1
        return count

    def load_directory(self, dir_path: Path) -> int:
        if not dir_path.is_dir():
            return 0
        count = 0
        for path in sorted(dir_path.glob('*.txt')):
            count += self.load_file(path)
        return count

    def contains(self, text: str) -> bool:
        normalized = normalize_text(text)
        if not normalized:
            return False
        length = len(normalized)
        for start in range(length):
            node = self._root
            for i in range(start, length):
                ch = normalized[i]
                if ch not in node:
                    break
                node = node[ch]
                if _END in node:
                    return True
        return False


_filter: DFAFilter | None = None


def get_dfa_filter() -> DFAFilter:
    global _filter
    if _filter is None:
        base_dir = Path(__file__).resolve().parent
        _filter = DFAFilter()
        _filter.load_file(base_dir / 'sensitive_words.txt')
        _filter.load_directory(base_dir / 'lexicon')
    return _filter
