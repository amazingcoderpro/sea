# sea
自动化营销系统

## DB初始化
```
INSERT INTO `menu` (`id`, `menu_name`, `menu_url`, `parent_id`, `create_time`, `update_time`, `menu_num`, `icon`)
VALUES
    (1, 'Dashboard', '/dashboard', NULL, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 1, 'el-icon-lx-home'),
    (2, 'Report', '1', NULL, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 2, 'el-icon-lx-calendar'),
    (3, 'DailyReport', '2', 2, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 3, NULL),
    (4, 'SubAccountDailyReport', '/sub_account_daily_report', 3, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 4, NULL),
    (5, 'BoardsDailyReport', '/boards_daily_report', 3, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 5, NULL),
    (6, 'PinsDailyReport', '/pins_daily_report', 3, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 6, NULL),
    (7, 'SubAccountReport', '2-1', 2, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 7, NULL),
    (8, 'SubAccountReport', '/sub_account_report', 7, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 8, NULL),
    (9, 'BoardReport', '/board_report', 7, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 9, NULL),
    (10, 'PinsReport', '/pins_peport', 7, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 10, NULL),
    (11, 'AccountManager', '3', NULL, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 11, 'el-icon-lx-warn'),
    (12, 'AccountManager', '/account_manager', 11, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 12, NULL),
    (13, 'BoardManager', '/board_manager', 12, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 13, NULL),
    (14, 'PinManager', '/pin_manager', 12, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 14, NULL),
    (15, 'RuleManager', '3-1', 11, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 15, NULL),
    (16, 'ListManager', '/list_manager', 15, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 16, NULL),
    (17, 'RecordManager', '/record_manager', 15, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 17, NULL),
    (18, 'PersonalCenter', '4', NULL, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 18, 'el-icon-lx-home'),
    (19, 'PermissionManager', '4-1', 18, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 19, NULL),
    (20, 'UserManager', '/user_manager', 19, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 20, NULL),
    (21, 'RoleManager', '/role_manager', 19, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', 21, NULL);
	(22, 'StoreManager', '/store_manager', 18, '2019-05-14 03:14:35.111111', '2019-05-14 03:14:35.111111', 22, NULL);


INSERT INTO `role` (`id`, `name`, `user_id`, `create_time`, `update_time`, `menu_list`)
VALUES
    (1, '站长', 1, '2019-05-14 03:14:35.762968', '2019-05-14 03:14:35.762968', '[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]'),
    (2, '运营专员', 1, '2019-05-16 07:11:06.600170', '2019-05-16 07:11:06.811441', '[1,2]');

INSERT INTO `user` (`id`, `last_login`, `is_superuser`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `username`, `nickname`, `password`, `site_name`, `site_url`, `link`, `state`, `create_time`, `update_time`, `parent_id`, `role_id`)
VALUES
    (1, NULL, 0, '', '', 'admin@163.com', 0, 1, '2019-05-17 07:10:35.433454', 'admin', 'admin', 'pbkdf2_sha256$120000$kdMrvlFpMYri$7JLZQldPVEixS9BA+qslsJLSZdppvzKU+QFCknMfrug=', NULL, NULL, NULL, 0, '2019-05-17 07:10:35.472266', '2019-05-17 07:10:36.022218', NULL, 1);
```

## 服务启动

```
yum install supervisor
systemctl enable supervisord
systemctl start supervisord
systemctl stop supervisord
systemctl restart supervisord
```