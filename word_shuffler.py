# =============================================================================
#
# To know what this script does or what options it has use the flag "-h":
#     python3 myscript.py -h (it may not be python3 for you)
# Or just scroll to "parse_args" function and read the description.
#
# Template structure:
#   _main()          → The program starts from here
#   _parse_args()    → Arguments and explanation go here.
#   _setup_logging() → configures logging detail and message format (usually no
#     need to touch it)
#
# Conventions:
#   - Functions and variables starting with "_" are internal and should not be
#       imported elsewhere.
#   - Specify function args type and return type.
#   - Double enter between functions.
#   - Try to keep lines below 80 characters, wrap long ones into multiple
#       lines.
#   - Use this docstring to document new functions:
#       """
#       Description saying what the function does.
#       
#       Args:
#       - name (type) (optional): Description
#           More Lines
#       
#       Returns:
#       - type: Description
#           More Lines
#       
#       Raises:
#       - type: Description
#           More Lines
#       """
#   - _main() should return an integer exit code (0 = success) (default = 0).
#
# =============================================================================

import argparse
import logging
import sys
import os

# =============================================================================
# MORE IMPORTS HERE
import pandas as pd
import random

# =============================================================================
# GLOBAL DEFINES
DEFAULT_TEST_LENGTH = 20
MODES_LIST = ["german", "translated", "both", "plural", "article",]
CSV_COLUMNS = ["Article", "Word", "Plural", "Translation", "Category"]
# =============================================================================

def _word_from_row(row: tuple, plural: bool = False) -> str:
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
    

def _mode_german(
    df: pd.DataFrame,
    args: argparse.Namespace
) -> list[tuple[str, str]]:
    """
    Generates a list containing a pair "Test" and "Expected".
    "Test" are any german words/phrases, adds the article if it's a noun.
    "Expected" are the translations.
    The length of the list is args.test_length.

    Args:
    - df: Dataframe from where the words will be sampled
    - args: input arguments of the program

    Returns:
    - list[tuple[str,str]]: List containing "Test" "Expected" pairs.

    Raises:
    None
    """
    sample = df.sample(args.length)
    output_list = []
    for row in sample.itertuples():
        if args.no_show_category:
            test = _word_from_row(row, plural = False)
        else:
            test = f"[{row.Category}] {_word_from_row(row, plural = False)}"
        expected = row.Translation
        output_list.append((test, expected))
    return output_list


