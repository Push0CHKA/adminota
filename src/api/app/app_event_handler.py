from loguru import logger

from src.core.database.database import Database
from src.core.models.db_models import Base, Group, Change
from src.core.services.common import AppEventHandler
from src.parser.dispatcher import get_dispatcher


class ApiEventHandler(AppEventHandler):
    async def on_startup(self):
        logger.info("Starting API...")
        database = Database()
        async with database.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        get_dispatcher()

    async def on_shutdown(self):
        logger.info("Stopping API...")
