# -*- coding: utf-8 -*-
# Created by: Leemon7
# Created on: 2019/5/17
import json

from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

import datetime

from sea_app import models


def get_request_params(request):
    # 获取请求参数
    start_time = request.GET.get("start_time", datetime.datetime.now() + datetime.timedelta(days=-7))
    end_time = request.GET.get("end_time", datetime.datetime.now())
    if isinstance(start_time, str):
        start_time = datetime.datetime(*map(int, start_time.split('-')))
    if isinstance(end_time, str):
        end_time = datetime.datetime(*map(int, end_time.split('-')))
    pinterest_account_id = request.GET.get("pinterest_account_id")
    board_id = request.GET.get("board_id")
    pin_id = request.GET.get("pin_id")
    search_word = request.GET.get("search", "").strip()
    store_id = request.GET.get("store_id")  # 必传
    # platform = request.GET.get("platform_id", 1)  # 必传
    return start_time, end_time, pinterest_account_id, board_id, pin_id, search_word, store_id


def get_common_data(request):
    # 获取请求参数
    start_time, end_time, pinterest_account_id, board_id, pin_id, search_word, store_id = get_request_params(request)

    # 开始过滤PinterestHistoryData数据
    pin_set_list = models.PinterestHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)))
    if search_word:
        # 查询pin_uri or board_uri or pin_description or board_name
        pin_set_list = pin_set_list.filter(
            Q(pin_uri=search_word) | Q(pin_description__icontains=search_word) | Q(board_uri=search_word) | Q(
                board_name=search_word))
    else:
        # 按选择框输入查询
        if pinterest_account_id:
            pin_set_list = pin_set_list.filter(Q(pinterest_account_id=pinterest_account_id))

        if board_id:
            pin_set_list = pin_set_list.filter(board_id=board_id)

        if pin_id:
            pin_set_list = pin_set_list.filter(Q(pin_id=pin_id))

    # 开始过滤ProductHistoryData数据
    if store_id:
        product_set_list = models.ProductHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)),
                                                                    Q(store_id=store_id))
    else:
        product_set_list = models.ProductHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)))
    return pin_set_list, product_set_list


def daily_report(pin_set_list, product_set_list):
    # 组装每日pin数据
    data_list = []
    group_dict = {}
    for item in pin_set_list:
        date = item.update_time.date()
        if date not in group_dict:
            group_dict[date] = {
                "account_following": item.account_following,
                "account_follower": item.account_follower,
                "boards": [] if not item.board_id else [item.board_id],  # board数
                "board_follower": item.board_follower,
                "pins": [] if not item.pin_id else [item.pin_id],  # pin数
                "pin_repin": item.pin_repin,
                "pin_like": item.pin_like,
                "pin_comments": item.pin_comment,
                "pin_view": item.pin_views,
                "pin_clicks": item.pin_clicks,
                "product_sales": 0,
                "product_revenue": 0,
                "products": [] if not item.product_id else [item.product_id],  # product
            }
        else:
            group_dict[date]["account_following"] += item.account_following
            group_dict[date]["account_follower"] += item.account_follower
            group_dict[date]["boards"].append(item.board_id)
            group_dict[date]["board_follower"] += item.board_follower
            group_dict[date]["pins"].append(item.pin_id)
            group_dict[date]["pin_repin"] += item.pin_repin
            group_dict[date]["pin_like"] += item.pin_like
            group_dict[date]["pin_comments"] += item.pin_comment
            group_dict[date]["pin_view"] += item.pin_views
            group_dict[date]["pin_clicks"] += item.pin_clicks
            group_dict[date]["products"].append(item.product_id)
    for day, info in group_dict.items():
        data = {
            "date": day.strftime("%Y-%m-%d"),
            "account_following": info["account_following"],
            "account_follower": info["account_follower"],
            "boards": len(set(filter(lambda x: x, info["boards"]))),
            "board_follower": info["board_follower"],
            "pins": len(set(filter(lambda x: x, info["pins"]))),
            "pin_repin": info["pin_repin"],
            "pin_like": info["pin_like"],
            "pin_comments": info["pin_comments"],
            "pin_view": info["pin_view"],
            "pin_clicks": info["pin_clicks"],
            "product_sales": info["product_sales"],
            "product_revenue": info["product_revenue"],
            # "product_list": info["products"],
        }

        # 组装每日product对应pin的数据
        product_set_list_pre = product_set_list.filter(Q(update_time__range=(day + datetime.timedelta(days=-1), day)))
        store_obj = product_set_list_pre.filter(Q(product_id=None)).first()
        if store_obj:
            data["store_visitors"] = store_obj.store_visitors
            data["store_new_visitors"] = store_obj.store_new_visitors
        else:
            data["store_visitors"] = 0
            data["store_new_visitors"] = 0
        product_set_list = product_set_list_pre.filter(Q(product_id__in=info["products"]))
        for item in product_set_list:
            data["product_sales"] += item.product_sale
            data["product_revenue"] += item.product_revenue

        data_list.append(data)
    return data_list


