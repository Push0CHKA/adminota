from typing import AsyncIterator

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.api.app.app_event_handler import ApiEventHandler
from src.api.routers.test_routers import router as test_router
from src.api.routers.group_routers import router as group_router
from src.core.services.common import App


api_event_handlers = ApiEventHandler()

api_tags_metadata = [
    {"name": "Test", "description": "Тест"},
    {"name": "Groups", "description": "Сообщества"},
]


class API(App):
    def __init__(self):
        super().__init__(
            tags_metadata=api_tags_metadata,
            title="API",
            reload=False,
        )

    async def lifespan(self, _: FastAPI) -> AsyncIterator[None]:
        await api_event_handlers.on_startup()
        redis = aioredis.from_url("redis://localhost")
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        yield
        await api_event_handlers.on_shutdown()

    def configure_routes(self):
        self._app.include_router(test_router)
        self._app.include_router(group_router)
