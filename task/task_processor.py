#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-05-11
# Function:
import os
import datetime
from io import BytesIO
import base64
import re
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from config import logger
from PIL import Image
import pymysql
import json
import requests
from sdk.pinterest.pinterest_api import PinterestApi
from sdk.shopify.get_shopify_products import ProductsApi


class DBUtil:
    def __init__(self, host="47.112.113.252", port=3306, db="sea", user="sea", password="sea@orderplus.com"):
        self.conn_pool = {}
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.pwd = password

    def get_instance(self):
        try:
            name = threading.current_thread().name
            if name not in self.conn_pool:
                conn = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    user=self.user,
                    password=self.pwd,
                    charset='utf8'
                )
                self.conn_pool[name] = conn
        except Exception as e:
            logger.exception("connect mysql error, e={}".format(e))
            return None
        return self.conn_pool[name]


class TaskProcessor:
    def __init__(self, rule_period=120, publish_pin_period=240, pinterest_period=600, shopify_period=600):
        self.bk_scheduler = BackgroundScheduler()
        self.bk_scheduler.start()
        self.pinterest_job = None
        self.shopify_job = None
        self.rule_job = None
        self.publish_pin_job = None
        self.pinterest_period = pinterest_period
        self.shopify_period = shopify_period
        self.rule_period = rule_period
        self.publish_pin_period = publish_pin_period

    def start(self):
        logger.info("TaskProcessor start work.")
        # 规则解析任务　
        self.analyze_rule()
        self.rule_job = self.bk_scheduler.add_job(self.analyze_rule, 'interval', seconds=self.rule_period, max_instances=50)

        # 定时发布pin
        # self.publish_pins(self.publish_pin_period)
        # self.publish_pin_job = self.bk_scheduler.add_job(self.publish_pins, 'interval', seconds=self.publish_pin_period, args=(self.publish_pin_period,))

        # 定时更新pinterest数据
        self.update_pinterest_data()
        self.pinterest_job = self.bk_scheduler.add_job(self.update_pinterest_data, 'interval', seconds=self.pinterest_period)

        # 定时更新shopify数据
        self.update_shopify_data()
        self.shopify_job = self.bk_scheduler.add_job(self.update_shopify_data, 'interval', seconds=self.shopify_period)


    def stop(self):
        logger.warning("TaskProcessor stop work.")
        self.bk_scheduler.remove_all_jobs()

    def pause(self):
        logger.info("TaskProcessor pause work.")
        if self.bk_scheduler.running:
            self.bk_scheduler.pause()

    def resume(self):
        logger.info("TaskProcessor resume.")
        self.bk_scheduler.resume()

    def update_pinterest_data(self):
        """
                拉取所有pinteres 正常账号下的所有board, 并增量式的插入数据库，有则更新，无则插入
                :return:
                """
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False

            # 拉取所有正常状态的账号
            authorized = 1
            account_state = 0
            cursor.execute('''
                    select id, token, account_uri from `pinterest_account` where state=%s and authorized=%s
                    ''', (account_state, authorized))
            accounts = cursor.fetchall()
            if not accounts:
                logger.info("accounts is empty!")
                return True

            # 拿到所有已经存在的board
            cursor.execute('''
                    select id, board_uri from `board` where id>=0''')
            exist_boards = cursor.fetchall()
            exist_boards_dict = {}
            if exist_boards:
                for exb in exist_boards:
                    exist_boards_dict[exb[1]] = exb[0]

            cursor.execute('''
                    select id, pin_uri from `pin` where id>=0''')
            exist_pins = cursor.fetchall()
            exist_pins_dict = {}
            if exist_pins:
                for exp in exist_pins:
                    exist_pins_dict[exp[1]] = exp[0]


            for account in accounts:
                account_id, token, account_uri = account
                if not token:
                    logger.warning("pinterest account token is None, account uri={}".format(account_uri))
                    continue

                p_api = PinterestApi(access_token=token)
                ret = p_api.get_user_info()
                if ret['code'] == 1:
                    account_info = ret.get("data", {})
                    if account_info:
                        time_now = datetime.datetime.now()
                        print(account_info)
                        user_name = account_info.get("username", "")
                        bio = account_info.get("bio", "")
                        account_type = account_info.get("account_type", "")
                        account_type = 0 if account_type == "individual" else 1
                        account_url = account_info.get("url", "")
                        created_at = account_info.get("created_at", "")
                        if created_at:
                            create_at = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S")
                        counts = account_info.get("counts", {})
                        pins = counts.get("pins", 0)
                        boards = counts.get("boards", 0)
                        account_followings = counts.get("following")
                        account_followers = counts.get("followers")
                        account_uuid = account_info.get("id", '')
                        cursor.execute('''update `pinterest_account` set nickname=%s, description=%s, type=%s, create_time=%s, boards=%s, pins=%s, followings=%s, followers=%s, uuid=%s, update_time=%s where id=%s''',
                                       (user_name, bio, account_type, create_at, boards, pins, account_followings, account_followers, account_uuid, time_now, account_id))
                        conn.commit()
                    else:
                        logger.warning("get pinterest account info empty! account={}, token={}".format(account_uri, token))
                else:
                    logger.error("get user info failed, account={}, token={}, ret={}".format(account_uri, token, ret))

                # 获取该账号下的所有board,并刷新数据库
                ret = p_api.get_user_boards()
                if ret["code"] == 1:
                    boards = ret["data"]
                    if boards:
                        time_now = datetime.datetime.now()

                        # 因为在测试过程发现user info中的boards数量与实际不符，所以在此再次更新一下boards数量
                        cursor.execute(
                            '''update `pinterest_account` set boards=%s update_time=%s where id=%s''', (len(boards), account_id))
                        conn.commit()

                        for board in boards:
                            uri = board.get("id", "")
                            name = board.get("name", "")
                            description = board.get("description", "")
                            state = 1 if board.get('privacy') == "public" else 0
                            create_time = datetime.datetime.strptime(board["created_at"], "%Y-%m-%dT%H:%M:%S")
                            add_time = time_now
                            update_time = time_now
                            url = board.get("url", "")

                            counts = board.get("counts", {})
                            board_pins = counts.get("pins", 0)
                            board_collaborators = counts.get("collaborators", 0)
                            board_followers = counts.get("followers", 0)
                            # 如果board　uri 已经存在，则进行更新即可
                            if uri in exist_boards_dict.keys():
                                board_id = exist_boards_dict[uri]
                                cursor.execute(
                                    '''update `board` set name=%s, description=%s, state=%s, update_time=%s, pins=%s, followers=%s, collaborators=%s''',
                                    (name, description, state, update_time, board_pins, board_followers,
                                     board_collaborators))
                            else:
                                cursor.execute('''insert into `board` (`board_uri`, `name`, `create_time`, `description`, `state`, 
                                `add_time`, `update_time`, `pinterest_account_id`, `url`, `pins`, `followers`, `collaborators`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ''',
                                               (uri, name, create_time, description, state, add_time, update_time,
                                                account_id, url, board_pins, board_followers, board_collaborators))
                                board_id = cursor.lastrowid

                            cursor.execute(
                                '''insert into `pinterest_history_data` (`board_uri`, `board_name`, `board_followers`, 
                                `board_id`, `pinterest_account_id`, `update_time`, `account_followings`, 
                                `account_followers`, `account_views`, `pin_likes`, `pin_comments`, `pin_saves`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                (uri, name, board_followers, board_id, account_id, time_now, 0, 0, 0, 0, 0, 0))

                        conn.commit()
                else:
                    logger.error(
                        "update boards get_user_boards error, account={} token={}, ret={}".format(account_uri, token,
                                                                                                  ret))

                # 获取该账号下的所有pins, 并刷新数据库
                ret = p_api.get_user_pins()
                if ret["code"] == 1:
                    pins = ret["data"]
                    if pins:
                        time_now = datetime.datetime.now()
                        for pin in pins:
                            uri = pin.get("id", "")
                            create_time = datetime.datetime.strptime(pin["created_at"], "%Y-%m-%dT%H:%M:%S")
                            update_time = time_now
                            url = pin.get("url", "")
                            media_type = pin.get("media", {}).get("type", 'image')
                            note = pin.get("note", "")
                            link = pin.get("link", "")
                            original_link = pin.get("original_link", "")
                            board_url = pin.get("board", {}).get("url", "")
                            board_uri = pin.get("board", {}).get("id", "")
                            board_name = pin.get("board", {}).get("name", "")

                            counts = pin.get("counts", {})
                            pin_saves = counts.get("saves", 0)
                            pin_comments = counts.get("comments", 0)

                            image = pin.get("image", {}).get("original", {})
                            image_path = image.get("url", "")
                            image_width, image_height = image.get("width", 200), image.get("height", 200)
                            metadata = pin.get("metadata", {})

                            pin_thumbnail = self.image_2_base64(image_path)
                            pin_likes = 0
                            pin_views = 0
                            pin_clicks = 0

                            # 如果pin　uri 已经存在，则进行更新即可
                            if uri in exist_pins_dict.keys():
                                # , saves = % s, comments = % s
                                pin_id = exist_pins_dict[uri]
                                cursor.execute(
                                    '''update `pin` set note=%s, update_time=%s, saves=%s, comments=%s, likes=%s''',
                                    (note, update_time, pin_saves, pin_comments, pin_likes))
                            else:
                                board_id = None
                                product_id = None
                                # 通过uri找到对应的board
                                cursor.execute("select id from `board` where board_uri=%s", board_uri)
                                board = cursor.fetchone()
                                if board:
                                    board_id = board[0]

                                # 通过pin背后的链接，找到他对应的产品
                                cursor.execute("select id from `product` where url=%s", original_link)
                                product = cursor.fetchone()
                                if product:
                                    product_id = product[0]

                                cursor.execute('''insert into `pin` (`pin_uri`, `url`, `note`, `origin_link`, 
                                    `thumbnail`, `publish_time`, `update_time`, `board_id`, `product_id`, `saves`, 
                                    `comments`, `likes`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ''',
                                               (uri, url, note, original_link, pin_thumbnail, create_time, update_time,
                                                board_id, product_id, pin_saves, pin_comments, pin_likes))
                                pin_id = cursor.lastrowid

                            # 先合入，因为下面的历史表中有外键关联
                            conn.commit()

                            # 　更新历史数据表
                            cursor.execute(
                                '''insert into `pinterest_history_data` (`pin_uri`, `pin_note`, `pin_thumbnail`, `pin_likes`, `pin_comments`, `pin_saves`, `pin_clicks`, `update_time`, `board_id`, `pin_id`, `pinterest_account_id`, `product_id`, `account_followings`, 
                                `account_followers`, `account_views`, `board_followers`, `board_uri`, `board_name`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                (uri, note, pin_thumbnail, pin_likes, pin_comments, pin_saves, pin_clicks,
                                 update_time, board_id, pin_id, account_id, product_id, ))

                            conn.commit()
                else:
                    logger.error(
                        "update pins get_user_pins error, account={} token={}, ret={}".format(account_uri, token, ret))
            return True
        except Exception as e:
            logger.exception("update_pinterest_data exception e={}".format(e))
            return False
        finally:
            cursor.close() if cursor else 0
            conn.close() if conn else 0

    def update_shopify_data(self):
        """
         获取所有店铺的所有products, 并保存至数据库
         :return:
         """
        logger.info("update_shopify_data is cheking...")
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False

            cursor.execute('''select id, name, url, token, user_id from `store` where id>=0''')
            stores = cursor.fetchall()

            # 取中已经存在的所有products, 只需更新即可
            cursor.execute('''select id, uuid from `product` where id>=0''')
            exist_products = cursor.fetchall()
            exist_products_dict = {}
            for exp in exist_products:
                exist_products_dict[exp[1]] = exp[0]

            # 遍历数据库中的所有store
            for store in stores:
                store_id, store_name, store_url, store_token, user_id = store
                if not all([store_url, store_token]):
                    logger.warning("store url or token is invalid, store id={}".format(store_id))
                    continue

                papi = ProductsApi(store_token, store_url)
                ret = papi.get_shop_info()
                if ret["code"] == 1:
                    shop = ret["data"].get("shop", {})
                    logger.info("shop info={}".format(shop))
                    shop_uuid = shop.get("id", "")
                    shop_name = shop.get("name", "")
                    shop_timezone = shop.get("timezone", "")
                    shop_domain = shop.get("domain", "")
                    shop_email = shop.get("email", "")
                    shop_owner = shop.get("shop_owner", "")
                    shop_country_name = shop.get("country_name", "")
                    created_at = shop.get("created_at", '')
                    updated_at = shop.get("updated_at", '')
                    shop_phone = shop.get("phone", "")
                    shop_city = shop.get("city", '')
                    # shop_myshopify_domain = shop.get("myshopify_domain", "")
                    cursor.execute('''update `store` set url=%s, uuid=%s, name=%s, timezone=%s, email=%s, owner_name=%s, 
                    owner_phone=%s, country=%s, city=%s, store_create_time=%s, store_update_time=%s where id=%s''',
                                   (shop_domain, shop_uuid, shop_name, shop_timezone, shop_email, shop_owner, shop_phone,
                                    shop_country_name, shop_city, datetime.datetime.strptime(created_at[0:-6], "%Y-%m-%dT%H:%M:%S"),
                                    datetime.datetime.strptime(updated_at[0:-6], "%Y-%m-%dT%H:%M:%S"), store_id))
                    conn.commit()

                # 获取店铺里的所有产品
                ret = papi.get_all_products()
                if ret["code"] == 1:
                    time_now = datetime.datetime.now()
                    products = ret["data"].get("products", [])
                    for pro in products:
                        pro_uri = str(pro.get("id", ""))
                        pro_title = pro.get("title", "")
                        pro_url = "https://{}/products/{}".format(store_url, pro_title)
                        pro_type = pro.get("product_type", "")
                        variants = pro.get("variants", [])
                        pro_sku = ""
                        pro_price = 0
                        if variants:
                            pro_sku = variants[0].get("sku", "")
                            pro_price = float(variants[0].get("price", "0"))

                        pro_tags = pro.get("tags", "")
                        if pro_uri in exist_products_dict.keys():
                            pro_id = exist_products_dict[pro_uri]
                            cursor.execute('''update `product` set url=%s, name=%s, price=%s, tag=%s, update_time=%s''',
                                           (pro_url, pro_title, pro_price, pro_tags, time_now))
                        else:
                            # pro_create_time = datetime.datetime.strptime(pro.get("created_at"), "%Y-%m-%dT%H:%M:%S")
                            pro_publish_time = datetime.datetime.strptime(pro.get("published_at", "")[0:-6], "%Y-%m-%dT%H:%M:%S")
                            pro_image = pro.get("image", {}).get("src", "")
                            thumbnail = self.image_2_base64(pro_image)
                            cursor.execute(
                                "insert into `product` (`sku`, `url`, `name`, `image_url`,`thumbnail`, `price`, `tag`, `create_time`, `update_time`, `store_id`, `publish_time`, `uuid`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (pro_sku, pro_url, pro_title, pro_image, thumbnail, pro_price, pro_tags, time_now,
                                 time_now, store_id, pro_publish_time, pro_uri))

                    conn.commit()
                    return True
        except Exception as e:
            logger.exception("get_products e={}".format(e))
            return False
        finally:
            cursor.close() if cursor else 0
            conn.close() if conn else 0

        return True

    def analyze_rule(self):
        """
        根据发布规则生成待发布记录
        :return:
        """
        logger.info("analyze_rule checking...")
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False

            # 取到所有新建未拆解的规则进行拆解
            cursor.execute('''
            select id,product_list,update_time,board_id,start_time,end_time from `rule` where state=%s
            ''', -1)
            rules = cursor.fetchall()
            if not rules:
                logger.info("there have no new rule to analyze.")
                return True

            analyzed_rule_ids = []
            for rule in rules:
                rule_id, product_list, update_time, board_id, rule_start_time, rule_end_time = rule
                analyzed_rule_ids.append(rule_id)
                product_list = eval(product_list)
                # 调整至零点
                rule_start_time = datetime.datetime.combine(rule_start_time, datetime.time.min)
                rule_end_time = datetime.datetime.combine(rule_end_time, datetime.time.max)

                cursor.execute('''
                        select weekday,start_time, end_time, interval_time from `rule_schedule` where rule_id=%s
                        ''', rule_id)
                schedules = cursor.fetchall()
                schedule_list = []
                for sch in schedules:
                    schedule_list.append({"weekday": sch[0], "beg": sch[1], "end": sch[2], "interval": sch[3]})

                execute_time_list = []
                while rule_start_time <= rule_end_time:
                    for schedule in schedule_list:
                        if rule_start_time.weekday() == schedule["weekday"]:
                            beg = rule_start_time + schedule["beg"]
                            end = rule_start_time + schedule["end"]
                            while beg <= end:
                                execute_time_list.append(beg)
                                beg += datetime.timedelta(seconds=int(schedule["interval"]))

                    rule_start_time += datetime.timedelta(days=1)

                time_now = datetime.datetime.now()
                for idx, exe_time in enumerate(execute_time_list):
                    # 如果发布时间小于当前时间, 不发布
                    if exe_time < time_now:
                        continue
                    product_id = product_list[idx % len(product_list)]
                    cursor.execute('''
                    insert into `publish_record` (`execute_time`, `board_id`, `product_id`, `rule_id`, `create_time`, `update_time`, `state`) values (%s, %s, %s, %s, %s, %s, %s)''',
                                   (exe_time, board_id, product_id, rule_id, time_now, time_now, 0))

                cursor.execute('''update `rule` set state=0, update_time=%s where id=%s and state=-1
                ''', (time_now, rule_id))
                conn.commit()

            logger.info("analyze rules succeed, rule ids={}".format(analyzed_rule_ids))
            return True
        except Exception as e:
            logger.exception("analyze_rule exception={}".format(e))
            return False
        finally:
            cursor.close() if cursor else 0
            conn.close() if conn else 0

    def get_records(self, execute_beg=None, execute_end=None, status=0):
        """
        获取执行时间在某一段时间内的发布记录, 数据来源PublishRecord表
        :param execute_beg: 执行时间范围起点, datetime类型
        :param execute_end: 执行时间范围终点, datetime类型
        :param status: 发布状态　0－－未发布，１－－已发布
        :return: list
        """
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False

            # 先拿到所有状态为status,执行时间在指定范围内的record
            if execute_beg and execute_end:
                cursor.execute('''
                        select id, execute_time, board_id, product_id, rule_id from `publish_record` where state=%s and execute_time between %s and %s''',
                               (status, execute_beg, execute_end))
            elif execute_beg:
                cursor.execute('''
                        select id, execute_time, board_id, product_id, rule_id from `publish_record` where state=%s and execute_time >= %s''',
                               (status, execute_beg))
            elif execute_end:
                cursor.execute('''
                        select id, execute_time, board_id, product_id, rule_id from `publish_record` where state=%s and execute_time <= %s''',
                               (status, execute_end))
            else:
                cursor.execute('''
                        select id, execute_time, board_id, product_id, rule_id from `publish_record` where state=%s''',
                               (status, execute_beg))

            records = cursor.fetchall()
            if not records:
                return []

            target_records = []
            # 遍历每一个record, 收集发布所需的所有参数
            for record in records:
                record_id, execute_time, board_id, product_id, rule_id = record

                # 取到待发布的pin所隶属的board信息
                cursor.execute('''
                        select board_uri, name, pinterest_account_id, state from `board` where id=%s
                        ''', board_id)
                board = cursor.fetchone()
                board_uri, board_name, pinterest_account_id, board_state = board

                # 取到待发布的pin所隶属的账号信息，　主要是token
                cursor.execute('''
                        select account_uri, state, token from `pinterest_account` where id=%s
                        ''', pinterest_account_id)
                account = cursor.fetchone()

                account_uri, account_state, token = account

                # 取到待发布的pin所关联的产品信息
                cursor.execute('''
                        select sku, url, name, image_url, price, tag from `product` where id=%s
                        ''', product_id)
                product = cursor.fetchone()
                sku, product_url, name, image_url, price, tag = product
                pending_record = {"id": record_id,
                                  "execute_time": execute_time,
                                  "board_id": board_id,
                                  "board_uri": board_uri,
                                  "board_state": board_state,
                                  "account_id": pinterest_account_id,
                                  "account_uri": account_uri,
                                  "account_state": account_state,
                                  "token": token,
                                  "product_id": product_id,
                                  "img_url": image_url,
                                  "note": name,
                                  "link": product_url}

                target_records.append(pending_record)
        except Exception as e:
            logger.exception("get_records exception e={}".format(e))
        finally:
            cursor.close() if cursor else 0
            conn.close() if conn else 0

        return target_records

    def publish_pins(self, period=240):
        logger.info("publish_pins_by_recodes checking")
        #获取最近period秒内的所有状态为0的(待发布的)record, 前后误差10秒
        records = self.get_records(0, datetime.datetime.now()-datetime.timedelta(seconds=period/2+10), datetime.datetime.now()+datetime.timedelta(seconds=period/2+10))
        if not records:
            logger.info("there have no record for publishing.")
            return True
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False
            utm_params = ""
            for record in records:
                pin_api = PinterestApi(access_token=record["token"])
                note = record["note"]
                link = record["link"] + utm_params
                board_id = record["board_id"]
                product_id = record["product_id"]
                ret = pin_api.create_pin(board_id=record["board_uri"], note=record["note"], image_url=record["img_url"], link=link)
                time_now = datetime.datetime.now()
                if ret["code"] == 1:
                    data = json.loads(ret[1])["data"]
                    pin_uri = data["id"]
                    url = data["url"]
                    # site_url = data["original_link"]
                    thumbnail = self.image_2_base64(record["img_url"])
                    cursor.execute('''insert into `pin` (`pin_uri`, `url`, `description`, `origin_link`, `thumbnail`, `publish_time`, `update_time`, `board_id`, `product_id`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (pin_uri, url, note, link, thumbnail, time_now, time_now, board_id, product_id))
                    pin_id = cursor.lastrowid

                    state = 1
                    remark = "success"
                    update_time = finished_time = time_now

                    cursor.execute('''
                            update `publish_record` set state=%s, remark=%s, finished_time=%s, pin_id=%s, update_time=%s where id=%s
                            ''', (state, remark, finished_time, pin_id, update_time, record["id"]))
                else:
                    # 发布失败
                    state = 2
                    remark = ret.get("msg", "")
                    update_time = finished_time = time_now
                    cursor.execute('''
                            update `publish_record` set state=%s, remark=%s, finished_time=%s, update_time=%s where id=%s
                            ''', (state, remark, finished_time, update_time, record["id"]))
                conn.commit()
        except Exception as e:
            logger.exception("publish_pins exception e={}".format(e))
            return False
        finally:
            cursor.close() if cursor else 0
            conn.close() if conn else 0

        return True

    def image_2_thumbnail(self, image_src, image_thumb, size=(100, 100)):
        if not os.path.exists(image_src):
            response = requests.get(image_src)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_src)

        image.thumbnail(size).save(image_thumb)
        return True

    def image_2_base64(self, image_src, is_thumb=True, size=(100, 100), format='png'):
        try:
            base64_str = ""
            if not os.path.exists(image_src):
                response = requests.get(image_src)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image_src)

            if is_thumb:
                image.thumbnail(size)

            output_buffer = BytesIO()
            image.save(output_buffer, format=format)
            byte_data = output_buffer.getvalue()
            base64_str = base64.b64encode(byte_data)
            base64_str = base64_str.decode("utf-8")
        except Exception as e:
            logger.error("image_2_base64 e={}".format(e))
        return base64_str

    def base64_2_image(self, base64_str, image_path):
        base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
        byte_data = base64.b64decode(base64_data)
        image_data = BytesIO(byte_data)
        img = Image.open(image_data)
        img.save(image_path)
        return True


def test_task_pro():
    tsp = TaskProcessor(pinterest_period=20, shopify_period=20, rule_period=10, publish_pin_period=50)
    # ret = tsp.analyze_rule()
    tsp.start()
    import time
    time.sleep(100)
    # tsp.pause()
    # time.sleep(20)
    tsp.resume()
    # time.sleep(20)
    tsp.stop()
    time.sleep(2)
    tsp.start()
    time.sleep(20)

    # pt.get_products()
    # st.update_products()
    # base64_str = pt.image_2_base64("https://www.theadultman.com/wp-content/uploads/2016/08/Things-Every-Man-Should-Own-1-1.jpg", is_thumb=False)
    # pt.base64_2_image(base64_str, "123.jpg")
    # pt.update_pinterest_data()

if __name__ == '__main__':
    test_task_pro()