from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class Menu(models.Model):
    """菜单表"""
    menu_name = models.CharField(max_length=255, verbose_name="菜单名称")
    menu_url = models.CharField(blank=True, null=True, max_length=255, verbose_name="菜单链接")
    parent_id = models.IntegerField(db_index=True, blank=True, null=True, verbose_name="菜单ID")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    menu_num = models.FloatField(blank=True, null=True, verbose_name="菜单排序")
    icon = models.CharField(blank=True, null=True, max_length=255, verbose_name="菜单主题")

    class Meta:
        managed = False
        db_table = 'menu'


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=255, verbose_name="角色名称")
    user_id = models.IntegerField(blank=True, null=True, verbose_name="创建者")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    menu_list = models.CharField(max_length=255, verbose_name="菜单权限")  # 格式："[1,2,3]"

    class Meta:
        managed = False
        db_table = 'role'
        unique_together = ('name', 'user_id',)


class User(AbstractUser):
    """系统用户表"""
    username = models.CharField(max_length=64, verbose_name="账户名", unique=True)
    nickname = models.CharField(max_length=45, blank=True, null=True, verbose_name="昵称")
    password = models.CharField(max_length=128, verbose_name="密码")
    site_name = models.CharField(max_length=45, blank=True, null=True, verbose_name="站点名称")
    site_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="站点URL")
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name="链接参数")
    state_choices = ((0, '正常'), (1, '隐蔽'), (2, '关闭'))
    state = models.SmallIntegerField(choices=state_choices, default=0, verbose_name="用户状态")
    # parent_id = models.IntegerField(db_index=True, blank=True, null=True, verbose_name="站长ID")
    parent = models.ForeignKey("self", on_delete=models.DO_NOTHING, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user'
        ordering = ["-id"]


class Platform(models.Model):
    """平台表"""
    name = models.CharField(max_length=64, unique=True, verbose_name="平台名称")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="平台URL")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        managed = False
        db_table = 'platform'


class Store(models.Model):
    """店铺表"""
    name = models.CharField(max_length=64, verbose_name="店铺名称")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="店铺URL")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    platform = models.ForeignKey(Platform, on_delete=models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'store'


class ProductCategory(models.Model):
    """产品类型表"""
    name = models.CharField(max_length=255, verbose_name="名称")
    uid = models.IntegerField(db_index=True, blank=True, null=True, verbose_name="类型标识")
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING, blank=True, null=True)
    parent_id = models.IntegerField(db_index=True, blank=True, null=True, verbose_name="产品父ID")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        managed = False
        db_table = 'product_category'


class Product(models.Model):
    """产品表"""
    sku = models.CharField(max_length=64, verbose_name="产品标识符")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="产品URL")
    name = models.CharField(max_length=255, verbose_name="产品名称")
    image_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="图片URL")

    thumbnail = models.TextField(verbose_name="缩略图", default="")
    price = models.FloatField(verbose_name="产品价格")
    category = models.ForeignKey(ProductCategory, on_delete=models.DO_NOTHING, blank=True, null=True)
    tag = models.CharField(max_length=64, verbose_name="所属标签")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'product'


class PinterestAccount(models.Model):
    """Pin账户表"""
    account_uri = models.CharField(max_length=32, verbose_name="PinterestAccount唯一标识码")
    name = models.CharField(max_length=64, verbose_name="账户名称")
    email = models.CharField(max_length=255, verbose_name="登陆邮箱")
    create_time = models.DateTimeField(verbose_name="账号创建时间")
    type = models.CharField(max_length=64, verbose_name="账户类型")
    state = models.BooleanField(default=True, verbose_name="账号状态")
    token = models.CharField(max_length=255, verbose_name="账号使用标识")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pinterest_account'


class Board(models.Model):
    """Pin Board表"""
    board_uri = models.CharField(max_length=32, verbose_name="Board唯一标识码")
    name = models.CharField(max_length=64, verbose_name="Board名称")
    create_time = models.DateTimeField(verbose_name="Board创建时间")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")

    pinterest_account = models.ForeignKey(PinterestAccount, related_name='board_pinterest_account', on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:

        db_table = 'board'


class Pin(models.Model):
    """Pin 表"""
    pin_uri = models.CharField(max_length=32, verbose_name="Pin唯一标识码")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="Pin URL")
    description = models.TextField(verbose_name="Pin 描述")
    site_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="产品URL")
    thumbnail = models.TextField(verbose_name="缩略图")
    publish_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    board = models.ForeignKey(Board, on_delete=models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pin'


class PinterestHistoryData(models.Model):
    """Pinterest历史数据表"""
    pinterest_account = models.ForeignKey(PinterestAccount, on_delete=models.DO_NOTHING, blank=True, null=True)
    account_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="账户名称")
    account_following = models.IntegerField(default=0, verbose_name="账户关注量")
    account_follower = models.IntegerField(default=0, verbose_name="账户粉丝")
    board = models.ForeignKey(Board, on_delete=models.DO_NOTHING, blank=True, null=True)
    board_uri = models.CharField(max_length=32, blank=True, null=True, verbose_name="Board唯一标识码")
    board_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Board名称")
    board_follower = models.IntegerField(default=0, verbose_name="board粉丝")
    pin = models.ForeignKey(Pin, on_delete=models.DO_NOTHING, blank=True, null=True)
    pin_uri = models.CharField(max_length=32, blank=True, null=True, verbose_name="Pin唯一标识码")
    pin_description = models.TextField(blank=True, null=True, verbose_name="Pin 描述")
    pin_thumbnail = models.TextField(blank=True, null=True, verbose_name="缩略图")
    pin_like = models.IntegerField(default=0, verbose_name="喜欢量")
    pin_comment = models.IntegerField(default=0, verbose_name="评论量")
    pin_repin = models.IntegerField(default=0, verbose_name="转发量")
    pin_views = models.IntegerField(default=0, verbose_name="视图量")
    pin_clicks = models.IntegerField(default=0, verbose_name="点击量")

    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, blank=True, null=True)

    update_time = models.DateTimeField(auto_now=True, db_index=True, verbose_name="数据更新时间")

    class Meta:
        managed = False
        db_table = 'pinterest_history_data'
        ordering = ["-update_time"]


