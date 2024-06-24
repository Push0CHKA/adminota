from typing import Callable

from pydantic import ValidationError

from src.core.crud.gid import get_gid_crud
from src.core.database.database import get_session
from src.core.log.setup_log import ParsLogger
from src.core.models.db_models import Token
from src.core.schemas.schemas import GidSchema
from src.parser.exceptions import exc
from src.parser.schemas.vk_api_schemas import VkApiErrorCodes, VkApiParams
from src.parser.utils.reqsts import VkApiRequest
from src.parser.utils.script_maker import GidScriptIterator
from src.parser.utils.token_manager import get_token


class Parser:
    """Vk parser"""

    vk_request: VkApiRequest = VkApiRequest

    def __init__(self, pars_id: int):
        self.pars_id = pars_id
        self.token: Token | None = None
        self.logger: ParsLogger = ParsLogger(pars_id)

    async def run_parse_gids(self):
        await self._update_token()
        await self._pars_gids()

    async def _update_token(self):
        self.logger.info("Try update token for parser")
        self.token = await get_token().get_active_token()
        self.logger.info("Token was successfully updated")

    async def _upload_gids(self, data: list[list[dict]]):
        for group_data in data:
            try:
                if not group_data:
                    self.logger.warning(
                        f"Failed mapped json data do Gid model. Json: {group_data}"
                    )
                    continue
                if group_data[0].get("members_count", 0) < VkApiParams.MIN_MEMBERS_CNT:
                    continue
                gid = GidSchema.parse_obj(group_data[0])
                gid.id = None
            except ValidationError:
                continue
            async with get_session() as session:
                await get_gid_crud().create_with_commit(session, obj_in=gid)

    async def _execute_cript(self, script: str, upload: Callable):
        try:
            await upload(
                await self.vk_request.request(
                    method="POST",
                    url="https://api.vk.com/method/execute",
                    data={
                        "access_token": self.token.token,
                        "v": 5.131,
                        "code": script,
                    },
                )
            )
        except exc.VkApiError as e:
            if e.error_code in VkApiErrorCodes.TOKEN_ERROR:
                self.logger.debug(f"Received token error [{e.error_code}, {e.message}]")
                await self._update_token()
            elif e.error_code in VkApiErrorCodes.TOO_BIG_DATA:
                # todo change response size
                ...
            raise
        except Exception as e:
            self.logger.error(f"Unhandled error when parsing group ids. Error: {e}")
            raise

    async def _pars_gids(self):
        """Parsing all group ids"""
        self.logger.info("Start parsing groups id")
        async for script in GidScriptIterator(self.pars_id):
            await self._execute_cript(script, self._upload_gids)
        self.logger.info("Finish parsing groups id")
