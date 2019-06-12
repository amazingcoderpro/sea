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
        fields = ("id", "account", "nickname", "state")


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Board
        depth = 1
        fields = ("id", "name", "pinterest_account_id", "uuid", "description")


class PinListSerializer(serializers.ModelSerializer):
    board_uri = serializers.CharField(source="board.uuid", read_only=True)
    board_name = serializers.CharField(source="board.name")
    class Meta:
        model = models.Pin
        fields = ("id", "note", "board", "uuid", "url", "board_uri", "board_name")

