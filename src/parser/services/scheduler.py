import asyncio

from src.core.services.common import Service
from src.parser.schemas.vk_api_schemas import VkApiParams
from src.parser.utils.parser import Parser
from src.parser.utils.token_manager import get_token


class Scheduler(Service):
    """Vk parser scheduler"""

    def __init__(self):
        self.tasks: list[asyncio.Task] = []
        super().__init__(name="Scheduler")

    async def run_parser(self):
        for parser_id in range(VkApiParams.PARSERS_CNT):
            parser = Parser(parser_id)
            self.tasks.append(
                asyncio.create_task(parser.run_parse_gids(), name=f"parser_{parser_id}")
            )

    async def _run(self):
        await get_token().activate_all()
        await self.run_parser()
        while True:
            # todo check tasks
            await asyncio.sleep(10)

    async def _initialize_logic(self):
        ...

    async def cleanup(self):
        ...
