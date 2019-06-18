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
        page_size = int(request.query_params.dict().get('page_size', '10'))
        page = int(request.query_params.dict().get('page', '1'))
        account_set = models.PinterestAccount.objects.filter(user=request.user)
        if not account_set.exists():
            return {"count": 0, "results": []}
        account_id_list = []
        for account in account_set[(page-1)*page_size:page*page_size]:
            account_id_list.append(account.id)
        # 获取所有子账号最近两天的数据(今天的数据可以获取最新的一次数据)
        today_date = datetime.today().date()
        while True:
            today_data_set = queryset.filter(Q(update_time__range=(today_date, today_date + timedelta(days=1))),
                                             Q(pinterest_account_id__in=account_id_list), ~Q(tag=0))
            if today_data_set.exists():
                # 取今天最新的一批数据
                lastest_tag = today_data_set.order_by('-tag').first().tag
                today_data_set = today_data_set.filter(tag=lastest_tag)
                break
            if datetime.today().date() - today_date >= timedelta(days=5):
                break
            today_date = today_date + timedelta(days=-1)
        yesterday_date = today_date
        while True:
            yesterday_data_set = queryset.filter(Q(update_time__range=(yesterday_date + timedelta(days=-1), yesterday_date)),
                                                 Q(pinterest_account_id__in=account_id_list), ~Q(tag=0))
            if yesterday_data_set.exists():
                # 取昨天最新的一批数据
                lastest_tag = yesterday_data_set.order_by('-tag').first().tag
                yesterday_data_set = yesterday_data_set.filter(tag=lastest_tag)
                break
            if datetime.today().date() - yesterday_date >= timedelta(days=10):
                break
            yesterday_date = yesterday_date + timedelta(days=-1)
        today_group_dict = self.get_data(today_data_set, account_id_list)
        yesterday_group_dict = self.get_data(yesterday_data_set)
        account_list = []
        today_publish_set = models.PublishRecord.objects.filter(
            Q(execute_time__range=(today_date, today_date + timedelta(days=1))),
            Q(board__pinterest_account_id__in=today_group_dict.keys()))
        for a_id, info in today_group_dict.items():
            # 获取账号增量
            pin_id_under_account = list(set(filter(lambda x: x, info["pin_list"])))
            try:
                info["account_publish_time"] = models.Pin.objects.filter(Q(id__in=pin_id_under_account)).order_by('-publish_time').first().publish_time.strftime("%Y-%m-%d %H:%M:%S")
            except AttributeError:
                info["account_publish_time"] = "no publish information"
            yesterday_info = yesterday_group_dict.get(a_id)
            if yesterday_info:
                yesterday_pins = yesterday_info.get("pins", 0)
                yesterday_saves = yesterday_info.get("saves", 0)
                # yesterday_likes = yesterday_info.get("likes", 0)
                yesterday_comment = yesterday_info.get("comments", 0)
            else:
                yesterday_pins = yesterday_saves = yesterday_comment = 0
            info["pins_increment"] = info["pins"] - yesterday_pins
            info["saves_increment"] = info["saves"] - yesterday_saves
            # info["likes_increment"] = info["likes"] - yesterday_likes
            info["comments_increment"] = info["comments"] - yesterday_comment
        # 添加发布数，并整理输出结果
        # account_list = []
        # a_id_list = today_group_dict.keys()
        # today_publish_set = models.PublishRecord.objects.filter(
        #     Q(execute_time__range=(today_date, today_date + timedelta(days=1))),
        #     Q(board__pinterest_account_id__in=a_id_list))
        # for index, a in enumerate(today_group_dict.items()):
        #     a_id, info = a
            info["pinterest_account_id"] = a_id
            # info["index"] = index + 1
            # 获取账号数据相关联的board_id
            today_publish_account = today_publish_set.filter(board__pinterest_account_id=a_id)
            info["finished"] = today_publish_account.filter(state=1, finished_time__range=(datetime.now().date(), datetime.now())).count()
            info["pending"] = today_publish_account.filter(state=0, execute_time__range=(datetime.now(), datetime.now().date()+timedelta(days=1))).count()
            # info["failed"] = today_publish_account.filter(state=2).count()
            info.pop("pin_list")
            account_list.append(info)
        return {"count": len(account_set), "results": account_list}

    def get_data(self, data_set, account_id_list=None):
        group_dict = {}
        for today in data_set:
            if today.pinterest_account_id not in group_dict:
                # 除去有更新数据的账号
                if account_id_list is not None:
                    account_id_list.remove(today.pinterest_account_id)
                # 获取账号数据
                group_dict[today.pinterest_account_id] = {
                    "pin_list": [] if not today.pin_id else [today.pin_id],  # pin_id 列表
                    "pins": today.pinterest_account.pins,  # pin数
                    "saves": today.pin_saves,
                    # "likes": today.pin_likes,
                    "comments": today.pin_comments,
                }
                if account_id_list is not None:
                    group_dict[today.pinterest_account_id].update({
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
                   })
            else:
                group_dict[today.pinterest_account_id]["pin_list"].append(today.pin_id)
                group_dict[today.pinterest_account_id]["saves"] += today.pin_saves
                # group_dict[today.pinterest_account_id]["likes"] += today.pin_likes
                group_dict[today.pinterest_account_id]["comments"] += today.pin_comments
        if account_id_list is None:
            return group_dict
        # 获取没有更新数据的基本信息
        for account_obj in models.PinterestAccount.objects.filter(id__in=account_id_list):
            group_dict[account_obj.id] = {
                "account_uri": account_obj.account,
                "account_name": account_obj.nickname,
                "account_thumbnail": account_obj.thumbnail,
                "account_email": account_obj.email,
                "account_description": account_obj.description,
                "account_create_time": account_obj.create_time.strftime("%Y-%m-%d %H:%M:%S") if account_obj.create_time else "",
                "account_type": account_obj.type,
                "account_authorized": account_obj.authorized,
                "update_person": account_obj.user.username,
                "account_state": account_obj.state,
                "account_crawl_time": account_obj.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                "pin_list": [],  # pin_id 列表
                "pins": account_obj.pins,  # pin数
                "saves": 0,
                # "likes": 0,
                "comments": 0,
            }
        return group_dict


