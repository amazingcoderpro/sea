# -*- coding: utf-8 -*-
# Created by: Leemon7
# Created on: 2019/5/17

from django.db.models import Q

import datetime

from sea_app import models


def get_request_datetime(request):
    start_time = request.GET.get("start_time", datetime.datetime.now() + datetime.timedelta(days=-6))
    end_time = request.GET.get("end_time", datetime.datetime.now())
    if isinstance(start_time, str):
        try:
            start_time = datetime.datetime(*map(int, start_time.split('-')))
        except:
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    if isinstance(end_time, str):
        try:
            end_time = datetime.datetime(*map(int, end_time.split('-')))
        except:
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    return start_time, end_time


def get_request_params(request):
    # 获取请求参数
    start_time, end_time = get_request_datetime(request)
    pinterest_account_id = request.GET.get("pinterest_account_id")
    board_id = request.GET.get("board_id")
    pin_id = request.GET.get("pin_id")
    search_word = request.GET.get("search", "").strip()
    # store_id = request.GET.get("store_id")  # 必传(如果一个用户绑定一个商店的话，就可以通过当前用户获取当前店铺)
    store = models.Store.objects.filter(user_id=request.user).first()
    store_id = store.id if store else None
    # platform = request.GET.get("platform_id", 1)  # 必传
    return start_time, end_time, pinterest_account_id, board_id, pin_id, search_word, store_id


def get_common_data(request):
    # 获取请求参数
    start_time, end_time, pinterest_account_id, board_id, pin_id, search_word, store_id = get_request_params(request)

    # 当前用户下所有的账号id_list
    account_id_list = []
    for account in models.PinterestAccount.objects.filter(user=request.user):
        if account.id not in account_id_list:
            account_id_list.append(account.id)
    # 开始过滤PinterestHistoryData数据
    pin_set_list = models.PinterestHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)),
                                                              Q(pinterest_account_id__in=account_id_list))
    if search_word:
        # 查询pin_uuid or board_uuid or pin_note or board_name
        pin_set_list = pin_set_list.filter(
            Q(pin_uuid__icontains=search_word) | Q(pin_note__icontains=search_word) | Q(board_uuid__icontains=search_word) | Q(
                board_name__icontains=search_word))
    else:
        # 按选择框输入查询
        if pinterest_account_id:
            pin_set_list = pin_set_list.filter(pinterest_account_id=pinterest_account_id)

        if board_id:
            pin_set_list = pin_set_list.filter(board_id=board_id)

        if pin_id:
            pin_set_list = pin_set_list.filter(pin_id=pin_id)

    # 开始过滤ProductHistoryData数据
    product_set_list = models.ProductHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)),
                                                                Q(store_id=store_id))
    return pin_set_list, product_set_list


