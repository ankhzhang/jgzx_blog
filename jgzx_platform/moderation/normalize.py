"""文本归一化：降低空格、符号等简单绕过手段的影响。"""
import re
import unicodedata

# 常见谐音/变体替换（可按需扩展）
_HOMOPHONE_MAP = str.maketrans({
    '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
    '５': '5', '６': '6', '７': '7', '８': '8', '９': '9',
    'Ａ': 'a', 'Ｂ': 'b', 'Ｃ': 'c', 'Ｄ': 'd', 'Ｅ': 'e',
    'Ｆ': 'f', 'Ｇ': 'g', 'Ｈ': 'h', 'Ｉ': 'i', 'Ｊ': 'j',
    'Ｋ': 'k', 'Ｌ': 'l', 'Ｍ': 'm', 'Ｎ': 'n', 'Ｏ': 'o',
    'Ｐ': 'p', 'Ｑ': 'q', 'Ｒ': 'r', 'Ｓ': 's', 'Ｔ': 't',
    'Ｕ': 'u', 'Ｖ': 'v', 'Ｗ': 'w', 'Ｘ': 'x', 'Ｙ': 'y', 'Ｚ': 'z',
})


def normalize_text(text: str) -> str:
    """检测前统一文本格式。"""
    if not text:
        return ''
    text = unicodedata.normalize('NFKC', text)
    text = text.translate(_HOMOPHONE_MAP)
    text = text.lower()
    text = re.sub(r'[\u200b-\u200d\ufeff]', '', text)
    # 去除常见插入符号（如 色*情、杀_人）
    text = re.sub(r'[\s\*\.·•\-_~|/\\@#]+', '', text)
    return text
