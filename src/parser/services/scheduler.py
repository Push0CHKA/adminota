import asyncio

from src.core.configuration.settings import get_settings
from src.core.services.common import Service
from src.parser.schemas.vk_api_schemas import VkApiParams
from src.parser.utils.parser import Parser
from src.parser.utils.token_manager import get_token
from src.parser.utils.utils import get_time


class Scheduler(Service):
    """Vk parser scheduler"""

    def __init__(self):
        self.tasks: list = []
        super().__init__(name="Scheduler")

    async def run_parser(self):
        self.logger.info("Parsing started")
        for parser_id in range(VkApiParams.PARSERS_CNT):
            parser = Parser(parser_id)
            self.tasks.append(parser.run_parse_gids())
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.logger.success("Parsing was successfully finished")

    async def _run(self):
        while True:
            if get_time(get_settings().parser.utc) == get_settings().parser.start_time:
                self.logger.info("The time has come. Start parser...")
                await get_token().activate_all()
                await self.run_parser()
                self.logger.info(
                    f"Stop parser. Next start in {get_settings().parser.start_time} "
                    f"(utc+{get_settings().parser.utc})"
                )
            await asyncio.sleep(50)

    async def _initialize_logic(self):
        ...

    async def cleanup(self):
        ...