def daily_report(pin_set_list, product_set_list, request):
    start_time, end_time = get_request_datetime(request)
    time_list = time_range_list(start_time, end_time)
    # 组装每日最新pin数据
    data_list = []
    for date in time_list:
        # 获取当天的pin数据
        pin_queryset= pin_set_list.filter(Q(update_time__range=(date, date+datetime.timedelta(days=1))),
                                          ~Q(tag=0))
        if not pin_queryset.exists():
            data_list.append({"date": date.strftime("%Y-%m-%d"), "accounts": 0, "account_followings": 0, "account_followers": 0,
                    "account_views": 0, "boards": 0, "board_followers": 0, "pins": 0, "pin_saves": 0, "pin_likes": 0,
                    "pin_comments": 0, "product_clicks": 0, "product_visitors": 0, "product_new_visitors": 0,
                    "product_sales": 0, "product_revenue": 0})
            continue
        pin_queryset = pin_queryset.filter(tag=pin_queryset.order_by('-tag').first().tag)
        # 初始化数据
        group_dict = {"date":date.strftime("%Y-%m-%d"), "accounts": [], "account_followings": 0, "account_followers": 0,
                    "account_views": 0, "boards": [], "board_followers": 0, "pins": [], "pin_saves": 0, "pin_likes": 0,
                    "pin_comments": 0, "product_clicks": 0, "product_visitors": 0, "product_new_visitors": 0,
                    "product_sales": 0, "product_revenue": 0, "products": []}
        for item in pin_queryset:
            group_dict["accounts"].append(item.pinterest_account_id)
            group_dict["account_followings"] += item.account_followings
            group_dict["account_followers"] += item.account_followers
            group_dict["boards"].append(item.board_id)
            group_dict["board_followers"] += item.board_followers
            group_dict["pins"].append(item.pin_id)
            group_dict["pin_saves"] += item.pin_saves
            group_dict["pin_likes"] += item.pin_likes
            group_dict["pin_comments"] += item.pin_comments
            group_dict["account_views"] += item.account_views
            group_dict["products"].append(item.product_id)

        # 组装每日product对应pin的数据
        product_set_list_pre = product_set_list.filter(
            Q(update_time__range=(date, date + datetime.timedelta(days=1))), ~Q(tag=0))
        if product_set_list_pre.exists():
            product_set_list_pre = product_set_list_pre.filter(tag=product_set_list_pre.order_by('-tag').first().tag)
            p_list = list(set(filter(lambda x: x, group_dict["products"])))
            product_list = product_set_list_pre.filter(product_id__in=p_list)

            for item in product_list:
                # 只能叠加当天最新一次拉取的数据
                # 每一个产品只加一次
                group_dict["product_clicks"] += item.product_scan
                group_dict["product_sales"] += item.product_sales
                group_dict["product_revenue"] += item.product_revenue
                group_dict["product_visitors"] += item.product_visitors
                group_dict["product_new_visitors"] += item.product_new_visitors

        # 组装最后数据
        group_dict["accounts"] = len(set(filter(lambda x: x, group_dict["accounts"])))
        group_dict["boards"] = len(set(filter(lambda x: x, group_dict["boards"])))
        group_dict["pins"] = len(set(filter(lambda x: x, group_dict["pins"])))
        group_dict.pop("products")
        data_list.append(group_dict)

    data_list = sorted(data_list, key=lambda x: x["date"], reverse=True)
    return {"count": len(data_list), "results": data_list}


def daily_report_view(request):
    """日报视图函数"""
    pin_set_list, product_set_list = get_common_data(request)
    data_list = daily_report(pin_set_list, product_set_list, request)
    return data_list


def subaccount_report_view(request, type):
    """子账号视图函数"""
    pin_set_list, product_set_list = get_common_data(request)
    # 取PinterestHistoryData最新一天的数据,
    start_time, end_time = get_request_datetime(request)
    pin_set_list_result = []
    while end_time >= start_time:
        pin_set_list_result = pin_set_list.filter(~Q(tag=0), Q(update_time__range=(end_time + datetime.timedelta(days=-1), end_time)))
        if pin_set_list_result.exists():
            pin_set_list_result = pin_set_list_result.filter(tag=pin_set_list_result.order_by('-tag').first().tag)
            break
        end_time += datetime.timedelta(days=-1)
    # 取有数据当天的最晚的一批数据
    pin_set_list = pin_set_list_result
    # ProductHistoryData时间范围内每一天的最新数据
    product_time_list = time_range_list(start_time, end_time)
    for date in product_time_list:
        current_set = product_set_list.filter(update_time__range=(date, date+datetime.timedelta(days=1)))
        if current_set.exists():
            lastest_tag = current_set.order_by('-tag').first().tag
            # 排除当天非最新数据
            product_set_list = product_set_list.exclude(Q(update_time__range=(date, date+datetime.timedelta(days=1))),
                                                        ~Q(tag=lastest_tag))


    if type == 'pins':
        # pins report
        data_list = pins_report(pin_set_list, product_set_list)
    elif type == 'board':
        # boards report
        data_list = board_report(pin_set_list, product_set_list)
    elif type == 'subaccount':
        # subaccount report
        data_list = subaccount_report(pin_set_list, product_set_list, request)
    else:
        # 请求有误
        data_list = "An error occurred in the request and data could not be retrieved"
    return data_list


