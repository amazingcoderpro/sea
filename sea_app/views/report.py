# -*- coding: utf-8 -*-
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from sea_app import models
from sea_app.pageNumber.pageNumber import PNPagination
from sea_app.serializers.report import SunAccountSerializer


class SubAccountDailyReportView(generics.ListAPIView):
    """日报列表展示"""
    queryset = models.User.objects.all()
    serializer_class = SunAccountSerializer
    # pagination_class = PNPagination
    # filter_backends = ('',)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)



class SubAccountReportView(generics.ListAPIView):
    """子账户报告列表展示"""
    queryset = models.User.objects.all()
    serializer_class = ''
    pagination_class = PNPagination
    # filter_backends = ('',)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
