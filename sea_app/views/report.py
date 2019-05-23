# -*- coding: utf-8 -*-
import datetime
from datetime import datetime, timedelta

from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from sea_app import models
from sea_app.filters import personal_center
from sea_app.pageNumber.pageNumber import PNPagination
from sea_app.serializers import report
from sea_app.filters import report as report_filters
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
            return self.get_paginated_response(data_list)
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
            return self.get_paginated_response(data_list)
        return Response(data_list)


class DashBoardChangePartView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        data = reports.dash_board_change_part(request)
        return Response(data)


class DashBoardFixedPartView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        data = reports.dash_board_fixed_part(request)
        return Response(data)

