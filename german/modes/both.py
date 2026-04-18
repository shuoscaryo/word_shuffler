import pandas as pd
import argparse
from . import normal, inverted

def both(
    df: pd.DataFrame,
    args: argparse.Namespace
) -> list[tuple[str, str]]:
    """
    Generates a list containing a pair "Test" and "Expected".
    "Test" some german some translated words.
    "Expected" some german some translated words.
    The length of the list is args.test_length.

    Args:
    - df: Dataframe from where the words will be sampled
    - args: input arguments of the program

    Returns:
    - list[tuple[str,str]]: List containing "Test" "Expected" pairs.

    Raises:
    None
    """
    list_german = normal(df, args)
    list_german = list_german[:len(list_german)//2]
    list_german = [(f"(German) {i[0]}", i[1]) for i in list_german]

    list_translated = inverted(df, args)
    list_translated = list_translated[:len(list_translated)//2]
    list_translated = [(f"(Translated) {i[0]}", i[1]) for i in list_translated]

    output_list = list_german + list_translated
    return output_list
