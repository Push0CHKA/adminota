from functools import lru_cache

from src.core.crud.common import CRUDBase
from src.core.models.db_models import Group
from src.core.schemas.schemas import GroupSchema
from src.core.schemas.schemas import GroupSchemaCreate


class GroupCrud(CRUDBase[Group, GroupSchema, GroupSchemaCreate]):
    ...


@lru_cache(None)
def get_group_crud() -> GroupCrud:
    return GroupCrud(Group)
