from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework import status

from sea_app import models
from sea_app.filters.report import AccountListFilter
from sea_app.serializers import account_manager, report
from sea_app.filters import account_manager as account_manager_filters
from sea_app.pageNumber.pageNumber import PNPagination
from sea_app.permission.permission import RolePermission
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
    permission_classes = (IsAuthenticated, RolePermission)
    authentication_classes = (JSONWebTokenAuthentication,)


class ProductView(generics.ListAPIView):
    """产品"""
    queryset = models.Product.objects.all()
    serializer_class = account_manager.ProductSerializer
    filter_backends = (account_manager_filters.ProductFilter, filters.SearchFilter)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    search_fields = ("name",)


class ProductCount(generics.ListAPIView):
    """获取符合条件的产品"""
    queryset = models.ProductHistoryData.objects.all()
    serializer_class = account_manager.ProductSerializer
    filter_backends = (account_manager_filters.ProductCountFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        scan_sign = request.query_params.get("scan_sign", '')
        scan = request.query_params.get("scan", '')
        sale_sign = request.query_params.get("sale_sign", '')
        sale = request.query_params.get("sale", '')
        res = []
        queryset = self.filter_queryset(self.get_queryset())
        result = queryset.values("product").annotate(scan=Sum("product_scan"), sale=Sum("product_sale"))
        if scan and sale:
            for item in result:
                scan_codition = "{} {} {}".format(item["scan"], scan_sign, scan)
                sale_codition = "{} {} {}".format(item["sale"], sale_sign, sale)
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


class AccountListView(generics.ListAPIView):
    queryset = models.PinterestHistoryData.objects.all()
    serializer_class = report.DailyReportSerializer
    pagination_class = PNPagination
    filter_backends = (AccountListFilter,)
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
    """增加Pinterest 账号"""
    queryset = models.PinterestAccount.objects.all()
    serializer_class = account_manager.PinterestAccountCreateSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class PinterestAccountOuthView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request,*args, **kwargs):
        instance = models.PinterestAccount.objects.filter(id=kwargs["pk"]).first()
        code, html = pinterest_api.PinterestApi().get_pinterest_code(instance.account_uri)
        if code == 200:
            return Response({"message": html})
        return Response({"detail": "outh failed"}, status=status.HTTP_400_BAD_REQUEST)


class PinterestAccountListView(generics.ListAPIView):
    queryset = models.PinterestAccount.objects.all()
    serializer_class = report.PinterestAccountListSerializer
    filter_backends = (account_manager_filters.PinterestAccountFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class BoardListView(generics.ListAPIView):
    queryset = models.Board.objects.all()
    serializer_class = report.BoardListSerializer
    filter_backends = (account_manager_filters.BoardListFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class PinListView(generics.ListAPIView):
    queryset = models.Pin.objects.all()
    serializer_class = report.PinListSerializer
    filter_backends = (account_manager_filters.PinListFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
>>>>>>> df5e69fca9be55d28bc7f6ebd605829142aaf591
