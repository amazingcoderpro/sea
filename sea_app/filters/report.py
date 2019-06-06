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
            # 查询pin_uri or board_uri or pin_note or board_nam
            set_list = set_list.filter(
                Q(pin_uuid=search_word) | Q(pin_note__icontains=search_word) | Q(board_uuid=search_word) | Q(
                    board_name=search_word))
        else:
            # 按选择框输入查询
            if condtions.get('pinterest_account_id', '').strip():
                set_list = set_list.filter(Q(pinterest_account_id=condtions.get('pinterest_account_id').strip()))

            if condtions.get('board_id', '').strip():
                set_list = set_list.filter(board_id=condtions.get('board_id').strip())

            if condtions.get('pin_id', '').strip():
                set_list = queryset.filter(Q(pin_id=condtions.get('pin_id').strip()))

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
        today_group_dict = self.get_data(today_data_set, account_id_list)
        yesterday_group_dict = self.get_data(yesterday_data_set)
        for a_id, info in today_group_dict.items():
            # 获取账号增量
            pin_id_under_account = set(filter(lambda x: x, info["pins"]))
            try:
                info["account_publish_time"] = models.Pin.objects.filter(Q(id__in=pin_id_under_account)).order_by('-publish_time').first().publish_time.strftime("%Y-%m-%d %H:%M:%S")
            except AttributeError:
                info["account_publish_time"] = "no publish information"
            info["pins"] = len(pin_id_under_account)
            yesterday_info = yesterday_group_dict.get(a_id)
            if yesterday_info:
                yesterday_pins = len(set(filter(lambda x: x, yesterday_info.get("pins", 0))))
                yesterday_saves = yesterday_info.get("saves", 0)
                yesterday_likes = yesterday_info.get("likes", 0)
                yesterday_comment = yesterday_info.get("comments", 0)
            else:
                yesterday_pins = yesterday_saves = yesterday_likes = yesterday_comment = 0
            info["pins_increment"] = info["pins"] - yesterday_pins
            info["saves_increment"] = info["saves"] - yesterday_saves
            info["likes_increment"] = info["likes"] - yesterday_likes
            info["comments_increment"] = info["comments"] - yesterday_comment
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

    def get_data(self, data_set, account_id_list=None):
        group_dict = {}
        for today in data_set:
            if today.pinterest_account_id not in group_dict:
                # 除去有更新数据的账号
                if account_id_list is not None:
                    account_id_list.remove(today.pinterest_account_id)
                # 获取账号数据
                group_dict[today.pinterest_account_id] = {
                    "account_uri": today.pinterest_account.account,
                    "account_name": today.pinterest_account.nickname,
                    "account_thumbnail": today.pinterest_account.thumbnail,
                    "account_email": today.pinterest_account.email,
                    "account_description": today.pinterest_account.description,
                    "account_create_time": today.pinterest_account.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "account_type": today.pinterest_account.type,
                    "account_authorized": today.pinterest_account.authorized,
                    "update_person": today.pinterest_account.user.username,
                    "account_state": today.pinterest_account.state,
                    "account_crawl_time": today.pinterest_account.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "pins": [] if not today.pin_id else [today.pin_id],  # pin数
                    "saves": today.pin_saves,
                    "likes": today.pin_likes,
                    "comments": today.pin_comments,
                }
            else:
                group_dict[today.pinterest_account_id]["pins"].append(today.pin_id)
                group_dict[today.pinterest_account_id]["saves"] += today.pin_saves
                group_dict[today.pinterest_account_id]["likes"] += today.pin_likes
                group_dict[today.pinterest_account_id]["comments"] += today.pin_comments
        if account_id_list is None:
            return group_dict
        # 获取没有更新数据的基本信息
        for account_id in account_id_list:
            account_obj = models.PinterestAccount.objects.get(pk=account_id)
            group_dict[account_id] = {
                "account_uri": account_obj.account,
                "account_name": account_obj.nickname,
                "account_thumbnail": account_obj.thumbnail,
                "account_email": account_obj.email,
                "account_description": account_obj.description,
                "account_create_time": account_obj.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "account_type": account_obj.type,
                "account_authorized": account_obj.authorized,
                "update_person": account_obj.user.username,
                "account_state": account_obj.state,
                "account_crawl_time": account_obj.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                "pins": [],  # pin数
                "saves": 0,
                "likes": 0,
                "comments": 0,
            }
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
        today_group_dict = self.get_data(today_data_set, board_id_list)
        yesterday_group_dict = self.get_data(yesterday_data_set)
        # 获取board增量
        for b_id, b_info in today_group_dict.items():
            if not isinstance(b_info["pins"], int):
                b_info["pins"] = len(set(filter(lambda x: x, b_info["pins"])))
            yesterday_b_info = yesterday_group_dict.get("b_id")
            if yesterday_b_info:
                yesterday_pins = len(set(filter(lambda x: x, yesterday_b_info.get("pins", 0))))
                yesterday_saves = yesterday_b_info.get("saves", 0)
                yesterday_likes = yesterday_b_info.get("likes", 0)
                yesterday_comment = yesterday_b_info.get("comments", 0)
            else:
                yesterday_pins = yesterday_saves = yesterday_likes = yesterday_comment = 0
            b_info["pins_increment"] = b_info["pins"] - yesterday_pins
            b_info["saves_increment"] = b_info["saves"] - yesterday_saves
            b_info["likes_increment"] = b_info["likes"] - yesterday_likes
            b_info["comments_increment"] = b_info["comments"] - yesterday_comment
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

    def get_data(self, data_set, board_id_list=None):
        group_dict = {}
        for today in data_set:
            if today.board_id not in group_dict:
                # 除去有更新数据的board
                if board_id_list is not None:
                    board_id_list.remove(today.board_id)
                group_dict[today.board_id] = {
                    "board_uri": today.board.uuid,
                    "board_description": today.board.description,
                    "board_state": today.board.state,
                    "pins": [] if not today.pin_id else [today.pin_id],  # pin数
                    "saves": today.pin_saves,
                    "likes": today.pin_likes,
                    "comments": today.pin_comments,
                }
            else:
                group_dict[today.board_id]["pins"].append(today.pin_id)
                group_dict[today.board_id]["saves"] += today.pin_saves
                group_dict[today.board_id]["likes"] += today.pin_likes
                group_dict[today.board_id]["comments"] += today.pin_comments
        if not board_id_list:
            return group_dict
        # 获取没有数据的board基本信息
        for board_obj in models.Board.objects.filter(Q(id__in=board_id_list)):
            group_dict[board_obj.id] = {
                    "board_uri": board_obj.uuid,
                    "board_description": board_obj.description,
                    "board_state": board_obj.state,
                    "pins": board_obj.pins,  # pin数
                    "saves": 0,
                    "likes": 0,
                    "comments": 0,
                }
        return group_dict


