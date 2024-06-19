from typing import AsyncGenerator

from loguru import logger
from sqlalchemy import and_
from sqlalchemy import select

from src.core.configuration.script_settings import ID_GROUP_PARAMS
from src.core.configuration.script_settings import VKS_MAIN_GROUP
from src.core.configuration.script_settings import VKS_RETURN_LIST
from src.core.database.database import get_session
from src.core.models.db_models import Gid
from src.parser.schemas.vk_api_schemas import VkApiParams


class GidScriptIterator:
    """Groups id script async iterator. Create vk scripts."""

    logger = logger

    def __init__(self, pars_id: int, start_gid: int = 0):
        self.pars_id = pars_id  # parser id
        self.start_id = start_gid  # start group id
        self.generator = self._get_gid_script()

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await anext(self.generator)

    async def _get_gid_script(self) -> AsyncGenerator:
        """Create script for all vk group id"""
        vk_script = str()  # VkScript
        gid_str = str()  # groups id str
        grp_cnt = 0  # groups count
        script_cnt = 0  # group id scripts count
        offset = self.start_id  # group id offset
        db_gids = list()  # db groups id
        for gid in range(
            self.start_id + self.pars_id,
            VkApiParams.MAX_GID,
            VkApiParams.pars_cnt,
        ):
            if gid > offset:
                async with get_session() as session:
                    db_gids = await session.execute(
                        select(Gid.group_id).where(
                            and_(
                                Gid.group_id % VkApiParams.pars_cnt == self.pars_id,
                                Gid.group_id > offset,
                                Gid.group_id
                                < offset
                                + VkApiParams.gid_scr_cnt * VkApiParams.grp_cnt_req,
                            )
                        )
                    )
                    db_gids = db_gids.scalars().all()
                db_gids = [gid for gid in db_gids]
                offset += VkApiParams.gid_scr_cnt * VkApiParams.grp_cnt_req
            if gid in db_gids:
                db_gids.remove(gid)
                continue
            grp_cnt += 1
            gid_str += f"{gid},"
            if (
                grp_cnt % VkApiParams.grp_cnt_req == 0
                or gid >= VkApiParams.MAX_GID - VkApiParams.pars_cnt
            ):
                # create vk script
                vk_script += VKS_MAIN_GROUP.format(
                    group_ids=gid_str[:-1],
                    fields=ID_GROUP_PARAMS,
                )
                gid_str = ""
                script_cnt += 1
            if (
                script_cnt % VkApiParams.gid_scr_cnt == 0 and script_cnt != 0
            ) or gid == VkApiParams.MAX_GID - self.pars_id:
                self.logger.debug(
                    f"Parser №{self.pars_id}({VkApiParams.pars_cnt}) "
                    f"get group id. Offset: {offset}"
                )
                yield VKS_RETURN_LIST.format(data=vk_script[:-1])
                vk_script = ""
                script_cnt = 0
