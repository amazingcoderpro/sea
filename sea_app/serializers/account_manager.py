from rest_framework import serializers
from sea_app import models


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Board
        fields = "__all__"


class PinterestAccountSerializer(serializers.ModelSerializer):
    board_pinterest_account = BoardSerializer(many=True, read_only=True)

    class Meta:
        model = models.PinterestAccount
        fields = (
            "id",
            "account_uri",
            "name",
            "email",
            "type",
            "state",
            "add_time",
            "create_time",
            "update_time",
            "user",
            "board_pinterest_account"
        )


class RuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Rule
        fields = ("id",
                  "start_time",
                  "end_time",
                  "interval_time",
                  "scan_sign",
                  "scan",
                  "sale_sign",
                  "sale",
                  "tag",
                  "state",
                  "state",
                  "create_time",
                  "update_time"
        )