from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from sea_app import models


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, min_length=5, error_messages={
        "blank": "请输入用户名",
        "required": "请携带该参数",
        "max_length": "用户名格式不对",
        "min_length": "用户名长度最少为5位",
    })

    password = serializers.CharField(required=True, min_length=5, error_messages={
        "blank": "请输入用户名",
        "required": "请携带该参数",
    }, write_only=True)

    class Meta:
        model = models.User
        fields = ("id", "username", "password")
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'read_only': True}
        }