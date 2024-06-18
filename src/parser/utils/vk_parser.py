from loguru import logger

from src.core.schemas.api_schemas import VkApiCodes
from src.core.models.db_models import Token
from src.parser.exceptions import exc
from src.parser.exceptions.exc import TokenError
from src.parser.utils.reqsts import VkApiRequest
from src.parser.utils.script_maker import VkScriptMaker
from src.parser.utils.token_manager import TokenManager


class Parser:
    """Vk parser"""

    logger = logger
    vk_request = VkApiRequest

    def __init__(self, pars_id: int):
        self.pars_id = pars_id
        self.token: Token | None = None
        self.scr_maker: VkScriptMaker = VkScriptMaker(pars_id)

    async def run_parse_gids(self):
        try:
            await self._update_token()
        except TokenError:
            raise
        await self._pars_gids()

    async def _update_token(self):
        self.logger.debug(f"Parser {self.pars_id}: Try update token for parser")
        self.token = await TokenManager.get_active_token()
        self.logger.debug(f"Parser {self.pars_id}: token was successfully updated")

    async def _pars_gids(self):
        gen = self.scr_maker.get_gid_script()
        while True:
            try:
                script = await anext(gen)
            except StopAsyncIteration:
                break
            try:
                data: list[dict] = await self.vk_request.request(
                    method="POST",
                    url="https://api.vk.com/method/execute",
                    data={
                        "access_token": self.token.token,
                        "v": 5.131,
                        "code": script,
                    },
                )
            except exc.VkApiError as e:
                if e.error_code in VkApiCodes.token_error:
                    await self._update_token()
                elif e.error_code in VkApiCodes.too_big_data:
                    # todo change response size
                    ...
                continue
            except Exception:
                raise
            for d in data:
                print(d)