def subaccount_report(pin_set_list, product_set_list, request):
    # subaccount report
    data_list = []
    group_dict = {}
    account_id_list = [account.id for account in models.PinterestAccount.objects.filter(user_id=request.user)]
    set_list = pin_set_list.filter(~Q(pinterest_account_id=None))
    # 取时间范围内最新subaccount数据及subaccount下所有board数和pin信息总数
    for item in set_list:
        subaccount_id = item.pinterest_account_id
        if subaccount_id not in group_dict:
            if subaccount_id in account_id_list:
                account_id_list.remove(subaccount_id)
            group_dict[subaccount_id] = {
                "account_name": item.pinterest_account.nickname,
                "boards": item.pinterest_account.boards,  # board数
                "account_followings": item.account_followings,
                "account_followers": item.account_followers,
                "account_views": item.account_views,
                "pins": item.pinterest_account.pins,  # pin数
                "pin_saves": item.pin_saves,
                # "pin_likes": item.pin_likes,
                "pin_comments": item.pin_comments,
                # "product_clicks": item.product_clicks,
                "products": [] if not item.product_id else [item.product_id],  # product
            }
        else:
            # group_dict[subaccount_id]["boards"].append(item.board_id)  # board数
            # group_dict[subaccount_id]["pins"].append(item.pin_id)  # pin数
            group_dict[subaccount_id]["pin_saves"] += item.pin_saves
            group_dict[subaccount_id]["account_followings"] += item.account_followings
            group_dict[subaccount_id]["account_followers"] += item.account_followers
            group_dict[subaccount_id]["pin_comments"] += item.pin_comments
            # group_dict[subaccount_id]["pin_view"] += item.pin_views
            # group_dict[subaccount_id]["pin_clicks"] += item.pin_clicks
            group_dict[subaccount_id]["products"].append(item.product_id)  # product
    for subaccount_id, info in group_dict.items():
        data = {
            "subaccount_id": subaccount_id,
            "account_name": info["account_name"],
            "account_followings": info["account_followings"],
            "account_followers": info["account_followers"],
            "account_views": info["account_views"],
            "boards": info["boards"],
            "pins": info["pins"],
            "pin_saves": info["pin_saves"],
            # "pin_likes": info["pin_likes"],
            "pin_comments": info["pin_comments"],
            # "pin_clicks": info["pin_clicks"],
            "product_visitors": 0,
            "product_new_visitors": 0,
            "product_clicks": 0,
            "product_sales": 0,
            "product_revenue": 0
        }
        # 组装product对应pin的数据,并且还需要是最新的product数据
        product_id_list = list(set([i for i in info["products"] if i]))
        product_set = product_set_list.filter(product_id__in=product_id_list)
        has_data_p_list = []
        for item in product_set:
            if (item.update_time.date(), item.product_id) in has_data_p_list:
                continue
            has_data_p_list.append((item.update_time.date(), item.product_id))
            data["product_visitors"] += item.product_visitors
            data["product_new_visitors"] += item.product_new_visitors
            data["product_clicks"] += item.product_scan
            data["product_sales"] += item.product_sales
            data["product_revenue"] += item.product_revenue
        data_list.append(data)
    for account in models.PinterestAccount.objects.filter(id__in=account_id_list):
        data_list.append({
            "subaccount_id": account.id,
            "account_name": account.nickname,
            "account_followings": 0,
            "account_followers": 0,
            "account_views": account.views,
            "boards": account.boards,
            "pins": account.pins,
            "pin_saves": 0,
            "pin_comments": 0,
            "product_visitors": 0,
            "product_new_visitors": 0,
            "product_clicks": 0,
            "product_sales": 0,
            "product_revenue": 0
        })
    return data_list


def board_report(pin_set_list, product_set_list):
    # board report
    data_list = []
    group_dict = {}
    set_list = pin_set_list.filter(~Q(board_id=None))
    # 取时间范围内最新board数据及board下所有pin总数
    for item in set_list:
        board_id = item.board_id
        if board_id not in group_dict:
            group_dict[board_id] = {
                "update_time": item.update_time,
                "board_name": item.board_name,
                "board_followers": item.board_followers,
                "pins": [] if not item.pin_id else [item.pin_id],  # pin数
                "pin_saves": item.pin_saves,
                # "pin_likes": item.pin_likes,
                "pin_comments": item.pin_comments,
                # "pin_view": item.pin_views,
                # "pin_clicks": item.pin_clicks,
                "products": [] if not item.product_id else [item.product_id],  # product
            }
        else:
            group_dict[board_id]["pins"].append(item.pin_id)  # pin数
            group_dict[board_id]["pin_saves"] += item.pin_saves
            group_dict[board_id]["board_followers"] += item.board_followers
            group_dict[board_id]["pin_comments"] += item.pin_comments
            # group_dict[board_id]["pin_view"] += item.pin_views
            # group_dict[board_id]["pin_clicks"] += item.pin_clicks
            group_dict[board_id]["products"].append(item.product_id)  # product

    for board_id, info in group_dict.items():
        data = {
            "board_id": board_id,
            "board_name": info["board_name"],
            "board_followers": info["board_followers"],
            "pins": len(set(filter(lambda x: x, info["pins"]))),
            "pin_saves": info["pin_saves"],
            # "pin_likes": info["pin_likes"],
            "pin_comments": info["pin_comments"],
            # "pin_view": info["pin_view"],
            "product_visitors": 0,
            "product_new_visitors": 0,
            "product_clicks": 0,
            "product_sales": 0,
            "product_revenue": 0
        }
        # 组装product对应pin的数据
        product_id_list = list(set([i for i in info["products"] if i]))
        product_set = product_set_list.filter(product_id__in=product_id_list)
        has_data_p_list = []
        for item in product_set:
            if (item.update_time.date(), item.product_id) in has_data_p_list:
                continue
            has_data_p_list.append((item.update_time.date(), item.product_id))
            data["product_visitors"] += item.product_visitors
            data["product_new_visitors"] += item.product_new_visitors
            data["product_clicks"] += item.product_scan
            data["product_sales"] += item.product_sales
            data["product_revenue"] += item.product_revenue

        data_list.append(data)
    return data_list


