# -*- coding: utf-8 -*-
from rest_framework import serializers

from sea_app import models


class DailyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PinterestHistoryData
        depth = 1
        # fields = ("pinterest_account", "pin_id", "pin_repin", "pin_like", "pin_comment", "pin")
        fields = "__all__"
