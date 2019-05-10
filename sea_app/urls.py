from django.conf.urls import url, include
from rest_framework import routers

from sea_app import views


router = routers.DefaultRouter()
router.register(r'v1/users', views.UserViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    # 注册 登陆
    url(r'^account/login/$', views.LoginView.as_view()),
    url(r'^account/register/$', views.RegisterView.as_view()),


    # 获取电商
    url(r'v1/store', views.StoreView.as_view())

]