def pins_report(pin_set_list, product_set_list):
    # pins report
    data_list = []
    group_dict = {}
    set_list = pin_set_list.filter(~Q(pin_uuid=None), ~Q(pin_uuid=""))
    # 取时间范围内最新的pin数据
    for item in set_list:
        pin_uuid = item.pin_uuid
        if pin_uuid not in group_dict:
            group_dict[pin_uuid] = {
                "update_time": item.update_time,
                "pin_thumbnail": item.pin_thumbnail,
                "pin_saves": item.pin_saves,
                # "pin_likes": item.pin_likes,
                "pin_comments": item.pin_comments,
                # "pin_view": item.pin_views,
                # "pin_clicks": item.pin_clicks,
                "product_id": item.product_id
            }
        else:
            if item.update_time > group_dict[pin_uuid]["update_time"]:
                group_dict[pin_uuid] = {
                    "update_time": item.update_time,
                    "pin_thumbnail": item.pin_thumbnail,
                    "pin_saves": item.pin_saves,
                    # "pin_likes": item.pin_likes,
                    "pin_comments": item.pin_comments,
                    # "pin_view": item.pin_views,
                    # "pin_clicks": item.pin_clicks,
                    "product_id": item.product_id
                }
    for pin_uuid, info in group_dict.items():
        data = {
            "pin_uri": pin_uuid,
            "pin_thumbnail": info["pin_thumbnail"],
            "pin_saves": info["pin_saves"],
            # "pin_likes": info["pin_likes"],
            "pin_comments": info["pin_comments"],
            # "pin_view": info["pin_view"],
            "product_visitors": 0,
            "product_new_visitors": 0,
            "product_clicks": 0,
            "product_sales": 0,
            "product_revenue": 0,
            # "product_id": info["product_id"]
        }
        # 组装product对应pin的数据
        # store_set_list = product_set_list.filter(Q(product_id=None))
        # for item in store_set_list:
        #     data["store_visitors"] += item.store_visitors
        #     data["store_new_visitors"] += item.store_new_visitors
        product_obj_list = product_set_list.filter(product_id=info["product_id"])
        has_data_p_list = []
        for product_obj in product_obj_list:
            if (product_obj.update_time.date(), product_obj.product_id) in has_data_p_list:
                continue
            has_data_p_list.append((product_obj.update_time.date(), product_obj.product_id))
            data["product_visitors"] += product_obj.product_visitors
            data["product_new_visitors"] += product_obj.product_new_visitors
            data["product_clicks"] += product_obj.product_scan
            data["product_sales"] += product_obj.product_sales
            data["product_revenue"] += product_obj.product_revenue

        data_list.append(data)
    return data_list


def get_num(queryset, fieldname):
    # 通过queryset获取计数
    lst = []
    for item in queryset:
        if getattr(item, fieldname) not in lst:
            lst.append(getattr(item, fieldname))
    return len(lst)


def count_num(queryset, fieldname):
    # 获取fieldname的总数
    fieldname_num = 0
    for item in queryset:
        fieldname_num += getattr(item, fieldname)
    return fieldname_num


