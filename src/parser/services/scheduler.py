from src.core.services.common import Service
from src.parser.utils.vk_parser import Parser


class Scheduler(Service):
    """Vk parser scheduler"""

    def __init__(self):
        super().__init__(name="Scheduler")

    async def start_parser(self, parser_id: int):
        parser = Parser(parser_id)
        await parser.run_parse_gids()

    async def _run(self):
        while True:
            await self.start_parser(1)

    async def _initialize_logic(self):
        ...

    async def cleanup(self):
        ...
