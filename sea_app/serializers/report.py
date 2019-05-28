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
        fields = ("id", "name", "pinterest_account_id", "board_uri", "description")


class PinListSerializer(serializers.ModelSerializer):
    baord_uri = serializers.CharField(source="board.board_uri", read_only=True)
    class Meta:
        model = models.Pin
        fields = ("id", "note", "board", "pin_uri", "url", "baord_uri")

