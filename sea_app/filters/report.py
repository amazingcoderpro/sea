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
        account_set = models.PinterestAccount.objects.filter(user=request.user)
        account_id_list = []
        for account in account_set:
            account_id_list.append(account.id)
        # 获取所有子账号最近两天的数据
        today_date = datetime.today().date()
        today_data_set = queryset.filter(Q(update_time__range=(today_date, today_date + timedelta(days=1))),
                                         Q(pinterest_account_id__in=account_id_list))
        yesterday_data_set = queryset.filter(Q(update_time__range=(today_date + timedelta(days=-1), today_date)),
                                             Q(pinterest_account_id__in=account_id_list))
        today_group_dict = self.get_data(today_data_set)
        yesterday_group_dict = self.get_data(yesterday_data_set)
        for a_id, info in today_group_dict.items():
            # 获取账号增量
            pin_id_under_account = set(filter(lambda x: x, info["pins"]))
            info["account_publish_time"] = models.Pin.objects.filter(Q(id__in=pin_id_under_account)).order_by('-publish_time').first().publish_time.strftime("%Y-%m-%d %H:%M:%S")
            info["pins"] = len(pin_id_under_account)
            yesterday_info = yesterday_group_dict.get(a_id)
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
        # 添加发布数，并整理输出结果
        account_list = []
        for index, a in enumerate(today_group_dict.items()):
            a_id, info = a
            info["pinterest_account_id"] = a_id
            info["index"] = index + 1
            # 获取账号数据相关联的board_id
            today_publish_account = models.PublishRecord.objects.filter(
                Q(execute_time__range=(today_date, today_date + timedelta(days=1))),
                Q(board__pinterest_account_id=a_id))
            info["finished"] = today_publish_account.filter(state=1).count()
            info["pending"] = today_publish_account.filter(state=0).count()
            info["failed"] = today_publish_account.filter(state=2).count()
            account_list.append(info)
        return account_list

    def get_data(self, data_set):
        group_dict = {}
        for today in data_set:
            if today.pinterest_account_id not in group_dict:
                # 获取账号数据
                group_dict[today.pinterest_account_id] = {
                    "account_uri": today.pinterest_account.account_uri,
                    "account_name": today.pinterest_account.nickname,
                    "account_email": today.pinterest_account.email,
                    "account_description": today.pinterest_account.description,
                    "account_create_time": today.pinterest_account.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "account_type": today.pinterest_account.type,
                    "account_authorized": today.pinterest_account.authorized,
                    "update_person": today.pinterest_account.user.username,
                    "account_state": today.pinterest_account.state,
                    "account_crawl_time": today.pinterest_account.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "pins": [] if not today.pin_id else [today.pin_id],  # pin数
                    "repin": today.pin_repin,
                    "like": today.pin_like,
                    "comment": today.pin_comment,
                }
            else:
                group_dict[today.pinterest_account_id]["pins"].append(today.pin_id)
                group_dict[today.pinterest_account_id]["repin"] += today.pin_repin
                group_dict[today.pinterest_account_id]["like"] += today.pin_like
                group_dict[today.pinterest_account_id]["comment"] += today.pin_comment
        return group_dict


