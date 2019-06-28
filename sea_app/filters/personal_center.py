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
        queryobj = models.PinterestAccount.objects.get(pk=account_id)
        total_time = eval(queryobj.post_time)
        # 查询此账号下，所有的rule
        rule_ids = models.Rule.objects.filter(pinterest_account_id=account_id).values_list('id', flat=True)
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
        for day in total_time.keys():
            if day == "every":
                continue
            [total_time[day].remove(t) for t in total_time[day] if t in time_dict[day]]
        total_time.pop("every")
        total_time["every"] = self.intersection_for_multi_list(total_time.values())
        return total_time

    def intersection_for_multi_list(self, item_list):
        fm = lambda x, y: list(set(x).intersection(set(y))) if isinstance(x, list) and isinstance(y, list) else 'error'
        fn = lambda x: x[0] if len(x) == 1 else [] if len(x) == 0 else reduce(fm, tuple(y for y in x))
        item_list = fn(item_list)
        return sorted(item_list)