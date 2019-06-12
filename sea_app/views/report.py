# -*- coding: utf-8 -*-
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from sea_app.pageNumber.pageNumber import PNPagination
from sea_app.views import reports


class DailyReportView(generics.ListAPIView):
    """日报列表展示"""
    pagination_class = PNPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        data_list = reports.daily_report_view(request)
        page = self.paginate_queryset(data_list)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(data_list)


class SubAccountReportView(generics.ListAPIView):
    """子账户 列表展示"""
    pagination_class = PNPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        type = kwargs["type"]
        data_list = reports.subaccount_report_view(request, type)
        page = self.paginate_queryset(data_list)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(data_list)


