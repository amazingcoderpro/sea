from django.conf.urls import url, include

from sea_app.views import reports, personal_center, account_manager

v1_urlpatterns = [
    # 注册 登陆
    url(r'^account/login/$', personal_center.LoginView.as_view()),
    url(r'^account/register/$', personal_center.RegisterView.as_view()),

    # 用户管理
    url(r'users/$', personal_center.UserView.as_view()),
    url(r'users/(?P<pk>[0-9]+)/$', personal_center.UserOperView.as_view()),

    # 角色管理
    url(r'role/$', personal_center.RoleView.as_view()),
    url(r'role/(?P<pk>[0-9]+)/$', personal_center.RoleOperView.as_view()),

    # 报告
    # url(r'dashboard/$', report.DashBoardView.as_view()),
    url(r'dailyreport/$', reports.daily_report_view),
    url(r'subaccountreport/(?P<type>[a-zA-Z]+)/$', reports.subaccount_report_view),

    # 规则管理
    url(r'rule/$', account_manager.RuleView.as_view()),
    url(r'rule/(?P<pk>[0-9]+)/$', account_manager.RuleOperView.as_view()),

    # 获取pin账号
    url(r'pinterestaccount/$', account_manager.PinterestAccountView.as_view()),

    # 获取产品
    url(r'product/$', account_manager.ProductView.as_view()),


]


urlpatterns = [
    url(r'^v1/', include(v1_urlpatterns)),
]