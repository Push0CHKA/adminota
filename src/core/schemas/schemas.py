from datetime import datetime

from pydantic import BaseModel


class OrmSchema(BaseModel):
    class ConfigDict:
        from_attributes = True


class IdIntIndexSchema(OrmSchema):
    id: int


class DateCreateSchema(OrmSchema):
    created_at: datetime = datetime.now()


class TokenSchemaCreate(OrmSchema):
    token: str
    in_use: bool
    deactivated: bool
    last_use_date: datetime | None = None


class TokenSchema(IdIntIndexSchema, DateCreateSchema, TokenSchemaCreate):
    ...
