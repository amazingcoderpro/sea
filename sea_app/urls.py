from django.conf.urls import url, include

from sea_app.views import reports, personal_center, account_manager, report

v1_urlpatterns = [
    # 注册 登陆
    url(r'^account/login/$', personal_center.LoginView.as_view()),
    url(r'^account/register/$', personal_center.RegisterView.as_view()),

    # 用户 角色管理
    url(r'users/$', personal_center.UserView.as_view()),
    url(r'users/(?P<pk>[0-9]+)/$', personal_center.UserOperView.as_view()),
    url(r'users/operation_record/$', reports.operation_record_listview),
    url(r'role/$', personal_center.RoleView.as_view()),
    url(r'role/(?P<pk>[0-9]+)/$', personal_center.RoleOperView.as_view()),

    # 报告
    url(r'dashboard/change_part/$', report.DashBoardChangePartView.as_view()),
    url(r'dashboard/fixed_part/$', report.DashBoardFixedPartView.as_view()),
    url(r'daily_report/$', report.DailyReportView.as_view()),
    url(r'subaccount_report/(?P<type>[a-zA-Z]+)/$', report.SubAccountReportView.as_view()),

    # 选择列表
    url(r'select/account/$', account_manager.PinterestAccountListView.as_view()),
    url(r'select/board/$', account_manager.BoardListView.as_view()),
    url(r'select/pin/$', account_manager.PinListView.as_view()),

    # 规则管理
    url(r'rule/$', account_manager.RuleView.as_view()),
    url(r'rule/(?P<pk>[0-9]+)/$', account_manager.RuleOperView.as_view()),
    # 增加规则获取账号列表
    url(r'product_count/$', account_manager.ProductCount.as_view()),
    # 获取pin账号
    url(r'pinterest_account_board/$', account_manager.PinterestAccountView.as_view()),
    # 获取产品
    url(r'product/$', account_manager.ProductView.as_view()),
    # 发布记录
    url(r'report/$', account_manager.ReportView.as_view()),

    # 店铺和账户授权
    url(r'store_auth/$', personal_center.StoreAuthView.as_view()),
    url(r'pinterest_account_auth/(?P<pk>[0-9]+)/$', account_manager.PinterestAccountAuthView.as_view()),
    url(r'shopify/callback/$', personal_center.ShopifyCallback.as_view()),
    url(r'pinterest/callback/$', personal_center.PinterestCallback.as_view()),

    # 账户管理
    url(r'account_list/$', account_manager.AccountListManageView.as_view()),
    url(r'account_list/(?P<aid>[0-9]+)/$', account_manager.BoardListManageView.as_view()),
    url(r'account_list/(?P<aid>[0-9]+)/(?P<bid>[0-9]+)/$', account_manager.PinListManageView.as_view()),
    url(r'board_manage/(?P<pk>[0-9]+)/$', account_manager.BoardManageView.as_view()),
    url(r'pin_manage/(?P<pk>[0-9]+)/$', account_manager.PinManageView.as_view()),
    url(r'account_manage/(?P<pk>[0-9]+)/$', account_manager.AccountManageView.as_view()),
    # 增加账户
    url(r'pinterest_account/$', account_manager.PinterestAccountCreateView.as_view()),

]


urlpatterns = [
    url(r'^v1/', include(v1_urlpatterns)),
]