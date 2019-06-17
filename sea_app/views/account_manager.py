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
from sea_app.permission.permission import RulePermission,PublishRecordPermission
from sdk.pinterest import pinterest_api
import datetime


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
    queryset = models.Product.objects.all()
    serializer_class = account_manager.ProductSerializer
    filter_backends = (account_manager_filters.ProductCountFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        res = []
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            return Response(res)
        for item in queryset:
            res.append(item.id)
        return Response(res)
        # scan_sign = request.query_params.get("scan_sign", '')
        # scan = request.query_params.get("scan", '')
        # sale_sign = request.query_params.get("sale_sign", '')
        # sale = request.query_params.get("sale", '')
        # if not sale_sign or not sale:
        #     if scan_sign not in [">", "<", ">=", "<=", "=="] or type(scan) != str or not scan.isdigit():
        #         return Response({"deails": "Request parameter error"}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     if scan_sign not in [">", "<",">=","<=","=="] or sale_sign not in [">","<",">=","<=","=="]\
        #             or type(scan) != str or type(sale) != str or not sale.isdigit() or not scan.isdigit():
        #         return Response({"deails": "Request parameter error"}, status=status.HTTP_400_BAD_REQUEST)
        # res = []
        # queryset = self.filter_queryset(self.get_queryset())
        # if not queryset:
        #     return Response(res)
        # result = queryset.values("product").annotate(scan=Sum("product_scan"), sales=Sum("product_sales"))
        # if scan and sale:
        #     for item in result:
        #         scan_codition = "{} {} {}".format(item["scan"], scan_sign, scan)
        #         sale_codition = "{} {} {}".format(item["sales"], sale_sign, sale)
        #         if eval(scan_codition) and eval(sale_codition):
        #             res.append(item["product"])
        # else:
        #     for item in result:
        #         scan_codition = "{} {} {}".format(item["scan"], scan_sign, scan)
        #         if eval(scan_codition):
        #             res.append(item["product"])
        # return Response(res)


class ReportView(generics.ListAPIView):
    queryset = models.PublishRecord.objects.all()
    serializer_class = account_manager.PublishRecordSerializer
    pagination_class = PNPagination
    # filter_backends = (DjangoFilterBackend,)
    # filter_backends = (DjangoFilterBackend, account_manager_filters.ReportFilter)
    filter_backends = (account_manager_filters.ReportFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    # filterset_fields = ("product__sku",)


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

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     return self.get_paginated_response(page)
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

        # page = self.paginate_queryset(queryset)
        # if page is not None:
            # return self.get_paginated_response(queryset)
        return Response(queryset)


class PinListManageView(generics.ListAPIView):
    """账号管理 -- pin 列表显示"""
    queryset = models.PinterestHistoryData.objects.all()
    filter_backends = (report_filters.PinListFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(queryset)


class PinterestAccountCreateView(generics.CreateAPIView):
    """增加账号"""
    queryset = models.PinterestAccount.objects.all()
    serializer_class = account_manager.PinterestAccountCreateSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        state = "%s|%d" % (serializer.data["account"], request.user.id)
        url = pinterest_api.PinterestApi().get_pinterest_url(state)
        result = serializer.data
        result["url"] = url
        return Response(result, status=status.HTTP_201_CREATED, headers=headers)


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
        try:
            access_token = models.Board.objects.get(id=kwargs["pk"], uuid=data["board_uri"]).pinterest_account.token
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        result = PinterestApi(access_token=access_token).edit_board(data["board_uri"], data["name"], data["description"])
        if result["code"] == 1:
            return self.update(request, *args, **kwargs)
        else:
            return Response({"detail": result["msg"]}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            board_obj = models.Board.objects.get(pk=kwargs["pk"])
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        result = PinterestApi(access_token=board_obj.pinterest_account.token).delete_board(board_obj.uuid)
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
        try:
            pin_obj = models.Pin.objects.filter(uuid=data["pin_uri"]).first()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        access_token = pin_obj.board.pinterest_account.token
        # 通过board_name 查找board_uri
        board_obj = models.Board.objects.get(pk=data["board"])
        if not board_obj:
            return Response({"detail": "No board named is {}".format(data["board_name"])}, status=status.HTTP_400_BAD_REQUEST)
        result = PinterestApi(access_token=access_token).edit_pin(data["pin_uri"], board_obj.uuid, data["note"], data["url"])
        if result["code"] == 1:
            # 更新数据库
            pin_obj.board = board_obj
            pin_obj.note = data["note"]
            pin_obj.url = data["url"]
            pin_obj.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"detail": result["msg"]}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        pin_id_list = request.query_params.dict()["pin_list"]
        for pin_id in eval(pin_id_list):
            try:
                pin_obj = models.Pin.objects.get(pk=pin_id)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            result = PinterestApi(access_token=pin_obj.board.pinterest_account.token).delete_pin(pin_obj.uuid)
            if result["code"] == 1:
                pin_obj.delete()
            else:
                return Response({"detail": result["msg"]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class AccountManageView(generics.DestroyAPIView):
    """Pin账号管理 删除"""
    queryset = models.PinterestAccount.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class RuleStatusView(generics.UpdateAPIView):
    """修改规则状态"""
    queryset = models.Rule.objects.all()
    serializer_class = account_manager.RuleStatusSerializer
    permission_classes = (IsAuthenticated, RulePermission)
    authentication_classes = (JSONWebTokenAuthentication,)

    # def put(self, request, *args, **kwargs):
    #     #     rule_id_list = eval(request.query_params.dict()["rule_list"])
    #     #     statedata = request.data["statedata"]
    #     #     models.Rule.objects.filter(id__in=rule_id_list).update(state=statedata)
    #     #     return Response(status.HTTP_204_NO_CONTENT)


class SendPinView(APIView):
    """页面发布pin"""
    permission_classes = (IsAuthenticated, RulePermission)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        publish_instance = models.PublishRecord.objects.filter(id=kwargs["pk"]).first()
        token = publish_instance.board.pinterest_account.token
        if token:
            result = PinterestApi(access_token=token).create_pin(publish_instance.board.uuid, publish_instance.product.name, publish_instance.product.image_url, publish_instance.product.url)
            if result["code"] != 1:
                models.PublishRecord.objects.filter(id=kwargs["pk"]).update(state=3, remark=result["msg"])
                return Response({"detail": result["msg"]},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                # print(result["data"]["id"])
                obj = models.PublishRecord.objects.filter(id=kwargs["pk"]).first()
                obj.state = 1
                obj.remark = ""
                obj.finished_time = datetime.datetime.now()
                obj.save()
                pin_obj = models.Pin.objects.filter(id=obj.pin_id).first()
                pin_obj.uuid = result["data"]["id"]
                pin_obj.url = result["data"]["url"]
                pin_obj.publish_time = datetime.datetime.now()
                pin_obj.save()
                return Response({"detail": result["msg"]})
        else:
            return Response({"detail": "This pinterest_account is not authorized"}, status=status.HTTP_400_BAD_REQUEST)


class PublishRecordDelView(APIView):
    """发布规则删除"""
    queryset = models.PublishRecord.objects.all()
    permission_classes = (IsAuthenticated, PublishRecordPermission)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        publish_record_list = request.data.get("publish_record_list", "None")
        if not publish_record_list or type(eval(publish_record_list)) != list:
            return Response({"detail": "parameter error"}, status=status.HTTP_400_BAD_REQUEST)
        obj = models.PublishRecord.objects.filter(id__in=eval(publish_record_list)).update(state=5)
        return Response([])