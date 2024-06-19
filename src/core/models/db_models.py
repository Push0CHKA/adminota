from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from src.core.database.database import Base
from src.core.database.mixins import BlacklistedMixin
from src.core.database.mixins import DateCreateMixin
from src.core.database.mixins import IdIntMixin


class Gids(IdIntMixin, BlacklistedMixin, Base):
    """Groups id"""

    group_id = Column(Integer, unique=True)
    members = Column(Integer, nullable=False)
    deactivated_days_count = Column(Integer, default=0, nullable=False)


class Token(IdIntMixin, DateCreateMixin, Base):
    """Vk tokens"""

    token = Column(String, nullable=False, unique=True)
    in_use = Column(Boolean, default=False, nullable=False)
    deactivated = Column(Boolean, default=False, nullable=False)
    last_use_date = Column(DateTime, default=None, nullable=True)
