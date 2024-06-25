import asyncio
from functools import lru_cache

import sqlalchemy
from loguru import logger
from sqlalchemy.exc import NoResultFound

from src.core.crud.token import get_token_crud
from src.core.database.database import get_session
from src.core.models.db_models import Token
from src.parser.exceptions import exc
from src.parser.exceptions.exc import TokenError
from src.parser.schemas.vk_api_schemas import VkApiParams
from src.parser.schemas.vk_api_schemas import VkApiSettings
from src.parser.utils.reqsts import VkApiRequest


class TokenManager:
    logger = logger
    vk_request = VkApiRequest
    _is_approved = asyncio.Event()

    def __init__(self):
        self._is_approved.set()

    @classmethod
    async def get_active_token(cls) -> Token:
        await cls._is_approved.wait()
        while True:
            cls._is_approved.clear()
            if await cls._is_valid_token(token := await cls._get_token_from_db()):
                await cls._mark_token_as_using(token)
                cls._is_approved.set()
                return token

    @classmethod
    async def _is_valid_token(cls, token: Token) -> bool:
        cls.logger.debug(f"Check token with ID: {token.id}")
        try:
            _ = await cls.vk_request.request(
                method="GET",
                url="https://api.vk.com/method/groups.getById",
                params={
                    "access_token": token.token,
                    "v": VkApiParams.API_VERSION,
                    "group_id": "1",
                },
                attempts_count=VkApiSettings.ATTEMPT_COUNT,
            )
        except exc.VkApiError:
            cls.logger.debug(f"Token(ID:{token.id}) verification failed")
            await cls._mark_token_as_spoiled(token)
            return False
        cls.logger.debug(f"Token(ID:{token.id}) was passed")
        return True

    @staticmethod
    async def _mark_token_as_spoiled(token: Token):
        async with get_session() as session:
            await get_token_crud().update(
                session,
                update_filter=[[{Token.id.name: token.id}]],
                update_values={
                    Token.in_use.name: False,
                    Token.deactivated.name: True,
                },
            )
            await get_token_crud().commit(session)

    @staticmethod
    async def _mark_token_as_using(token: Token):
        async with get_session() as session:
            await get_token_crud().update(
                session,
                update_filter=[[{Token.id.name: token.id}]],
                update_values={Token.in_use.name: True},
            )
            await get_token_crud().commit(session)

    @classmethod
    async def _get_token_from_db(cls) -> Token:
        cls.logger.debug("Try get vk token from database")
        async with get_session() as session:
            try:
                token = await get_token_crud().get_one_model(
                    session,
                    [
                        [
                            {Token.in_use.name: False},
                            {Token.deactivated.name: False},
                        ]
                    ],
                )
                if token is None:
                    raise TokenError("No available token in database")
            except sqlalchemy.exc.SQLAlchemyError as e:
                raise TokenError(f"Unhandled SQLAlchemy error: {e}")
        cls.logger.debug("Token was successfully got from database")
        return token

    @classmethod
    async def activate_all(cls):
        async with get_session() as session:
            await get_token_crud().update(
                session,
                update_values={Token.in_use.name: False},
            )
            await get_token_crud().commit(session)


@lru_cache(None)
def get_token() -> TokenManager:
    return TokenManager()
