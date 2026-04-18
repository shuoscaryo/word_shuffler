import pandas as pd
import argparse
from . import utils

def article(
    df: pd.DataFrame,
    args: argparse.Namespace
) -> list[tuple[str, str]]:
    """
    Generates a list containing a pair "Test" and "Expected".
    "Test" are singular german nouns without article.
    "Expected" are the nouns with the article.
    The length of the list is args.test_length.

    Args:
    - df: Dataframe from where the words will be sampled
    - args: input arguments of the program

    Returns:
    - list[tuple[str,str]]: List containing "Test" "Expected" pairs.

    Raises:
    None
    """
    # filter only nouns
    df = df[df["Category"] == "noun"]

    output_list = []
    for row in df.itertuples():
        test = row.Word
        expected = utils.word_from_row(row, plural = False)
        output_list.append((test, expected))
    return output_list
