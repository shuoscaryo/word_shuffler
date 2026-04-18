def word_from_row(row: tuple, plural: bool = False) -> str:
    """
    Creates the word from the row with the article if exists. The plural option
    generates the plural version "die + row.Plural". If Word or Plural columns
    are empty in each case, it returns empty string.

    Args:
    - row: Pandas row from itertuples() function.
    - plural: Flag to select plural (true) or normal (false) versions.

    Returns:
    - str: Word with the article if exists.

    Raises:
    None
    """
    # Get article and word
    if plural == False:
        article = row.Article if isinstance(row.Article, str) else ""
        word = row.Word
    else:
        article = "die"
        word = row.Plural
    # Check for empty word
    if not isinstance(word, str) or len(word) == 0:
        return ""
    return f"{article} {word}".strip()
