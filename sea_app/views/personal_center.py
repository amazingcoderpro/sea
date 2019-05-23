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
from sea_app.permission.permission import UserPermission, RolePermission
from sdk.shopify.oauth_info import ShopifyBase


class LoginView(generics.CreateAPIView):
    """登陆"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = request.data.get('username')
            password = request.data.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                res = {}
                res["user"] = personal_center.LoginSerializer(instance=user, many=False).data
                payload = jwt_payload_handler(user)
                res["token"] = "jwt {}".format(jwt_encode_handler(payload))
                # 生成菜单
                menu_tree, route_list = MenuTree(user).crate_menu_tree()
                res["menu_tree"] = menu_tree
                res["router_list"] = route_list
                return Response(res, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "用户名密码错误"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """注册"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.RegisterSerializer


class UserView(generics.ListCreateAPIView):
    """用户 增 列表展示"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.UserSerializer
    pagination_class = PNPagination
    filter_backends = (personal_center_filters.UserFilter, DjangoFilterBackend)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    filterset_fields = ("nickname",)


class UserOperView(generics.RetrieveUpdateDestroyAPIView):
    """用户 删 该 查"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.UserOperSerializer
    permission_classes = (IsAuthenticated, UserPermission)
    authentication_classes = (JSONWebTokenAuthentication,)


class RoleView(generics.ListCreateAPIView):
    """角色 增 列表展示"""
    queryset = models.Role.objects.all()
    serializer_class = personal_center.RoleSerializer
    pagination_class = PNPagination
    filter_backends = (personal_center_filters.RoleFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class RoleOperView(generics.RetrieveUpdateDestroyAPIView):
    """角色 删 改 查"""
    queryset = models.Role.objects.all()
    serializer_class = personal_center.RoleSerializer
    permission_classes = (IsAuthenticated, RolePermission)
    authentication_classes = (JSONWebTokenAuthentication,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        is_exit = models.User.objects.filter(role=instance)
        if is_exit:
            return Response({"message": "The role also has user binding"}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StoreOuthView(APIView):
    """店铺授权接口"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        store_name = request.data.get("store_name",None)
        permission_list = request.data.get("permission_list", None)
        status, html = ShopifyBase(store_name).ask_permission(store_name, scopes=permission_list)
        if status == 200:
            return Response({"code": 1, "message": html})
        return Response({"code": 0, "message": "outh failed"})


class ShopifyCallback(APIView):
    """shopify 回调接口"""
    def get(self, request):
        code = request.data.get("code", None)
        store_name = request.data.get("status", None)
        status, token = ShopifyBase(store_name).get_token(code)
        if status:
            models.Store.objects.filter(platform=1, name=store_name).update(token=token)
        return HttpResponseRedirect(redirect_to="http://www.baidu.com")


class PinterestCallback(APIView):
    """pinterest 回调接口"""
    def get(self, request, *args, **kwargs):
        code = request.data.get("code", None)
        state = request.data.get("state", None)
        from sdk.pinterest import pinterest_api
        status, token = pinterest_api.PinterestApi().get_token(code)
        if status:
            models.PinterestAccount.objects.filter(account_uri=state).update(token=token)
        return HttpResponseRedirect(redirect_to="http://www.baidu.com")