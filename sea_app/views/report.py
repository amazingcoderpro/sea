# -*- coding: utf-8 -*-
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from sea_app import models
from sea_app.filters import filters
from sea_app.pageNumber.pageNumber import PNPagination
from sea_app.serializers.report import SubAccountSerializer, PinSerializer


class SubAccountDailyReportView(generics.ListAPIView):
    """日报列表展示"""
    queryset = models.Pin.objects.all()
    serializer_class = PinSerializer
    # pagination_class = PNPagination
    # filter_backends = (filters.SubAccountFilter,)
    # permission_classes = (IsAuthenticated,)
    # authentication_classes = (JSONWebTokenAuthentication,)



class BoardsDailyReportView(generics.ListAPIView):
    """Boards报告列表展示"""
    queryset = models.Board.objects.all()
    serializer_class = ''
    pagination_class = PNPagination
    # filter_backends = ('',)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class PinsDailyReportView(generics.ListAPIView):
    """Pins报告列表展示"""

    queryset = models.Pin.objects.all()
    serializer_class = PinSerializer
    filter_backends = (filters.PinFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        data_list = []
        queryset = self.filter_queryset(self.get_queryset())
        group_dict = {}
        for item in queryset:
            date = item.update_time.date()
            if date not in group_dict:
                group_dict[date] = {
                    "repin": item.repin,
                    "like" : item.like,
                    "comments": item.comment,
                    "visitors": item.visitors,
                    "new_visitors": item.new_visitors,
                    "view": item.views,
                    "clicks": item.clicks,
                    "sales": item.product.sale,
                    "revenue": item.product.revenue
                }
            else:
                group_dict[date]["repin"] += item.repin
                group_dict[date]["like"] += item.like
                group_dict[date]["comments"] += item.comment
                group_dict[date]["visitors"] += item.visitors
                group_dict[date]["new_visitors"] += item.new_visitors
                group_dict[date]["view"] += item.views
                group_dict[date]["clicks"] += item.clicks
                group_dict[date]["sales"] += item.product.sale
                group_dict[date]["revenue"] += item.product.revenue

        for day, info in group_dict.items():
            data = {
                "date": day,
                "repin": info["repin"],
                "like": info["like"],
                "comments": info["comments"],
                "visitors": info["visitors"],
                "new_visitors": info["new_visitors"],
                "view": info["view"],
                "clicks": info["clicks"],
                "sales": info["sales"],
                "revenue": info["revenue"]
            }
            data_list.append(data)
        return Response(data_list)