class PinListFilter(BaseFilterBackend):
    """pin 列表管理 过滤器"""

    def filter_queryset(self, request, queryset, view):
        account_id = request._request.resolver_match.kwargs['aid']
        board_id = request._request.resolver_match.kwargs['bid']
        pin_id_list = []
        query_str = request.query_params.dict().get("query_str")
        if query_str:
            pin_set = models.Pin.objects.filter(Q(note=query_str) | Q(product__sku=query_str), Q(board_id=board_id))
        else:
            pin_set = models.Pin.objects.filter(board_id=board_id)
        for pin in pin_set:
            pin_id_list.append(pin.id)
        # 获取所有pin最近两天的数据
        today_date = datetime.today().date()
        today_data_set = queryset.filter(Q(update_time__range=(today_date, today_date + timedelta(days=1))),
                                         Q(pin_id__in=pin_id_list))
        yesterday_data_set = queryset.filter(Q(update_time__range=(today_date + timedelta(days=-1), today_date)),
                                             Q(pin_id__in=pin_id_list))
        today_group_dict = self.get_data(today_data_set, pin_id_list)
        yesterday_group_dict = self.get_data(yesterday_data_set)
        # 获取pin增量
        for p_id, p_info in today_group_dict.items():
            yesterday_p_info = yesterday_group_dict.get("p_id")
            if yesterday_p_info:
                # yesterday_view = yesterday_p_info.get("views", 0)
                yesterday_saves = yesterday_p_info.get("saves", 0)
                yesterday_likes = yesterday_p_info.get("likes", 0)
                yesterday_comment = yesterday_p_info.get("comments", 0)
            else:
                yesterday_saves = yesterday_likes = yesterday_comment = 0
            # p_info["view_increment"] = p_info["views"] - yesterday_view
            p_info["saves_increment"] = p_info["saves"] - yesterday_saves
            p_info["likes_increment"] = p_info["likes"] - yesterday_likes
            p_info["comments_increment"] = p_info["comments"] - yesterday_comment
            p_info["under_board_id"] = board_id
            p_info["under_account_id"] = account_id
            p_info["under_board_name"] = models.Board.objects.get(pk=board_id).name
            p_info["under_account_name"] = models.PinterestAccount.objects.get(pk=account_id).nickname
        # 获取pin数据
        pins_list = []
        for p_index, p in enumerate(today_group_dict.items()):
            p_id, p_info = p
            p_info["pin_id"] = p_id
            p_info["index"] = p_index + 1
            pins_list.append(p_info)
        return pins_list

    def get_data(self, data_set, pin_id_list=None):
        group_dict = {}
        for today in data_set:
            if today.pin_id not in group_dict:
                # 除去有更新数据的pin
                if pin_id_list is not None:
                    pin_id_list.remove(today.pin_id)
                group_dict[today.pin_id] = {
                    "pin_uri": today.pin.uuid,
                    "pin_thumbnail": today.pin.thumbnail,
                    "pin_note": today.pin.note,
                    "pin_url": today.pin.url,
                    "product_sku": today.pin.product.sku if today.pin.product else "",
                    # "views": today.pin_views,
                    "saves": today.pin_saves,
                    "likes": today.pin_likes,
                    "comments": today.pin_comments,
                }
            else:
                # group_dict[today.pin_id]["views"] += today.pin_views
                group_dict[today.pin_id]["saves"] += today.pin_saves
                group_dict[today.pin_id]["likes"] += today.pin_likes
                group_dict[today.pin_id]["comments"] += today.pin_comments
        if not pin_id_list:
            return group_dict
        # 获取没有更新数据pin的基本信息
        for pin_obj in models.Pin.objects.filter(Q(id__in=pin_id_list)):
            group_dict[pin_obj.id] = {
                "pin_uri": pin_obj.uuid,
                "pin_thumbnail": pin_obj.thumbnail,
                "pin_note": pin_obj.note,
                "pin_url": pin_obj.url,
                "product_sku": pin_obj.product.sku if pin_obj.product else "",
                # "views": today.pin_views,
                "saves": pin_obj.saves,
                "likes": pin_obj.likes,
                "comments": pin_obj.comments,
            }
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
                yesterday_saves = yesterday_info.get("saves", 0)
                yesterday_likes = yesterday_info.get("likes", 0)
                yesterday_comment = yesterday_info.get("comments", 0)
            else:
                yesterday_pins = yesterday_saves = yesterday_likes = yesterday_comment = 0
            info["pins_increment"] = info["pins"] - yesterday_pins
            info["saves_increment"] = info["saves"] - yesterday_saves
            info["likes_increment"] = info["likes"] - yesterday_likes
            info["comments_increment"] = info["comments"] - yesterday_comment
            # 获取board增量
            for b_id, b_info in info["board_list"].items():
                pin_id_under_board = set(filter(lambda x: x, b_info["pins"]))
                b_info["pins"] = len(pin_id_under_board)
                try:
                    yesterday_b_info = yesterday_group_dict.get(a_id)["board_list"].get("b_id")
                    if yesterday_b_info:
                        yesterday_pins = len(set(filter(lambda x: x, yesterday_b_info.get("pins", 0))))
                        yesterday_saves = yesterday_b_info.get("saves", 0)
                        yesterday_likes = yesterday_b_info.get("likes", 0)
                        yesterday_comment = yesterday_b_info.get("comments", 0)
                    else:
                        yesterday_pins = yesterday_saves = yesterday_likes = yesterday_comment = 0
                except:
                    yesterday_pins = yesterday_saves = yesterday_likes = yesterday_comment = 0
                b_info["pins_increment"] = b_info["pins"] - yesterday_pins
                b_info["saves_increment"] = b_info["saves"] - yesterday_saves
                b_info["likes_increment"] = b_info["likes"] - yesterday_likes
                b_info["comments_increment"] = b_info["comments"] - yesterday_comment
                # 获取pin增量
                for p_id, p_info in b_info["pin_list"].items():
                    try:
                        yesterday_p_info = yesterday_group_dict.get(a_id)["board_list"].get("b_id")["pin_list"].get("p_id")
                        if yesterday_p_info:
                            yesterday_view = yesterday_p_info.get("views", 0)
                            yesterday_saves = yesterday_p_info.get("saves", 0)
                            yesterday_likes = yesterday_p_info.get("likes", 0)
                            yesterday_comment = yesterday_p_info.get("comments", 0)
                        else:
                            yesterday_view = yesterday_saves = yesterday_likes = yesterday_comment = 0
                    except:
                        yesterday_view = yesterday_saves = yesterday_likes = yesterday_comment = 0
                    p_info["view_increment"] = p_info["views"] - yesterday_view
                    p_info["saves_increment"] = p_info["saves"] - yesterday_saves
                    p_info["likes_increment"] = p_info["likes"] - yesterday_likes
                    p_info["comments_increment"] = p_info["comments"] - yesterday_comment
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
                    "saves": today.pin_saves,
                    "likes": today.pin_likes,
                    "comments": today.pin_comments,
                    "board_list": {}
                }
            else:
                # group_dict[today.pinterest_account_id]["boards"].append(today.board_id)
                group_dict[today.pinterest_account_id]["pins"].append(today.pin_id)
                group_dict[today.pinterest_account_id]["saves"] += today.pin_saves
                group_dict[today.pinterest_account_id]["likes"] += today.pin_likes
                group_dict[today.pinterest_account_id]["comments"] += today.pin_comments
            # 获取board数据
            if today.board_id and today.board_id not in group_dict[today.pinterest_account_id]["board_list"]:
                group_dict[today.pinterest_account_id]["board_list"][today.board_id] = {
                    "board_description": today.board.description,
                    "board_state": "Public" if today.board.state else "Private",
                    "pins": [] if not today.pin_id else [today.pin_id],  # pin数
                    "saves": today.pin_saves,
                    "likes": today.pin_likes,
                    "comments": today.pin_comments,
                    "pin_list": {}
                }
            elif today.board_id and today.board_id in group_dict[today.pinterest_account_id]["board_list"]:
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pins"].append(today.pin_id)
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["saves"] += today.pin_saves
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["likes"] += today.pin_likes
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["comments"] += today.pin_comments

            # 获取pin数据
            if today.pin_id and today.pin_id not in group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"]:
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"][today.pin_id] = {
                    "pin_thumbnail": today.pin.thumbnail,
                    "pin_note": today.pin.note,
                    "pin_url": today.pin.url,
                    "product_sku": today.pin.product.sku,
                    "views": today.pin_views,
                    "saves": today.pin_saves,
                    "likes": today.pin_likes,
                    "comments": today.pin_comments,
                }
            elif today.pin_id and today.pin_id in group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"]:
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"][today.pin_id]["views"] += today.pin_views
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"][today.pin_id]["saves"] += today.pin_saves
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"][today.pin_id]["likes"] += today.pin_likes
                group_dict[today.pinterest_account_id]["board_list"][today.board_id]["pin_list"][today.pin_id]["comments"] += today.pin_comments

        return group_dict