class BoardListFilter(BaseFilterBackend):
    """board 列表管理 过滤器"""
    def filter_queryset(self, request, queryset, view):
        account_id = request._request.resolver_match.kwargs['aid']
        page_size = int(request.query_params.dict().get('page_size', '10'))
        page = int(request.query_params.dict().get('page', '1'))
        board_set = models.Board.objects.filter(pinterest_account_id=account_id)
        if not board_set.exists():
            return {"count": 0, "results": []}
        board_id_list = []
        for board in board_set[(page-1)*page_size:page*page_size]:
            board_id_list.append(board.id)
        # 获取所有board最近两天的数据
        today_date = datetime.today().date()
        while True:
            today_data_set = queryset.filter(Q(update_time__range=(today_date, today_date + timedelta(days=1))),
                                             Q(board_id__in=board_id_list), ~Q(tag=0))
            if today_data_set.exists():
                # 取今天最新的一批数据
                lastest_tag = today_data_set.order_by('-tag').first().tag
                today_data_set = today_data_set.filter(tag=lastest_tag)
                break
            if datetime.today().date() - today_date >= timedelta(days=5):
                break
            today_date = today_date + timedelta(days=-1)
        yesterday_date = today_date
        while True:
            yesterday_data_set = queryset.filter(Q(update_time__range=(yesterday_date + timedelta(days=-1), yesterday_date)),
                                                 Q(board_id__in=board_id_list), ~Q(tag=0))
            if yesterday_data_set.exists():
                # 取昨天最新的一批数据
                lastest_tag = yesterday_data_set.order_by('-tag').first().tag
                yesterday_data_set = yesterday_data_set.filter(tag=lastest_tag)
                break
            if datetime.today().date() - yesterday_date >= timedelta(days=10):
                break
            yesterday_date = yesterday_date + timedelta(days=-1)
        today_group_dict = self.get_data(today_data_set, board_id_list)
        yesterday_group_dict = self.get_data(yesterday_data_set)
        # 获取board增量
        boards_list = []
        # today_publish_set = models.PublishRecord.objects.filter(
        #     Q(execute_time__range=(today_date, today_date + timedelta(days=1))),
        #     Q(board_id__in=today_group_dict.keys()))
        for b_id, b_info in today_group_dict.items():
            # if not isinstance(b_info["pins"], int):
            #     b_info["pins"] = len(set(filter(lambda x: x, b_info["pins"])))
            yesterday_b_info = yesterday_group_dict.get("b_id")
            if yesterday_b_info:
                yesterday_pins = yesterday_b_info.get("pins", 0)
                yesterday_saves = yesterday_b_info.get("saves", 0)
                yesterday_followers = yesterday_b_info.get("board_followers", 0)
                yesterday_comment = yesterday_b_info.get("comments", 0)
            else:
                yesterday_pins = yesterday_saves = yesterday_comment = yesterday_followers = 0
            b_info["pins_increment"] = b_info["pins"] - yesterday_pins
            b_info["saves_increment"] = b_info["saves"] - yesterday_saves
            b_info["followers_increment"] = b_info["board_followers"] - yesterday_followers
            b_info["comments_increment"] = b_info["comments"] - yesterday_comment
            b_info["board_id"] = b_id
            # 获取board发布数据
            # today_publish_board = today_publish_set.filter(board_id=b_id)
            # b_info["finished"] = today_publish_board.filter(state=1).count()
            # # b_info["pending"] = today_publish_board.filter(state=0).count()
            # b_info["failed"] = today_publish_board.filter(state=2).count()
        # boards_list = []
        # today_publish_set = models.PublishRecord.objects.filter(
        #     Q(execute_time__range=(today_date, today_date + timedelta(days=1))),
        #     Q(board_id__in=today_group_dict.keys()))
        # for b_id, b_info in today_group_dict.items():
            # b_info["board_id"] = b_id
            # b_info["index"] = b_index + 1
            # today_publish_board = today_publish_set.filter(board_id=b_id)
            # b_info["finished"] = today_publish_board.filter(state=1).count()
            # b_info["pending"] = today_publish_board.filter(state=0).count()
            # b_info["failed"] = today_publish_board.filter(state=2).count()
            boards_list.append(b_info)
        return {"count": len(board_set), "results": boards_list}

    def get_data(self, data_set, board_id_list=None):
        group_dict = {}
        for today in data_set:
            if today.board_id not in group_dict:
                # 除去有更新数据的board
                if board_id_list is not None:
                    board_id_list.remove(today.board_id)
                group_dict[today.board_id] = {
                    "pins": today.board.pins,  # pin数
                    "saves": today.pin_saves,
                    "board_followers": today.board_followers,
                    # "likes": today.pin_likes,
                    "comments": today.pin_comments,
                }
                if board_id_list is not None:
                    group_dict[today.board_id].update({
                        "board_uri": today.board.uuid,
                        "board_name": today.board.name,
                        "board_description": today.board.description,
                        "board_state": today.board.state,
                        "finished": today.board.publishrecord_set.filter(state=1, finished_time__range=(datetime.now().date(), datetime.now())).count(),
                        "pending": today.board.publishrecord_set.filter(state=0, execute_time__range=(datetime.now(), datetime.now().date()+timedelta(days=1))).count()
                    })
            else:
                # group_dict[today.board_id]["pins"].append(today.pin_id)
                group_dict[today.board_id]["saves"] += today.pin_saves
                group_dict[today.board_id]["board_followers"] += today.board_followers
                group_dict[today.board_id]["comments"] += today.pin_comments
        if not board_id_list:
            return group_dict
        # 获取没有数据的board基本信息
        for board_obj in models.Board.objects.filter(Q(id__in=board_id_list)):
            group_dict[board_obj.id] = {
                    "board_uri": board_obj.uuid,
                    "board_name": board_obj.name,
                    "board_description": board_obj.description,
                    "board_state": board_obj.state,
                    "pins": board_obj.pins,  # pin数
                    "saves": 0,
                    "board_followers": 0,
                    # "likes": 0,
                    "comments": 0,
                    "finished": board_obj.publishrecord_set.filter(state=1, finished_time__range=(datetime.now().date(), datetime.now())).count(),
                    "pending": board_obj.publishrecord_set.filter(state=0, execute_time__range=(datetime.now(), datetime.now().date()+timedelta(days=1))).count()
                }
        return group_dict


