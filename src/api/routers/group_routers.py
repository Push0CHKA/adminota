from typing import List

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from sqlalchemy import desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.payload import (
    main_offset,
    main_limit,
    club_type,
    ClubType,
    main_sort,
    Sort,
    main_sort_by,
    main_interval,
)
from src.api.schemas.response import GroupData
from src.core.crud.group import get_group_crud
from src.core.database.database import get_db, get_session
from src.core.models.db_models import Group, Gstat

router = APIRouter(prefix="/groups")


@router.get("/get", tags=["Groups"], response_model=List[GroupData])
@cache(expire=60)
async def groups_data(
    interval: main_interval,
    offset: main_offset,
    limit: main_limit,
    club: club_type,
    sort_by: main_sort_by,
    sort: main_sort,
    db: AsyncSession = Depends(get_db),
):
    return await get_group_crud().get_multi_model(
        db,
        offset=offset,
        limit=limit,
        where_=[[{Group.type.name: club.value}]] if club is not ClubType.all else None,
        order_by=desc(sort_by.value) if sort is Sort.desc else asc(sort_by.value),
        filter_=Group.statistic.any(Gstat.interval == interval.value),
    )
