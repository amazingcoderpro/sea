import time
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


# class Menu(models.Model):
#     """菜单表"""
#     menu_name = models.CharField(max_length=255, verbose_name="菜单名称")
#     menu_url = models.CharField(blank=True, null=True, max_length=255, verbose_name="菜单链接")
#     parent_id = models.IntegerField(db_index=True, blank=True, null=True, verbose_name="菜单ID")
#     create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
#     update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
#     menu_num = models.FloatField(blank=True, null=True, verbose_name="菜单排序")
#     icon = models.CharField(blank=True, null=True, max_length=255, verbose_name="菜单主题")
#
#     class Meta:
#         # managed = False
#         db_table = 'menu'


# class Role(models.Model):
#     """角色表"""
#     name = models.CharField(max_length=255, verbose_name="角色名称")
#     user_id = models.IntegerField(blank=True, null=True, verbose_name="创建者")
#     create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
#     update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
#     menu_list = models.CharField(max_length=255, verbose_name="菜单权限")  # 格式："[1,2,3]"
#
#     class Meta:
#         # managed = False
#         db_table = 'role'
#         unique_together = ('name', 'user_id',)


class User(AbstractUser):
    """系统用户表"""
    username = models.CharField(max_length=255, unique=True, verbose_name="账户")
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="账户邮箱")
    # nickname = models.CharField(max_length=45, verbose_name="昵称")
    password = models.CharField(max_length=128, blank=True, null=True,  verbose_name="密码")
    # site_name = models.CharField(max_length=45, blank=True, null=True, verbose_name="站点名称")
    # site_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="站点URL")
    # link = models.CharField(max_length=255, blank=True, null=True, verbose_name="链接参数")
    # state_choices = ((0, '正常'), (1, '隐蔽'), (2, '关闭'))
    # state = models.SmallIntegerField(choices=state_choices, default=0, verbose_name="用户状态")
    # parent_id = models.IntegerField(db_index=True, blank=True, null=True, verbose_name="站长ID")
    # parent = models.ForeignKey("self", on_delete=models.DO_NOTHING, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True, unique=True, verbose_name="用户唯一标识")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    # role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)

    class Meta:
        # managed = False
        db_table = 'user'
        ordering = ["-id"]


class Platform(models.Model):
    """平台表"""
    name = models.CharField(max_length=64, unique=True, verbose_name="平台名称")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="平台URL")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # managed = False
        db_table = 'platform'
        ordering = ["-id"]


class Store(models.Model):
    """店铺表"""
    name = models.CharField(blank=True, null=True, max_length=255, verbose_name="店铺名称")
    url = models.CharField(blank=True, null=False, max_length=255, unique=True, verbose_name="店铺URL")
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        blank=True,
    )

    visitors = models.IntegerField(blank=True, null=True, default=0, verbose_name="访问量")
    scan = models.IntegerField(blank=True, null=True, default=0, verbose_name="浏览量")
    sale = models.FloatField(blank=True, null=True, default=0.00, verbose_name="营收额")
    # authorized_choices = ((0, 'no_authorized'), (1, 'authorized'))
    # authorized = models.SmallIntegerField(choices=authorized_choices, default=0, verbose_name="是否认证")
    token = models.CharField(blank=True, null=True, max_length=255, verbose_name="账号使用标识")
    platform = models.ForeignKey(Platform, on_delete=models.DO_NOTHING)
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, blank=True, null=True, unique=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    uuid = models.CharField(blank=True, null=True, max_length=64, verbose_name="店铺的唯一标识")
    timezone = models.CharField(blank=True, null=True, max_length=255, verbose_name="店铺的时区")
    country = models.CharField(blank=True, null=True, max_length=255, verbose_name="店铺所在的国家")
    city = models.CharField(blank=True, null=True, max_length=255, verbose_name="店铺所在的城市")
    currency = models.CharField(blank=True, null=True, max_length=20, verbose_name="店铺所使用的计价货币符号")
    owner_name = models.CharField(blank=True, null=True, max_length=255, verbose_name="店主的名称")
    owner_phone = models.CharField(blank=True, null=True, max_length=50, verbose_name="店主的电话")
    store_create_time = models.DateTimeField(blank=True, null=True,verbose_name="店铺的创建时间")
    store_update_time = models.DateTimeField(blank=True, null=True,verbose_name="店铺的更新时间")
    store_view_id = models.CharField(blank=True, null=True, max_length=100, verbose_name=u"店铺的GA中的view id")


    class Meta:
        # managed = False
        # unique_together = ("name", "platform")
        db_table = 'store'
        ordering = ["-id"]


class ProductCategory(models.Model):
    """产品类型表"""
    name = models.CharField(max_length=255, verbose_name="名称")
    uid = models.IntegerField(db_index=True, blank=True, null=True, verbose_name="类型标识")
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING, blank=True, null=True)
    parent_id = models.IntegerField(db_index=True, blank=True, null=True, verbose_name="产品父ID")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # managed = False
        db_table = 'product_category'


