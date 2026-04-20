import pandas as pd
import argparse
from my_logger import logger

def _hasKanji(word: str) -> bool:
    if not isinstance(word, str):
        return False
    return any('\u4e00' <= ch <= '\u9fff' for ch in word)


def kanji(
    df: pd.DataFrame,
    args: argparse.Namespace
) -> list[tuple[str, str]]:
    """
    Generates a list containing a pair "Test" and "Expected".
    "Test" is the prompt that will be shown.
    "Expected" is the expected answer for each prompt.

    Args:
    - df: Dataframe from where the words will be sampled
    - args: input arguments of the program

    Returns:
    - list[tuple[str,str]]: List containing "Test" "Expected" pairs.

    Raises:
    None
    """
    output_list = []

    mask = df["Word"].apply(_hasKanji)
    filtered_df = df[mask]

    for row in filtered_df.itertuples():
        test = row.Word
        expected = f"{row.Translation} ({row.Reading})"
        output_list.append((test, expected))

    return output_list
