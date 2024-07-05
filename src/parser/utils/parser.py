from typing import Callable

from pydantic import ValidationError

from src.core.crud.change import get_change_crud
from src.core.crud.gid import get_gid_crud
from src.core.crud.group import get_group_crud
from src.core.crud.group_stat import get_group_stat_crud
from src.core.database.database import get_session
from src.core.log.setup_log import ParsLogger
from src.core.models.db_models import Token, Group, Change, Gstat
from src.core.schemas.schemas import GidSchema, GroupSchema, ChangeSchema, GstatSchema
from src.parser.exceptions import exc
from src.parser.exceptions.exc import get_tb
from src.parser.schemas.vk_api_schemas import VkApiErrorCodes, VkApiParams
from src.parser.utils.reqsts import VkApiRequest
from src.parser.utils.script_maker import (
    GidScriptIterator,
    GroupScriptIterator,
    GstatIterator,
)
from src.parser.utils.token_manager import get_token
from src.parser.utils.utils import get_grp_changes, get_group_stat_changes


class Parser:
    """Vk parser"""

    vk_request: VkApiRequest = VkApiRequest

    def __init__(self, pars_id: int):
        self.pars_id = pars_id
        self.token: Token | None = None
        self.logger: ParsLogger = ParsLogger(pars_id)

    async def _update_token(self):
        self.logger.info("Try update token for parser")
        self.token = await get_token().get_active_token()
        self.logger.info("Token was successfully updated")

    async def _upload_gid(self, data: list[list[dict]]):
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
                    gid = GidSchema.model_validate(group_data[0])
                except ValidationError:
                    continue
                await get_gid_crud().create(session, obj_in=gid)
            await get_gid_crud().commit(session)

    async def _upload_group(self, data: list[list[dict]]):
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
                        group = GroupSchema.model_validate(group_data)
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
                            obj_in=ChangeSchema.model_validate(
                                {
                                    Change.group_id.name: group.group_id,
                                    Change.changes.name: changes,
                                }
                            ),
                        )
            await get_group_crud().commit(session)

    async def _upload_group_stat(self, data: list[dict], **kwargs):
        if not data:
            self.logger.warning(
                f"Failed mapped json data do group statistic model. Json: {data}"
            )
        async with get_session() as session:
            for group_stat in data:
                for gid, data in group_stat.items():
                    if isinstance(data, bool):
                        grp_stt = {"group_id": int(gid)}
                    elif isinstance(data, list):
                        grp_stt = data[0]
                        grp_stt["group_id"] = int(gid)
                    else:
                        self.logger.error(
                            "Unhandled group statistic response. Data: data"
                        )
                        continue
                    grp_stt["interval"] = kwargs["interval"]
                    # group statistic data validation
                    try:
                        stat = GstatSchema.model_validate(grp_stt)
                    except ValidationError as e:
                        self.logger.warning(
                            f"Failed mapped json data do group statistic model. "
                            f"Json: {group_stat}. Error: {e}"
                        )
                        continue
                    # Group from db (or None if not exists)
                    db_stat = await get_group_stat_crud().get_one_model(
                        session,
                        [
                            [
                                {Gstat.group_id.name: stat.group_id},
                                {Gstat.interval.name: kwargs["interval"]},
                            ],
                        ],
                    )

                    # new stat
                    if db_stat is None:
                        await get_group_stat_crud().create(session, obj_in=stat)
                        continue

                    # upload changes
                    if changes := get_group_stat_changes(
                        db_stat.as_dict(), stat.as_dict()
                    ):
                        await get_group_stat_crud().update(
                            session,
                            update_filter=[
                                [
                                    {Gstat.group_id.name: stat.group_id},
                                    {Gstat.interval.name: kwargs["interval"]},
                                ]
                            ],
                            update_values=changes,
                        )
            await get_group_stat_crud().commit(session)

    async def _execute_cript(self, script: str, upload: Callable, **kwargs):
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
                ),
                **kwargs,
            )
        except exc.VkApiError as e:
            if e.error_code in VkApiErrorCodes.TOKEN_ERROR:
                self.logger.debug(f"Received token error [{e.error_code}, {e.message}]")
                await self._update_token()
            elif e.error_code in VkApiErrorCodes.TOO_BIG_DATA:
                self.logger.debug(
                    f"Received too big response size [{e.error_code}, {e.message}]"
                )
                # todo change request size
                ...
        except Exception as e:
            self.logger.error(
                f"Unhandled error when parsing group ids. Traceback {get_tb(e)}"
            )
            raise

    async def _pars_gids(self):
        """Parsing all group ids"""
        self.logger.info("Start parsing groups id")
        # TODO get start_gid
        async for script in GidScriptIterator(self.pars_id, 1):
            try:
                await self._execute_cript(script, self._upload_gid)
            except Exception:
                self.logger.error("Execute gid script failed.")
                raise
        self.logger.info("Finish parsing groups id")

    async def _pars_groups(self):
        self.logger.info("Start parsing groups main data")
        async for script in GroupScriptIterator(self.pars_id):
            try:
                await self._execute_cript(script, self._upload_group)
            except Exception as e:
                self.logger.error(
                    f"Executing group data script failed. Traceback {get_tb(e)}"
                )
                raise
        self.logger.info("Finish parsing groups main data")

    async def _parse_groups_stat(self):
        self.logger.info("Start parsing group statistic")
        async for script, interval in GstatIterator(self.pars_id):
            try:
                await self._execute_cript(
                    script, self._upload_group_stat, interval=interval
                )
            except Exception as e:
                self.logger.error(
                    f"Executing group statistic script failed. Traceback {get_tb(e)}"
                )
                raise
        self.logger.info("Finish parsing group statistic")

    async def run_parse_gids(self):
        try:
            await self._update_token()
        except Exception as e:
            self.logger.critical(f"Token updating failed. {get_tb(e)}")
            raise
        try:
            await self._pars_gids()
        except Exception as e:
            self.logger.error(f"Gid parsing failed. Error: {get_tb(e)}")
            raise
        try:
            await self._pars_groups()
        except Exception as e:
            self.logger.error(f"Group data parsing failed. Error: {get_tb(e)}")
            raise
        try:
            await self._parse_groups_stat()
        except Exception as e:
            self.logger.error(f"Group data parsing failed. Error: {get_tb(e)}")
            raise
