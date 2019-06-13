# PinBooster自动化营销系统

## 1. 初始化数据库
- user表增加管理员
- platform 增加三条数据
	
```
	INSERT INTO `user` (`id`, `last_login`, `is_superuser`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `username`, `email`, `password`, `code`, `create_time`, `update_time`)
VALUES
	(1, NULL, 0, 'admin', 'admin', 0, 0, '2019-06-01 00:00:00.852191', 'admin', 'victor.fang@orderplus.com', 'pbkdf2_sha256$120000$M0cY6Z6wcYr9$iwqYBe/MJfOLkpx2/2mMWtt2f1X7GBSt7D0EKRdjdV8=', NULL, '2019-06-01 00:00:00.899300', '2019-06-01 00:00:00.899300'),
	(2, NULL, 0, 'test001', 'test001', 0, 1, '2019-05-29 06:55:41.852191', 'test001', 'victor.fang@orderplus.com', 'pbkdf2_sha256$120000$Fp9sbcrgfWrJ$OlH4Z49b15v5MMwTMd/m3w/I0BZWynyALmTD2ydlTa8=', NULL, '2019-06-01 00:00:00.899300', '2019-06-01 00:00:00.899300'),
	(3, NULL, 0, 'test002', 'test002', 0, 0, '2019-05-29 06:55:41.852191', 'test002', 'victor.fang@orderplus.com', 'pbkdf2_sha256$120000$Fp9sbcrgfWrJ$OlH4Z49b15v5MMwTMd/m3w/I0BZWynyALmTD2ydlTa8=', NULL, '2019-06-01 00:00:00.899300', '2019-06-01 00:00:00.899300'),
	(4, NULL, 0, 'test002', 'test002', 0, 0, '2019-05-29 06:55:41.852191', 'test003', 'victor.fang@orderplus.com', 'pbkdf2_sha256$120000$Fp9sbcrgfWrJ$OlH4Z49b15v5MMwTMd/m3w/I0BZWynyALmTD2ydlTa8=', NULL, '2019-06-01 00:00:00.899300', '2019-06-01 00:00:00.899300');


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

INSERT INTO `store` (`id`, `name`, `url`, `email`, `visitors`, `scan`, `sale`, `token`, `create_time`, `update_time`, `uuid`, `timezone`, `country`, `city`, `currency`, `owner_name`, `owner_phone`, `store_create_time`, `store_update_time`, `store_view_id`, `platform_id`, `user_id`)
VALUES
	(1, '大卖场', 'https://pinbooster.seamarketings.com/', 'victor.fang@orderplus.com', 0, 0, 0, '12456789', '2019-05-29 11:54:56.178368', '2019-06-04 10:21:49.487091', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, 1),
	(2, '大卖场', 'https://pinbooster001.seamarketings.com/', 'victor.fang@orderplus.com', 0, 0, 0, '12456789', '2019-05-29 11:54:56.178368', '2019-06-04 10:21:49.487091', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, 2),
	(3, '大卖场', 'https://pinbooster002.seamarketings.com/', 'victor.fang@orderplus.com', 0, 0, 0, '12456789', '2019-05-29 11:54:56.178368', '2019-06-04 10:21:49.487091', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, 3),
	(4, '大卖场', 'https://pinbooster004.seamarketings.com/', 'victor.fang@orderplus.com', 0, 0, 0, '12456789', '2019-05-29 11:54:56.178368', '2019-06-04 10:21:49.487091', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, 4);

```
## 3. 登陆创建pinterest账户(授权)

```
	INSERT INTO `pinterest_account` (`id`, `account`, `nickname`, `email`, `type`, `state`, `description`, `create_time`, `token`, `boards`, `pins`, `views`, `authorized`, `add_time`, `update_time`, `followings`, `followers`, `uuid`, `user_id`)
VALUES
	(2, 'shaowei580@gmail.com', '', 'shaowei580@gmail.com', 1, 0, 'shaowei', '2019-06-04 16:00:00.000000', 'AiP-ymRCgT7SSGBguKHjT-SPcSNOFaTxExO9J4JF2gxXLuC2Ugj5ADAAAlZaReXFJ1qgudIAAAAA', 0, 0, 0, 1, '2019-06-04 08:18:18.955160', '2019-06-04 08:18:19.015593', 0, 0, NULL, 1),
	(3, 'twobercancan@gmail.com', '', 'twobercancan@gmail.com', 0, 0, '我的测试账号', '2019-06-03 16:00:00.000000', 'AgQB_G73xNSSzpVeGQ_tSUSEmrN2FaTxDryiQudF2gxXLuC2Ugp2ADAAAk1KReXFV78AwisAAAAA', 0, 0, 0, 1, '2019-06-04 08:20:02.559245', '2019-06-04 08:20:02.619872', 0, 0, NULL, 1),
	(4, 'wcadaydayup@gmail.com', '', 'wcadaydayup@gmail.com', 0, 0, '121313', '2019-05-31 16:00:00.000000', 'AjgtAa8EoSLMjLVynCwNQDyS8NflFaTxE1fD18NF2gxXLuC2UgqqwDAAAkqYRd3mmh2gvB0AAAAA', 0, 0, 0, 1, '2019-06-04 08:20:18.669652', '2019-06-04 08:20:18.723059', 0, 0, NULL, 1);

```

## 4. 测试店铺授权

```
https://tiptopfree.myshopify.com/admin/oauth/authorize?client_id=7fced15ff9d1a461f10979c3eae2eca8&scope=read_content,write_content,read_themes,write_themes,read_products,write_products,read_product_listings,read_customers,write_customers,read_orders,write_orders,read_shipping,write_draft_orders,read_inventory,write_inventory,read_shopify_payments_payouts,read_draft_orders,read_locations,read_script_tags,write_script_tags,read_fulfillments,write_shipping,read_analytics,read_checkouts,write_resource_feedbacks,write_checkouts,read_reports,write_reports,read_price_rules,write_price_rules,read_marketing_events,write_marketing_events,read_resource_feedbacks,read_shopify_payments_disputes,write_fulfillments&redirect_uri=https%3A//pinbooster.seamarketings.com/api/v1/auth/shopify/callback/&state=chicgostyle&grant_options[]=

Tiptopfree Shopify后台:登录网址：https://tiptopfree.myshopify.com/admin
登录邮箱：alicia.wang@orderplus.com
登录密码：%￥^&561

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