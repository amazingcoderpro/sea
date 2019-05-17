# -*- coding: utf-8 -*-
from rest_framework import serializers

from sea_app import models


class DailyReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PinterestHistoryData
        depth = 1
        fields = "__all__"

