from functools import lru_cache

from src.core.crud.common import CRUDBase
from src.core.models.db_models import Token
from src.core.schemas.schemas import TokenSchema
from src.core.schemas.schemas import TokenSchemaCreate


class TokenCrud(CRUDBase[Token, TokenSchema, TokenSchemaCreate]):
    ...


@lru_cache(None)
def get_token_crud() -> TokenCrud:
    return TokenCrud(Token)
