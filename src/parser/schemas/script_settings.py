VKS_MAIN_GROUP = (
    'API.groups.getById({{"group_ids": "{group_ids}", "fields": "{fields}"}}),'
)
VKS_GROUP_STAT = (
    '{{"{group_id}": API.stats.get({{"group_id": "{group_id}", "interval": "{interval}", '
    '"timestamp_from": {timestamp_from}, "timestamp_to": {timestamp_to}, '
    '"intervals_count": {intervals_count}, "extended": 1, "stats_groups": "{group_stat_param}"}})}},'
)
VKS_ADMIN_GROUP = 'API.users.get({{"user_ids": "{user_ids}", "fields": "connections,contacts,photo_200,verified"}}),'
VKS_RETURN_LIST = "return [{data}];"
