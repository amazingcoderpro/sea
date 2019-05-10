from django.conf.urls import url
from sea_app import views


urlpatterns = [
    # 注册 登陆
    url(r'^account/login/$', views.LoginView.as_view()),
]