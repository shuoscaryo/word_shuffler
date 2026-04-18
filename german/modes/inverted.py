import pandas as pd
import argparse
from . import utils

def inverted(
    df: pd.DataFrame,
    args: argparse.Namespace
) -> list[tuple[str, str]]:
    """
    Generates a list containing a pair "Test" and "Expected".
    "Test" are translated words.
    "Expected" are the german words.
    The length of the list is args.test_length.

    Args:
    - df: Dataframe from where the words will be sampled
    - args: input arguments of the program

    Returns:
    - list[tuple[str,str]]: List containing "Test" "Expected" pairs.

    Raises:
    None
    """
    output_list = []
    for row in df.itertuples():
        if args.no_show_category:
            test = row.Translation
        else:
            test = f"[{row.Category}] {row.Translation}"
        expected = utils.word_from_row(row, plural = False)
        output_list.append((test, expected))
    return output_list