class BoardListFilter(BaseFilterBackend):
    """board 列表管理 过滤器"""
    def filter_queryset(self, request, queryset, view):
        account_id = request._request.resolver_match.kwargs['aid']
        board_set = models.Board.objects.filter(pinterest_account_id=account_id)
        board_id_list = []
        for board in board_set:
            board_id_list.append(board.id)
        # 获取所有board最近两天的数据
        today_date = datetime.today().date()
        today_data_set = queryset.filter(Q(update_time__range=(today_date, today_date + timedelta(days=1))),
                                         Q(board_id__in=board_id_list))
        yesterday_data_set = queryset.filter(Q(update_time__range=(today_date + timedelta(days=-1), today_date)),
                                             Q(board_id__in=board_id_list))
        today_group_dict = self.get_data(today_data_set)
        yesterday_group_dict = self.get_data(yesterday_data_set)
        # 获取board增量
        for b_id, b_info in today_group_dict.items():
            b_info["pins"] = len(set(filter(lambda x: x, b_info["pins"])))

            yesterday_b_info = yesterday_group_dict.get("b_id")
            if yesterday_b_info:
                yesterday_pins = len(set(filter(lambda x: x, yesterday_b_info.get("pins", 0))))
                yesterday_repin = yesterday_b_info.get("repin", 0)
                yesterday_like = yesterday_b_info.get("like", 0)
                yesterday_comment = yesterday_b_info.get("comment", 0)
            else:
                yesterday_pins = yesterday_repin = yesterday_like = yesterday_comment = 0
            b_info["pins_increment"] = b_info["pins"] - yesterday_pins
            b_info["repin_increment"] = b_info["repin"] - yesterday_repin
            b_info["like_increment"] = b_info["like"] - yesterday_like
            b_info["comment_increment"] = b_info["comment"] - yesterday_comment
        # 获取board发布数据
        boards_list = []
        for b_index, b in enumerate(today_group_dict.items()):
            b_id, b_info = b
            b_info["board_id"] = b_id
            b_info["index"] = b_index + 1
            today_publish_board = models.PublishRecord.objects.filter(
                Q(execute_time__range=(today_date, today_date + timedelta(days=1))),
                Q(board_id=b_id))
            b_info["finished"] = today_publish_board.filter(state=1).count()
            b_info["pending"] = today_publish_board.filter(state=0).count()
            b_info["failed"] = today_publish_board.filter(state=2).count()
            boards_list.append(b_info)
        return boards_list

    def get_data(self, data_set):
        group_dict = {}
        for today in data_set:
            if today.board_id not in group_dict:
                group_dict[today.board_id] = {
                    "board_uri": today.board.board_uri,
                    "board_description": today.board.description,
                    "board_state": today.board.state,
                    "pins": [] if not today.pin_id else [today.pin_id],  # pin数
                    "repin": today.pin_repin,
                    "like": today.pin_like,
                    "comment": today.pin_comment,
                }
            else:
                group_dict[today.board_id]["pins"].append(today.pin_id)
                group_dict[today.board_id]["repin"] += today.pin_repin
                group_dict[today.board_id]["like"] += today.pin_like
                group_dict[today.board_id]["comment"] += today.pin_comment
        return group_dict


class PinListFilter(BaseFilterBackend):
    """pin 列表管理 过滤器"""

    def filter_queryset(self, request, queryset, view):
        account_id = request._request.resolver_match.kwargs['aid']
        board_id = request._request.resolver_match.kwargs['bid']
        pin_set = models.Pin.objects.filter(board_id=board_id)
        pin_id_list = []
        for pin in pin_set:
            pin_id_list.append(pin.id)
        # 获取所有pin最近两天的数据
        today_date = datetime.today().date()
        today_data_set = queryset.filter(Q(update_time__range=(today_date, today_date + timedelta(days=1))),
                                         Q(pin_id__in=pin_id_list))
        yesterday_data_set = queryset.filter(Q(update_time__range=(today_date + timedelta(days=-1), today_date)),
                                             Q(pin_id__in=pin_id_list))
        today_group_dict = self.get_data(today_data_set)
        yesterday_group_dict = self.get_data(yesterday_data_set)
        # 获取pin增量
        for p_id, p_info in today_group_dict.items():
            yesterday_p_info = yesterday_group_dict.get("p_id")
            if yesterday_p_info:
                yesterday_view = yesterday_p_info.get("view", 0)
                yesterday_repin = yesterday_p_info.get("repin", 0)
                yesterday_like = yesterday_p_info.get("like", 0)
                yesterday_comment = yesterday_p_info.get("comment", 0)
            else:
                yesterday_view = yesterday_repin = yesterday_like = yesterday_comment = 0
            p_info["view_increment"] = p_info["view"] - yesterday_view
            p_info["repin_increment"] = p_info["repin"] - yesterday_repin
            p_info["like_increment"] = p_info["like"] - yesterday_like
            p_info["comment_increment"] = p_info["comment"] - yesterday_comment
            p_info["under_board_id"] = board_id
            p_info["under_account_id"] = account_id
        # 获取pin数据
        pins_list = []
        for p_index, p in enumerate(today_group_dict.items()):
            p_id, p_info = p
            p_info["pin_id"] = p_id
            p_info["index"] = p_index + 1
            pins_list.append(p_info)
        return pins_list

    def get_data(self, data_set):
        group_dict = {}
        for today in data_set:
            if today.board_id not in group_dict:
                group_dict[today.pin_id] = {
                    "pin_uri": today.pin.pin_uri,
                    "pin_thumbnail": today.pin.thumbnail,
                    "pin_description": today.pin.description,
                    "pin_url": today.pin.url,
                    "product_sku": today.pin.product.sku,
                    "view": today.pin_views,
                    "repin": today.pin_repin,
                    "like": today.pin_like,
                    "comment": today.pin_comment,
                }
            else:
                group_dict[today.pin_id]["view"] += today.pin_views
                group_dict[today.pin_id]["repin"] += today.pin_repin
                group_dict[today.pin_id]["like"] += today.pin_like
                group_dict[today.pin_id]["comment"] += today.pin_comment
        return group_dict


