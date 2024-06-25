import re

from src.core.configuration.settings import DBSettings

REGULAR_COMP = re.compile(r"((?<=[a-z\d])[A-Z]|(?!^)[A-Z](?=[a-z]))")

class_registry: dict = {}


def camel_to_snake(camel_string):
    return REGULAR_COMP.sub(r"_\1", camel_string).lower()


def get_db_url() -> str:
    return (
        f"postgresql+asyncpg://{DBSettings().user}:"
        # f"{DBSettings().password}@{DBSettings().host}:"
        f"{DBSettings().password}@host.docker.internal:"
        f"{DBSettings().port}/{DBSettings().name}"
    )
