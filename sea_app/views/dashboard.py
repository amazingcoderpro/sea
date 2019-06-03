# -*- coding: utf-8 -*-
# Created by: Leemon7
# Created on: 2019/6/3
# Function:
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from sea_app.views import reports


class DashBoardView(APIView):
    """dashboard 视图"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        # 过滤筛选条件
        pin_set_list, product_set_list = reports.get_common_data(request)
        part = kwargs["pk"]
        pins_period = request.query_params.dict().get("pins_period", 7)
        boards_period = request.query_params.dict().get("boards_period", 7)
        if part == '1':
            # 账户总览 图数据
            overview_list = reports.account_overview_chart(pin_set_list, product_set_list, request)
            # 账户总览 表数据
            total_data = reports.account_overview_table(overview_list)
            return Response({"overview_list": overview_list, "total_data": total_data})
        elif part == '2':
            # 最新新增数据
            resp = reports.latest_updates(pin_set_list, product_set_list, request)
        elif part == '3':
            # top pins
            resp = reports.top_pins(request, period=pins_period)
        elif part == '4':
            # top board
            resp = reports.top_board(request, period=boards_period)
        elif part == '5':
            # activity log
            resp = reports.operation_record(request)
        else:
            raise Exception("part {} 参数超出范围".format(part))
        return Response(resp)

