from rest_framework import serializers
from rest_framework.validators import UniqueValidator,UniqueTogetherValidator

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


class UserSerializer(serializers.ModelSerializer):
    """用户增加 显示列表"""
    username = serializers.CharField(required=True, min_length=5, error_messages={
        "blank": "请输入账户",
        "required": "请携带该参数",
        "max_length": "用户名格式不对",
        "min_length": "用户名长度最少为5位",
    }, validators=[UniqueValidator(queryset=models.User.objects.all(), message="账号已经存在")])
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(error_messages={"invalid": "请输入有效地址"}, validators=[UniqueValidator(queryset=models.User.objects.all(), message="邮箱已经存在")])
    nickname = serializers.CharField(required=True, min_length=5, error_messages={
        "blank": "请输入昵称",
        "required": "请携带该参数",
        "max_length": "用户名格式不对",
        "min_length": "用户名长度最少为5位",
    })

    class Meta:
        model = models.User
        fields = ("id", "username", "password", "password2", "email", "role", "create_time", "nickname", "update_time")
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        # 检查角色,如果是站长不能创建
        admin_role = models.Role.objects.filter(**{"user_id": self.context["request"].data["role"], "name": "站长"})
        if admin_role:
            raise serializers.ValidationError("不能分配站长角色")
        # 检查两次秘密是否一致
        if not attrs["password"] == attrs["password2"]:
            raise serializers.ValidationError("两次密码不一致，请重新输入")
        del attrs["password2"]
        return attrs

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.parent_id = self.context["request"].user.id
        user.save()
        return user


class UserOperSerializer(serializers.ModelSerializer):
    """用户删 改 查"""
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = models.User
        fields = ("id", "username", "password", "password2", "email", "role", "create_time", "nickname")
        extra_kwargs = {
            'username': {'write_only': False, 'read_only': True},
            'password': {'write_only': True, 'read_only': False},
            'email': {'write_only': False, 'read_only': True},
        }

    def validate(self, attrs):
        if not attrs["password"] == attrs["password2"]:
            raise serializers.ValidationError("两次密码不一致，请重新输入")
        del attrs["password2"]
        return attrs


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Role
        fields = ("id", "name", "menu_list", "create_time", "update_time")

    def validate(self, attrs):
        is_exit = models.Role.objects.filter(user_id=self.context["request"].user.id, name=attrs["name"])
        if is_exit:
            raise serializers.ValidationError("角色名已经存在")
        return attrs

    def create(self, validated_data):
        role = super(RoleSerializer, self).create(validated_data=validated_data)
        role.user_id = self.context["request"].user.id
        role.save()
        return role