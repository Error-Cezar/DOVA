from argparse import ArgumentParser


def parse(parser: ArgumentParser):
    parser.add_argument("-i", "--input", type=str, help="Input string to be processed")
    parser.add_argument(
        "--chat", action="store_true", help="Enable text input instead of voice"
    )
