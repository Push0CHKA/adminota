from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import Integer


class BlacklistedMixin:
    """Provides bool blacklisted flag"""

    blacklisted = Column(Boolean, default=False)


class IdIntMixin:
    """Provides int id"""

    id = Column(Integer, primary_key=True, autoincrement=True)


class DateCreateMixin:
    """Provides datetime created date"""

    created_at = Column(DateTime, default=datetime.now, server_default=func.now())
