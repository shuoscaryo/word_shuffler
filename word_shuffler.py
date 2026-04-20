# =============================================================================
#
# To know what this script does or what options it has use the flag "-h":
#     python3 myscript.py -h (it may not be python3 for you)
# Or just scroll to "parse_args" function and read the description.
#
# Template structure:
#   _main()          → The program starts from here
#   _parse_args()    → Arguments and explanation go here.
#   _setup_logger() → configures logger detail and message format (usually no
#     need to touch it)
#
# Conventions:
#   - Functions and variables starting with "_" are internal and should not be
#       imported elsewhere.
#   - Specify function args type and return type.
#   - Use "logger" object to print stuff
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
from my_logger import logger, setup_logger

# =============================================================================
# MORE IMPORTS HERE
import pandas as pd
import random
import sys
import german.modes
import japanese.modes

# =============================================================================
# GLOBAL DEFINES
from typing import Callable

class ModeSelector:
    # modes = {
    #   "lang1": {
    #       "mode1": {"function": func, "description": "text"}
    #   },
    #   ...
    # }
    modes = {}

    def add(
        language: str,
        mode: str,
        description: str,
        function: Callable[[pd.DataFrame, argparse.Namespace], list[tuple[str, str]]]
    ) -> None:
        # Create a new tag for the language
        if not language in ModeSelector.modes:
            ModeSelector.modes[language] = {}
        # Don't allow duplicated additions
        if mode in ModeSelector.modes[language]:
            logger.error(f"Mode \"{mode}\" already in language \"{language}\"")
            return
        # Add the mode
        ModeSelector.modes[language][mode] = {
            "description": description,
            "function": function
        }
    
    def func(language: str, mode: str) -> Callable[[pd.DataFrame, argparse.Namespace], list[tuple[str, str]]]:
        return ModeSelector.modes[language][mode]["function"]
    
    def lang_help() -> str:
        str_list = []
        mode_help = "What language to use.\n"
        str_list.append(mode_help)
        for lang in ModeSelector.modes.keys():
            str_list.append(f"\t- {lang}\n")
        return "".join(str_list)
    
    def mode_help() -> str:
        str_list = []
        mode_help = "What kind of test to do with the selected language.\n"\
            "For each language there are different available modes.\n"
        str_list.append(mode_help)
        for lang, modes in ModeSelector.modes.items():
            str_list.append(f"> {lang}:\n")
            for mode, content in modes.items():
                str_list.append(f'\t- {mode}: {content["description"]}\n')
        return "".join(str_list)



#CSV_COLUMNS = ["Article", "Word", "Plural", "Translation", "Category"]
# =============================================================================

def read_csv_list(csv_list: list[str]) -> pd.DataFrame:
    # Create a list with all the words
    df_list = []
    for csv in csv_list:
        try:
            logger.info(f"Reading file {csv}")
            df = pd.read_csv(csv)
            df_list.append(df)
        except:
            logger.error(f"Couldn't read file {csv}. Skipping")
    if not df_list:
        return pd.DataFrame()
    output_df = pd.concat(df_list, ignore_index = True)

    # normalize text columns, to lower, no spaces, no duplicates
    for col in output_df.select_dtypes(include="object").columns:
        output_df[col] = output_df[col].str.lower().str.strip()
    output_df = output_df.drop_duplicates()

    return output_df


def main(args: argparse.Namespace) -> int:    
    # load data
    df = read_csv_list(args.input_csv)
    logger.info(f"Words in input: {len(df)}")
    if (df.empty):
        logger.error(f"Exiting ...")
        return 1

    # Call the function that generates the values
    pair_list = ModeSelector.func(args.lang, args.mode)(df, args)
    logger.info(f"Total words for mode {args.mode}: {len(pair_list)}")

    # trim and shuffle
    total = len(pair_list) if args.length is None else min(len(pair_list), args.length)
    subset = random.sample(pair_list, total)
    logger.info(f"subset size: {total}")

    # Print
    for i in range(total):
        pair = subset[i]
        if (args.train):
            print(f"[{i + 1}/{total}] {pair[0]} -> {pair[1]}")
        else:
            input(f"[{i + 1}/{total}] {pair[0]}: ")
            RED = "\033[91m"
            RESET = "\033[0m"
            print(f"\t{RED}{pair[0]} -> {pair[1]}{RESET}")

    return 0


def parse_args() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
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
            "to check if you know them!",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog = f"Example: python3 {__file__} --lang german --mode normal --input-csv file.csv file2.csv",
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

    # - Flag
    # parser.add_argument('-s', '--skip-gaps', action='store_true', required = False, help = "")
    parser.add_argument(
        '-t', '--train',
        action='store_true',
        required = False,
        help = "If set to true, will just print the words and results all at once"
    )

    # -- With content "--output file.txt"
    # parser.add_argument('-o', '--output', type = str, help = "")
    parser.add_argument(
        "--lang",
        choices = ModeSelector.modes.keys(),
        type = str.lower,
        required = True,
        help = ModeSelector.lang_help()
    )
    parser.add_argument(
        '--mode',
        type = str.lower,
        required = True,
        help = ModeSelector.mode_help()
    )
    parser.add_argument(
        "--input-csv",
        type=str,
        nargs="+",
        required=True,
        help="Paths to the csvs with the words."
    )
    parser.add_argument(
        '-l',
        '--length',
        default = None,
        type = int,
        help = "How many words to show in test. If not set, takes all",
    )
    parser.add_argument(
        '--no-show-category',
        action = 'store_true',
        help = "Don't show the category of the word in test.",
    )
    # =========================================================================
    # No params prints help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # VALIDATE INPUTS HERE
    if args.mode not in ModeSelector.modes[args.lang]:
        parser.error(f"Invalid mode {args.mode} for language {args.lang}")

    if args.length is not None and args.length <= 0:
        parser.error("argument --length must be greater than 0.")
    
    return parser, args


if __name__ == "__main__":
    # =========================================================================
    # ADD MODES HERE
        # german
    ModeSelector.add("german", "normal", "shows singular in german, expects translation", german.modes.normal)
    ModeSelector.add("german", "inverted", "shows translation, expects german singular", german.modes.inverted)
    ModeSelector.add("german", "both", "some normal, some inverted", german.modes.both)
    ModeSelector.add("german", "plural", "shows singular in german, expects plural in german", german.modes.plural)
    ModeSelector.add("german", "article", "shows singular in german, expects article", german.modes.article)
        # japanese
    ModeSelector.add("japanese", "normal", "shows japanese plus reading, expects meaning", japanese.modes.normal)
    ModeSelector.add("japanese", "inverted", "shows meaning, expects japanese", japanese.modes.inverted)
    ModeSelector.add("japanese", "kanji", "shows word with kanji expects pronunciation and meaning", japanese.modes.kanji)
    # =========================================================================
    parser, args = parse_args()
    setup_logger(args.log_level, args.log_file)
    if not parser.description.strip():
        logger.warning("Parser has no description.")
    print(vars(args))
    result = main(args)
    if not isinstance(result, int):
        logger.warning(
            f"_main() returned {type(result).__name__}, expected int. "
            "Using exit code 0."
        )
        result = 0
    raise SystemExit(result) # exit code from main to CLI
