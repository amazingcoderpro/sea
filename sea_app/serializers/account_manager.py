import datetime

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


class PublishRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PublishRecord
        depth = 2
        fields = "__all__"


class PublishRecordDSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PublishRecord
        fields = "__all__"


class RuleSerializer(serializers.ModelSerializer):
    schedule_rule = RuleScheduleSerializer(many=True, read_only=True)
    publish_record = PublishRecordDSerializer(many=True, read_only=True)
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
                  "board_name",
                  "account_name",
                  "pinterest_account",
                  "product_key",
                  "product_start",
                  "product_end",
                  "publish_record"
        )

    def create(self, validated_data):
        with transaction.atomic():
            validated_data["user"] = self.context["request"].user
            schedule_rule_list = eval(self.context["request"].data["schedule_rule"])
            # 对product_list使用uuid去重
            product_list = eval(self.context["request"].data["product_list"])
            product_tuple = models.Product.objects.filter(id__in=product_list).values("id", "uuid")
            product_dict = {}
            for item in product_tuple:
                if item["uuid"] not in product_dict:
                    product_dict.update({item["uuid"]: item["id"]})
            product_list = list(product_dict.values())
            # 需要计算规则的开始时间和结束时间
            publish_list = self.create_publish_record(product_list, schedule_rule_list,
                        self.context["request"].data["start_time"],self.context["request"].data["end_time"])
            # validated_data["start_time"] = publish_list[0]["execute_time"].strftime("%Y-%m-%d %H:%M:%S")
            # validated_data["end_time"] = publish_list[-1]["execute_time"].strftime("%Y-%m-%d %H:%M:%S")
            rule_instance = super(RuleSerializer, self).create(validated_data)
            for row in schedule_rule_list:
                row["rule"] = rule_instance
                models.RuleSchedule.objects.create(**row)
            for row in publish_list:
                row["rule"] = rule_instance
                row["board_id"] = self.context["request"].data["board"]
                row["pinterest_account_id"] = self.context["request"].data["pinterest_account"]
                row["state"] = 0
                models.PublishRecord.objects.create(**row)
        return rule_instance

    def create_publish_record(self, product_list, schedule_rule, start_time, end_time):
        # 生成发布记录列表
        publish_list = []
        date = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        while len(product_list) > 0:
            if date.weekday() in [item["weekday"] for item in schedule_rule]:
                for item in schedule_rule:
                    if item["weekday"] != date.weekday():
                        continue
                    for t in item["post_time"]:
                        # 开始日期第一天已过期的时间不计算
                        if date.date() == datetime.datetime.today().date() and date.strftime("%H:%M") >= t:
                            continue
                        execute_time = datetime.datetime.strptime(date.date().strftime("%Y-%m-%d") + " " + t, "%Y-%m-%d %H:%M")
                        # 结束日期最后一个时间点到后直接返回
                        if execute_time.strftime("%Y-%m-%d %H:%M:%S") > end_time:
                            return sorted(publish_list, key=lambda x: x["execute_time"])
                        if len(product_list) > 0:
                            publish_list.append({"execute_time": execute_time, "product_id": product_list.pop()})
            date = date + datetime.timedelta(days=1)
        return sorted(publish_list, key=lambda x: x["execute_time"])


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


class GetCategorySerializer(serializers.ModelSerializer):
    "产品类目列表"
    class Meta:
        model = models.ProductCategory
        fields = ("id", "title")
