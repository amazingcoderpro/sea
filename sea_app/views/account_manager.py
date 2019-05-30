import json

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework import status

from sdk.pinterest.pinterest_api import PinterestApi
from sea_app import models
from sea_app.filters import report as report_filters
from sea_app.serializers import account_manager, report
from sea_app.filters import account_manager as account_manager_filters
from sea_app.pageNumber.pageNumber import PNPagination
from sea_app.permission.permission import RulePermission
from sdk.pinterest import pinterest_api


class PinterestAccountView(generics.ListAPIView):
    """pinterest账号和对应board"""
    queryset = models.PinterestAccount.objects.all()
    serializer_class = account_manager.PinterestAccountSerializer
    filter_backends = (account_manager_filters.PinterestAccountFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class RuleView(generics.ListCreateAPIView):
    """规则"""
    queryset = models.Rule.objects.all()
    serializer_class = account_manager.RuleSerializer
    pagination_class = PNPagination
    filter_backends = (account_manager_filters.RuleFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class RuleOperView(generics.UpdateAPIView):
    queryset = models.Rule.objects.all()
    serializer_class = account_manager.RuleSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class ProductView(generics.ListAPIView):
    """产品"""
    queryset = models.Product.objects.all()
    serializer_class = account_manager.ProductSerializer
    filter_backends = (account_manager_filters.ProductFilter, filters.SearchFilter)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    search_fields = ("name",)


class SearchProductView(generics.ListAPIView):
    """获取符合条件的产品"""
    queryset = models.ProductHistoryData.objects.all()
    serializer_class = account_manager.ProductHistorySerializer
    filter_backends = (account_manager_filters.ProductCountFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        scan_sign = request.query_params.get("scan_sign", '')
        scan = request.query_params.get("scan", '')
        sale_sign = request.query_params.get("sale_sign", '')
        sale = request.query_params.get("sale", '')
        if not sale_sign or not sale:
            if scan_sign not in [">", "<", ">=", "<=", "=="] or type(scan) != str or not scan.isdigit():
                return Response({"deails": "请求参数错误"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if scan_sign not in [">", "<",">=","<=","=="] or sale_sign not in [">","<",">=","<=","=="]\
                    or type(scan) != str or type(sale) != str or not sale.isdigit() or not scan.isdigit():
                return Response({"deails": "请求参数错误"}, status=status.HTTP_400_BAD_REQUEST)
        res = []
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            return Response(res)
        result = queryset.values("product").annotate(scan=Sum("product_scan"), sales=Sum("product_sales"))
        if scan and sale:
            for item in result:
                scan_codition = "{} {} {}".format(item["scan"], scan_sign, scan)
                sale_codition = "{} {} {}".format(item["sales"], sale_sign, sale)
                if eval(scan_codition) and eval(sale_codition):
                    res.append(item["product"])
        else:
            for item in result:
                scan_codition = "{} {} {}".format(item["scan"], scan_sign, scan)
                if eval(scan_codition):
                    res.append(item["product"])
        return Response(res)


class ReportView(generics.ListAPIView):
    queryset = models.PublishRecord.objects.all()
    serializer_class = account_manager.PublishRecordSerializer
    pagination_class = PNPagination
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    filterset_fields = ("product__sku", "state")


class AccountListManageView(generics.ListAPIView):
    """账号管理 -- 账号 列表显示"""
    queryset = models.PinterestHistoryData.objects.all()
    serializer_class = report.DailyReportSerializer
    pagination_class = PNPagination
    filter_backends = (report_filters.AccountListFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(queryset)
        return Response(queryset)


class BoardListManageView(generics.ListAPIView):
    """账号管理 -- board 列表显示"""
    queryset = models.PinterestHistoryData.objects.all()
    serializer_class = report.DailyReportSerializer
    pagination_class = PNPagination
    filter_backends = (report_filters.BoardListFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(queryset)
        return Response(queryset)


class PinListManageView(generics.ListAPIView):
    """账号管理 -- pin 列表显示"""
    queryset = models.PinterestHistoryData.objects.all()
    serializer_class = report.DailyReportSerializer
    pagination_class = PNPagination
    filter_backends = (report_filters.PinListFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(queryset)
        return Response(queryset)


class PinterestAccountCreateView(generics.CreateAPIView):
    """增加账号"""
    queryset = models.PinterestAccount.objects.all()
    serializer_class = account_manager.PinterestAccountCreateSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class PinterestAccountListView(generics.ListAPIView):
    """账号 select框显示"""
    queryset = models.PinterestAccount.objects.all()
    serializer_class = report.PinterestAccountListSerializer
    filter_backends = (account_manager_filters.PinterestAccountFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class BoardListView(generics.ListAPIView):
    """board select框显示"""
    queryset = models.Board.objects.all()
    serializer_class = report.BoardListSerializer
    filter_backends = (account_manager_filters.BoardListFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class PinListView(generics.ListAPIView):
    """pin select框显示"""
    queryset = models.Pin.objects.all()
    serializer_class = report.PinListSerializer
    filter_backends = (account_manager_filters.PinListFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class BoardManageView(generics.RetrieveUpdateDestroyAPIView):
    """Board管理 更新 删除"""
    queryset = models.Board.objects.all()
    serializer_class = report.BoardListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def put(self, request, *args, **kwargs):
        data = request.data
        access_token = models.Board.objects.get(board_uri=data["board_uri"]).pinterest_account.token
        result = PinterestApi(access_token=access_token).edit_board(data["board_uri"], data["name"], data["description"])
        if result["code"] == 1:
            return self.update(request, *args, **kwargs)
        else:
            return Response({"detail": result["msg"]}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        board_obj = models.Board.objects.get(pk=kwargs["pk"])
        result = PinterestApi(access_token=board_obj.pinterest_account.token).delete_board(board_obj.board_uri)
        if result["code"] == 1:
            return self.destroy(request, *args, **kwargs)
        else:
            return Response({"detail": result["msg"]}, status=status.HTTP_400_BAD_REQUEST)


class PinManageView(generics.RetrieveUpdateDestroyAPIView):
    """pin管理 更新 删除"""
    queryset = models.Pin.objects.all()
    serializer_class = report.PinListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def put(self, request, *args, **kwargs):
        data = request.data
        pin_obj = models.Pin.objects.get(pin_uri=data["pin_uri"])
        access_token = pin_obj.board.pinterest_account.token
        board_uri = models.Board.objects.get(pk=data["board"]).board_uri
        result = PinterestApi(access_token=access_token).edit_pin(data["pin_uri"], board_uri, data["note"], data["url"])
        if result["code"] == 1:
            return self.update(request, *args, **kwargs)
        else:
            return Response({"detail": result["msg"]}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        pin_obj = models.Pin.objects.get(pk=kwargs["pk"])
        result = PinterestApi(access_token=pin_obj.board.pinterest_account.token).delete_pin(pin_obj.pin_uri)
        if result["code"] == 1:
            return self.destroy(request, *args, **kwargs)
        else:
            return Response({"detail": result["msg"]}, status=status.HTTP_400_BAD_REQUEST)


class AccountManageView(generics.UpdateAPIView):
    """Pin账号管理 删除"""
    queryset = models.PinterestAccount.objects.all()
    serializer_class = report.PinterestAccountListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class RuleStatusView(generics.UpdateAPIView):
    """修改规则状态"""
    queryset = models.Rule.objects.all()
    serializer_class = account_manager.RuleStatusSerializer
    permission_classes = (IsAuthenticated, RulePermission)
    authentication_classes = (JSONWebTokenAuthentication,)


