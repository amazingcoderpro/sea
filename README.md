# PinBooster自动化营销系统

## 1. 初始化数据库
- user表增加管理员
- platform 增加三条数据
	
```
	INSERT INTO `user` (`id`, `last_login`, `is_superuser`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `username`, `email`, `password`, `code`, `create_time`, `update_time`)
VALUES
	(1, NULL, 0, '', '', 0, 1, '2019-06-01 00:00:00.852191', 'admin', 'victor.fang@orderplus.com', 'pbkdf2_sha256$120000$M0cY6Z6wcYr9$iwqYBe/MJfOLkpx2/2mMWtt2f1X7GBSt7D0EKRdjdV8=', NULL, '2019-06-01 00:00:00.899300', '2019-06-01 00:00:00.744339'),
	(2, NULL, 0, '', '', 0, 0, '2019-05-29 06:55:41.852191', 'admin001', 'victor.fang@orderplus.com', 'pbkdf2_sha256$120000$M0cY6Z6wcYr9$iwqYBe/MJfOLkpx2/2mMWtt2f1X7GBSt7D0EKRdjdV8=', NULL, '2019-05-29 06:55:41.899300', '2019-05-29 07:17:42.744339'),


INSERT INTO `platform` (`id`, `name`, `url`, `create_time`, `update_time`)
VALUES
	(1, 'Shopify', NULL, '2019-06-01 00:00:00.852191', '2019-06-01 00:00:00.852191'),
	(2, 'Cloud', NULL, '2019-06-01 00:00:00.852191', '2019-06-01 00:00:00.852191'),
	(3, 'Individual', NULL, '2019-06-01 00:00:00.852191', '2019-06-01 00:00:00.852191');

```

## 2. 注册用户(创建店铺和用户)
- shopify用户授权
- 设置密码发送邮件
- 店铺邮箱账户登陆激活

```

INSERT INTO `store` (`id`, `name`, `url`, `email`, `visitors`, `scan`, `sale`, `token`, `create_time`, `update_time`, `platform_id`, `user_id`)
VALUES
	(1, 'ordersea', 'ordersea.myshopify.com', '', 0, 0, 0, '89fd432044e87807ff26d62f39698246', '2019-05-29 11:54:56.178368', '2019-05-29 12:44:13.583658', 1, 4);


INSERT INTO `user` (`id`, `last_login`, `is_superuser`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `username`, `email`, `password`, `code`, `create_time`, `update_time`)
VALUES
	(4, NULL, 0, '', '', 0, 0, '2019-05-29 11:54:56.724673', 'ordersea.myshopify.com', 'twobercancan@gmail.com', 'pbkdf2_sha256$120000$n8xKHPHAqsw0$gaeCn0M9SR8oJ0xRSNcYfY7b4AT/gewzCGHiRvRvmrM=', '878Ey2', '2019-05-29 11:54:56.739924', '2019-05-29 13:12:01.419512');

```
## 3. 登陆创建pinterest账户(授权)

```
	INSERT INTO `pinterest_account` (`id`, `account_uri`, `nickname`, `email`, `type`, `state`, `description`, `create_time`, `token`, `boards`, `views`, `authorized`, `add_time`, `update_time`, `followings`, `followers`, `user_id`)
	VALUES
		(1, 'shaowei580@gmail.com', '123', 'shaowei580@gmail.com', 1, 0, '123123', '2019-05-30 16:00:00.000000', 'AnWLrM41pDqkKjVOtayNpIR0qww0FaNXVLehYvRF0n-lswCyYAj5ADAAAlZaRd8vtRSgzAAAAAAA', 0, 0, 1, '2019-05-30 02:49:53.300878', '2019-05-30 02:49:53.474150', 0, 0, 1),
		(3, 'yongyuanzhiqizhi@gmail.com', '', 'yongyuanzhiqizhi@gmail.com', 1, 0, '123123', '2019-05-30 03:15:23.000000', NULL, 0, 0, 0, '2019-05-30 03:13:49.110437', '2019-05-30 03:13:49.333120', 0, 0, 1);

```


4. 后台操作
- 更新店铺信息, 包括店铺的基本信息和从GA拉取的店铺浏览量，销售额等数据
- 更新Pinsterest账户信息，包括所有boards, pins, 以及boards,pins的属性信息，如likes,comments,saves等
- 开启定时任务，以天为单位循环更新以上两条
## 服务启动

```
yum install supervisor
systemctl enable supervisord
systemctl start supervisord
systemctl stop supervisord
systemctl restart supervisord
```