def daily_report_view(request):
    """日报视图函数"""
    pin_set_list, product_set_list = get_common_data(request)
    data_list = daily_report(pin_set_list, product_set_list)
    return data_list


def subaccount_report_view(request, type):
    """子账号视图函数"""
    pin_set_list, product_set_list = get_common_data(request)
    # 取PinterestHistoryData最新一天的数据, ProductHistoryData时间范围内所有数据
    start_time = request.GET.get("start_time", datetime.datetime.now() + datetime.timedelta(days=-7))
    end_time = request.GET.get("end_time", datetime.datetime.now())
    if isinstance(start_time, str):
        start_time = datetime.datetime(*map(int, start_time.split('-')))
    if isinstance(end_time, str):
        end_time = datetime.datetime(*map(int, end_time.split('-')))

    while end_time >= start_time:
        pin_set_list_result = pin_set_list.filter(
            Q(update_time__range=(end_time + datetime.timedelta(days=-1), end_time)))
        if pin_set_list_result:
            break
        end_time += datetime.timedelta(days=-1)
    pin_set_list = pin_set_list_result
    if type == 'pins':
        # pins report
        data_list = pins_report(pin_set_list, product_set_list)
    elif type == 'board':
        # boards report
        data_list = board_report(pin_set_list, product_set_list)
    elif type == 'subaccount':
        # subaccount report
        data_list = subaccount_report(pin_set_list, product_set_list)
    else:
        # 请求有误
        data_list = "An error occurred in the request and data could not be retrieved"

    return data_list


