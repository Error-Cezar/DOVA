from argparse import ArgumentParser


def parse(parser: ArgumentParser):
    parser.add_argument("--dev", help="Run in development mode", action="store_true")
    parser.add_argument("--model", help="Model to use", default="gemma4:e4b")
    parser.add_argument("--port", required=False, help="Port to run the server on", default=5764)
    parser.add_argument("--host", required=False, help="Host to run the server on", default="0.0.0.0")
