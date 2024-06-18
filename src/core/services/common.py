import asyncio
from abc import ABC, abstractmethod

import uvicorn
from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from src.core.configuration.settings import get_settings
from src.core.utils.common import SystemManager


class Service(ABC):
    """Common abstract service"""

    logger = logger

    def __init__(self, name: str = "Service"):
        self.name = name
        self._required_init = True
        self.task = asyncio.create_task(self._loop(), name=name)
        self.task.add_done_callback(self.main_task_done_callback)

    @abstractmethod
    async def _run(self):
        raise NotImplementedError

    @abstractmethod
    async def _initialize_logic(self):
        raise NotImplementedError

    @abstractmethod
    async def cleanup(self):
        raise NotImplementedError

    def main_task_done_callback(self, task: asyncio.Task):
        try:
            self.logger.warning(
                f"Result of {self.name} main task {task.result()}"
            )
        except asyncio.CancelledError:
            self.logger.info(f"Cancelling {self.name}...")
        except Exception as e:
            self.logger.error(f"Main {self.name} task finished with {e}")

    async def initialize(self):
        self.logger.info(f"Start initializing service {self.name}")
        await self._initialize_logic()
        self.logger.info(f"Service {self.name} initialize successfully")

    async def _handling_exception(self, e: Exception):
        """For handling custom exceptions
        you can change self._required_init here or do smth else
        return True on handled
        """
        self.logger.warning(f"There is no handler for {e} [{type(e)}")
        return False

    async def _loop(self):
        while True:
            try:
                if self._required_init:
                    await self.initialize()
                self.logger.info(f"Run {self.name} service")
                await self._run()
            except asyncio.CancelledError:
                await self.cancelled()
                self.logger.info(f"Stopping service {self.name}")
                raise
            except asyncio.TimeoutError:
                self.logger.error("Timeout error occurred!")
                continue
            except Exception as e:
                is_handled = await self._handling_exception(e)
                if not is_handled:
                    self.logger.warning(
                        f"There is no handler for {e} [{type(e)}"
                    )
                continue
            finally:
                self.logger.info(f"Cleaning up after {self.name} service")
                await self.cleanup()
                await asyncio.sleep(1)

    def stop(self):
        self.logger.info(f"Force stop task {self.name}")
        raise asyncio.CancelledError

    async def cancelled(self):
        self.logger.info(f"Task {self.name} stopping")


class AppEventHandler(ABC):

    @abstractmethod
    async def on_startup(self):
        raise NotImplementedError

    @abstractmethod
    async def on_shutdown(self):
        raise NotImplementedError


class App(ABC):
    def __init__(
        self,
        tags_metadata,
        event_handler: AppEventHandler,
        title="App",
        reload=False,
    ):
        self._title = title
        self._event_handler = event_handler
        self._reload = reload
        self._app: FastAPI = FastAPI(
            openapi_tags=tags_metadata,
            docs_url="/docs",
        )
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @abstractmethod
    def configure_routes(self):
        raise NotImplementedError

    def configure_dependencies(self):
        @self._app.on_event("startup")
        async def startup_event():
            await self._event_handler.on_startup()

        @self._app.on_event("shutdown")
        async def shutdown_event():
            await self._event_handler.on_shutdown()

    def run(self, loop=None):
        SystemManager.load_default_config()
        self.configure_routes()
        self.configure_dependencies()
        if loop:
            config = uvicorn.Config(
                self._app,
                loop=loop,
                use_colors=True,
                **get_settings().uvicorn_kwargs,
            )
            server = uvicorn.Server(config)
            loop.run_until_complete(server.serve())
        else:
            uvicorn.run(
                self._app,
                use_colors=True,
                **get_settings().uvicorn_kwargs,
            )

    def get_app(self) -> FastAPI:
        """For testing"""
        self.configure_routes()
        return self._app

