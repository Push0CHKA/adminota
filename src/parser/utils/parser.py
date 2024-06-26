from datetime import datetime
from typing import Callable

from pydantic import ValidationError

from src.core.crud.change import get_change_crud
from src.core.crud.gid import get_gid_crud
from src.core.crud.group import get_group_crud
from src.core.database.database import get_session
from src.core.log.setup_log import ParsLogger
from src.core.models.db_models import Token, Group, Change
from src.core.schemas.schemas import GidSchema, GroupSchema, ChangeSchema
from src.parser.exceptions import exc
from src.parser.schemas.vk_api_schemas import VkApiErrorCodes, VkApiParams
from src.parser.utils.reqsts import VkApiRequest
from src.parser.utils.script_maker import (
    GidScriptIterator,
    GroupScriptIterator,
)
from src.parser.utils.token_manager import get_token
from src.parser.utils.utils import get_grp_changes


class Parser:
    """Vk parser"""

    vk_request: VkApiRequest = VkApiRequest

    def __init__(self, pars_id: int):
        self.pars_id = pars_id
        self.token: Token | None = None
        self.logger: ParsLogger = ParsLogger(pars_id)

    async def run_parse_gids(self):
        try:
            await self._update_token()
        except Exception as e:
            self.logger.critical(f"Token updating failed. Error: {e}")
            raise
        try:
            await self._pars_gids()
        except Exception as e:
            self.logger.error(f"Gid parsing failed. Error: {e}")
            raise
        try:
            await self._pars_groups()
        except Exception as e:
            self.logger.error(f"Group data parsing failed. Error: {e}")
            raise

    async def _update_token(self):
        self.logger.info("Try update token for parser")
        self.token = await get_token().get_active_token()
        self.logger.info("Token was successfully updated")

    async def _upload_gid(self, data: list[list[dict]]):
        start = datetime.now()
        async with get_session() as session:
            for group_data in data:
                if not group_data:
                    self.logger.warning(
                        f"Failed mapped json data do Gid model. Json: {group_data}"
                    )
                    continue
                try:
                    if (
                        group_data[0].get("members_count", 0)
                        < VkApiParams.MIN_MEMBERS_CNT
                    ):
                        continue
                    gid = GidSchema.parse_obj(group_data[0])
                    gid.id = None
                except ValidationError:
                    continue
                await get_gid_crud().create(session, obj_in=gid)
            await get_gid_crud().commit(session)
        self.logger.info(f"Uploading gids has finished. Time: {datetime.now() - start}")

    async def _upload_group(self, data: list[list[dict]]):
        start = datetime.now()
        async with get_session() as session:
            for groups_data in data:
                if not groups_data:
                    self.logger.warning(
                        f"Failed mapped json data do group model. Json: {groups_data}"
                    )
                    continue
                for group_data in groups_data:
                    # group data validation
                    try:
                        group = GroupSchema.parse_obj(group_data)
                        group.id = None
                    except ValidationError:
                        continue

                    # Group from db (or None if not exists)
                    db_group = await get_group_crud().get_one_model(
                        session, [[{Group.group_id.name: group.group_id}]]
                    )
                    if db_group is None:
                        await get_group_crud().create(session, obj_in=group)
                        continue

                    updates, changes = get_grp_changes(
                        db_group.as_dict(), group.as_dict()
                    )
                    # update change in group data
                    if updates:
                        await get_group_crud().update(
                            session,
                            update_filter=[[{Group.group_id.name: group.group_id}]],
                            update_values=updates,
                        )
                    # add changes in changes
                    if changes:
                        await get_change_crud().create(
                            session,
                            obj_in=ChangeSchema.parse_obj(
                                {
                                    Change.group_id.name: group.group_id,
                                    Change.changes.name: changes,
                                }
                            ),
                        )
            await get_group_crud().commit(session)
        self.logger.info(
            f"Uploading group data has finished. Time: {datetime.now() - start}"
        )

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
                # todo change request size
                ...
            raise
        except Exception as e:
            self.logger.error(f"Unhandled error when parsing group ids. Error: {e}")
            raise

    async def _pars_gids(self):
        """Parsing all group ids"""
        self.logger.info("Start parsing groups id")
        # TODO get start_gid
        async for script in GidScriptIterator(self.pars_id, 1):
            try:
                await self._execute_cript(script, self._upload_gid)
            except Exception as e:
                self.logger.error(f"Execute gid script failed. Error: {e}")
                raise
        self.logger.info("Finish parsing groups id")

    async def _pars_groups(self):
        self.logger.info("Start parsing groups main data")
        async for script in GroupScriptIterator(self.pars_id):
            try:
                await self._execute_cript(script, self._upload_group)
            except Exception as e:
                self.logger.error(f"Executing group data script failed. Error: {e}")
                raise
        self.logger.info("Finish parsing groups main data")