def subaccount_report(pin_set_list, product_set_list):
    # subaccount report
    data_list = []
    group_dict = {}
    set_list = pin_set_list.filter(~Q(pinterest_account_id=None))
    # 取时间范围内最新subaccount数据及subaccount下所有board数和pin信息总数
    for item in set_list:
        subaccount_id = item.pinterest_account_id
        if subaccount_id not in group_dict:
            group_dict[subaccount_id] = {
                "account_name": item.account_name,
                "boards": [] if not item.board_id else [item.board_id],  # board数
                "account_following": item.account_following,
                "account_follower": item.account_follower,
                "pins": [] if not item.pin_id else [item.pin_id],  # pin数
                "pin_repin": item.pin_repin,
                "pin_like": item.pin_like,
                "pin_comments": item.pin_comment,
                "pin_view": item.pin_views,
                "pin_clicks": item.pin_clicks,
                "products": [] if not item.product_id else [item.product_id],  # product
            }
        else:
            group_dict[subaccount_id]["boards"].append(item.board_uri)  # board数
            group_dict[subaccount_id]["pins"].append(item.pin_uri)  # pin数
            group_dict[subaccount_id]["pin_repin"] += item.pin_repin
            group_dict[subaccount_id]["pin_like"] += item.pin_like
            group_dict[subaccount_id]["pin_comments"] += item.pin_comment
            group_dict[subaccount_id]["pin_view"] += item.pin_views
            group_dict[subaccount_id]["pin_clicks"] += item.pin_clicks
            group_dict[subaccount_id]["products"].append(item.product_id)  # product
    for subaccount_id, info in group_dict.items():
        data = {
            "subaccount_id": subaccount_id,
            "account_name": info["account_name"],
            "account_following": info["account_following"],
            "account_follower": info["account_follower"],
            "boards": len(set(filter(lambda x: x, info["boards"]))),
            "pins": len(set(filter(lambda x: x, info["pins"]))),
            "pin_repin": info["pin_repin"],
            "pin_like": info["pin_like"],
            "pin_comments": info["pin_comments"],
            "pin_view": info["pin_view"],
            "pin_clicks": info["pin_clicks"],
            "store_visitors": 0,
            "store_new_visitors": 0,
            "product_sales": 0,
            "product_revenue": 0
        }
        # 组装product对应pin的数据
        store_set_list = product_set_list.filter(Q(product_id__in=info["products"]) | Q(product_id=None))
        for item in store_set_list:
            data["store_visitors"] += item.store_visitors
            data["store_new_visitors"] += item.store_new_visitors
            data["product_sales"] += item.product_sale
            data["product_revenue"] += item.product_revenue

        data_list.append(data)
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
                "board_follower": item.board_follower,
                "pins": [] if not item.pin_id else [item.pin_id],  # pin数
                "pin_repin": item.pin_repin,
                "pin_like": item.pin_like,
                "pin_comments": item.pin_comment,
                "pin_view": item.pin_views,
                "pin_clicks": item.pin_clicks,
                "products": [] if not item.product_id else [item.product_id],  # product
            }
        else:
            group_dict[board_id]["pins"].append(item.pin_id)  # pin数
            group_dict[board_id]["pin_repin"] += item.pin_repin
            group_dict[board_id]["pin_like"] += item.pin_like
            group_dict[board_id]["pin_comments"] += item.pin_comment
            group_dict[board_id]["pin_view"] += item.pin_views
            group_dict[board_id]["pin_clicks"] += item.pin_clicks
            group_dict[board_id]["products"].append(item.product_id)  # product

    for board_id, info in group_dict.items():
        data = {
            "board_id": board_id,
            "board_name": info["board_name"],
            "board_follower": info["board_follower"],
            "pins": len(set(filter(lambda x: x, info["pins"]))),
            "pin_repin": info["pin_repin"],
            "pin_like": info["pin_like"],
            "pin_comments": info["pin_comments"],
            "pin_view": info["pin_view"],
            "pin_clicks": info["pin_clicks"],
            "store_visitors": 0,
            "store_new_visitors": 0,
            "product_sales": 0,
            "product_revenue": 0
        }
        # 组装product对应pin的数据
        store_set_list = product_set_list.filter(Q(product_id__in=info["products"]) | Q(product_id=None))
        for item in store_set_list:
            data["store_visitors"] += item.store_visitors
            data["store_new_visitors"] += item.store_new_visitors
            data["product_sales"] += item.product_sale
            data["product_revenue"] += item.product_revenue

        data_list.append(data)
    return data_list


