from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

# Create your models here.


class Menu(models.Model):
    module = models.CharField(max_length=255, verbose_name="菜单名称")

    class Meta:
        managed = False
        db_table = 'menu'


class Role(models.Model):
    name = models.CharField(unique=True, max_length=255, verbose_name="角色名称")
    owner = models.IntegerField(blank=True, null=True, verbose_name="创建者")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    menu = models.CharField(max_length=45, blank=True, null=True, verbose_name="菜单权限")

    class Meta:
        managed = False
        db_table = 'role'


class User(AbstractBaseUser):
    username = models.CharField(max_length=64, unique=True, verbose_name="用户名")
    nickname = models.CharField(max_length=45, blank=True, null=True, verbose_name="昵称")
    password = models.CharField(max_length=32, verbose_name="密码")
    site_name = models.CharField(max_length=45, blank=True, null=True, verbose_name="站点名称")
    site_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="站点URL")
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name="链接参数")
    state_choices = ((0, '正常'), (1, '隐蔽'), (2, '关闭'))
    state = models.CharField(choices=state_choices, default=0, verbose_name="用户状态")
    parent = models.IntegerField(blank=True, null=True, verbose_name="用户名")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'
