from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP

from src.core.database.database import Base
from src.core.database.mixins import BlacklistedMixin
from src.core.database.mixins import DateCreateMixin
from src.core.database.mixins import IdMixin


class Token(IdMixin, DateCreateMixin, Base):
    """Vk tokens"""

    token = Column(String, nullable=False, unique=True)
    in_use = Column(Boolean, default=False, nullable=False)
    deactivated = Column(Boolean, default=False, nullable=False)
    last_use_date = Column(DateTime, default=None, nullable=True)


class Gid(IdMixin, BlacklistedMixin, Base):
    """Groups id"""

    group_id = Column(Integer, unique=True)
    members_count = Column(Integer, nullable=False)
    deactivated_day_count = Column(Integer, default=0, nullable=False)


class Group(IdMixin, BlacklistedMixin, Base):
    """Таблица с основными данными сообществ"""

    group_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)
    screen_name = Column(String, nullable=False)
    is_closed = Column(Boolean, default=None)
    deactivated = Column(String, default=None)
    type = Column(String, nullable=False)
    photo = Column(String, default=None)
    activity = Column(String, default=None)
    addresses = Column(JSONB, default=None)
    age_limits = Column(Integer, default=None)
    ban_info = Column(JSONB, default=None)
    city = Column(JSONB, default=None)
    contacts = Column(JSONB, default=None)
    counters = Column(JSONB, default=None)
    country = Column(JSONB, default=None)
    cover = Column(JSONB, default=None)
    description = Column(String, default=None)
    fixed_post = Column(Integer, default=None)
    has_photo = Column(Boolean, default=None)
    links = Column(JSONB, default=None)
    main_album_id = Column(Integer, default=None)
    main_section = Column(Integer, default=None)
    market = Column(JSONB, default=None)
    members_count = Column(Integer, nullable=False)
    place = Column(JSONB, default=None)
    public_date_label = Column(String, default=None)
    site = Column(String, default=None)
    start_date = Column(TIMESTAMP, default=None)
    finish_date = Column(TIMESTAMP, default=None)
    status = Column(String, default=None)
    trending = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    wall = Column(Integer, default=None)
    wiki_page = Column(String, default=None)


class Change(IdMixin, DateCreateMixin, BlacklistedMixin, Base):
    """Таблица с изменениями сообществ"""

    group_id = Column(Integer, nullable=False)
    changes = Column(JSONB, nullable=False)
