from datetime import datetime, timezone, timedelta

from src.core.models.db_models import Group


def cut_photo_url(photo_url: str) -> str | None:
    if photo_url is None:
        return
    return photo_url.split("userapi.com")[-1].replace("c_uniq_tag", "u")


def get_cid(contacts: list | None) -> list[int] | None:
    """return list with vk user id"""
    if contacts is None:
        return None
    cont_list = list()
    for contact in contacts:
        if contact.get("user_id"):
            cont_list.append(contact.get("user_id"))
    return cont_list


def get_grp_changes(old: dict, new: dict) -> tuple[dict, dict]:
    updates = dict()
    changes = dict()
    for k in new:
        if (
            k in [Group.photo.name, Group.cover.name]
            and cut_photo_url(old[k]) != cut_photo_url(new[k])
            or k == Group.contacts.name
            and get_cid(old[k]) != get_cid(new[k])
            or old[k] != new[k]
            and k != Group.id.name
            and k != Group.photo.name
            and k != Group.activity.name
            and k != Group.members_count.name
            and k != Group.contacts.name
            and k != Group.market.name
        ):
            updates[k] = new[k]
            changes[k] = {"old": old[k], "new": new[k]}

        # check members count (need only for updates)
        if k == Group.members_count.name and old[k] != new[k]:
            updates[k] = new[k]

    return updates, changes


def get_time(tz: int = 3) -> str:
    return datetime.now(timezone(timedelta(hours=tz))).strftime("%H:%M")