# 以下AccountListFilter_b类暂未使用，作为备用
class AccountListFilter_b(BaseFilterBackend):
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
        today_date = datetime.today().date()
        today_data_set = queryset.filter(Q(update_time__range=(today_date, today_date+timedelta(days=1))),
                                     Q(pinterest_account_id__in=account_id_list))
        yesterday_data_set = queryset.filter(Q(update_time__range=(today_date+timedelta(days=-1), today_date)),
                                     Q(pinterest_account_id__in=account_id_list))

        today_group_dict = self.get_data(today_data_set)
        yesterday_group_dict = self.get_data(yesterday_data_set)
        for a_id, info in today_group_dict.items():
            # 获取账号增量
            pin_id_under_account = set(filter(lambda x: x, info["pins"]))
            info["account_publish_time"] = models.Pin.objects.filter(Q(id__in=pin_id_under_account)).order_by('-publish_time').first().publish_time
            info["pins"] = len(pin_id_under_account)
            yesterday_info = yesterday_group_dict.get(a_id)
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
            # 获取board增量
            for b_id, b_info in info["board_list"].items():
                pin_id_under_board = set(filter(lambda x: x, b_info["pins"]))
                b_info["pins"] = len(pin_id_under_board)
                try:
                    yesterday_b_info = yesterday_group_dict.get(a_id)["board_list"].get("b_id")
                    if yesterday_b_info:
                        yesterday_pins = len(set(filter(lambda x: x, yesterday_b_info.get("pins", 0))))
                        yesterday_repin = yesterday_b_info.get("repin", 0)
                        yesterday_like = yesterday_b_info.get("like", 0)
                        yesterday_comment = yesterday_b_info.get("comment", 0)
                    else:
                        yesterday_pins = yesterday_repin = yesterday_like = yesterday_comment = 0
                except:
                    yesterday_pins = yesterday_repin = yesterday_like = yesterday_comment = 0
                b_info["pins_increment"] = b_info["pins"] - yesterday_pins
                b_info["repin_increment"] = b_info["repin"] - yesterday_repin
                b_info["like_increment"] = b_info["like"] - yesterday_like
                b_info["comment_increment"] = b_info["comment"] - yesterday_comment
                # 获取pin增量
                for p_id, p_info in b_info["pin_list"].items():
                    try:
                        yesterday_p_info = yesterday_group_dict.get(a_id)["board_list"].get("b_id")["pin_list"].get("p_id")
                        if yesterday_p_info:
                            yesterday_view = yesterday_p_info.get("view", 0)
                            yesterday_repin = yesterday_p_info.get("repin", 0)
                            yesterday_like = yesterday_p_info.get("like", 0)
                            yesterday_comment = yesterday_p_info.get("comment", 0)
                        else:
                            yesterday_view = yesterday_repin = yesterday_like = yesterday_comment = 0
                    except:
                        yesterday_view = yesterday_repin = yesterday_like = yesterday_comment = 0
                    p_info["view_increment"] = p_info["view"] - yesterday_view
                    p_info["repin_increment"] = p_info["repin"] - yesterday_repin
                    p_info["like_increment"] = p_info["like"] - yesterday_like
                    p_info["comment_increment"] = p_info["comment"] - yesterday_comment
                    p_info["under_board_id"] = b_id
                    p_info["under_account_id"] = a_id

        # 添加发布数，并整理输出结果
        account_list = []
        for index, a in enumerate(today_group_dict.items()):
            a_id, info = a
            info["pinterest_account_id"] = a_id
            info["index"] = index + 1
            # 获取账号数据相关联的board_id
            today_publish_account = models.PublishRecord.objects.filter(Q(execute_time__range=(today_date, today_date+timedelta(days=1))),
                                                                      Q(board__pinterest_account_id=a_id))
            info["finished"] = today_publish_account.filter(state=1).count()
            info["pending"] = today_publish_account.filter(state=0).count()
            info["failed"] = today_publish_account.filter(state=2).count()
            # 获取board发布数据
            info["boards_list"] = []
            for b_index, b in enumerate(info["board_list"].items()):
                b_id, b_info = b
                b_info["board_id"] = b_id
                b_info["index"] = b_index + 1
                today_publish_board = models.PublishRecord.objects.filter(Q(execute_time__range=(today_date, today_date + timedelta(days=1))),
                                                                          Q(board_id=b_id))
                b_info["finished"] = today_publish_board.filter(state=1).count()
                b_info["pending"] = today_publish_board.filter(state=0).count()
                b_info["failed"] = today_publish_board.filter(state=2).count()
                # 获取pin数据
                b_info["pins_list"] = []
                for p_index, p in enumerate(b_info["pin_list"].items()):
                    p_id, p_info = p
                    p_info["pin_id"] = p_id
                    p_info["index"] = p_index + 1
                    b_info["pins_list"].append(p_info)
                del b_info["pin_list"]
                info["boards_list"].append(b_info)
            del info["board_list"]
            account_list.append(info)
        return account_list

    def get_data(self, data_set):
        group_dict = {}
        for today in data_set:
            if today.pinterest_account_id not in group_dict:
                # 获取账号数据
                group_dict[today.pinterest_account_id] = {
                    "account_name": today.pinterest_account.name,
                    "account_email": today.pinterest_account.email,
                    "account_create_time": today.pinterest_account.create_time,
                    "account_type": today.pinterest_account.type,
                    "update_person": today.pinterest_account.user.username,
                    "account_state": today.pinterest_account.state,
                    "account_crawl_time": today.pinterest_account.update_time,
                    # "boards": [] if not today.board_id else [today.board_id],  # board数
                    "pins": [] if not today.pin_id else [today.pin_id],  # pin数
                    "repin": today.pin_repin,
                    "like": today.pin_like,
                    "comment": today.pin_comment,
                    "board_list": {}
                }
            else:
                # group_dict[today.pinterest_account_id]["boards"].append(today.board_id)
                group_dict[today.pinterest_account_id]["pins"].append(today.pin_id)
                group_dict[today.pinterest_account_id]["repin"] += today.pin_repin
                group_dict[today.pinterest_account_id]["like"] += today.pin_like
                group_dict[today.pinterest_account_id]["comment"] += today.pin_comment
            # 获取board数据
            if today.board_id and today.board_id not in group_dict[today.pinterest_account_id]["board_list"]:
                group_dict[today.pinterest_account_id]["board_list"][today.board_id] = {
                    "board_description": today.board.description,
                    "board_state": "Public" if today.board.state else "Private",
                    "pins": [] if not today.pin_id else [today.pin_id],  # pin数
                    "repin": today.pin_repin,
                    "like": today.pin_like,
                    "comment": today.pin_comment,
                    "pin_list": {}
                }
            elif today.board_id and today.board_id in group_dict[today.pinterest_account_id]["board_list"]:
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pins"].append(today.pin_id)
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["repin"] += today.pin_repin
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["like"] += today.pin_like
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["comment"] += today.pin_comment

            # 获取pin数据
            if today.pin_id and today.pin_id not in group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"]:
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"][today.pin_id] = {
                    "pin_thumbnail": today.pin.thumbnail,
                    "pin_description": today.pin.description,
                    "pin_url": today.pin.url,
                    "product_sku": today.pin.product.sku,
                    "view": today.pin_views,
                    "repin": today.pin_repin,
                    "like": today.pin_like,
                    "comment": today.pin_comment,
                }
            elif today.pin_id and today.pin_id in group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"]:
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"][today.pin_id]["view"] += today.pin_views
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"][today.pin_id]["repin"] += today.pin_repin
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"][today.pin_id]["like"] += today.pin_like
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"][today.pin_id]["comment"] += today.pin_comment

        return group_dict

