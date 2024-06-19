from functools import lru_cache

from src.core.crud.common import CRUDBase
from src.core.models.db_models import Gid
from src.core.schemas.schemas import GidSchema
from src.core.schemas.schemas import GidSchemaCreate


class GidCrud(CRUDBase[Gid, GidSchema, GidSchemaCreate]):
    ...


@lru_cache(None)
def get_gid_crud() -> GidCrud:
    return GidCrud(Gid)