class PinListFilter(BaseFilterBackend):
    """pin 列表管理 过滤器"""

    def filter_queryset(self, request, queryset, view):
        account_id = request._request.resolver_match.kwargs['aid']
        board_id = request._request.resolver_match.kwargs['bid']
        under_board_name = models.Board.objects.get(pk=board_id).name
        under_account_name = models.PinterestAccount.objects.get(pk=account_id).nickname
        page_size = int(request.query_params.dict().get('page_size', '10'))
        page = int(request.query_params.dict().get('page', '1'))
        pin_id_list = []
        query_str = request.query_params.dict().get("query_str")
        if query_str:
            pin_set = models.Pin.objects.filter(Q(note__icontains=query_str) | Q(product__sku__icontains=query_str), Q(board_id=board_id))
        else:
            pin_set = models.Pin.objects.filter(board_id=board_id)
        pin_set = pin_set.filter(~Q(uuid=None), ~Q(url=None))
        if not pin_set.exists():
            return {"count": 0, "results": []}
        for pin in pin_set[(page-1)*page_size:page*page_size]:
            pin_id_list.append(pin.id)
        # 获取所有pin最近两天的数据
        today_date = datetime.today().date()
        while True:
            today_data_set = queryset.filter(Q(update_time__range=(today_date, today_date + timedelta(days=1))),
                                             Q(pin_id__in=pin_id_list), ~Q(tag=0))
            if today_data_set.exists():
                # 取今天最新的一批数据
                lastest_tag = today_data_set.order_by('-tag').first().tag
                today_data_set = today_data_set.filter(tag=lastest_tag)
                break
            if datetime.today().date() - today_date >= timedelta(days=10):
                break
            today_date = today_date + timedelta(days=-1)
        while True:
            yesterday_data_set = queryset.filter(Q(update_time__range=(today_date + timedelta(days=-1), today_date)),
                                                 Q(pin_id__in=pin_id_list), ~Q(tag=0))
            if yesterday_data_set.exists():
                # 取昨天最新的一批数据
                lastest_tag = yesterday_data_set.order_by('-tag').first().tag
                yesterday_data_set = yesterday_data_set.filter(tag=lastest_tag)
                break
            if datetime.today().date() - today_date >= timedelta(days=20):
                break
            today_date = today_date + timedelta(days=-1)
        today_group_dict = self.get_data(today_data_set, pin_id_list)
        yesterday_group_dict = self.get_data(yesterday_data_set)
        pins_list = []
        # 获取pin增量
        for p_id, p_info in today_group_dict.items():
            yesterday_p_info = yesterday_group_dict.get("p_id")
            if yesterday_p_info:
                # yesterday_view = yesterday_p_info.get("views", 0)
                yesterday_saves = yesterday_p_info.get("saves", 0)
                # yesterday_likes = yesterday_p_info.get("likes", 0)
                yesterday_comment = yesterday_p_info.get("comments", 0)
            else:
                yesterday_saves = yesterday_comment = 0
            # p_info["view_increment"] = p_info["views"] - yesterday_view
            p_info["saves_increment"] = p_info["saves"] - yesterday_saves
            # p_info["likes_increment"] = p_info["likes"] - yesterday_likes
            p_info["comments_increment"] = p_info["comments"] - yesterday_comment
            p_info["under_board_id"] = board_id
            p_info["under_account_id"] = account_id
            p_info["under_board_name"] = under_board_name
            p_info["under_account_name"] = under_account_name
            p_info["pin_id"] = p_id
        # 获取pin数据

        # for p_index, p in enumerate(today_group_dict.items()):
        #     p_id, p_info = p

            # p_info["index"] = p_index + 1
            pins_list.append(p_info)
        return {"count": len(pin_set), "results": pins_list}

    def get_data(self, data_set, pin_id_list=None):
        group_dict = {}
        for today in data_set:
            if today.pin_id not in group_dict:
                # 除去有更新数据的pin
                if pin_id_list is not None:
                    pin_id_list.remove(today.pin_id)
                group_dict[today.pin_id] = {
                    # "views": today.pin_views,
                    "saves": today.pin_saves,
                    # "likes": today.pin_likes,
                    "comments": today.pin_comments,
                }
                if pin_id_list is not None:
                    group_dict[today.pin_id].update({
                        "pin_uri": today.pin.uuid,
                        "pin_thumbnail": today.pin.thumbnail,
                        "pin_image": today.pin.image_url,
                        "pin_note": today.pin.note,
                        "pin_url": today.pin.url,
                        "product_sku": today.pin.product.sku if today.pin.product else "",
                    })
            else:
                # group_dict[today.pin_id]["views"] += today.pin_views
                group_dict[today.pin_id]["saves"] += today.pin_saves
                # group_dict[today.pin_id]["likes"] += today.pin_likes
                group_dict[today.pin_id]["comments"] += today.pin_comments
        if not pin_id_list:
            return group_dict
        # 获取没有更新数据pin的基本信息
        for pin_obj in models.Pin.objects.filter(Q(id__in=pin_id_list)):
            group_dict[pin_obj.id] = {
                "pin_uri": pin_obj.uuid,
                "pin_thumbnail": pin_obj.thumbnail,
                "pin_image": pin_obj.image_url,
                "pin_note": pin_obj.note,
                "pin_url": pin_obj.url,
                "product_sku": pin_obj.product.sku if pin_obj.product else "",
                # "views": today.pin_views,
                "saves": pin_obj.saves,
                # "likes": pin_obj.likes,
                "comments": pin_obj.comments,
            }
        return group_dict