class Product(models.Model):
    """产品表"""
    sku = models.CharField(max_length=64, verbose_name="产品标识符")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="产品URL")
    uuid = models.CharField(max_length=64, verbose_name="产品唯一标识", unique=True)
    name = models.CharField(db_index=True, max_length=255, verbose_name="产品名称")
    image_url = models.CharField(max_length=255, verbose_name="图片URL")
    thumbnail = models.TextField(verbose_name="缩略图", blank=True, null=True, default=None)
    price = models.CharField(max_length=255, verbose_name="产品价格")
    category = models.ForeignKey(ProductCategory, on_delete=models.DO_NOTHING, blank=True, null=True)
    tag = models.CharField(max_length=255, verbose_name="所属标签")
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING)
    publish_time = models.DateTimeField(blank=True, null=True, verbose_name="发布时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    url_with_utm = models.CharField(blank=True, null=True, max_length=255, verbose_name=u"产品的带utm构建的url")

    class Meta:
        # managed = False
        db_table = 'product'
        ordering = ["-id"]


class PinterestAccountManager(models.Manager):
    def get_queryset(self):
        return super(PinterestAccountManager, self).get_queryset().filter(state__in=[0, 1])


class PinterestAccount(models.Model):
    """Pin账户表"""
    account = models.CharField(max_length=64, verbose_name="PinterestAccount唯一标识码")
    nickname = models.CharField( blank=True, null=True, max_length=64, verbose_name="账户名称")
    email = models.CharField(blank=True, null=True, max_length=255, verbose_name="登陆邮箱")
    type_choices = ((0, 'individual'), (1, 'business'))
    type = models.SmallIntegerField(choices=type_choices, default=0, verbose_name="账号类型")
    state_choices = ((0, 'normal'), (1, 'forbidden'), (2, 'deleted'))
    state = models.SmallIntegerField(choices=state_choices, default=0, verbose_name="账号状态")
    description = models.TextField(blank=True, null=True, verbose_name="账户描述")
    create_time = models.DateTimeField(blank=True, null=True, verbose_name="账号创建时间")
    token = models.CharField(blank=True, null=True, max_length=255, verbose_name="账号使用标识")
    boards = models.IntegerField(default=0, verbose_name=u"account下的board个数")
    pins = models.IntegerField(default=0, verbose_name=u"account下的pin个数")
    views = models.IntegerField(default=0, verbose_name="访问量")
    authorized_choices = ((0, 'no_authorized'), (1, 'authorized'), (2, 'authorized_faield'))
    authorized = models.SmallIntegerField(choices=authorized_choices, default=0, verbose_name="是否认证")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    followings = models.IntegerField(default=0, verbose_name="账户关注量")
    followers = models.IntegerField(default=0, verbose_name="账户粉丝")
    uuid = models.CharField(unique=True, max_length=64, verbose_name="账户的uuid")
    thumbnail = models.TextField(verbose_name="缩略图", default=None, blank=True, null=True)

    objects = PinterestAccountManager()

    class Meta:
        # managed = False
        unique_together = ("uuid", "user")
        db_table = 'pinterest_account'
        ordering = ["-id"]

    def delete(self, using=None, keep_parents=False):
        self.state = 2
        self.uuid = str(uuid.uuid1()) + str(time.time())
        self.save()
        return 'success'


class Board(models.Model):
    """Pin Board表"""
    uuid = models.CharField(db_index=True, max_length=64, verbose_name="Board唯一标识码")
    name = models.CharField(max_length=64, verbose_name="Board名称")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="Board URL")
    create_time = models.DateTimeField(verbose_name="Board创建时间")
    description = models.TextField(blank=True, null=True, verbose_name="Board 描述")
    state_choices = ((0, 'Private'), (1, 'Public'))
    state = models.SmallIntegerField(choices=state_choices, default=1, verbose_name="账号状态")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    pins = models.IntegerField(default=0, verbose_name=u"board的下的pin个数")
    followers = models.IntegerField(default=0, verbose_name=u"board的follow数")
    collaborators = models.IntegerField(default=0, verbose_name=u"board的合作者个数")
    pinterest_account = models.ForeignKey(PinterestAccount, related_name='board_pinterest_account', on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:

        db_table = 'board'
        ordering = ["-id"]


class Pin(models.Model):
    """Pin 表"""
    uuid = models.CharField(db_index=True, max_length=64, verbose_name="Pin唯一标识码")
    url = models.URLField(max_length=255, blank=True, null=True, verbose_name="Pin URL")
    note = models.TextField(verbose_name="Pin 描述")
    origin_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="产品URL")
    image_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="产品大图URL")
    thumbnail = models.TextField(verbose_name="缩略图", blank=True, null=True, default=None)
    publish_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    board = models.ForeignKey(Board, on_delete=models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, blank=True, null=True)
    saves = models.IntegerField(default=0, verbose_name=u"转发量")
    comments = models.IntegerField(default=0, verbose_name=u"评论量")
    likes = models.IntegerField(default=0, verbose_name=u"点赞数, pinterest平台已经没有了,暂时保留")

    class Meta:
        # managed = False
        db_table = 'pin'
        ordering = ["-id"]


