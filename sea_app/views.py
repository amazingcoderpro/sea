from django.contrib import auth
from django.db.models import Q
from rest_framework import generics, viewsets ,status
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication

from sea_app import models
from sea_app.serializers import userinfo_serializers, app_serializers
from sea_app.utils.menu_tree import MenuTree
from sea_app.pageNumber.pageNumber import PNPagination


class LoginView(generics.CreateAPIView):
    """登陆"""
    queryset = models.User.objects.all()
    serializer_class = userinfo_serializers.LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = request.data.get('username')
            password = request.data.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                request = {}
                request["user"] = userinfo_serializers.LoginSerializer(instance=user, many=False).data
                payload = jwt_payload_handler(user)
                request["token"] = jwt_encode_handler(payload)
                # 生成菜单
                menu_tree = MenuTree(user).crate_menu_tree()
                request["menu_tree"] = menu_tree
                return Response(request, status=status.HTTP_200_OK)
            else:
                return Response({"message": "用户名密码错误"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """注册"""
    queryset = models.User.objects.all()
    serializer_class = userinfo_serializers.RegisterSerializer


class UserViewSet(viewsets.ModelViewSet):
    """用户的增删该查"""
    queryset = models.User.objects.all()
    serializer_class = userinfo_serializers.UserSerializer
    pagination_class = PNPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get_queryset(self):
        parent_id = self.request.user.parent_id
        if parent_id:
            return models.User.objects.filter(Q(parent_id=parent_id) | Q(id=parent_id))
        return models.User.objects.filter(id=self.request.user.id)


class StoreView(generics.ListAPIView):
    """电商"""
    queryset = models.Store.objects.all()
    serializer_class = app_serializers.StoreSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get_queryset(self):
        return models.Store.objects.filter(user=self.request.user)
