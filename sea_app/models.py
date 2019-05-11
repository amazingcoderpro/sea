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

    class Meta:
        managed = False
        db_table = 'menu'


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=255, verbose_name="角色名称")
    user_id = models.IntegerField(blank=True, null=True, verbose_name="创建者")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    menu_list = models.CharField(max_length=45, blank=True, null=True, verbose_name="菜单权限")  # 格式："[1,2,3]"

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
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'
        ordering = ["-id"]


class Platform(models.Model):
    """平台表"""
    name = models.CharField(max_length=64, unique=True, verbose_name="平台名称")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="平台URL")

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


class Product(models.Model):
    """产品表"""
    sku = models.CharField(max_length=64, verbose_name="产品标识符")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="产品URL")
    sale = models.FloatField(verbose_name="销售额")
    revenue = models.FloatField(verbose_name="收益")
    image_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="图片URL")
    thumbnail = models.TextField(verbose_name="缩略图")
    scan = models.IntegerField(default=0, verbose_name="浏览量")
    category = models.CharField(max_length=64, verbose_name="类目")
    price = models.FloatField(verbose_name="产品价格")
    tag = models.CharField(max_length=64, verbose_name="所属标签")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product'


class Account(models.Model):
    """Pin账户表"""
    name = models.CharField(max_length=64, verbose_name="账户名称")
    email = models.CharField(max_length=255, verbose_name="登陆邮箱")
    create_time = models.DateTimeField(verbose_name="账号创建时间")
    type = models.CharField(max_length=64, verbose_name="账户类型")
    following = models.IntegerField(default=0, verbose_name="关注量")
    follower = models.IntegerField(default=0, verbose_name="粉丝")
    state = models.BooleanField(default=True, verbose_name="账号状态")
    token = models.CharField(max_length=255, verbose_name="账号使用标识")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'account'


class Board(models.Model):
    """Pin Board表"""
    name = models.CharField(max_length=64, verbose_name="Board名称")
    follower = models.IntegerField(default=0, verbose_name="粉丝")
    create_time = models.DateTimeField(verbose_name="Board创建时间")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    account = models.ForeignKey(Account, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'board'


class Pin(models.Model):
    """Pin 表"""
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="Pin URL")
    description = models.TextField(verbose_name="Pin 描述")
    like = models.IntegerField(default=0, verbose_name="喜欢量")
    comment = models.IntegerField(default=0, verbose_name="评论量")
    repin = models.IntegerField(default=0, verbose_name="转发量")
    site_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="产品URL")
    thumbnail = models.TextField(verbose_name="缩略图")
    publish_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    board = models.ForeignKey(Board, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pin'


class Rule(models.Model):
    """规则表"""
    start_time = models.DateTimeField(verbose_name="发布开始时间")
    end_time = models.DateTimeField(verbose_name="发布结束时间")
    delta_time = models.FloatField(verbose_name="发布间隔时间（秒）")
    low_scan = models.IntegerField(default=0, verbose_name="低浏览量")
    high_scan = models.IntegerField(default=0, verbose_name="高浏览量")
    low_sale = models.IntegerField(default=0, verbose_name="低销售额")
    high_sale = models.IntegerField(default=0, verbose_name="高销售额")
    category01 = models.CharField(max_length=64, blank=True, null=True, verbose_name="产品类目01")
    category02 = models.CharField(max_length=64, blank=True, null=True, verbose_name="产品类目02")
    category03 = models.CharField(max_length=64, blank=True, null=True, verbose_name="产品类目03")
    tag = models.CharField(max_length=64, blank=True, null=True, verbose_name="规则标签")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    board = models.ManyToManyField(Board)

    class Meta:
        managed = False
        db_table = 'rule'


class PublishRecord(models.Model):
    """发布记录表"""
    board = models.ForeignKey(Board, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, blank=True, null=True)
    state = models.BooleanField(default=True, verbose_name="是否发布")
    finished = models.BooleanField(default=True, verbose_name="是否发布成功")
    remark = models.TextField(blank=True, null=True, verbose_name="备注")
    execute_time = models.DateTimeField(auto_now_add=True, verbose_name="执行时间")

    class Meta:
        managed = False
        db_table = 'publishrecord'