def pins_report(pin_set_list, product_set_list):
    # pins report
    data_list = []
    group_dict = {}
    set_list = pin_set_list.filter(~Q(pin_uri=None), ~Q(pin_uri=""))
    # 取时间范围内最新的pin数据
    for item in set_list:
        pin_uri = item.pin_uri
        if pin_uri not in group_dict:
            group_dict[pin_uri] = {
                "update_time": item.update_time,
                "pin_thumbnail": item.pin_thumbnail,
                "pin_repin": item.pin_repin,
                "pin_like": item.pin_like,
                "pin_comments": item.pin_comment,
                "pin_view": item.pin_views,
                "pin_clicks": item.pin_clicks,
                "product_id": item.product_id
            }
        else:
            if item.update_time > group_dict[pin_uri]["update_time"]:
                group_dict[pin_uri] = {
                    "update_time": item.update_time,
                    "pin_thumbnail": item.pin_thumbnail,
                    "pin_repin": item.pin_repin,
                    "pin_like": item.pin_like,
                    "pin_comments": item.pin_comment,
                    "pin_view": item.pin_views,
                    "pin_clicks": item.pin_clicks,
                    "product_id": item.product_id
                }
    for pin_uri, info in group_dict.items():
        data = {
            "pin_uri": pin_uri,
            "pin_thumbnail": info["pin_thumbnail"],
            "pin_repin": info["pin_repin"],
            "pin_like": info["pin_like"],
            "pin_comments": info["pin_comments"],
            "pin_view": info["pin_view"],
            "pin_clicks": info["pin_clicks"],
            "store_visitors": 0,
            "store_new_visitors": 0,
            "product_sales": 0,
            "product_revenue": 0,
            # "product_id": info["product_id"]
        }
        # 组装product对应pin的数据
        store_set_list = product_set_list.filter(Q(product_id=None))
        for item in store_set_list:
            data["store_visitors"] += item.store_visitors
            data["store_new_visitors"] += item.store_new_visitors
        product_obj_list = product_set_list.filter(Q(product_id=info["product_id"]))
        for product_obj in product_obj_list:
            data["product_sales"] += product_obj.product_sale
            data["product_revenue"] += product_obj.product_revenue

        data_list.append(data)
    return data_list


def dash_board_change_part(request):
    """DashBoard视图 随筛选变动部分"""
    pin_set_list, product_set_list = get_common_data(request)
    # 账户总览 图数据
    overview_list = account_overview_chart(pin_set_list, product_set_list, request)
    # 账户总览 表数据
    total_data = account_overview_table(overview_list)
    # 最新新增数据
    latest_update = latest_updates(pin_set_list, product_set_list, request)

    return {"overview_list": overview_list, "total_data": total_data, "latest_update": latest_update}


def dash_board_fixed_part(request):
    """DashBoard视图 固定部分"""
    # top pins
    top_5_pins = top_pins(request, period=7)
    # top board
    top_5_board = top_board(request, period=7)
    # activity log
    record_list = operation_record(request)
    return {"top_5_pins": top_5_pins, "top_5_board": top_5_board, "record_list": record_list}


def get_num(queryset, fieldname):
    # 通过queryset获取计数
    lst = []
    for item in queryset:
        lst.append(getattr(item, fieldname))
    return len(set(lst))


def count_num(queryset, fieldname):
    # 获取fieldname的总数
    fieldname_num = 0
    for item in queryset:
        fieldname_num += getattr(item, fieldname)
    return fieldname_num


def site_count(pin_set_list, product_set_list, oneday=datetime.datetime.now()):
    # 获取oneday的数据，默认取昨天更新的数据
    # 获取站点总数
    site_num = get_num(product_set_list, "store_id")
    pin_queryset = pin_set_list.filter(Q(update_time__range=(oneday + datetime.timedelta(days=-1), oneday)))
    if not pin_queryset:
        return {"site_num": site_num, "subaccount_num": 0, "board_num": 0, "pin_num": 0,
                "visitor_num": 0, "click_num": 0, "sales_num": 0, "revenue_num": 0,
                "board_followers": 0, "pin_repins": 0}
    # 获取帐号总数
    subaccount_set = pin_queryset.filter(Q(board_id=None), Q(pin_id=None))
    subaccount_num = get_num(subaccount_set, "pinterest_account_id")
    # 获取Board总数
    board_set = pin_queryset.filter(~Q(board_id=None), Q(pin_id=None))
    board_num = get_num(board_set, "board_id")
    board_followers = count_num(board_set, 'board_follower')
    # 获取pin总数
    pin_set = pin_queryset.filter(~Q(pin_id=None))
    pin_num = get_num(pin_set, "pin_id")
    # 获取click总数
    click_num = count_num(pin_set, "pin_clicks")
    pin_repins = count_num(pin_set, "pin_repin")

    # 获取product_id_list
    product_id_list = []
    for pin in pin_set:
        product_id_list.append(pin.product_id)
    product_id_list = set(product_id_list)

    # 获取sales总数
    product_set = product_set_list.filter(Q(product_id__in=product_id_list))
    sales_num = count_num(product_set, "product_sale")
    # 获取revenue总数
    revenue_num = count_num(product_set, "product_revenue")
    # 获取visitor总数,需要关联pin中的product_id,通过product_set获取store_set
    store_id_list = []
    for product in product_set:
        store_id_list.append(product.store_id)
    store_id_list = set(store_id_list)
    store_set = product_set_list.filter(Q(store_id__in=store_id_list), Q(product_id=None))
    visitor_num = count_num(store_set, "store_visitors")

    return {
        "site_num": site_num,
        "subaccount_num": subaccount_num,
        "board_num": board_num,
        "pin_num": pin_num,
        "visitor_num": visitor_num,
        "click_num": click_num,
        "sales_num": sales_num,
        "revenue_num": revenue_num,
        "board_followers": board_followers,
        "pin_repins": pin_repins
    }


