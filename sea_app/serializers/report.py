# -*- coding: utf-8 -*-
from rest_framework import serializers

from sea_app import models


class DailyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PinterestHistoryData
        depth = 1
        fields = {"pinterest_account__id","account_following", "account_follower", "board__id","board_name","board_follower"
                  "pin__id","pin_description","pin_thumbnail","pin_like","pin_comment","pin_repin",
                  "pin_views","pin_clicks","update_time","pin__product"}

