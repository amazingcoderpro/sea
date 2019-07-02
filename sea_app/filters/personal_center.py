from datetime import datetime, timedelta
from functools import reduce

from rest_framework.filters import BaseFilterBackend
from django.db.models import Q

# class UserFilter(BaseFilterBackend):
#     """用户列表过滤"""
#
#     def filter_queryset(self, request, queryset, view):
#         parent_id = request.user.parent_id
#         if not parent_id:
#             return queryset.filter(Q(parent_id=request.user.id) | Q(id=request.user.id))
#         return queryset.filter(id=request.user.id)


# class RoleFilter(BaseFilterBackend):
#     """角色列表 站长不显示"""
#
#     def filter_queryset(self, request, queryset, view):
#         queryset_list = []
#         set_list = queryset.filter(user_id=request.user.id)
#         if not set_list:
#             return queryset_list
#         for item in set_list:
#             if item.name in ["站长", "管理员"]:
#                 continue
#             queryset_list.append(item)
#         return queryset_list
from sea_app import models


class PostTimeFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        account_list = request.query_params.get("account_list", "[]")
        return queryset.filter(user_id=request.user.id, id__in=eval(account_list))


class SelectPostTimeFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        account_id = request.query_params.get("account_id", None)
        try:
            queryobj = models.PinterestAccount.objects.get(pk=account_id)
        except:
            return None
        total_time = eval(queryobj.post_time)
        # 查询此账号下，所有的rule
        rule_ids = models.Rule.objects.filter(pinterest_account_id=account_id, state__in=[-1,0,1,2]).values_list('id', flat=True)
        # 查询已使用过的时间
        result_list = models.RuleSchedule.objects.filter(rule_id__in=rule_ids).values("weekday", "post_time")
        time_dict = {}
        for res in result_list:
            key = {0: "mon", 1: "tues", 2: "wed", 3: "thur", 4: "fri", 5: "sat", 6: "sun"}[res["weekday"]]
            if key not in time_dict:
                time_dict.update({key: [res["post_time"], ] if res["post_time"] else []})
            else:
                if res["post_time"]:
                    time_dict[key].append(res["post_time"])
        # 给每一个时间节点加一个状态（"0:00",1）
        for item in total_time.values():
            new_item = []
            for t in item["time"]:
                new_item.append({"T": t, "S": 1})
            item["time"] = new_item

        for day in total_time.keys():
            if day == "every" or total_time[day]["state"] == 0 or day not in time_dict:
                continue
            for t in total_time[day]["time"]:
                if t["T"] in time_dict[day]:
                    total_time[day]["time"]["S"] = 0
        total_time.pop("every")
        # 组装item_list
        item_list = []
        for item in total_time.values():
            if item["state"] == 1:
                item_list.append([t["T"] for t in item["time"]])
        total_time["every"] = {"state": 1, "time": item_list}
        return total_time

    def intersection_for_multi_list(self, item_list):
        fm = lambda x, y: list(set(x).intersection(set(y))) if isinstance(x, list) and isinstance(y, list) else 'error'
        fn = lambda x: x[0] if len(x) == 1 else [] if len(x) == 0 else reduce(fm, tuple(y for y in x))
        item_list = fn(item_list)
        return sorted(item_list)
