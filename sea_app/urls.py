from django.conf.urls import url, include

from sea_app.views import reports
from sea_app.views import personnal_center


v1_urlpatterns = [
    # 注册 登陆
    url(r'^account/login/$', personnal_center.LoginView.as_view()),
    url(r'^account/register/$', personnal_center.RegisterView.as_view()),

    # 用户管理
    url(r'users/$', personnal_center.UserView.as_view()),
    url(r'users/(?P<pk>[0-9]+)/$', personnal_center.UserOperView.as_view()),

    # 角色管理
    url(r'role/$', personnal_center.RoleView.as_view()),
    url(r'role/(?P<pk>[0-9]+)/$', personnal_center.RoleOperView.as_view()),

    # 报告
    # url(r'dashboard/$', report.DashBoardView.as_view()),
    url(r'dailyreport/$', reports.daily_report_view),
    # url(r'subaccountreport/(?P<type>[a-zA-Z]+)/$', report.SubAccountReportView.as_view()),

]


urlpatterns = [
    url(r'^v1/', include(v1_urlpatterns)),
]