def time_range_list(start_time, end_time):
    time_list = []
    for i in range((end_time.date() - start_time.date()).days + 1):
        day = start_time + datetime.timedelta(days=i)
        time_list.append(day)
    return time_list


def account_overview_chart(pin_set_list, product_set_list, request, reslut_num=None):
    """账户总览 图"""
    # 按天循环时间范围内，获取当天数据
    start_time = request.GET.get("start_time", datetime.datetime.now() + datetime.timedelta(days=-7))
    end_time = request.GET.get("end_time", datetime.datetime.now())
    if isinstance(start_time, str):
        start_time = datetime.datetime(*map(int, start_time.split('-')))
    if isinstance(end_time, str):
        end_time = datetime.datetime(*map(int, end_time.split('-')))
    time_list = time_range_list(start_time, end_time)
    overview_list = []
    for day in time_list[::-1]:
        day_count = site_count(pin_set_list, product_set_list, day)
        day_count["date"] = day.strftime("%Y-%m-%d %H:%M:%S")
        overview_list.append(day_count)
        if reslut_num and len(overview_list) >= reslut_num:
            break
    return overview_list


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
            total_data["visitor_num"] += data["visitor_num"]
            total_data["click_num"] += data["click_num"]
            total_data["sales_num"] += data["sales_num"]
            total_data["revenue_num"] += data["revenue_num"]
    total_data.pop("date")
    return total_data


def latest_updates(pin_set_list, product_set_list, request):
    """最近更新视图"""
    new_value, old_value = account_overview_chart(pin_set_list, product_set_list, request, reslut_num=2)
    return {
        "datetime": new_value["date"],
        "new_accounts": new_value["subaccount_num"] - old_value["subaccount_num"],
        "new_board": new_value["board_num"] - old_value["board_num"],
        "new_pins": new_value["pin_num"] - old_value["pin_num"],
        "new_followers": new_value["board_followers"] - old_value["board_followers"],
        "new_repins": new_value["pin_repins"] - old_value["pin_repins"]}


