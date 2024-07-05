from functools import lru_cache

from src.core.crud.common import CRUDBase
from src.core.models.db_models import Gstat
from src.core.schemas.schemas import GstatSchema
from src.core.schemas.schemas import GstatSchemaCreate


class GstatCrud(CRUDBase[Gstat, GstatSchema, GstatSchemaCreate]):
    ...


@lru_cache(None)
def get_group_stat_crud() -> GstatCrud:
    return GstatCrud(Gstat)
