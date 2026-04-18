import pandas as pd
import argparse
from . import utils

def plural(
    df: pd.DataFrame,
    args: argparse.Namespace
) -> list[tuple[str, str]]:
    """
    Generates a list containing a pair "Test" and "Expected".
    "Test" are singular german nouns.
    "Expected" are plural german nouns.
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
    sample = df[df["Category"] == "noun"]

    output_list = []
    for row in sample.itertuples():
        test = utils.word_from_row(row, plural = False)
        expected = utils.word_from_row(row, plural = True)
        if len(expected) == 0:
            continue
        expected = f"{expected} ({row.Translation})"
        output_list.append((test, expected))
    return output_list
