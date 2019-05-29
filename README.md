# sea
自动化营销系统

## DB初始化
```
INSERT INTO `user` (`id`, `last_login`, `is_superuser`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `username`, `email`, `password`, `site_name`, `site_url`, `link`, `code`, `create_time`, `update_time`)
VALUES
	(1, NULL, 0, '', '', 0, 1, '2019-06-01 00:00:00.852191', 'admin', 'victor.fang@orderplus.com', 'pbkdf2_sha256$120000$M0cY6Z6wcYr9$iwqYBe/MJfOLkpx2/2mMWtt2f1X7GBSt7D0EKRdjdV8=', NULL, NULL, NULL, NULL, '2019-06-01 00:00:00.899300', '2019-06-01 00:00:00.744339');


INSERT INTO `platform` (`id`, `name`, `url`, `update_time`, `create_time`)
VALUES
	(1, 'Shopify', NULL, '2019-06-01 00:00:00.852191', '2019-06-01 00:00:00.852191'),
	(2, 'Cloud', NULL, '2019-06-01 00:00:00.852191', '2019-06-01 00:00:00.852191'),
	(3, 'Individual', NULL, '2019-06-01 00:00:00.852191', '2019-06-01 00:00:00.852191');



```

## 服务启动

```
yum install supervisor
systemctl enable supervisord
systemctl start supervisord
systemctl stop supervisord
systemctl restart supervisord
```