def site_count(pin_set_list, product_set_list, oneday=datetime.datetime.now().date()):
    # 获取oneday的数据，默认取昨天更新的数据
    lastest_pin_data = pin_set_list.filter(
        Q(update_time__range=(oneday, oneday + datetime.timedelta(days=1))), ~Q(tag=0)).order_by('-tag').first()
    # 获取当天最晚一批数据的更新时间
    if not lastest_pin_data:
        return {"subaccount_num": 0, "board_num": 0, "pin_num": 0,
                "visitor_num": 0, "click_num": 0, "sales_num": 0, "revenue_num": 0,
                "board_followers": 0, "pin_saves": 0, "lastest_time": None}
    lastest_time = lastest_pin_data.update_time.strftime("%Y-%m-%d %H:%M:%S")
    pin_queryset = pin_set_list.filter(tag=lastest_pin_data.tag)
    # 获取帐号总数
    subaccount_set = pin_queryset.filter(board_id=None, pin_id=None)
    subaccount_num = get_num(subaccount_set, "pinterest_account_id")
    # 获取Board总数
    board_set = pin_queryset.filter(~Q(board_id=None), Q(pin_id=None))
    board_num = get_num(board_set, "board_id")
    board_followers = count_num(board_set, 'board_followers')
    # 获取pin总数
    pin_set = pin_queryset.filter(~Q(pin_id=None))
    pin_num = get_num(pin_set, "pin_id")
    pin_saves = count_num(pin_set, "pin_saves")

    lastest_product_data = product_set_list.filter(
        Q(update_time__range=(oneday, oneday + datetime.timedelta(days=1))), ~Q(tag=0)).order_by('-tag').first()
    # 获取当天最晚一批产品数据的更新时间
    if not lastest_product_data:
        return {"subaccount_num": subaccount_num, "board_num": board_num, "pin_num": pin_num,
                "visitor_num": 0, "click_num": 0, "sales_num": 0, "revenue_num": 0,
                "board_followers": board_followers, "pin_saves": pin_saves, "lastest_time": lastest_time}
    product_queryset = product_set_list.filter(tag=lastest_product_data.tag)
    # 获取product_id_list
    product_id_list = []
    for pin in pin_set:
        if pin.product_id and pin.product_id not in product_id_list:
            product_id_list.append(pin.product_id)
    # 获取sales总数
    product_set = product_queryset.filter(product_id__in=product_id_list)
    sales_num = count_num(product_set, "product_sales")
    # 获取click总数
    click_num = count_num(product_set, "product_scan")
    # 获取revenue总数
    revenue_num = count_num(product_set, "product_revenue")
    visitor_num = count_num(product_set, "product_visitors")

    return {
        "subaccount_num": subaccount_num,
        "board_num": board_num,
        "pin_num": pin_num,
        "visitor_num": visitor_num,
        "click_num": click_num,
        "sales_num": sales_num,
        "revenue_num": revenue_num,
        "board_followers": board_followers,
        "pin_saves": pin_saves,
        "lastest_time": lastest_time
    }


def time_range_list(start_time, end_time):
    time_list = []
    for i in range((end_time.date() - start_time.date()).days + 1):
        day = start_time + datetime.timedelta(days=i)
        time_list.append(day.date())
    return time_list


def account_overview_chart(pin_set_list, product_set_list, request, reslut_num=None):
    """账户总览 图"""
    # 按天循环时间范围内，获取当天数据
    start_time, end_time = get_request_datetime(request)
    time_list = time_range_list(start_time, end_time)
    overview_list = []
    for day in time_list[::-1]:
        day_count = site_count(pin_set_list, product_set_list, day)
        day_count["date"] = day.strftime("%Y-%m-%d %H:%M:%S")
        day_count["site_num"] = models.Store.objects.filter(user_id=request.user).count()
        overview_list.append(day_count)
        if reslut_num and len(overview_list) >= reslut_num:
            break
    return tuple(overview_list)


