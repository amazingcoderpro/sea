from datetime import datetime, timedelta

from rest_framework.filters import BaseFilterBackend
from django.db.models import Q

from sea_app import models


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


class AccountListFilter(BaseFilterBackend):
    """账户列表管理 过滤器"""
    def filter_queryset(self, request, queryset, view):
        # 获取当前用户的所有子账号
        condtions = request.query_params.dict()
        user_id = condtions.get('user_id')
        account_set = models.PinterestAccount.objects.filter(user_id=user_id)
        account_id_list = []
        for account in account_set:
            account_id_list.append(account.id)
        # 获取所有子账号最近两天的数据
        today_date = datetime.today().date() + timedelta(days=-1)
        today_data_set = queryset.filter(Q(update_time__range=(today_date, today_date+timedelta(days=1))),
                                     Q(pinterest_account_id__in=account_id_list))
        yesterday_data_set = queryset.filter(Q(update_time__range=(today_date+timedelta(days=-1), today_date)),
                                     Q(pinterest_account_id__in=account_id_list))
        today_group_dict = self.get_data(today_data_set)
        yesterday_group_dict = self.get_data(yesterday_data_set)
        for p_id, info in today_group_dict.items():
            all_pin_id = set(filter(lambda x: x, info["pins"]))
            info["account_publish_time"] = models.Pin.objects.filter(Q(id__in=all_pin_id)).order_by('-publish_time').first().publish_time
            info["pins"] = len(all_pin_id)
            yesterday_info = yesterday_group_dict.get(p_id)
            if yesterday_info:
                yesterday_pins = len(set(filter(lambda x: x, yesterday_info.get("pins", 0))))
                yesterday_repin = yesterday_info.get("repin", 0)
                yesterday_like = yesterday_info.get("like", 0)
                yesterday_comment = yesterday_info.get("comment", 0)
            else:
                yesterday_pins = yesterday_repin = yesterday_like = yesterday_comment = 0
            info["pins_increment"] = info["pins"] - yesterday_pins
            info["repin_increment"] = info["repin"] - yesterday_repin
            info["like_increment"] = info["like"] - yesterday_like
            info["comment_increment"] = info["comment"] - yesterday_comment
        account_list = []
        for index, d in enumerate(today_group_dict.items()):
            p_id, info = d
            info["pinterest_account_id"] = p_id
            info["index"] = index + 1
            # 获取相关联的board_id
            today_publish_board = models.PublishRecord.objects.filter(Q(execute_time__range=(today_date, today_date+timedelta(days=1))),
                                                                      Q(board__pinterest_account_id=p_id))
            info["finished"] = today_publish_board.filter(state=1).count()
            info["pending"] = today_publish_board.filter(state=0).count()
            info["failed"] = today_publish_board.filter(state=2).count()
            account_list.append(info)
        return account_list

    def get_data(self, data_set):
        group_dict = {}
        for today in data_set:
            if today.pinterest_account_id not in group_dict:
                group_dict[today.pinterest_account_id] = {
                    "account_name": today.pinterest_account.name,
                    "account_email": today.pinterest_account.email,
                    "account_create_time": today.pinterest_account.create_time,
                    "account_type": today.pinterest_account.type,
                    "update_person": today.pinterest_account.user.username,
                    "account_state": today.pinterest_account.state,
                    "account_crawl_time": today.pinterest_account.update_time,
                    "pins": [] if not today.pin_id else [today.pin_id],  # pin数
                    "repin": today.pin_repin,
                    "like": today.pin_like,
                    "comment": today.pin_comment,
                }
            else:
                group_dict[today.pinterest_account_id]["pins"].append(today.pin_id)
                group_dict[today.board_id]["repin"] += today.pin_repin
                group_dict[today.board_id]["like"] += today.pin_like
                group_dict[today.board_id]["comment"] += today.pin_comment
        return group_dict

