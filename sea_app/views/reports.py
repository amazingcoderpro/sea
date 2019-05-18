# -*- coding: utf-8 -*-
# Created by: Leemon7
# Created on: 2019/5/17
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
    product_set_list = models.ProductHistoryData.objects.filter(Q(update_time__range=(start_time, end_time)),
                                                                Q(store_id=store_id))
    return pin_set_list, product_set_list


def subaccount_daily_report(pin_set_list, product_set_list):
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
                "products": [] if not item.product_id else [item.product_id],  # product数
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
            "date": day,
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


def board_daily_report(pin_set_list, product_set_list):
    pass


def pins_daily_report(pin_set_list, product_set_list):
    pass


def daily_report_view(request):
    pin_set_list, product_set_list = get_common_data(request)
    type = 'subaccount'
    if type == 'pins':
        # pins report
        data_list = pins_daily_report(pin_set_list, product_set_list)
    elif type == 'board':
        # boards report
        data_list = board_daily_report(pin_set_list, product_set_list)
    elif type == 'subaccount':
        # subaccount report
        data_list = subaccount_daily_report(pin_set_list, product_set_list)
    return JsonResponse({"data": data_list, "type": type, "status":status.HTTP_200_OK})
