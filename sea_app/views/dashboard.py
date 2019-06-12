# -*- coding: utf-8 -*-
# Created by: Leemon7
# Created on: 2019/6/3
# Function:
import httplib2
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.cache import get_cache_key
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from sea_app.views import reports
from config import logger


class DashBoardView(APIView):
    """dashboard 视图"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        # 过滤筛选条件
        # logger.info("dashboard trigger! ")
        pin_set_list, product_set_list = reports.get_common_data(request)
        part = int(eval(kwargs["pk"]))
        # logger.info("dashboard trigger! pd={}".format(part))
        if part == 1:
            # 账户总览 图数据
            overview_list = reports.account_overview_chart(pin_set_list, product_set_list, request)
            # 账户总览 表数据
            total_data = reports.account_overview_table(overview_list)
            # logger.info("dashboard trigger! total_data={}".format(total_data))
            return Response({"overview_list": overview_list, "total_data": total_data})
        elif part == 2:
            # 最新新增数据
            resp = reports.latest_updates(pin_set_list, product_set_list, request)
        elif part == 3:
            # top pins
            pins_period = request.query_params.dict().get("pins_period", 7)
            resp = reports.top_pins(request, period=pins_period)
        elif part == 4:
            # top board
            boards_period = request.query_params.dict().get("boards_period", 7)
            resp = reports.top_board(request, period=boards_period)
        elif part == 5:
            # activity log
            resp = reports.operation_record(request)
        else:
            raise Exception("part {} 参数超出范围".format(part))
        return Response(resp)


class CleanCacheView(generics.DestroyAPIView):
    """清除所有缓存"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def delete(self, request, *args, **kwargs):
        dic = cache._cache
        for key in list(dic.keys()):
            key = key[key.index('v'):]
            cache.delete(key)
        return Response(status=status.HTTP_204_NO_CONTENT)
