from datetime import datetime, timezone, timedelta

from src.core.models.db_models import Group


def cut_photo_url(photo_url: str) -> str:
    return photo_url.split("userapi.com")[-1].replace("c_uniq_tag", "u")


def get_grp_changes(old: dict, new: dict) -> tuple[dict, dict]:
    updates = dict()
    changes = dict()
    for k in new:
        if (
            k == Group.photo.name
            and cut_photo_url(old[k]) != cut_photo_url(new[k])
            or old[k] != new[k]
            and k != Group.id.name
            and k != Group.photo.name
            and k != Group.activity.name
        ):
            updates[k] = new[k]
            changes[k] = {"old": old[k], "new": new[k]}
    return updates, changes


def get_time(tz: int = 3) -> str:
    return datetime.now(timezone(timedelta(hours=tz))).strftime("%H:%M")