def top_pins(request, period=7):
    """pins排行榜视图"""
    start_time = datetime.datetime.now() + datetime.timedelta(days=-period)
    end_time = datetime.datetime.now()
    prev_start_time = datetime.datetime.now() + datetime.timedelta(days=-period * 2)
    store_id = request.GET.get("store_id")
    # 开始过滤ProductHistoryData数据
    if store_id:
        product_set_list = models.ProductHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)),
                                                                    Q(store_id=store_id))
    else:
        product_set_list = models.ProductHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)))
    product_id_list = []
    for product in product_set_list:
        product_id_list.append(product.product_id)
    product_id_list = list(set(filter(lambda x: x, product_id_list)))
    # 过滤PinterestHistoryData数据(时间范围内最新的一次数据)
    query_time = start_time
    while query_time <= end_time:
        old_queryset = models.PinterestHistoryData.objects.filter(Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
                                                              Q(product_id__in=product_id_list))
        if old_queryset:
            break
        query_time += datetime.timedelta(days=1)
    query_time = end_time
    while query_time >= start_time:
        new_queryset = models.PinterestHistoryData.objects.filter(Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
                                                              Q(product_id__in=product_id_list))
        if new_queryset:
            break
        query_time += datetime.timedelta(days=-1)
    pin_dict = pins_period(new_queryset,old_queryset)

    query_time = prev_start_time
    while query_time <= start_time:
        prev_old_queryset = models.PinterestHistoryData.objects.filter(
            Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
            Q(product_id__in=product_id_list))
        if prev_old_queryset:
            break
        query_time += datetime.timedelta(days=1)
    query_time = start_time
    while query_time >= prev_start_time:
        prev_new_queryset = models.PinterestHistoryData.objects.filter(
            Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
            Q(product_id__in=product_id_list))
        if prev_new_queryset:
            break
        query_time += datetime.timedelta(days=-1)
    prev_pin_dict = pins_period(prev_new_queryset, prev_old_queryset)
    # 计算trends
    for pin_id, pin in pin_dict.items():
        prev_pin = prev_pin_dict.get(pin_id)
        if not prev_pin:
            prev_repins = 0
        else:
            prev_repins = prev_pin.get("increment",0)
        if prev_repins == 0:
            trends = pin.get("increment",0)
        else:
            trends = (pin.get("increment",0) - prev_repins) * 1.0 / prev_repins
        pin["trends"] = trends
    # 计算前5名
    top_5_pins = sorted(pin_dict.values(), key=lambda v: v["repins"], reverse=True)[0:5]
    return top_5_pins


def pins_period(new_queryset, old_queryset):
    # 计算同一个pin在一个周期的增量（最后一天的数据，减去第一天的数据)

    pin_dict = {}
    for pin_obj in new_queryset:
        if pin_obj.pin_id not in pin_dict:
            old_repin = old_queryset.filter(Q(pin_id=pin_obj.pin_id)).first()
            old_repin = old_repin.pin_repin if old_repin else 0
            pin_dict[pin_obj.pin_id] = {
                "SKU": pin_obj.product.sku,
                "image": pin_obj.pin_thumbnail,
                "pin_date": pin_obj.pin.publish_time,
                "repins": pin_obj.pin_repin,
                "increment": pin_obj.pin_repin - old_repin
            }
    return pin_dict


def top_board(request, period=7):
    """board排行版视图"""
    start_time = datetime.datetime.now() + datetime.timedelta(days=-period)
    end_time = datetime.datetime.now()
    prev_start_time = datetime.datetime.now() + datetime.timedelta(days=-period * 2)
    store_id = request.GET.get("store_id")
    # 开始过滤ProductHistoryData数据
    if store_id:
        product_set_list = models.ProductHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)),
                                                                    Q(store_id=store_id))
    else:
        product_set_list = models.ProductHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)))
    # 获取board_id_list
    board_id_list = []
    for product_obj in product_set_list:
        if not product_obj.product_id:
            continue
        pin_set_all = product_obj.product.pin_set.all()
        for pin_set in pin_set_all:
            board_id_list.append(pin_set.board_id)
    board_id_list = list(set(filter(lambda x: x, board_id_list)))
    # 过滤PinterestHistoryData数据(时间范围内最新的一次数据)
    query_time = start_time
    while query_time <= end_time:
        old_queryset = models.PinterestHistoryData.objects.filter(
            Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
            Q(board_id__in=board_id_list))
        if old_queryset:
            break
        query_time += datetime.timedelta(days=1)
    query_time = end_time
    while query_time >= start_time:
        new_queryset = models.PinterestHistoryData.objects.filter(
            Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
            Q(board_id__in=board_id_list))
        if new_queryset:
            break
        query_time += datetime.timedelta(days=-1)
    board_dict = board_period(new_queryset, old_queryset)

    query_time = prev_start_time
    while query_time <= start_time:
        prev_old_queryset = models.PinterestHistoryData.objects.filter(
            Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
            Q(board_id__in=board_id_list))
        if prev_old_queryset:
            break
        query_time += datetime.timedelta(days=1)
    query_time = start_time
    while query_time >= prev_start_time:
        prev_new_queryset = models.PinterestHistoryData.objects.filter(
            Q(update_time__range=(query_time + datetime.timedelta(days=-1), query_time)),
            Q(board_id__in=board_id_list))
        if prev_new_queryset:
            break
        query_time += datetime.timedelta(days=-1)
    prev_pin_dict = board_period(prev_new_queryset, prev_old_queryset)
    # 计算trends
    for b_id, data in board_dict.items():
        prev_board = prev_pin_dict.get(b_id)
        if not prev_board:
            prev_increment = 0
        else:
            prev_increment = prev_board.get("increment", 0)
        if prev_increment == 0:
            trends = data.get("increment", 0)
        else:
            trends = (data.get("increment", 0) - prev_increment) * 1.0 / prev_increment
        data["trends"] = trends
    # 计算前5名
    top_5_board = sorted(board_dict.values(), key=lambda v: v["followers"], reverse=True)[0:5]
    return top_5_board


