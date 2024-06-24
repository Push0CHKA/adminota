from dataclasses import dataclass


@dataclass
class VkApiSettings:
    ATTEMPT_COUNT: int = 5
    TIMEOUT: int = 30


@dataclass
class VkApiParams:
    API_VERSION: float = 5.131
    MAX_GID: int = 1000000
    MIN_MEMBERS_CNT: int = 10000
    pars_cnt: int = 2
    grp_cnt_req: int = 450
    req_timeout: int = 15
    grp_scr_cnt: int = 10
    gid_scr_cnt: int = 20
    stat_scr_cnt: int = 20
    adm_scr_cnt: int = 20


@dataclass
class VkApiErrorCodes:
    """Vk API error codes"""

    TOKEN_ERROR = [5]
    TOO_BIG_DATA = [13]
