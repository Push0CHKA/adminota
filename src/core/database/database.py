from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import declared_attr, as_declarative

from src.core.database.db_utils import get_db_url, camel_to_snake, class_registry


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
    database = Database()
    try:
        async with database.AsyncSessionLocal() as session:
            yield session
    except SQLAlchemyError:
        await session.rollback()
        raise
    finally:
        await session.close()
