from dataclasses import dataclass


@dataclass
class VkApiSettings:
    ATTEMPT_COUNT: int = 5
    TIMEOUT: int = 30


@dataclass
class VkApiParams:
    API_VERSION: float = 5.131
    MAX_GID: int = 1000000
    MIN_MEMBERS_CNT: int = 1
    PARSERS_CNT: int = 2


class MainGroupApiParams(VkApiParams):
    """Main groups data params"""

    GROUPS_CNT_IN_REQ: int = 450
    GROUP_SCR_CNT_IN_REQ: int = 10
    FIELDS: str = (
        "members_count,activity,addresses,age_limits,"
        "ban_info,city,contacts,counters,country,cover,"
        "description,fixed_post,has_photo,links,main_album_id,"
        "main_section,market,place,public_date_label,site,"
        "status,trending,verified,wall,wiki_page"
    )


class GidApiParams(VkApiParams):
    """Gid params"""

    GROUPS_CNT_IN_REQ: int = 450
    GID_SCR_CNT_IN_REQ: int = 20
    FIELDS = "members_count,contacts"


@dataclass
class VkApiErrorCodes:
    """Vk API error codes"""

    TOKEN_ERROR = [5]
    TOO_BIG_DATA = [13]
