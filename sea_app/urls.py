from django.conf.urls import url, include
from django.views.decorators.cache import cache_page, cache_control

from sea_app.views import personal_center, account_manager, report, dashboard, store

v1_urlpatterns = [

    # 报告
    url(r'dashboard/(?P<pk>[1-5]+)/$', cache_page(5*60)(dashboard.DashBoardView.as_view())),
    url(r'daily_report/$', cache_page(5)(report.DailyReportView.as_view())),
    url(r'subaccount_report/(?P<type>[a-zA-Z]+)/$', cache_page(5*60)(report.SubAccountReportView.as_view())),

    # 选择列表
    url(r'select/account/$', cache_page(5*60)(account_manager.PinterestAccountListView.as_view())),
    url(r'select/board/$', cache_page(5*60)(account_manager.BoardListView.as_view())),
    url(r'select/pin/$', cache_page(5*60)(account_manager.PinListView.as_view())),

    # 账户管理
    url(r'account_list/$', cache_page(2)(account_manager.AccountListManageView.as_view())),
    url(r'account_list/(?P<aid>[0-9]+)/$', cache_page(2)(account_manager.BoardListManageView.as_view())),
    url(r'account_list/(?P<aid>[0-9]+)/(?P<bid>[0-9]+)/$', cache_page(2)(account_manager.PinListManageView.as_view())),
    url(r'board_manage/(?P<pk>[0-9]+)/$', account_manager.BoardManageView.as_view()),
    url(r'pin_manage/$', account_manager.PinManageView.as_view()),
    url(r'account_manage/(?P<pk>[0-9]+)/$', account_manager.AccountManageView.as_view()),
    # 增加账户
    url(r'pinterest_account/$', account_manager.PinterestAccountCreateView.as_view()),

    # 店铺管理
    # url(r'store/$', store.StoreView.as_view()),
    url(r'store/(?P<pk>[0-9]+)/$', store.StoreOperView.as_view()),

    # 清除缓存
    # url(r'clean_cache/$', dashboard.expire_page)
]

# 规则管理 `/v1/rule/`
rule_urlpatterns = [

    # 增加规则 规则列表
    url(r'^$', account_manager.RuleView.as_view()),
    # 增加规则: 查询符合条件的产品列表
    url(r'search_product/$', account_manager.SearchProductView.as_view()),
    # 增加规则: 获取某用户的pinterest账号和board
    url(r'pinterest_account_board/$', account_manager.PinterestAccountView.as_view()),

    # 修改规则状态
    url(r'state/(?P<pk>[0-9]+)/$', account_manager.RuleStatusView.as_view()),
    # url(r'state/batch/$', account_manager.RuleStatusView.as_view()),

    # 发布记录和发布列表
    url(r'report/$', account_manager.ReportView.as_view()),
    # 发布pin
    url(r'report/send_pin/(?P<pk>[0-9]+)/$', account_manager.SendPinView.as_view()),

    # 修改规则
    # url(r'rule/(?P<pk>[0-9]+)/$', account_manager.RuleOperView.as_view()),
    # 发布列表
    # url(r'rule/product/$', account_manager.ProductView.as_view()),
]

# 用户中心 `/v1/account/`
account_urlpatterns = [

    # 注册 登陆
    url(r'^login/$', personal_center.LoginView.as_view()),
    url(r'^register/$', personal_center.RegisterView.as_view()),
    # shopfy注册设置密码
    url(r'^set_password/(?P<pk>[0-9]+)/$', personal_center.SetPasswordView.as_view()),
    # 登陆状态下设置密码
    url(r'^set_passwords/(?P<pk>[0-9]+)/$', personal_center.SetPasswordsView.as_view()),

    # 用户 角色管理
    # url(r'users/$', personal_center.UserView.as_view()),
    url(r'users/(?P<pk>[0-9]+)/$', personal_center.UserOperView.as_view()),
    url(r'users/operation_record/$', cache_page(5)(personal_center.OperationRecord.as_view())),
    # url(r'role/$', personal_center.RoleView.as_view()),
    # url(r'role/(?P<pk>[0-9]+)/$', personal_center.RoleOperView.as_view()),
]

# 授权 `/v1/auth/`
auth_urlpatterns = [

    # 店铺和账户授权
    url(r'store/(?P<pk>[0-9]+)/$', personal_center.StoreAuthView.as_view()),
    url(r'pinterest_account/(?P<pk>[0-9]+)/$', personal_center.PinterestAccountAuthView.as_view()),
    url(r'shopify/callback/$', personal_center.ShopifyCallback.as_view()),
    url(r'shopify/ask_permission/$', personal_center.ShopifyAuthView.as_view()),
    url(r'pinterest/callback/$', personal_center.PinterestCallback.as_view()),
]

urlpatterns = [
    url(r'^v1/', include(v1_urlpatterns)),
    url(r'^v1/rule/', include(rule_urlpatterns)),
    url(r'^v1/account/', include(account_urlpatterns)),
    url(r'^v1/auth/', include(auth_urlpatterns)),
]