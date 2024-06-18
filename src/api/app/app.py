from src.api.app.app_event_handler import ApiEventHandler
from src.api.routers.test_routers import router as test_router
from src.core.services.common import App


api_event_handlers = ApiEventHandler()

api_tags_metadata = [
    {"name": "Test", "description": "Тест"},
]


class API(App):
    def __init__(self):
        super().__init__(
            tags_metadata=api_tags_metadata,
            event_handler=api_event_handlers,
            title="API",
            reload=False,
        )

    def configure_routes(self):
        self._app.include_router(test_router)
