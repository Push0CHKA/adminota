from sqlalchemy import Boolean, ForeignKey
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

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


class Gid(BlacklistedMixin, Base):
    """Groups id"""

    group_id = Column(Integer, primary_key=True)
    members_count = Column(Integer, nullable=False)
    deactivated_day_count = Column(Integer, default=0, nullable=False)


class Group(BlacklistedMixin, Base):
    """Main group data"""

    group_id = Column(
        Integer,
        primary_key=True,
    )
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
    country = Column(JSONB, default=None)
    cover = Column(String, default=None)
    description = Column(String, default=None)
    fixed_post = Column(Integer, default=None)
    has_photo = Column(Boolean, default=None)
    main_album_id = Column(Integer, default=None)
    main_section = Column(Integer, default=None)
    market = Column(JSONB, default=None)
    members_count = Column(Integer, nullable=False)
    site = Column(String, default=None)
    status = Column(String, default=None)
    trending = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    wall = Column(Integer, default=None)
    wiki_page = Column(String, default=None)

    change = relationship("Change", back_populates="group", lazy="subquery")
    statistic = relationship("Gstat", back_populates="group", lazy="subquery")


class Change(IdMixin, DateCreateMixin, Base):
    """Group changes"""

    group_id = Column(Integer, ForeignKey("group.group_id"), nullable=False, index=True)
    changes = Column(JSONB, nullable=False)

    group = relationship("Group", back_populates="change", lazy="subquery")


class Gstat(Base):
    """Interval group statistic"""

    group_id = Column(Integer, ForeignKey("group.group_id"), primary_key=True)
    interval = Column(String, primary_key=True)
    closed_stat = Column(Boolean, default=True)
    comments = Column(Integer, default=None)
    copies = Column(Integer, default=None)
    hidden = Column(Integer, default=None)
    subscribed = Column(Integer, default=None)
    unsubscribed = Column(Integer, default=None)
    likes = Column(Integer, default=None)
    views = Column(Integer, default=None)
    visitors = Column(Integer, default=None)
    reach_reach = Column(Integer, default=None)
    reach_subscribers = Column(Integer, default=None)
    mobile_reach = Column(Integer, default=None)
    sex = Column(JSONB, default=None)
    age = Column(JSONB, default=None)
    sex_age = Column(JSONB, default=None)
    cities = Column(JSONB, default=None)
    countries = Column(JSONB, default=None)

    group = relationship("Group", back_populates="statistic", lazy="subquery")
