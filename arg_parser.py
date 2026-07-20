import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Redis Server")

    parser.add_argument("--host", type=str, default="localhost", help="Host Address")
    parser.add_argument("--port", type=int, default=6379, help="Port Address")
    parser.add_argument("--db_count", type=int, default=16, help="DB instances count")

    return parser.parse_args()
