# -*- coding: utf-8 -*-
from rest_framework import serializers

from sea_app import models


class DailyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PinterestHistoryData
        depth = 1
        fields = "__all__"


class PinterestAccountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PinterestAccount
        depth = 1
        fields = ("id", "nickname", "user")


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Board
        depth = 1
        fields = ("id", "name", "pinterest_account_id")


class PinListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pin
        depth = 1
        fields = ("id", "description", "board_id")

