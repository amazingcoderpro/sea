from datetime import datetime, timedelta

from rest_framework.filters import BaseFilterBackend
from django.db.models import Q


class UserFilter(BaseFilterBackend):
    """用户列表过滤"""

    def filter_queryset(self, request, queryset, view):
        parent_id = request.user.parent_id
        if parent_id:
            return queryset.filter(Q(parent_id=parent_id) | Q(id=parent_id))
        return queryset.filter(id=request.user.id)


class RoleFilter(BaseFilterBackend):
    """角色列表 站长不显示"""

    def filter_queryset(self, request, queryset, view):
        queryset_list = []
        set_list = queryset.filter(user_id=request.user.id)
        if not set_list:
            return queryset_list
        for item in set_list:
            if item.name in ["站长", "管理员"]:
                continue
            queryset_list.append(item)
        return queryset_list


class SubAccountFilter(BaseFilterBackend):
    """分账号显示"""

    def filter_queryset(self, request, queryset, view):
        condtions = request.query_params.dict()
        set_list = queryset.filter(Q(name=condtions.get('name')) | Q(account_uri=condtions.get('account_uri')))
        return set_list


class PinFilter(BaseFilterBackend):
    """分Pin显示"""

    def filter_queryset(self, request, queryset, view):
        # start_time, end_time, account=all, board = all, pin=all
        condtions = request.query_params.dict()
        # Setting default query values
        start_time = condtions.get('start_time',datetime.now().date() + timedelta(days=-7))
        end_time = condtions.get('end_time',datetime.now().date())

        search_word = condtions.get('search', '').strip()
        if search_word:
            # 查询pin_uri or board_uri or pin_description or board_nam
            set_list = queryset.filter(
                Q(pin_uri=search_word) | Q(description__icontains=search_word) | Q(board__board_uri=search_word) | Q(board__name=search_word),
                Q(update_time__range=(start_time, end_time))
            )
        else:
            # 按选择框输入查询
            if condtions.get('pin_id', '').strip():
                set_list = queryset.filter(Q(id=condtions.get('pin_id').strip()),
                        Q(update_time__range=(start_time, end_time)))
            else:
                set_list = queryset.filter(Q(update_time__range=(start_time, end_time)))

            if condtions.get('board_id', '').strip():
                set_list = set_list.filter(board__id=condtions.get('board_id').strip())

            if condtions.get('pinterest_account_id', '').strip():
                set_list = set_list.filter(board__pinterest_account__id=condtions.get('pinterest_account_id').strip())

        return set_list
