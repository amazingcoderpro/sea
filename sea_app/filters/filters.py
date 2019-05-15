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


class DailyReportFilter(BaseFilterBackend):
    """日报显示"""

    def filter_queryset(self, request, queryset, view):
        # start_time, end_time, account=all, board = all, pin=all
        condtions = request.query_params.dict()
        # Setting default query values
        start_time = condtions.get('start_time', datetime.now().date() + timedelta(days=-7))
        end_time = condtions.get('end_time', datetime.now().date())

        set_list = queryset.filter(Q(update_time__range=(start_time, end_time)))

        search_word = condtions.get('search', '').strip()
        if search_word:
            # 查询pin_uri or board_uri or pin_description or board_nam
            set_list = set_list.filter(
                Q(pin_uri=search_word) | Q(pin_description__icontains=search_word) | Q(board_uri=search_word) | Q(
                    board_name=search_word))
        else:
            # 按选择框输入查询
            if condtions.get('pinterest_account_uri', '').strip():
                set_list = set_list.filter(Q(pinterest_account_uri=condtions.get('pinterest_account_uri').strip()))

            if condtions.get('board_uri', '').strip():
                set_list = set_list.filter(board_uri=condtions.get('board_uri').strip())

            if condtions.get('pin_uri', '').strip():
                set_list = queryset.filter(Q(pin_uri=condtions.get('pin_uri').strip()))

        # return set_list.filter(~Q(pin_uri=None))
        return set_list


