import pandas as pd
import argparse
from . import utils

def inverted(
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

    for row in df.itertuples():
        test = row.Translation
        if (utils.hasKanji(row.Word)):
            expected = f"{row.Word} ({row.Reading})"
        else:
            expected = row.Word
        output_list.append((test, expected))

    return output_list
