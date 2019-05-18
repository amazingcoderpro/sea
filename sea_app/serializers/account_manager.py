from django.db import transaction
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


class RuleSchedule(serializers.ModelSerializer):
    class Meta:
        model = models.PinterestAccount
        fields = "__all__"


class RuleSerializer(serializers.ModelSerializer):
    schedule_rule = RuleSchedule(many=True,read_only=True)
    scan_sign_name = serializers.CharField(source="get_scan_sign_display",read_only=True)
    sale_sign_name = serializers.CharField(source="get_sale_sign_display",read_only=True)

    class Meta:
        model = models.Rule
        fields = ("id", "scan_sign", "scan_sign_name", "sale_sign_name", "scan", "sale_sign", "sale", "product_list", "tag", "state", "schedule_rule", "board")

    def create(self, validated_data):
        with transaction.atomic():
            print(self.context["request"].data.pop("schedule_rule"))
            print(self.context["request"].data.pop("schedule_rule"))
            xx = super(RuleSerializer, self).create(validated_data)
            return xx

    # def get_scan_sign(self, row):
    #     return 11
    #
    # def get_sale_sign(self, row):
    #     return 22