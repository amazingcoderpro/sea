from datetime import datetime, timedelta

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
            if res[0] not in time_dict:
                time_dict.update({res[0]: [res[1], ]})
            else:
                time_dict[res[0]].append(res[1])
        for day in total_time.keys():
            [total_time[day].remove(t) for t in total_time[day] if t in time_dict[day]]
        return total_time