def board_period(new_queryset,old_queryset):
    new_board_dict = board_period_part(new_queryset)
    old_board_dict = board_period_part(old_queryset)
    for b_id, data in new_board_dict.items():
        old_followers = old_board_dict.get(b_id)
        old_followers = old_followers.get("followers",0) if old_followers else 0
        data["pins"] = len(set(filter(lambda x: x, data["pins"])))
        data["increment"] = data.get("followers", 0) - old_followers
    return new_board_dict


def board_period_part(queryset):
    board_dict = {}
    for board_obj in queryset:
        if board_obj.board_id not in board_dict:
            board_dict[board_obj.board_id] = {
                "board_name": board_obj.board_name,
                "pins": [] if not board_obj.pin_id else [board_obj.pin_id],  # pin数
                "repins": board_obj.pin_repin,
                "create_date": board_obj.board.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "followers": board_obj.board_follower
            }
        else:
            board_dict[board_obj.board_id]["pins"].append(board_obj.pin_id)
            board_dict[board_obj.board_id]["repins"] += board_obj.pin_repin
            board_dict[board_obj.board_id]["followers"] += board_obj.board_follower
    return board_dict


def operation_record(request, result_num=None):
    # 获取请求参数
    start_time = request.GET.get("start_time", datetime.datetime.now() + datetime.timedelta(days=-7))
    end_time = request.GET.get("end_time", datetime.datetime.now())
    if isinstance(start_time, str):
        start_time = datetime.datetime(*map(int, start_time.split('-')))
    if isinstance(end_time, str):
        end_time = datetime.datetime(*map(int, end_time.split('-')))
    username_id = request.GET.get("user_id")  # 必传
    # 获取当前用户及下属用户的所有操作记录
    if username_id:
        current_user_id = username_id
    else:
        current_user_id = request.user.id
    # current_user_id 不能为空
    if current_user_id is None:
        return None
    sub_user_set = models.User.objects.filter(Q(parent_id=current_user_id))
    id_list = [current_user_id,]
    for sub_user in sub_user_set:
        id_list.append(sub_user.id)
    # 查找记录表
    record_set = models.OperationRecord.objects.filter(Q(user_id__in=id_list),
                 Q(operation_time__range=(start_time, end_time))).order_by("-operation_time")
    record_list = []
    for index, record in enumerate(record_set[:result_num]):
        record_list.append({
            "index": index + 1,
            "username": record.user.username,
            "action": record.action,
            "record": record.record,
            "operation_time": record.operation_time
        })
    return record_list


def operation_record_listview(request):
    """操作记录 视图"""
    record_list = operation_record(request)
    if record_list is None:
        return JsonResponse({"data": record_list, "status": status.HTTP_404_NOT_FOUND})
    return JsonResponse({"data": record_list, "status": status.HTTP_200_OK})

