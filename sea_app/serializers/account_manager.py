from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from sdk.pinterest import pinterest_api

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
            "account",
            "email",
            "type",
            "state",
            "authorized",
            "add_time",
            "create_time",
            "update_time",
            "user",
            "board_pinterest_account"
        )


class RuleScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RuleSchedule
        fields = "__all__"


class RuleSerializer(serializers.ModelSerializer):
    schedule_rule = RuleScheduleSerializer(many=True, read_only=True)
    scan_sign_name = serializers.CharField(source="get_scan_sign_display", read_only=True)
    sale_sign_name = serializers.CharField(source="get_sale_sign_display", read_only=True)
    board_name = serializers.CharField(source="board.name", read_only=True)
    account_name = serializers.CharField(source="board.pinterest_account.account", read_only=True)

    class Meta:
        model = models.Rule
        # depth = 2
        fields = ("id",
                  "scan_sign",
                  "scan_sign_name",
                  "sale_sign_name",
                  "scan",
                  "sale_sign",
                  "sale",
                  "product_list",
                  "tag",
                  "state",
                  "schedule_rule",
                  "board",
                  "create_time",
                  "start_time",
                  "end_time",
                  "state",
                  "board_name",
                  "account_name",
                  "pinterest_account",
                  "product_key",
                  "product_start",
                  "product_end"
        )

    def create(self, validated_data):
        with transaction.atomic():
            validated_data["user"] = self.context["request"].user
            schedule_rule_list = eval(self.context["request"].data["schedule_rule"])
            rule_instance = super(RuleSerializer, self).create(validated_data)
            for row in schedule_rule_list:
                row["rule"] = rule_instance
                models.RuleSchedule.objects.create(**row)
        return rule_instance

    def update(self, instance, validated_data):
        schedule_rule_list = eval(self.context["request"].data["schedule_rule"])
        with transaction.atomic():
            rule_instance = super(RuleSerializer, self).update(instance, validated_data)
            models.RuleSchedule.objects.filter(rule=instance).delete()
            for row in schedule_rule_list:
                row["rule"] = rule_instance
                models.RuleSchedule.objects.create(**row)
        return instance


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = "__all__"


class ProductHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductHistoryData
        fields = "__all__"


class PublishRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PublishRecord
        depth = 2
        fields = "__all__"


class PinterestAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PinterestAccount
        fields = (
            "id",
            "account",
            "nickname",
            "email",
            "type",
            # "state",
            "description",
            # "create_time"
            # "user"
        )
        # extra_kwargs = {
        #     'user': {'write_only': False},
        # }
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=models.PinterestAccount.objects.all(),
        #         fields=('account', 'user')
        #     )
        # ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        instance = super(PinterestAccountCreateSerializer, self).create(validated_data)
        instance.user = self.context["request"].user
        instance.save()
        return instance


class RuleStatusSerializer(serializers.ModelSerializer):
    """修改规则状态"""
    class Meta:
        model = models.Rule
        # depth = 2
        fields = ("id", "state",)

    def update(self, instance, validated_data):
        rule_instance = super(RuleStatusSerializer, self).update(instance, validated_data)
        if validated_data["state"] in [2, 5]:
            models.PublishRecord.objects.filter(**{"rule": rule_instance, "state__in": [-1, 0, 2, 4, 5]}).update(state=validated_data["state"])
        return instance


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("username", "email")


class GetCategorylizer(serializers.ModelSerializer):
    "产品类目列表"
    class Meta:
        model = models.ProductCategory
        fields = "__all__"
