def hasKanji(word: str) -> bool:
    if not isinstance(word, str):
        return False
    return any('\u4e00' <= ch <= '\u9fff' for ch in word)
