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
        depth = 1
        fields = ("id", "username", "password", "nickname", "role")
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'read_only': True}
        }


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, min_length=5, error_messages={
        "blank": "请输入用户名",
        "required": "请携带该参数",
        "max_length": "用户名格式不对",
        "min_length": "用户名长度最少为5位",
    }, validators=[UniqueValidator(queryset=models.User.objects.all(), message="用户名已经存在")])
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(error_messages={"invalid": "请输入有效地址"}, validators=[UniqueValidator(queryset=models.User.objects.all(), message="邮箱已经存在")])

    class Meta:
        model = models.User
        fields = ("id", "username", "password", "password2", "email", "role", "create_time", "nickname")
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        if not attrs["password"] == attrs["password2"]:
            raise serializers.ValidationError("两次密码不一致，请重新输入")
        del attrs["password2"]
        return attrs

    def create(self, validated_data):
        user = super(RegisterSerializer,self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user