def account_overview_table(overview_list):
    """账户总览 表"""
    # pin数据取最新，product数据全部叠加
    total_data = {}
    for data in overview_list:
        if not total_data:
            total_data = {
                "date": data["date"],
                "site_num": data["site_num"],
                "subaccount_num": data["subaccount_num"],
                "board_num": data["board_num"],
                "pin_num": data["pin_num"],
                "pin_saves": data["pin_saves"],
                "visitor_num": data["visitor_num"],
                "click_num": data["click_num"],
                "sales_num": data["sales_num"],
                "revenue_num": data["revenue_num"]
            }
        else:
            if data["date"] > total_data["date"]:
                total_data["date"] = data["date"]
                total_data["site_num"] = data["site_num"]
                total_data["subaccount_num"] = data["subaccount_num"]
                total_data["board_num"] = data["board_num"]
                total_data["pin_num"] = data["pin_num"]
                total_data["pin_saves"] = data["pin_saves"]
            total_data["visitor_num"] += data["visitor_num"]
            total_data["click_num"] += data["click_num"]
            total_data["sales_num"] += data["sales_num"]
            total_data["revenue_num"] += data["revenue_num"]
    # total_data.pop("date")
    return total_data


def latest_updates(pin_set_list, product_set_list, request):
    """最近更新视图"""
    new_value, old_value = account_overview_chart(pin_set_list, product_set_list, request, reslut_num=2)
    return {
        "datetime": new_value["lastest_time"] if new_value["lastest_time"] else new_value["date"],
        "new_accounts": new_value["subaccount_num"] - old_value["subaccount_num"],
        "new_board": new_value["board_num"] - old_value["board_num"],
        "new_pins": new_value["pin_num"] - old_value["pin_num"],
        "new_followers": new_value["board_followers"] - old_value["board_followers"],
        "new_saves": new_value["pin_saves"] - old_value["pin_saves"]}


def top_pins(request, period=7):
    """pins排行榜视图"""
    period = int(period)
    start_time = datetime.datetime.now() + datetime.timedelta(days=-period)
    end_time = datetime.datetime.now()
    # prev_start_time = datetime.datetime.now() + datetime.timedelta(days=-period * 2)
    # store_id = request.GET.get("store_id")
    # store = models.Store.objects.filter(user_id=request.user).first()
    # store_id = store.id if store else None
    # 开始过滤ProductHistoryData数据
    # product_set_list = models.ProductHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)),
    #                                                             Q(store_id=store_id), ~Q(tag=0))
    # if product_set_list.exists():
    #     product_set_list = product_set_list.filter(tag=product_set_list.order_by('-tag').first().tag)
    # product_id_list = []
    # for product in product_set_list:
    #     if product.product_id and product.product_id not in product_id_list:
    #         product_id_list.append(product.product_id)
    # 过滤PinterestHistoryData数据(时间范围内最新的一次数据)
    new_queryset = old_queryset = []
    query_time = start_time
    while query_time <= end_time:
        old_queryset = models.PinterestHistoryData.objects.filter(
            Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
            ~Q(product_id=None), ~Q(tag=0), Q(pinterest_account__user_id=request.user.id))
        if old_queryset.exists():
            old_queryset = old_queryset.filter(tag=old_queryset.order_by('-tag').first().tag)
            break
        query_time += datetime.timedelta(days=1)
    query_time = end_time
    while query_time >= start_time:
        # 最新数据为截止到今天0：00：00的数据
        new_queryset = models.PinterestHistoryData.objects.filter(
            Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
            ~Q(product_id=None), ~Q(tag=0), Q(pinterest_account__user_id=request.user.id))
        if new_queryset.exists():
            new_queryset = new_queryset.filter(tag=new_queryset.order_by('-tag').first().tag)
            break
        query_time += datetime.timedelta(days=-1)
    pin_dict = pins_period(new_queryset, old_queryset)
    # prev_new_queryset = prev_old_queryset = []
    # query_time = prev_start_time
    # while query_time <= start_time:
    #     prev_old_queryset = models.PinterestHistoryData.objects.filter(
    #         Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
    #         ~Q(product_id=None), ~Q(tag=0), Q(pinterest_account__user_id=request.user.id))
    #     if prev_old_queryset.exists():
    #         prev_old_queryset = prev_old_queryset.filter(tag=prev_old_queryset.order_by('-tag').first().tag)
    #         break
    #     query_time += datetime.timedelta(days=1)
    # query_time = start_time
    # while query_time >= prev_start_time:
    #     prev_new_queryset = models.PinterestHistoryData.objects.filter(
    #         Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
    #         ~Q(product_id=None), ~Q(tag=0), Q(pinterest_account__user_id=request.user.id))
    #     if prev_new_queryset.exists():
    #         prev_new_queryset = prev_new_queryset.filter(tag=prev_new_queryset.order_by('-tag').first().tag)
    #         break
    #     query_time += datetime.timedelta(days=-1)
    # prev_pin_dict = pins_period(prev_new_queryset, prev_old_queryset)
    # 计算trends
    # for pin_id, pin in pin_dict.items():
    #     prev_pin = prev_pin_dict.get(pin_id)
    #     if not prev_pin:
    #         prev_saves = 0
    #     else:
    #         prev_saves = prev_pin.get("increment", 0)
    #     if prev_saves == 0:
    #         trends = pin.get("increment", 0)
    #     else:
    #         trends = (pin.get("increment", 0) - prev_saves) * 1.0 / prev_saves
    #     pin["trends"] = trends
    # 计算前5名
    top_5_pins = sorted(pin_dict.values(), key=lambda v: (v["saves"], v["trends"]), reverse=True)
    return top_5_pins


