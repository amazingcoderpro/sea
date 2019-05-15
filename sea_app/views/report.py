# -*- coding: utf-8 -*-
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
    queryset = models.HistoryData.objects.all()
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




