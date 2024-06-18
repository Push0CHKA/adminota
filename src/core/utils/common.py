import argparse

from dotenv import load_dotenv, find_dotenv


class SystemManager:

    @staticmethod
    def arg_parse() -> argparse.Namespace:
        log_level = "INFO"
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-l",
            "--log-level",
            default=log_level,
            help=f"Logging level. Default: {log_level}",
        )
        parser.add_argument(
            "-p",
            "--log-path",
            default=None,
            help=f"Logging file path",
        )
        return parser.parse_args()

    @classmethod
    def load_default_config(cls) -> None:
        load_dotenv(find_dotenv(), verbose=True, override=True)