def pins_period(new_queryset, old_queryset):
    # 计算同一个pin在一个周期的增量（最后一天的数据减去第一天的数据)

    pin_dict = {}
    for pin_obj in new_queryset.order_by('-pin_saves')[:5]:
        if pin_obj.pin_id not in pin_dict:
            old_saves = old_queryset.filter(pin_id=pin_obj.pin_id).first()
            old_saves = old_saves.pin_saves if old_saves else 0
            pin_dict[pin_obj.pin_id] = {
                "pin_uri": pin_obj.pin_uuid,
                "pin_url": pin_obj.pin.url,
                "SKU": pin_obj.product.sku,
                "image": pin_obj.pin_thumbnail,
                "pin_date": pin_obj.pin.publish_time.strftime("%Y-%m-%d %H:%M:%S") if pin_obj.pin else "no pin date",
                "saves": pin_obj.pin_saves,
                "increment": pin_obj.pin_saves - old_saves,
                "trends": round((pin_obj.pin_saves - old_saves)*1.0/old_saves, 4) if old_saves!=0 else pin_obj.pin_saves,
            }
    return pin_dict


def top_board(request, period=7):
    """board排行版视图"""
    period = int(period)
    start_time = datetime.datetime.now() + datetime.timedelta(days=-period)
    end_time = datetime.datetime.now()
    # prev_start_time = datetime.datetime.now() + datetime.timedelta(days=-period * 2)
    # store = models.Store.objects.filter(user_id=request.user).first()
    # store_id = store.id if store else None
    # # 开始过滤ProductHistoryData数据
    # product_set_list = models.ProductHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)),
    #                                                             Q(store_id=store_id), ~Q(tag=0))
    # if product_set_list.exists():
    #     product_set_list = product_set_list.filter(tag=product_set_list.order_by('-tag').first().tag)
    # # 获取board_id_list
    # board_id_list = []
    # product_id_list = []
    # for product_obj in product_set_list:
    #     if product_obj.product_id not in product_id_list:
    #         product_id_list.append(product_obj.product_id)
    # pin_set_all = models.Pin.objects.filter(product_id__in=product_id_list)
    # for pin_set in pin_set_all:
    #     if pin_set.board_id and pin_set.board_id not in board_id_list:
    #         board_id_list.append(pin_set.board_id)
    # 过滤PinterestHistoryData数据(时间范围内最新的一次数据)
    new_queryset = old_queryset = []
    query_time = start_time
    while query_time <= end_time:
        old_queryset = models.PinterestHistoryData.objects.filter(
            Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
            ~Q(tag=0), Q(pinterest_account__user_id=request.user.id))
        if old_queryset.exists():
            old_queryset = old_queryset.filter(tag=old_queryset.order_by('-tag').first().tag)
            break
        query_time += datetime.timedelta(days=1)
    query_time = end_time
    while query_time >= start_time:
        new_queryset = models.PinterestHistoryData.objects.filter(
            Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
            ~Q(tag=0), Q(pinterest_account__user_id=request.user.id))
        if new_queryset.exists():
            new_queryset = new_queryset.filter(tag=new_queryset.order_by('-tag').first().tag)
            break
        query_time += datetime.timedelta(days=-1)
    board_dict = board_period(new_queryset, old_queryset)
    # prev_new_queryset = prev_old_queryset = []
    # query_time = prev_start_time
    # while query_time <= start_time:
    #     prev_old_queryset = models.PinterestHistoryData.objects.filter(
    #         Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
    #         Q(board_id__in=board_id_list), ~Q(tag=0))
    #     if prev_old_queryset.exists():
    #         prev_old_queryset = prev_old_queryset.filter(tag=prev_old_queryset.order_by('-tag').first().tag)
    #         break
    #     query_time += datetime.timedelta(days=1)
    # query_time = start_time
    # while query_time >= prev_start_time:
    #     prev_new_queryset = models.PinterestHistoryData.objects.filter(
    #         Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
    #         Q(board_id__in=board_id_list), ~Q(tag=0))
    #     if prev_new_queryset.exists():
    #         prev_new_queryset = prev_new_queryset.filter(tag=prev_new_queryset.order_by('-tag').first().tag)
    #         break
    #     query_time += datetime.timedelta(days=-1)
    # prev_pin_dict = board_period(prev_new_queryset, prev_old_queryset)
    # 计算trends
    # for b_id, data in board_dict.items():
    #     prev_board = prev_pin_dict.get(b_id)
    #     if not prev_board:
    #         prev_increment = 0
    #     else:
    #         prev_increment = prev_board.get("increment", 0)
    #     if prev_increment == 0:
    #         trends = data.get("increment", 0)
    #     else:
    #         trends = (data.get("increment", 0) - prev_increment) * 1.0 / prev_increment
    #     data["trends"] = trends
    # 计算前5名
    top_5_board = sorted(board_dict.values(), key=lambda v: (v["followers"], v["trends"]), reverse=True)
    return top_5_board


