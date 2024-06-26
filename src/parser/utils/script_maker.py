from abc import ABC, abstractmethod
from typing import AsyncGenerator

from src.core.crud.gid import get_gid_crud
from src.parser.schemas.script_settings import VKS_MAIN_GROUP
from src.parser.schemas.script_settings import VKS_RETURN_LIST
from src.core.database.database import get_session
from src.core.log.setup_log import ParsLogger
from src.core.models.db_models import Gid
from src.parser.schemas.vk_api_schemas import MainGroupApiParams, GidApiParams


class ScriptIterator(ABC):
    """Abstract script iterator"""

    def __init__(self, pars_id: int):
        self.pars_id = pars_id
        self.generator: AsyncGenerator = self._get_script_generator()  # noqa
        self.logger: ParsLogger = ParsLogger(pars_id)

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await anext(self.generator)

    @abstractmethod
    async def _get_script_generator(self) -> AsyncGenerator:
        raise NotImplementedError


class GidScriptIterator(ScriptIterator):
    def __init__(self, pars_id: int, start_gid: int = 1):
        self.start_id = start_gid  # start group id
        super().__init__(pars_id)

    @staticmethod
    def _get_offset_limit(offset):
        return (
            offset
            + GidApiParams.GID_SCR_CNT_IN_REQ * GidApiParams.GROUPS_CNT_IN_REQ * 2
        )

    async def _get_script_generator(self):
        """Create script for all vk group id"""
        vk_script = str()  # VkScript
        gid_str = str()  # groups id str
        grp_cnt = 0  # groups count
        script_cnt = 0  # group id scripts count
        offset = self.start_id  # group id offset
        db_gids = list()  # db groups id
        for gid in range(
            self.start_id + self.pars_id,
            GidApiParams.MAX_GID,
            GidApiParams.PARSERS_CNT,
        ):
            if gid > offset:
                async with get_session() as session:
                    db_gids = await get_gid_crud().get_multi_model(
                        session=session,
                        filter_=[
                            [
                                f"{Gid.group_id.name} % {GidApiParams.PARSERS_CNT} = {self.pars_id}",
                                f"{Gid.group_id.name} > {offset}",
                                f"{Gid.group_id.name} < {self._get_offset_limit(offset)}",
                            ]
                        ],
                    )
                db_gids = [gid.group_id for gid in db_gids]
                offset += (
                    GidApiParams.GID_SCR_CNT_IN_REQ * GidApiParams.GROUPS_CNT_IN_REQ
                )
            if gid in db_gids:
                db_gids.remove(gid)
                continue
            grp_cnt += 1
            gid_str += f"{gid},"
            if (
                grp_cnt % GidApiParams.GROUPS_CNT_IN_REQ == 0
                or gid >= GidApiParams.MAX_GID - GidApiParams.PARSERS_CNT
            ):
                # create vk script
                vk_script += VKS_MAIN_GROUP.format(
                    group_ids=gid_str[:-1],
                    fields=GidApiParams.FIELDS,
                )
                gid_str = ""
                script_cnt += 1
            if (
                script_cnt % GidApiParams.GID_SCR_CNT_IN_REQ == 0 and script_cnt != 0
            ) or gid == GidApiParams.MAX_GID - self.pars_id:
                self.logger.info(f"Generate gid script. Offset: {offset}")
                yield VKS_RETURN_LIST.format(data=vk_script[:-1])
                vk_script = ""
                script_cnt = 0


class GroupScriptIterator(ScriptIterator):
    def __init__(self, pars_id):
        super().__init__(pars_id)

    async def _get_script_generator(self) -> AsyncGenerator:
        """Main groups data script"""
        script_cnt = 0  # vksrcipt count
        vk_script = str()  # vksrcipt string
        # Groups count for this parser
        async with get_session() as session:
            gid_cnt = await get_gid_crud().get_count(
                session,
                filter_=[
                    [
                        f"{Gid.group_id.name} % {MainGroupApiParams.PARSERS_CNT} = {self.pars_id}",
                        {Gid.blacklisted.name: False},
                    ]
                ],
            )
        for offset in range(0, gid_cnt, MainGroupApiParams.GROUPS_CNT_IN_REQ):
            script_cnt += 1
            # Get gids from db
            async with get_session() as session:
                gids = await get_gid_crud().get_multi_model(
                    session,
                    limit=MainGroupApiParams.GROUPS_CNT_IN_REQ,
                    offset=offset,
                    filter_=[
                        [
                            f"{Gid.group_id} % {MainGroupApiParams.PARSERS_CNT} = {self.pars_id}"
                        ]
                    ],
                )
            # Create main group data vkscript
            vk_script += VKS_MAIN_GROUP.format(
                group_ids="".join(f"{gid.group_id}," for gid in gids)[:-1],
                fields=MainGroupApiParams.FIELDS,
            )
            # Yield vkscript
            if (
                script_cnt % MainGroupApiParams.GROUP_SCR_CNT_IN_REQ == 0
                and script_cnt != 0
                or offset >= gid_cnt - MainGroupApiParams.GROUPS_CNT_IN_REQ
            ):
                self.logger.info(f"Generate group main data script. Offset: {offset}")
                yield VKS_RETURN_LIST.format(data=vk_script[:-1])
                vk_script = ""
                script_cnt = 0
