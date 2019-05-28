from django.contrib import auth
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponseRedirect

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


from sea_app import models
from sea_app.serializers import personal_center
from sea_app.utils.menu_tree import MenuTree
from sea_app.pageNumber.pageNumber import PNPagination
from sea_app.filters import personal_center as personal_center_filters
# from sea_app.permission.permission import UserPermission, RolePermission
from sdk.shopify.shopify_oauth_info import ShopifyBase
from sdk.shopify.get_shopify_products import ProductsApi
from sdk.pinterest import pinterest_api
from sea_app.views import reports


class LoginView(generics.CreateAPIView):
    """登陆"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = request.data.get('username', '')
            password = request.data.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                res = {}
                res["user"] = personal_center.LoginSerializer(instance=user, many=False).data
                payload = jwt_payload_handler(user)
                res["token"] = "jwt {}".format(jwt_encode_handler(payload))
                return Response(res, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "用户名密码错误"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """注册"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.RegisterSerializer


class SetPasswordView(generics.UpdateAPIView):
    """设置密码"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.SetPasswordSerializer






# class UserView(generics.ListCreateAPIView):
#     """用户 增 列表展示"""
#     queryset = models.User.objects.all()
#     serializer_class = personal_center.UserSerializer
#     pagination_class = PNPagination
#     filter_backends = (personal_center_filters.UserFilter, DjangoFilterBackend)
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (JSONWebTokenAuthentication,)
#     filterset_fields = ("nickname",)


# class UserOperView(generics.RetrieveUpdateDestroyAPIView):
#     """用户 删 该 查"""
#     queryset = models.User.objects.all()
#     serializer_class = personal_center.UserOperSerializer
#     permission_classes = (IsAuthenticated, UserPermission)
#     authentication_classes = (JSONWebTokenAuthentication,)


# class RoleView(generics.ListCreateAPIView):
#     """角色 增 列表展示"""
#     queryset = models.Role.objects.all()
#     serializer_class = personal_center.RoleSerializer
#     pagination_class = PNPagination
#     filter_backends = (personal_center_filters.RoleFilter,)
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (JSONWebTokenAuthentication,)
#
#     def list(self, request, *args, **kwargs):
#         show_more = request.query_params.get("show_more", None)
#         if not show_more:
#             return super(RoleView, self).list(request)
#         queryset = self.filter_queryset(self.get_queryset())
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)


# class RoleOperView(generics.RetrieveUpdateDestroyAPIView):
#     """角色 删 改 查"""
#     queryset = models.Role.objects.all()
#     serializer_class = personal_center.RoleSerializer
#     permission_classes = (IsAuthenticated, RolePermission)
#     authentication_classes = (JSONWebTokenAuthentication,)
#
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         is_exit = models.User.objects.filter(role=instance)
#         if is_exit:
#             return Response({"detail": "The role also has user binding"}, status=status.HTTP_400_BAD_REQUEST)
#         self.perform_destroy(instance)
#         return Response(status=status.HTTP_204_NO_CONTENT)


class StoreAuthView(APIView):
    """店铺授权接口"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        instance = models.Store.objects.filter(id=kwargs["pk"]).first()
        # if instance.authorized == 1:
        #     return Response({"detail": "This store is authorized"}, status=status.HTTP_400_BAD_REQUEST)
        url = ShopifyBase(instance.name).ask_permission(instance.name)
        return Response({"message": url})


class PinterestAccountAuthView(APIView):
    """账户授权"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        instance = models.PinterestAccount.objects.filter(id=kwargs["pk"]).first()
        if instance.authorized == 1:
            return Response({"detail": "This account is authorized"}, status=status.HTTP_400_BAD_REQUEST)
        url = pinterest_api.PinterestApi().get_pinterest_url(instance.account_uri)
        return Response({"message": url})


class ShopifyCallback(APIView):
    """shopify 回调接口"""
    def get(self, request):
        code = request.query_params.get("code", None)
        shop = request.query_params.get("shop", None)
        if not code or not shop:
            return Response({"message": "auth faild"})
        print("####", code)
        print("####", shop)
        result = ShopifyBase(shop).get_token(code)
        if result["code"] == 1:
            instance = models.Store.objects.filter(url=shop).first()
            if instance:
                instance.token = result["data"]
                instance.save()
            else:
                print(shop, result["data"])
                store_data = {"name": shop, "url": shop, "platform": 1, "token": result["data"]}
                store_instance = models.Store.objects.create(**store_data)
                # TDD 调接口获取邮箱
                info = ProductsApi(access_token=result["data"], shop_name=shop).get_shop_info()
                print("#info", info)
                email = "163.com"
                user_data = {"username": email, "email": email}
                user_instance = models.User.objects.create(**user_data)
                store_instance.user = user_instance
                store_instance.save()
            return HttpResponseRedirect(redirect_to="http://www.baidu.com/?shop={}&email={}&id={}".format(shop, email, user_instance.id))
        return Response({"message": "auth faild"})


class PinterestCallback(APIView):
    """pinterest 回调接口"""
    def get(self, request, *args, **kwargs):
        code = request.query_params.get("code", None)
        account_uri = request.query_params.get("state", None)
        if not code or not account_uri:
            return Response({"message": "auth faild"})
        result = pinterest_api.PinterestApi().get_token(code)
        if result["code"] == 1:
            models.PinterestAccount.objects.filter(account_uri=account_uri).update(token=result["data"]["access_token"], authorized=1)
        return HttpResponseRedirect(redirect_to="http://www.baidu.com")


class OperationRecord(generics.ListAPIView):
    """操作记录 视图"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        data = reports.operation_record(request)
        return Response(data)