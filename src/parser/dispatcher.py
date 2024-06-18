import asyncio
from functools import lru_cache

from src.core.log.setup_log import reinit_logger
from src.core.services.common import Service
from src.core.utils.common import SystemManager
from src.parser.services.scheduler import Scheduler


class Dispatcher(Service):

    def __init__(self):
        self.scheduler = Scheduler()
        super().__init__(name="Dispatcher")

    async def _run(self):
        while True:
            await asyncio.sleep(10)

    async def _initialize_logic(self):
        args = SystemManager.arg_parse()
        reinit_logger(args.log_level.upper(), args.log_path)

    async def cleanup(self):
        self.scheduler.stop()


@lru_cache(None)
def get_dispatcher() -> Dispatcher:
    return Dispatcher()
