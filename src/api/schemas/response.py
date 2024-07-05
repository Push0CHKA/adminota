from typing import List

from src.core.schemas.schemas import GroupSchema, GstatSchema


class GroupData(GroupSchema):
    statistic: List[GstatSchema]
