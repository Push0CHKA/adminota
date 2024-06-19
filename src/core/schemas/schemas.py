from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class OrmSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IdIndexSchema(OrmSchema):
    id: int = None


class BlacklistedSchema(OrmSchema):
    blacklisted: bool = False


class DateCreateSchema(OrmSchema):
    created_at: datetime = datetime.now()


class TokenSchemaCreate(OrmSchema):
    token: str
    in_use: bool
    deactivated: bool
    last_use_date: datetime | None = None


class TokenSchema(IdIndexSchema, DateCreateSchema, TokenSchemaCreate):
    ...


class GidSchemaCreate(OrmSchema):
    group_id: int
    members_count: int
    deactivated_day_count: int = 0

    def __init__(self, **kwargs):
        kwargs["group_id"] = kwargs["id"]
        super().__init__(**kwargs)


class GidSchema(IdIndexSchema, BlacklistedSchema, GidSchemaCreate):
    ...