class ProductHistoryData(models.Model):
    """Product历史数据表"""
    Platform = models.ForeignKey(Platform, on_delete=models.DO_NOTHING, blank=True, null=True)

    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING, blank=True, null=True)
    store_visitors = models.IntegerField(default=0, verbose_name="访问量")
    store_new_visitors = models.IntegerField(default=0, verbose_name="新增访问量")
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    product_scan = models.IntegerField(default=0, verbose_name="浏览量")
    product_sale = models.FloatField(default=0.00, verbose_name="销售额")
    product_revenue = models.FloatField(default=0.00, verbose_name="收益")
    update_time = models.DateTimeField(auto_now=True, db_index=True, verbose_name="数据更新时间")

    class Meta:
        managed = False
        db_table = 'product_history_data'
        ordering = ["-update_time"]


class Rule(models.Model):
    """规则表"""
    scan_sign_choices = ((0, '='), (1, '>'), (2, '<'))
    scan_sign = models.SmallIntegerField(choices=scan_sign_choices, default=0, verbose_name="浏览量符号")
    scan = models.IntegerField(default=0, verbose_name="产品浏览量")
    sale_sign_choices = ((0, '='), (1, '>'), (2, '<'))
    sale_sign = models.SmallIntegerField(choices=sale_sign_choices, default=0, verbose_name="销量符号")
    sale = models.CharField(max_length=255, blank=True, null=True, default=0, verbose_name="产品销量")
    product_list = models.CharField(max_length=255, default="", verbose_name="产品列表")
    tag = models.CharField(max_length=64, blank=True, null=True, verbose_name="规则标签")
    board = models.ForeignKey(Board, on_delete=models.DO_NOTHING)
    state_choices = ((0, '待执行'), (1, '删除'), (2, '过期'), (3, '运行'), (4, '暂停'), (5,"已完成"))
    state = models.SmallIntegerField(choices=state_choices, default=0, verbose_name="规则状态")
    start_time = models.DateTimeField(verbose_name="发布开始时间")
    end_time = models.DateTimeField(verbose_name="发布结束时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:

        db_table = 'rule'


class RuleSchedule(models.Model):
    """规则时间表"""
    weekday_choices = ((0, "Sunday"), (1, "Monday"), (2, "Tuesday"), (3, "Wednesday"), (4, "Thursday"), (5, "Friday"), (6, "Saturday"))
    weekday = models.SmallIntegerField(choices=weekday_choices, default=0, verbose_name="周几发布")
    start_time = models.TimeField(verbose_name="每天开始时间")
    end_time = models.TimeField(verbose_name="每天结束时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    interval_time = models.FloatField(verbose_name="发布间隔时间（秒）")
    rule = models.ForeignKey(Rule, related_name="schedule_rule", on_delete=models.DO_NOTHING)

    class Meta:
        # managed = False
        db_table = 'rule_schedule'


class PublishRecord(models.Model):
    """发布记录表"""
    board = models.ForeignKey(Board, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, blank=True, null=True)
    rule = models.ForeignKey(Rule, on_delete=models.DO_NOTHING)
    pin = models.ForeignKey(Pin, on_delete=models.DO_NOTHING, blank=True, null=True)
    state_choices = ((0, 'pending'), (1, 'finished'), (2, 'failed'), )
    state = models.SmallIntegerField(choices=state_choices, default=0, verbose_name="发布状态")
    remark = models.TextField(blank=True, null=True, verbose_name="备注")
    execute_time = models.DateTimeField(verbose_name="执行时间")
    finished_time = models.DateTimeField(null=True, verbose_name="完成时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # managed = False
        db_table = 'publish_record'


class OperationRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    action = models.CharField(max_length=64, verbose_name="操作行为")
    record = models.TextField(blank=True, null=True, verbose_name="操作记录")
    operation_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")

    class Meta:
        # managed = False
        db_table = 'operation_record'