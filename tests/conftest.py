from typing import Generator, Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.app.app import API
from src.core.database.database import Database
from src.core.utils.common import SystemManager


SystemManager().load_default_config()
database = Database()
SessionTesting = database.AsyncSessionLocal


@pytest.fixture(scope="function")
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    _app = API().get_app()
    yield _app


@pytest.fixture(scope="function")
def db_session(app: FastAPI) -> Generator[SessionTesting, Any, None]:
    connection = database.engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(app: FastAPI) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    with TestClient(app) as client:
        yield client
