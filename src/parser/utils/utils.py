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


def is_change_addr(old: dict | None, new: dict | None) -> bool:
    """Check changes in address"""
    if old is None and new is None:
        return True

    if (
        old.get("count") != new.get("count")
        or old.get("is_enabled") != new.get("is_enabled")
        or old.get("main_address_id") != new.get("main_address_id")
    ):
        return True

    return False


def get_grp_changes(old: dict, new: dict) -> tuple[dict, dict]:
    updates = dict()
    changes = dict()
    for k in new:
        if (
            k in [Group.photo.name, Group.cover.name]
            and cut_photo_url(old[k]) != cut_photo_url(new[k])
            or k == Group.contacts.name
            and get_cid(old[k]) != get_cid(new[k])
            or k == Group.addresses.name
            and old[k] != new[k]
            and is_change_addr(old[k], new[k])
            or old[k] != new[k]
            and k
            not in [
                Group.photo.name,
                Group.activity.name,  # TODO delete when vk api will fix
                Group.members_count.name,
                Group.contacts.name,
                Group.market.name,
            ]
        ):
            updates[k] = new[k]
            changes[k] = {"old": old[k], "new": new[k]}

        # check members count (need only for updates)
        if k == Group.members_count.name and old[k] != new[k]:
            updates[k] = new[k]

    return updates, changes


def get_group_stat_changes(old: dict, new: dict) -> dict:
    """Return group stat changes"""
    updates = dict()
    for k in new:
        if old[k] != new[k]:
            updates[k] = new[k]
    return updates


def get_time(tz: int = 3) -> str:
    return datetime.now(timezone(timedelta(hours=tz))).strftime("%H:%M")


def now_unix_time():
    """Return unix time"""
    return int(datetime.timestamp(datetime.now() + timedelta(hours=3)))


def get_days_ago_time(days: int):
    """Return days ago time
    :param days: Days count
    :return: Unix time
    """
    return int(datetime.timestamp(datetime.now() - timedelta(days=days)))
