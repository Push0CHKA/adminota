from functools import lru_cache

from src.core.crud.common import CRUDBase
from src.core.models.db_models import Change
from src.core.schemas.schemas import ChangeSchema
from src.core.schemas.schemas import ChangeSchemaCreate


class ChangeCrud(CRUDBase[Change, ChangeSchema, ChangeSchemaCreate]):
    ...


@lru_cache(None)
def get_change_crud() -> ChangeCrud:
    return ChangeCrud(Change)
