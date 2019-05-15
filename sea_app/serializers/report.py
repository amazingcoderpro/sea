# -*- coding: utf-8 -*-
from rest_framework import serializers

from sea_app import models


class SubAccountSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(required=True, error_messages={
    #     "blank": "请输入账户名称",
    #     "required": "请携带该参数",
    #     "max_length": "用户名格式不对",
    # })

    class Meta:
        model = models.Pin
        depth = 1
        fields = ("id", "pin_uri", "repin", "like", "comment", "visitors", "new_visitors", "views", "clicks",
        "board", "product",)


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Board
        depth = 1
        fields = ("__all__", )


class PinSerializer(serializers.ModelSerializer):
    # board = BoardSerializer
    class Meta:
        model = models.Pin
        depth = 2
        fields = (
        "id", "pin_uri", "update_time", "repin", "like", "comment", "visitors", "new_visitors", "views", "clicks",
        "product", "board")
