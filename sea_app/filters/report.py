from datetime import datetime, timedelta

from rest_framework.filters import BaseFilterBackend
from django.db.models import Q


class DailyReportFilter(BaseFilterBackend):
    """日报显示"""

    def filter_queryset(self, request, queryset, view):
        # start_time, end_time, account=all, board = all, pin=all
        condtions = request.query_params.dict()
        # Setting default query values
        start_time = condtions.get('start_time', datetime.now() + timedelta(days=-7))
        end_time = condtions.get('end_time', datetime.now())
        store_url = condtions.get('store_url')
        if store_url:
            store_url = store_url.strip()
            set_list = queryset.filter(Q(update_time__range=(start_time, end_time)), Q(store_url=store_url))
        else:
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


class DashBoardFilter(BaseFilterBackend):
    """DashBoard 时间过滤"""

    def filter_queryset(self, request, queryset, view):
        condtions = request.query_params.dict()
        start_time = condtions.get('start_time', datetime.now() + timedelta(days=-7))
        end_time = condtions.get('end_time', datetime.now())
        store_url = condtions.get('store_url')
        if store_url:
            store_url = store_url.strip()
            set_list = queryset.filter(Q(update_time__range=(start_time, end_time)), Q(store_url=store_url))
        else:
            set_list = queryset.filter(Q(update_time__range=(start_time, end_time)))
        return set_list