class PinterestHistoryData(models.Model):
    """Pinterest历史数据表"""
    pinterest_account = models.ForeignKey(PinterestAccount, on_delete=models.DO_NOTHING, blank=True, null=True)
    account_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="账户名称")
    account_followings = models.IntegerField(default=0, verbose_name="账户关注量")
    account_followers = models.IntegerField(default=0, verbose_name="账户粉丝")
    account_views = models.IntegerField(default=0, verbose_name="账户访问量")
    board = models.ForeignKey(Board, on_delete=models.DO_NOTHING, blank=True, null=True)
    board_uuid = models.CharField(max_length=64, blank=True, null=True, verbose_name="Board唯一标识码")
    board_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Board名称")
    board_followers = models.IntegerField(default=0, verbose_name="board粉丝")
    pin = models.ForeignKey(Pin, on_delete=models.DO_NOTHING, blank=True, null=True)
    pin_uuid = models.CharField(max_length=64, blank=True, null=True, verbose_name="Pin唯一标识码")
    pin_note = models.TextField(blank=True, null=True, verbose_name="Pin 描述")
    pin_thumbnail = models.TextField(blank=True, null=True, default=None, verbose_name="缩略图")
    pin_likes = models.IntegerField(default=0, verbose_name="喜欢量, pinteres平台已经没有了, 暂时保留")
    pin_comments = models.IntegerField(default=0, verbose_name="评论量")
    pin_saves = models.IntegerField(default=0, verbose_name="转发量")

    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, blank=True, null=True)

    update_time = models.DateTimeField(auto_now=True, db_index=True, verbose_name="数据更新时间")

    class Meta:
        # managed = False
        db_table = 'pinterest_history_data'
        ordering = ["-update_time"]


class ProductHistoryData(models.Model):
    """Product历史数据表"""
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    product_visitors = models.IntegerField(default=0, verbose_name="访客总数")
    product_new_visitors = models.IntegerField(default=0, verbose_name="新访客数")
    product_clicks = models.IntegerField(default=0, verbose_name="点击量")
    product_scan = models.IntegerField(default=0, verbose_name="浏览量")
    product_sales = models.IntegerField(default=0, verbose_name="订单数")
    product_revenue = models.FloatField(default=0.00, verbose_name="销售额")
    update_time = models.DateTimeField(auto_now=True, db_index=True, verbose_name="数据更新时间")

    class Meta:
        #managed = False
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
    product_list = models.TextField(default="", verbose_name="产品列表")
    tag = models.CharField(max_length=64, blank=True, null=True, verbose_name="规则标签")
    board = models.ForeignKey(Board, on_delete=models.DO_NOTHING)
    state_choices = ((-1, '新建'), (0, '待执行'), (1, '运行中'), (2, '暂停中'), (3, '已完成'), (4, '已过期'), (5, '已删除'))
    state = models.SmallIntegerField(choices=state_choices, default=-1, verbose_name="规则状态, (-1, '新建'), (0, '待执行'), (1, '运行中'), (2, '暂停中'), (3, '已完成'), (4, '已过期'), (5, '已删除')")
    start_time = models.DateTimeField(verbose_name="发布开始时间")
    end_time = models.DateTimeField(verbose_name="发布结束时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        # managed = False
        db_table = 'rule'
        ordering = ["-update_time"]


class RuleSchedule(models.Model):
    """规则时间表"""
    weekday_choices = ((0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday"))
    weekday = models.SmallIntegerField(choices=weekday_choices, default=0, verbose_name="周几发布")
    start_time = models.TimeField(verbose_name="每天开始时间")
    end_time = models.TimeField(verbose_name="每天结束时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    interval_time = models.IntegerField(default=3600, verbose_name="发布间隔时间（秒）")
    rule = models.ForeignKey(Rule, related_name="schedule_rule", on_delete=models.DO_NOTHING)

    class Meta:
        # managed = False
        db_table = 'rule_schedule'
        ordering = ["-id"]


class PublishRecord(models.Model):
    """发布记录表"""
    board = models.ForeignKey(Board, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, blank=True, null=True)
    rule = models.ForeignKey(Rule, on_delete=models.DO_NOTHING)
    pin = models.ForeignKey(Pin, on_delete=models.DO_NOTHING, blank=True, null=True)
    state_choices = ((0, '待发布'), (1, '已发布'), (2, '暂停中'), (3, '发布失败'), (4, "已取消"), (5, "已删除"))
    state = models.SmallIntegerField(choices=state_choices, default=0, verbose_name="发布状态")
    remark = models.TextField(blank=True, null=True, verbose_name="备注")
    execute_time = models.DateTimeField(verbose_name="执行时间")
    finished_time = models.DateTimeField(null=True, verbose_name="完成时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # managed = False
        db_table = 'publish_record'
        ordering = ["-id"]


class OperationRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    action = models.CharField(max_length=64, verbose_name="操作行为")
    record = models.TextField(blank=True, null=True, verbose_name="操作记录")
    operation_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")

    class Meta:
        # managed = False
        db_table = 'operation_record'
        ordering = ["-id"]