from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class OrmSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    def as_dict(self, *exclude_fields: str):
        exclude_fields = list(exclude_fields)
        exclude_fields.append("_sa_instance_state")
        return {
            name: value
            for name, value in self.__dict__.items()
            if name not in exclude_fields
        }


class IdIndexSchema(OrmSchema):
    id: int = None


class BlacklistedSchema(OrmSchema):
    blacklisted: bool = False


class DateCreateSchema(OrmSchema):
    created_at: datetime | None = None


class GroupIdSchema(OrmSchema):
    group_id: int


class IntervalSchema(OrmSchema):
    interval: str


class TokenSchemaCreate(OrmSchema):
    token: str
    in_use: bool
    deactivated: bool
    last_use_date: datetime | None = None


class TokenSchema(IdIndexSchema, DateCreateSchema, TokenSchemaCreate):
    ...


class GidSchemaCreate(GroupIdSchema):
    members_count: int
    deactivated_day_count: int = 0

    def __init__(self, **kwargs):
        kwargs["group_id"] = kwargs["id"]
        super().__init__(**kwargs)


class GidSchema(BlacklistedSchema, GidSchemaCreate):
    ...


class ChangeSchemaCreate(GroupIdSchema):
    changes: dict


class ChangeSchema(IdIndexSchema, DateCreateSchema, ChangeSchemaCreate):
    ...


class GroupSchemaCreate(GroupIdSchema):
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
    country: dict | None = None
    cover: str | None = None
    description: str | None = None
    fixed_post: int | None = None
    has_photo: bool | None = None
    main_album_id: int | None = None
    main_section: int | None = None
    market: dict | None = None
    members_count: int
    site: str | None = None
    status: str | None = None
    trending: bool = False
    verified: bool = False
    wall: int | None = None
    wiki_page: str | None = None

    def __init__(self, **kwargs):
        kwargs["group_id"] = kwargs["id"]
        kwargs["photo"] = kwargs["photo_200"]
        kwargs["cover"] = (
            kwargs.get("cover", {}).get("images", [{"url": None}])[-1].get("url")
        )
        kwargs["addresses"] = (
            kwargs.get("addresses")
            if kwargs.get("addresses")
            not in [{"is_enabled": False}, {"is_enabled": True}]
            else None
        )
        kwargs["contacts"] = kwargs.get("contacts") if kwargs.get("contacts") else None
        super().__init__(**kwargs)


class GroupSchema(BlacklistedSchema, GroupSchemaCreate):
    ...


class GstatSchemaCreate(GroupIdSchema, IntervalSchema):
    closed_stat: bool = True
    comments: int | None = None
    copies: int | None = None
    hidden: int | None = None
    likes: int | None = None
    subscribed: int | None = None
    unsubscribed: int | None = None
    views: int | None = None
    visitors: int | None = None
    reach_reach: int | None = None
    reach_subscribers: int | None = None
    mobile_reach: int | None = None
    sex: list[dict] | None = None
    age: list[dict] | None = None
    sex_age: list[dict] | None = None
    cities: list[dict] | None = None
    countries: list[dict] | None = None

    def __init__(self, **kwargs):
        kwargs["comments"] = kwargs.get("activity", {}).get("comments")
        kwargs["copies"] = kwargs.get("activity", {}).get("copies")
        kwargs["hidden"] = kwargs.get("activity", {}).get("hidden")
        kwargs["likes"] = kwargs.get("activity", {}).get("likes")
        kwargs["subscribed"] = kwargs.get("activity", {}).get("subscribed")
        kwargs["unsubscribed"] = kwargs.get("activity", {}).get("unsubscribed")
        kwargs["closed_stat"] = (
            False
            if kwargs.get("activity")
            or kwargs.get("reach", {})
            or kwargs.get("visitors", {})
            else True
        )
        kwargs["views"] = kwargs.get("visitors", {}).get("views")
        kwargs["visitors"] = kwargs.get("visitors", {}).get("visitors")
        kwargs["reach_reach"] = kwargs.get("reach", {}).get("reach")
        kwargs["reach_subscribers"] = kwargs.get("reach", {}).get("reach_subscribers")
        kwargs["mobile_reach"] = kwargs.get("reach", {}).get("mobile_reach")
        kwargs["sex"] = kwargs.get("reach", {}).get("sex")
        kwargs["age"] = kwargs.get("reach", {}).get("age")
        kwargs["sex_age"] = kwargs.get("reach", {}).get("sex_age")
        kwargs["cities"] = kwargs.get("reach", {}).get("cities")
        kwargs["countries"] = kwargs.get("reach", {}).get("countries")
        super().__init__(**kwargs)


class GstatSchema(GstatSchemaCreate):
    ...