def board_period(new_queryset, old_queryset):
    # 获取排名前五并且有关联过产品的board_id
    top_board_id_list = []
    for top_obj in new_queryset.filter(Q(pin_id=None), ~Q(board_id=None)).order_by("-board_followers"):
        # 判断此board是否关联product
        board_id = top_obj.board_id
        if new_queryset.filter(Q(board_id=board_id), ~Q(product_id=None)).exists() and board_id not in top_board_id_list:
            top_board_id_list.append(board_id)
            if len(top_board_id_list)>=5:
                break
    new_board_dict = board_period_part(new_queryset, top_board_id_list)
    old_board_dict = board_period_part(old_queryset, top_board_id_list)
    for b_id, data in new_board_dict.items():
        old_followers = old_board_dict.get(b_id)
        old_followers = old_followers.get("followers", 0) if old_followers else 0
        data["pins"] = len(set(filter(lambda x: x, data["pins"])))
        data["increment"] = data.get("followers", 0) - old_followers
        data["trends"] = round(data["increment"]*1.0/old_followers, 4) if old_followers!=0 else data["increment"]
    return new_board_dict


def board_period_part(queryset, top_board_id_list):
    board_dict = {}
    for board_obj in queryset.filter(board_id__in=top_board_id_list):
        if board_obj.board_id not in board_dict:
            board_dict[board_obj.board_id] = {
                "board_name": board_obj.board_name,
                "board_url": board_obj.board.url,
                "pins": [] if not board_obj.pin_id else [board_obj.pin_id],  # pin数
                "saves": board_obj.pin_saves,
                "create_date": board_obj.board.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "followers": board_obj.board_followers
            }
        else:
            board_dict[board_obj.board_id]["pins"].append(board_obj.pin_id)
            board_dict[board_obj.board_id]["saves"] += board_obj.pin_saves
            board_dict[board_obj.board_id]["followers"] += board_obj.board_followers
    return board_dict


def operation_record(request, result_num=None):
    # 获取请求参数
    start_time, end_time = get_request_datetime(request)
    # username_id = request.GET.get("user_id")  # 必传
    # 获取当前用户及下属用户的所有操作记录
    # if username_id:
    #     current_user_id = username_id
    # else:
    current_user_id = request.user.id
    # current_user_id 不能为空
    if current_user_id is None:
        return None
    # sub_user_set = models.User.objects.filter(Q(id=current_user_id))
    # id_list = [current_user_id]
    # for sub_user in sub_user_set:
    #     id_list.append(sub_user.id)
    # 查找记录表
    record_set = models.OperationRecord.objects.filter(Q(user_id=current_user_id),
                                                       Q(operation_time__range=(start_time, end_time))).order_by(
        "-operation_time")
    record_list = []
    for index, record in enumerate(record_set[:result_num]):
        record_list.append({
            "index": index + 1,
            "username": record.user.username,
            "action": record.action,
            "record": record.record,
            "operation_time": record.operation_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    return record_list
