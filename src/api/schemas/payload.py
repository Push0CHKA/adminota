from enum import Enum
from typing import Annotated

from fastapi import Query

from src.core.models.db_models import Group


class ClubType(Enum):
    event = "event"
    group = "group"
    page = "page"
    all = "all"


class SortBy(Enum):
    members = Group.members_count.name


class Interval(Enum):
    day = "day"
    week = "week"
    month = "month"
    year = "year"


class Sort(Enum):
    asc = "asc"
    desc = "decs"


main_offset = Annotated[int, Query(..., ge=0, description="Сдвиг")]
main_limit = Annotated[int, Query(..., ge=1, le=50, description="Количество элементов")]
club_type = Annotated[ClubType, Query(..., description="Тип сообщества")]
main_sort = Annotated[Sort, Query(..., description="Сортировка")]
main_sort_by = Annotated[SortBy, Query(..., description="Сортировка по")]
main_interval = Annotated[Interval, Query(..., description="Интервал")]
