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