def _mode_translated(
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
    sample = df.sample(args.length)
    output_list = []
    for row in sample.itertuples():
        if args.no_show_category:
            test = row.Translation
        else:
            test = f"[{row.Category}] {row.Translation}"
        expected = _word_from_row(row, plural = False)
        output_list.append((test, expected))
    return output_list


def _mode_both(
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
    list_german = _mode_german(df, args)
    list_german = list_german[:len(list_german)//2]
    list_german = [(f"(German) {i[0]}", i[1]) for i in list_german]

    list_translated = _mode_translated(df, args)
    list_translated = list_translated[:len(list_translated)//2]
    list_translated = [(f"(Translated) {i[0]}", i[1]) for i in list_translated]

    output_list = list_german + list_translated
    random.shuffle(output_list)
    return output_list


def _mode_plural(
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
    df = df[df["Category"] == "noun"]
    length = min(args.length, len(df))
    sample = df.sample(length)

    output_list = []
    for row in sample.itertuples():
        test = _word_from_row(row, plural = False)
        expected = _word_from_row(row, plural = True)
        if len(expected) == 0:
            continue
        expected = f"{expected} ({row.Translation})"
        output_list.append((test, expected))
    return output_list


def _mode_article(
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
    length = min(args.length, len(df))
    sample = df.sample(length)

    output_list = []
    for row in sample.itertuples():
        test = row.Word
        expected = _word_from_row(row, plural = False)
        output_list.append((test, expected))
    return output_list


def _main(args: argparse.Namespace) -> int:
    """
    Entry point of the program. Args can be modified in 'parse_args()'.

    Args:
    - args (argparse.Namespace): Arguments parsed from the command line.
        Accesible by key 'args.example'. A key can be modified.
        eg. args.name = 'hello'

    Returns:
    - int: Exit code (0 = success, other values = error).
    """
    # load data
    df = pd.read_csv(args.input_csv)
    args.length = min(len(df), args.length)
    # Call the "_mode_*" functions that matches args.mode
    test_expected_list = globals()[f"_mode_{args.mode}"](df, args)
    total = len(test_expected_list)
    for i in range(total):
        pair = test_expected_list[i]
        input(f"[{i + 1}/{total}] {pair[0]}: ")
        print(f"\t{pair[0]} --> {pair[1]}")
    return 0


def _parse_args() -> argparse.Namespace:
    """
    This is the function used to configure what args the program has. Write the
    new args as in the examples below.
    Converts the arguments passed to the script into a variable. The variable
    stores each element in a key with the name defined inside the function.
    To access each key is "args.keyName".

    Args:
    - None

    Returns:
    - (argparse.ArgumentParser, argparse.Namespace): the parser and parsed args

    Raises:
    - SystemExit: If there is an issue in the parsing. Prints help and closes
        the program. Can be caught with except but for what reason!
    """
    parser = argparse.ArgumentParser(
        description = "Reads the words from the input_csv and displays some "
            " depending on the options to check if you know them!",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        epilog = "Example:",
    )
    # Default flag for setting how deep the logs should go
    parser.add_argument(
        "--log-level",
        type = int,
        choices = range(0,5),
        default = 1,
        metavar = "{0..4}",
        help = "0 = DEBUG, 1 = INFO, 2 = WARNING, 3 = ERROR, 4 = CRITICAL",
    )
    # Default flag to redirect log messages to a file
    parser.add_argument(
        "--log-file",
        type = str,
        default = "stderr",
        help = "Where the logs will be printed",
    )

    # =========================================================================
    # WRITE ARGS HERE
    # - Positional
    # parser.add_argument("name", type = str, help = "")
    mode_choices = [i.lower() for i in MODES_LIST]
    parser.add_argument(
        'mode',
        choices = mode_choices,
        type = str.lower,
        help = "What kind of test to do. \"German\" shows german words, "
            "\"Translated\" the translation, \"Both\" randomly shows "
            "translated or german with 50%% distribution, \"Plural\" shows the"
            " german plural of nouns and test for german singular and "
            "\"Article\" the german singular noun and expects the article."
    )
    parser.add_argument(
        "input_csv",
        type = str,
        help = "Path to the csv with the words."
    )
    # - Optional
    # -- Flag
    # parser.add_argument('-s', '--skip-gaps', action='store_true', help="")
    parser.add_argument(
        '--no-show-category',
        action = 'store_true',
        help = "Don't show the category of the word in test."
    )
    # -- With content "--output file.txt"
    # parser.add_argument('-o', '--output', type = str, help = "")
    parser.add_argument(
        '-l',
        '--length',
        default = DEFAULT_TEST_LENGTH,
        type = int,
        help = "How many words to show in test.",
    )
    ### NO MORE ARGS BELOW THIS
    # =========================================================================
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    # =========================================================================
    # ARG VALUE CHECK
    # if condition:
    #   parser.error("") # Terminates program
    if args.length < 0 :
        parser.error("argument --test-length must be greater than 0.")
    # =========================================================================
    return parser, args


def _setup_logging(args: argparse.Namespace) -> None:
    """
    Handles what level to show and the format of the messages while logging.

    Args:
    - args (argparse.Namespace): Arguments parsed from the command line.
        Expected attributes:
            - log_level (int): 0 (DEBUG) to 4 (CRITICAL)
            - log_file (str or None) (optional): path to a log file

    Returns:
    - None

    Raises:
    - ValueError: if "args.log_level" is out of range.
    """
    if not 0 <= args.log_level <= 4:
        raise ValueError("--log-level must be between 0 and 4")
    LEVELS = [
        logging.DEBUG,     # 0
        logging.INFO,      # 1
        logging.WARNING,   # 2
        logging.ERROR,     # 3
        logging.CRITICAL,  # 4
    ]

    handlers = []
    if args.log_file == "stderr":
        handlers.append(logging.StreamHandler(sys.stderr))
    elif args.log_file == "stdout":
        handlers.append(logging.StreamHandler(sys.stdout))
    elif args.log_file:
        os.makedirs(os.path.dirname(args.log_file) or ".", exist_ok=True)
        handlers.append(logging.FileHandler(args.log_file, mode="w", encoding="utf-8"))

    logging.basicConfig(
        level=LEVELS[args.log_level],
        format="%(asctime)s %(levelname)s | %(filename)s:%(lineno)d: %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
        force=True,
    )


if __name__ == "__main__":
    parser, args = _parse_args()
    _setup_logging(args)
    if not parser.description.strip():
        logging.warning("Parser has no description.")
    result = _main(args)
    if not isinstance(result, int):
        logging.warning(
            f"_main() returned {type(result).__name__}, expected int. "
            "Using exit code 0."
        )
        result = 0
    raise SystemExit(result) # exit code from main to CLI