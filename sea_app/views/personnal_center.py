from django.contrib import auth
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication

from sea_app import models
from sea_app.serializers import personnal_center
from sea_app.utils.menu_tree import MenuTree
from sea_app.pageNumber.pageNumber import PNPagination
from sea_app.filters import filters
from sea_app.permission.permission import UserPermission


class LoginView(generics.CreateAPIView):
    """登陆"""
    queryset = models.User.objects.all()
    serializer_class = personnal_center.LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = request.data.get('username')
            password = request.data.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                request = {}
                request["user"] = personnal_center.LoginSerializer(instance=user, many=False).data
                payload = jwt_payload_handler(user)
                request["token"] = "jwt {}".format(jwt_encode_handler(payload))
                # 生成菜单
                menu_tree, route_list = MenuTree(user).crate_menu_tree()
                request["menu_tree"] = menu_tree
                request["router_list"] = route_list
                return Response({"data": request, "code": 1}, status=status.HTTP_200_OK)
            else:
                return Response({"data": "用户名密码错误", "code": 0}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """注册"""
    queryset = models.User.objects.all()
    serializer_class = personnal_center.RegisterSerializer


class UserView(generics.ListCreateAPIView):
    """用户 增 列表展示"""
    queryset = models.User.objects.all()
    serializer_class = personnal_center.UserSerializer
    pagination_class = PNPagination
    filter_backends = (filters.UserFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class UserOperView(generics.RetrieveUpdateDestroyAPIView):
    """用户 删 该 查"""
    queryset = models.User.objects.all()
    serializer_class = personnal_center.UserOperSerializer
    permission_classes = (IsAuthenticated, UserPermission)
    authentication_classes = (JSONWebTokenAuthentication,)


class RoleView(generics.ListCreateAPIView):
    """角色 增 列表展示"""
    queryset = models.Role.objects.all()
    serializer_class = personnal_center.RoleSerializer
    pagination_class = PNPagination
    filter_backends = (filters.RoleFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class RoleOperView(generics.RetrieveUpdateDestroyAPIView):
    """角色 删 改 查"""
    queryset = models.Role.objects.all()
    serializer_class = personnal_center.RoleSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
