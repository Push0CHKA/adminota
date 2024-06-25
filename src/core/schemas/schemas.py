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


class ChangeSchemaCreate(OrmSchema):
    group_id: int
    changes: dict


class ChangeSchema(
    IdIndexSchema, BlacklistedSchema, DateCreateSchema, ChangeSchemaCreate
):
    ...


class GroupSchemaCreate(OrmSchema):
    group_id: int
    name: str
    screen_name: str
    is_closed: bool
    deactivated: str | None = None
    type: str
    photo: str
    activity: str | None = None
    addresses: dict | None = None
    age_limits: int | None = None
    ban_info: dict | None = None
    city: dict | None = None
    contacts: list[dict] | None = None
    counters: dict | None = None
    country: dict | None = None
    cover: list[dict] | None = None
    description: str | None = None
    fixed_post: int | None = None
    has_photo: bool | None = None
    links: list[dict] | None = None
    main_album_id: int | None = None
    main_section: int | None = None
    market: dict | None = None
    members_count: int
    place: dict | None = None
    public_date_label: str | None = None
    site: str | None = None
    start_date: datetime | None = None
    finish_date: datetime | None = None
    status: str | None = None
    trending: bool = False
    verified: bool = False
    wall: int | None = None
    wiki_page: str | None = None

    def __init__(self, **kwargs):
        kwargs["group_id"] = kwargs["id"]
        kwargs["photo"] = kwargs["photo_200"]
        kwargs["cover"] = kwargs.get("cover", {}).get("images", None)
        kwargs["addresses"] = (
            kwargs.get("addresses")
            if kwargs.get("addresses")
            not in [{"is_enabled": False}, {"is_enabled": True}]
            else None
        )
        kwargs["contacts"] = kwargs.get("contacts") if kwargs.get("contacts") else None
        super().__init__(**kwargs)


class GroupSchema(IdIndexSchema, BlacklistedSchema, GroupSchemaCreate):
    ...
