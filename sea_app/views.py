from django.contrib import auth
from rest_framework import generics, viewsets ,status
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

from sea_app import models
from sea_app.serializers import userinfo_serializers


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
                return Response(request, status=status.HTTP_200_OK)
            else:
                return Response({"message": "用户名密码错误"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """注册"""
    queryset = models.User.objects.all()
    serializer_class = userinfo_serializers.RegisterSerializer


