# -*- coding: utf-8 -*-
import datetime
from datetime import datetime, timedelta

from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from sea_app import models
from sea_app.filters import filters
from sea_app.pageNumber.pageNumber import PNPagination
from sea_app.serializers import report


class DailyReportView(generics.ListAPIView):
    """日报列表展示"""
    queryset = models.ProductHistoryData.objects.all()
    serializer_class = report.DailyReportSerializer
    pagination_class = PNPagination
    filter_backends = (filters.DailyReportFilter,)

    # permission_classes = (IsAuthenticated,)
    # authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        data_list = []
        queryset = self.filter_queryset(self.get_queryset())
        group_dict = {}
        for item in queryset:
            date = item.update_time.date()
            if date not in group_dict:
                group_dict[date] = {
                    "account_following": item.account_following,
                    "account_follower": item.account_follower,
                    "boards": [] if not item.board_uri else [item.board_uri],  # board数
                    "board_follower": item.board_follower,
                    "pins": [] if not item.pin_uri else [item.pin_uri],  # pin数
                    "pin_repin": item.pin_repin,
                    "pin_like": item.pin_like,
                    "pin_comments": item.pin_comment,
                    "store_visitors": item.store_visitors,
                    "store_new_visitors": item.store_new_visitors,
                    "pin_view": item.pin_views,
                    "pin_clicks": item.pin_clicks,
                    "product_sales": item.product_sale,
                    "product_revenue": item.product_revenue
                }
            else:
                group_dict[date]["account_following"] += item.account_following
                group_dict[date]["account_follower"] += item.account_follower
                group_dict[date]["boards"].append(item.board_uri)
                group_dict[date]["board_follower"] += item.board_follower
                group_dict[date]["pins"].append(item.pin_uri)
                group_dict[date]["pin_repin"] += item.pin_repin
                group_dict[date]["pin_like"] += item.pin_like
                group_dict[date]["pin_comments"] += item.pin_comment
                group_dict[date]["store_visitors"] += item.store_visitors
                group_dict[date]["store_new_visitors"] += item.store_new_visitors
                group_dict[date]["pin_view"] += item.pin_views
                group_dict[date]["pin_clicks"] += item.pin_clicks
                group_dict[date]["product_sales"] += item.product_sale
                group_dict[date]["product_revenue"] += item.product_revenue

        for day, info in group_dict.items():
            data = {
                "date": day,
                "account_following": info["account_following"],
                "account_follower": info["account_follower"],
                "boards": len(info["boards"]),
                "board_follower": info["board_follower"],
                "pins": len(info["pins"]),
                "pin_repin": info["pin_repin"],
                "pin_like": info["pin_like"],
                "pin_comments": info["pin_comments"],
                "store_visitors": info["store_visitors"],
                "store_new_visitors": info["store_new_visitors"],
                "pin_view": info["pin_view"],
                "pin_clicks": info["pin_clicks"],
                "product_sales": info["product_sales"],
                "product_revenue": info["product_revenue"]
            }
            data_list.append(data)

        page = self.paginate_queryset(data_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(data_list)
        return Response(data_list)


class SubAccountReportView(generics.ListAPIView):
    queryset = models.ProductHistoryData.objects.all()
    serializer_class = report.DailyReportSerializer
    pagination_class = PNPagination
    filter_backends = (filters.DailyReportFilter,)

    # permission_classes = (IsAuthenticated,)
    # authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 取最新一天的数据
        end_time = request.query_params.dict().get('end_time', datetime.now().date())
        queryset = queryset.filter(Q(update_time__range=(end_time + timedelta(days=-1), end_time)))
        data_list = []
        type = request.parser_context['kwargs']['type']
        if type == 'pins':
            # pins report
            data_list = self.pins_report(queryset)
        elif type == 'board':
            # boards report
            data_list = self.board_report(queryset)
        elif type == 'subaccount':
            # subaccount report
            data_list = self.subaccount_report(queryset)

        page = self.paginate_queryset(data_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(data_list)
        return Response(data_list)

    def pins_report(self, queryset):
        # pins report
        data_list = []
        group_dict = {}
        set_list = queryset.filter(~Q(pin_uri=None), ~Q(pin_uri=""))
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
                    "store_visitors": item.store_visitors,
                    "store_new_visitors": item.store_new_visitors,
                    "pin_view": item.pin_views,
                    "pin_clicks": item.pin_clicks,
                    "product_sales": item.product_sale,
                    "product_revenue": item.product_revenue
                }
            else:
                if item.update_time > group_dict[pin_uri]["update_time"]:
                    group_dict[pin_uri] = {
                        "update_time": item.update_time,
                        "pin_thumbnail": item.pin_thumbnail,
                        "pin_repin": item.pin_repin,
                        "pin_like": item.pin_like,
                        "pin_comments": item.pin_comment,
                        "store_visitors": item.store_visitors,
                        "store_new_visitors": item.store_new_visitors,
                        "pin_view": item.pin_views,
                        "pin_clicks": item.pin_clicks,
                        "product_sales": item.product_sale,
                        "product_revenue": item.product_revenue
                    }
        for pin_uri, info in group_dict.items():
            data = {
                "pin_uri": pin_uri,
                "pin_thumbnail": info["pin_thumbnail"],
                "pin_repin": info["pin_repin"],
                "pin_like": info["pin_like"],
                "pin_comments": info["pin_comments"],
                "store_visitors": info["store_visitors"],
                "store_new_visitors": info["store_new_visitors"],
                "pin_view": info["pin_view"],
                "pin_clicks": info["pin_clicks"],
                "product_sales": info["product_sales"],
                "product_revenue": info["product_revenue"]
            }
            data_list.append(data)
        return data_list

    def board_report(self, queryset):
        # board report
        data_list = []
        group_dict = {}
        set_list = queryset.filter(~Q(board_uri=None), ~Q(board_uri=""))
        # 取时间范围内最新board数据及board下所有pin总数
        for item in set_list:
            board_id = models.Board.objects.filter(id=item.board_uri).first().id
            if board_id not in group_dict:
                group_dict[board_id] = {
                    # "update_time": item.update_time,
                    "board_name": item.board_name,
                    "board_follower": item.board_follower,
                    "pins": [] if not item.pin_uri else [item.pin_uri],  # pin数
                    "pin_repin": item.pin_repin,
                    "pin_like": item.pin_like,
                    "pin_comments": item.pin_comment,
                    "store_visitors": item.store_visitors,
                    "store_new_visitors": item.store_new_visitors,
                    "pin_view": item.pin_views,
                    "pin_clicks": item.pin_clicks,
                    "product_sales": item.product_sale,
                    "product_revenue": item.product_revenue
                }
            else:
                group_dict[board_id]["pins"].append(item.pin_uri)  # pin数
                group_dict[board_id]["pin_repin"] += item.pin_repin
                group_dict[board_id]["pin_like"] += item.pin_like
                group_dict[board_id]["pin_comments"] += item.pin_comment
                group_dict[board_id]["store_visitors"] += item.store_visitors
                group_dict[board_id]["store_new_visitors"] += item.store_new_visitors
                group_dict[board_id]["pin_view"] += item.pin_views
                group_dict[board_id]["pin_clicks"] += item.pin_clicks
                group_dict[board_id]["product_sales"] += item.product_sale
                group_dict[board_id]["product_revenue"] += item.product_revenue
        for board_id, info in group_dict.items():
            data = {
                "board_id": board_id,
                "board_name": info["board_name"],
                "board_follower": info["board_follower"],
                "pins": len(info["pins"]),
                "pin_repin": info["pin_repin"],
                "pin_like": info["pin_like"],
                "pin_comments": info["pin_comments"],
                "store_visitors": info["store_visitors"],
                "store_new_visitors": info["store_new_visitors"],
                "pin_view": info["pin_view"],
                "pin_clicks": info["pin_clicks"],
                "product_sales": info["product_sales"],
                "product_revenue": info["product_revenue"]
            }
            data_list.append(data)
        return data_list

    def subaccount_report(self, queryset):
        # subaccount report
        data_list = []
        group_dict = {}
        set_list = queryset.filter(~Q(pinterest_account_uri=None), ~Q(pinterest_account_uri=""))
        # 取时间范围内最新subaccount数据及subaccount下所有board数和pin信息总数
        for item in set_list:
            subaccount_id = models.PinterestAccount.objects.filter(id=item.pinterest_account_uri).first().id
            if subaccount_id not in group_dict:
                group_dict[subaccount_id] = {
                    "account_name": item.account_name,
                    "boards": [] if not item.board_uri else [item.board_uri],  # board数
                    "account_following": item.account_following,
                    "account_follower": item.account_follower,
                    "pins": [] if not item.pin_uri else [item.pin_uri],  # pin数
                    "pin_repin": item.pin_repin,
                    "pin_like": item.pin_like,
                    "pin_comments": item.pin_comment,
                    "store_visitors": item.store_visitors,
                    "store_new_visitors": item.store_new_visitors,
                    "pin_view": item.pin_views,
                    "pin_clicks": item.pin_clicks,
                    "product_sales": item.product_sale,
                    "product_revenue": item.product_revenue
                }
            else:
                group_dict[subaccount_id]["boards"].append(item.board_uri)  # board数
                group_dict[subaccount_id]["pins"].append(item.pin_uri)  # pin数
                group_dict[subaccount_id]["pin_repin"] += item.pin_repin
                group_dict[subaccount_id]["pin_like"] += item.pin_like
                group_dict[subaccount_id]["pin_comments"] += item.pin_comment
                group_dict[subaccount_id]["store_visitors"] += item.store_visitors
                group_dict[subaccount_id]["store_new_visitors"] += item.store_new_visitors
                group_dict[subaccount_id]["pin_view"] += item.pin_views
                group_dict[subaccount_id]["pin_clicks"] += item.pin_clicks
                group_dict[subaccount_id]["product_sales"] += item.product_sale
                group_dict[subaccount_id]["product_revenue"] += item.product_revenue
        for subaccount_id, info in group_dict.items():
            data = {
                "subaccount_id": subaccount_id,
                "account_name": info["account_name"],
                "account_following": info["account_following"],
                "account_follower": info["account_follower"],
                "boards": len(info["boards"]),
                "pins": len(info["pins"]),
                "pin_repin": info["pin_repin"],
                "pin_like": info["pin_like"],
                "pin_comments": info["pin_comments"],
                "store_visitors": info["store_visitors"],
                "store_new_visitors": info["store_new_visitors"],
                "pin_view": info["pin_view"],
                "pin_clicks": info["pin_clicks"],
                "product_sales": info["product_sales"],
                "product_revenue": info["product_revenue"]
            }
            data_list.append(data)
        return data_list


class DashBoardView(generics.ListAPIView):
    queryset = models.PinterestHistoryData.objects.all()
    serializer_class = report.DailyReportSerializer
    # pagination_class = PNPagination
    filter_backends = (filters.DashBoardFilter,)

    # permission_classes = (IsAuthenticated,)
    # authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # self.account_overview(queryset, request)
        self.site_count(queryset)

    def get_num(self, queryset, fieldname):
        # 通过queryset获取计数
        lst = []
        for item in queryset:
            lst.append(getattr(item, fieldname))
        return len(set(lst))

    def count_num(self, queryset, fieldname):
        # 获取fieldname的总数
        fieldname_num = 0
        for item in queryset:
            fieldname_num += getattr(item, fieldname)
        return fieldname_num

    def time_range_list(self, start_time, end_time):
        time_list = []
        for i in range((end_time.date() - start_time.date()).days + 1):
            day = start_time + timedelta(days=i)
            time_list.append(day)
        return time_list

    def account_overview(self, queryset, request):
        # 按天循环时间范围内，获取当天数据
        condtions = request.query_params.dict()
        start_time = condtions.get('start_time', datetime.now() + timedelta(days=-7))
        end_time = condtions.get('end_time', datetime.now())
        time_list = self.time_range_list(start_time, end_time)
        overview_dict = {}
        for day in time_list:
            day_count = self.site_count(queryset, day)
            overview_dict[day] = day_count
        return overview_dict

    def site_count(self, queryset, oneday=datetime.now()):
        # ???如果有一天没更新，就没办法取昨天得数据
        # 获取截止到oneday最新的数据，默认取昨天更新的数据
        queryset = queryset.filter(Q(update_time__range=(oneday + timedelta(days=-1), oneday)))
        if not queryset:
            return {"site_num": 0, "subaccount_num": 0, "board_num": 0, "pin_num": 0,
                    "visitor_num": 0, "click_num": 0, "sales_num": 0, "revenue_num": 0}
        # 获取站点总数
        site_num = self.get_num(queryset, "store_url")
        # 获取帐号总数
        subaccount_set = queryset.filter(Q(board_uri=None) | Q(board_uri=""), Q(pin_uri=None) | Q(pin_uri=""))
        subaccount_num = self.get_num(subaccount_set, "pinterest_account_uri")
        # 获取Board总数
        board_set = queryset.filter(~Q(board_uri=None), ~Q(board_uri=""), Q(pin_uri=None) | Q(pin_uri=""))
        board_num = self.get_num(board_set, "board_uri")
        # 获取pin总数
        pin_set = queryset.filter(~Q(pin_uri=None), ~Q(pin_uri=""))
        pin_num = self.get_num(pin_set, "pin_uri")

        # 获取visitor总数
        visitor_num = self.count_num(pin_set, "store_visitors")
        # 获取click总数
        click_num = self.count_num(pin_set, "pin_clicks")
        # 获取sales总数
        sales_num = self.count_num(pin_set, "product_sale")
        # 获取revenue总数
        revenue_num = self.count_num(pin_set, "product_revenue")
        return {
            "site_num": site_num,
            "subaccount_num": subaccount_num,
            "board_num": board_num,
            "pin_num": pin_num,
            "visitor_num": visitor_num,
            "click_num": click_num,
            "sales_num": sales_num,
            "revenue_num": revenue_num
        }

    def latest_updates(self):
        pass

    def top_pins(self):
        pass

    def top_board(self):
        pass

    def activity_log(self):
        pass
