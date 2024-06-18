from dataclasses import dataclass

from pydantic import BaseModel

from src.core.schemas.common import singleton


@dataclass
class RequestSettings:
    attempt_count: int = 5
    timeout: int = 30


@dataclass
class VkApiCodes:
    token_error = [400]
    too_big_data = [13]
    server_error = [500]


@singleton
class VkApiParams(BaseModel):
    version: float = 5.131
    max_gid: int = 2000000000
    pars_cnt: int = 10
    min_memb_cnt: int = 10000
    grp_cnt_req: int = 10
    req_timeout: int = 15
    grp_scr_cnt: int = 10
    gid_scr_cnt: int = 20
    stat_scr_cnt: int = 20
    adm_scr_cnt: int = 20
