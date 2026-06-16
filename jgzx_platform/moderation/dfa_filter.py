"""基于 DFA（确定有限状态自动机）的敏感词检测。"""
from pathlib import Path

from .normalize import normalize_text

_END = '__end__'

# 仅加载与黄、赌、毒、暴力、政治相关的分类词库，不加载零时-Tencent 等大文件
CURATED_LEXICON_FILES = (
    '色情词库.txt',   # 黄
    '色情类型.txt',
    '涉枪涉爆.txt',   # 暴力
    '反动词库.txt',   # 政治
    '政治类型.txt',
)

# 最短匹配长度：2 字词误伤率高（如「手机」「温馨」），统一要求 3 字及以上
MIN_WORD_LENGTH = 3

# 开源词库中过于宽泛的单独词条（正常学术讨论也可能出现），改由短语级词条在 sensitive_words 中拦截
LEXICON_SKIP_WORDS = frozenset({'共产党', 'gc党'})


class DFAFilter:
    def __init__(self):
        self._root: dict = {}

    def add_word(self, word: str, *, min_length: int = MIN_WORD_LENGTH) -> None:
        word = normalize_text(word)
        if not word or len(word) < min_length:
            return
        node = self._root
        for ch in word:
            node = node.setdefault(ch, {})
        node[_END] = True

    def load_file(
        self,
        path: Path,
        *,
        min_length: int = MIN_WORD_LENGTH,
        skip_words: frozenset[str] | None = None,
    ) -> int:
        if not path.is_file():
            return 0
        count = 0
        with path.open(encoding='utf-8', errors='ignore') as fp:
            for line in fp:
                word = line.strip()
                if not word or word.startswith('#'):
                    continue
                normalized = normalize_text(word)
                if not normalized or len(normalized) < min_length:
                    continue
                if skip_words and normalized in skip_words:
                    continue
                self.add_word(word, min_length=min_length)
                count += 1
        return count

    def load_curated_lexicon(self, dir_path: Path) -> int:
        if not dir_path.is_dir():
            return 0
        count = 0
        for name in CURATED_LEXICON_FILES:
            count += self.load_file(
                dir_path / name,
                skip_words=LEXICON_SKIP_WORDS,
            )
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
        # 自定义词库：明确列举的赌/毒等词条，允许 2 字
        _filter.load_file(base_dir / 'sensitive_words.txt', min_length=2)
        # 开源分类词库：3 字起，降低日常用语误伤
        _filter.load_curated_lexicon(base_dir / 'lexicon')
    return _filter
