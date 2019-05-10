from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class Menu(models.Model):
    """菜单表"""
    module = models.CharField(max_length=255, verbose_name="菜单名称")
    menu_url = models.CharField(max_length=255, verbose_name="菜单链接")
    parent_id = models.IntegerField(blank=True, null=True, verbose_name="菜单ID")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # managed = False
        db_table = 'menu'


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=255, verbose_name="角色名称")
    user_id = models.IntegerField(blank=True, null=True, verbose_name="创建者")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    menu = models.CharField(max_length=45, blank=True, null=True, verbose_name="菜单权限")

    class Meta:
        # managed = False
        db_table = 'role'


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
    parent_id = models.IntegerField(db_index=True, blank=True, null=True, verbose_name="站长ID")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'user'


class Platform(models.Model):
    """平台表"""
    name = models.CharField(max_length=64, unique=True, verbose_name="平台名称")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="平台URL")

    class Meta:
        # managed = False
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
        # managed = False
        db_table = 'store'


# class Product(models.Model):
#     """产品表"""
#     sku = models.CharField(max_length=64, verbose_name="店铺名称")