from functools import wraps
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Generator
from typing import Generic
from typing import Iterable
from typing import TypeAlias
from typing import TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import CursorResult, text, and_, or_
from sqlalchemy import delete
from sqlalchemy import Select
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import OperatorExpression
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.sql.functions import func

from src.core.database.database import Base


ModelType = TypeVar("ModelType", bound=Base)
GetSchemaType = TypeVar("GetSchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


CRUDBaseCommonMethodType: TypeAlias = (
    Callable[[AsyncSession, dict[str, ...], int, int], Awaitable[list[ModelType]]]
    | Callable[[AsyncSession, dict[str, ...]], Awaitable[ModelType] | None]
    | Callable[[AsyncSession, dict[str, ...], dict[str, ...], bool], None]
)


def map_to_schema_result(func) -> ():
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        self: CRUDBase = args[0]
        get_schema: GetSchemaType = self.__orig_bases__[0].__args__[1]
        if isinstance(result, Iterable):
            return [get_schema.from_orm(res) for res in result]
        return get_schema.from_orm(result)

    return wrapper


UpdateFilter: TypeAlias = (
    list[list[str | dict]] | list[OperatorExpression] | OperatorExpression | Any
)


class CRUDBase(Generic[ModelType, GetSchemaType, CreateSchemaType]):
    def __init__(self, model: type[ModelType]):
        """
        CRUD object with default methods to
            Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self._create_schema = CreateSchemaType
        self._model = model

    @property
    def model(self):
        return self._model

    def _get_dict_condition(
        self, filter_dict: dict[str, ...] | None = None
    ) -> Generator[bool, Any, None]:
        filter_dict = filter_dict or {}
        return (
            getattr(self._model, field) == value for field, value in filter_dict.items()
        )

    def _generate_where_cause(
        self,
        filter_: list[list[str | dict]] | None = None,
    ):
        if not filter_:
            return text("")
        extern_cond = []
        for extern_filter in filter_:
            intern_cond = []
            for intern_filter in extern_filter:
                if isinstance(intern_filter, str):
                    intern_cond.append(text(intern_filter))
                else:
                    intern_cond.append(*self._get_dict_condition(intern_filter))
            extern_cond.append(and_(*intern_cond))
        return or_(*extern_cond)

    @property
    def _select_model(self) -> Select:
        """can be used for config options with inload"""
        return select(self._model)

    @property
    def _select_count(self) -> Select:
        """can be used for count of models"""
        return select(func.count()).select_from(self._model)

    @property
    def _select_for_count(self) -> Select:
        """can be used for rows count"""
        return select(self._model.id)

    def _resolve_filter(self, filter_: UpdateFilter) -> list[OperatorExpression]:
        if isinstance(filter_, list):
            filter_ = self._generate_where_cause(filter_)

        if not isinstance(filter_, Iterable):
            filter_ = [filter_]
        return filter_

    async def get_multi_model(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int | None = None,
        order_by: UnaryExpression | None = None,
        operator_expressions: list[OperatorExpression] | None = None,
        options: Any | None = None,
        where_: list[list[str | dict]] = None,
        filter_: Any | None = None,
    ) -> list[ModelType]:
        stmt = self._select_model
        if operator_expressions is not None:
            operator_expressions = self._resolve_filter(operator_expressions)
            stmt = stmt.where(*operator_expressions)
        if where_:
            operator_expressions = self._resolve_filter(where_)
            stmt = stmt.where(*operator_expressions)
        if options:
            operator_expressions = self._resolve_filter(options)
            stmt = stmt.options(*operator_expressions)
        stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        if order_by is not None:
            stmt = stmt.order_by(order_by)

        if filter_ is not None:
            stmt = stmt.filter(filter_)

        return (await session.execute(stmt)).scalars().all()

    @map_to_schema_result
    async def get_multi(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int | None = None,
        order_by: UnaryExpression | None = None,
        operator_expressions: list[OperatorExpression] | None = None,
        options: Any | None = None,
        filter_: list[list[str | dict[str, ...]]] = None,
    ) -> list[GetSchemaType]:
        return await self.get_multi_model(
            session,
            offset,
            limit,
            order_by,
            operator_expressions,
            options,
            filter_,
        )

    async def get_one_model(
        self,
        session: AsyncSession,
        filter_: list[list[str | dict[str, ...]]],
        options: Any | None = None,
    ) -> ModelType:
        stmt = self._select_model.where(self._generate_where_cause(filter_))
        if options:
            operator_expressions = self._resolve_filter(options)
            stmt = stmt.options(*operator_expressions)
        return (await session.execute(stmt)).scalars().first()

    @map_to_schema_result
    async def get_one(
        self,
        session: AsyncSession,
        filter_: list[list[str | dict[str, ...]]],
        options: Any | None = None,
    ) -> GetSchemaType:
        return await self.get_one_model(session, filter_, options)

    async def create(
        self, session: AsyncSession, *, obj_in: dict | CreateSchemaType
    ) -> ModelType:
        obj_in_data = obj_in
        if isinstance(obj_in_data, BaseModel):
            # Поле типа uuid преобразуется в строку и будет ошибка.
            obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)  # type: ignore
        session.add(db_obj)
        await session.flush([db_obj])
        return db_obj

    async def create_with_commit_model(
        self, session: AsyncSession, *, obj_in: dict | CreateSchemaType
    ) -> ModelType:
        obj = await self.create(session, obj_in=obj_in)
        await session.commit()
        await session.refresh(obj)
        return obj

    @map_to_schema_result
    async def create_with_commit(
        self, session: AsyncSession, *, obj_in: dict | CreateSchemaType
    ) -> GetSchemaType:
        return await self.create_with_commit_model(session, obj_in=obj_in)

    async def update(
        self,
        session: AsyncSession,
        *,
        update_filter: UpdateFilter | None = None,
        update_values: dict[str, ...],
        is_patch=True,
    ) -> int:
        """If is_patch = True - update only not nullable fields
        in other case set possible null values"""

        if is_patch:
            update_values = {k: v for k, v in update_values.items()}
        update_stmt = update(self._model)
        if update_filter:
            operator_expressions = self._resolve_filter(update_filter)
            update_stmt = update_stmt.where(*operator_expressions)
        update_stmt = update_stmt.values(**update_values)
        result: CursorResult = await session.execute(update_stmt)
        return result.rowcount

    async def get_count(
        self,
        session: AsyncSession,
        filter_: list[list[str | dict[str, ...]]] | None = None,
    ):
        stmt = self._select_count.where(self._generate_where_cause(filter_))
        return (await session.execute(stmt)).scalar()

    async def delete(
        self,
        session: AsyncSession,
        operator_expressions: list[OperatorExpression] | None = None,
        filter_: list[list[str | dict[str, ...]]] = None,
    ) -> int:
        stmt = delete(self._model)
        if operator_expressions is not None:
            operator_expressions = self._resolve_filter(operator_expressions)
            stmt = stmt.where(*operator_expressions)
        if filter_:
            operator_expressions = self._resolve_filter(filter_)
            stmt = stmt.where(*operator_expressions)

        result: CursorResult = await session.execute(stmt)
        await session.flush()
        return result.rowcount

    @classmethod
    async def commit(
        cls,
        session: AsyncSession,
    ):
        await session.commit()

    @classmethod
    async def refresh(cls, session: AsyncSession, obj: ModelType) -> ModelType:
        await session.refresh(obj)
        return obj
