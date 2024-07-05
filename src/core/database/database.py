from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import as_declarative
from sqlalchemy.orm import declared_attr

from src.core.database.db_utils import camel_to_snake
from src.core.database.db_utils import class_registry
from src.core.database.db_utils import get_db_url


class Database:
    def __init__(self):
        self.engine = create_async_engine(
            get_db_url(),
            execution_options={"check_same_thread": False},
            echo=False,
        )
        self.AsyncSessionLocal = async_sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            class_=AsyncSession,
        )


@as_declarative(class_registry=class_registry)
class Base:
    def as_dict(self, *exclude_fields: str):
        exclude_fields = list(exclude_fields)
        exclude_fields.append("_sa_instance_state")
        return {
            name: value
            for name, value in self.__dict__.items()
            if name not in exclude_fields
        }

    @declared_attr
    def __tablename__(cls) -> str:
        """this is a class method"""
        return camel_to_snake(cls.__name__)


@asynccontextmanager
async def get_session() -> AsyncSession:
    try:
        async with Database().AsyncSessionLocal() as session:
            yield session
    except SQLAlchemyError as e:
        logger.error(f"Sqlalchemy error! Error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db() -> AsyncSession:
    try:
        async with Database().AsyncSessionLocal() as session:
            yield session
    finally:
        await session.close()
