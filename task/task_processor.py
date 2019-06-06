#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-05-11
# Function:
import os, sys
import time
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
from sdk.googleanalytics.google_oauth_info import GoogleApi
from config import SHOPIFY_CONFIG


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
    def __init__(self, ):
        self.bk_scheduler = BackgroundScheduler()
        self.bk_scheduler.start()
        self.pinterest_job = None
        self.shopify_job = None
        self.rule_job = None
        self.publish_pin_job = None

    def start_job_analyze_rule_job(self, interval=120):
        # 规则解析任务　
        logger.info("start_job_analyze_rule_job")
        self.analyze_rule()
        self.rule_job = self.bk_scheduler.add_job(self.analyze_rule, 'interval', seconds=interval, max_instances=50)

    def start_job_update_pinterest_data(self, interval=7200):
        # 定时更新pinterest数据
        logger.info("start_job_update_pinterest_data")
        self.update_pinterest_data()
        self.pinterest_job = self.bk_scheduler.add_job(self.update_pinterest_data, 'interval', seconds=interval)

    def start_job_publish_pin_job(self, interval=240):
        # # 定时发布pin
        logger.info("start_job_publish_pin_job")
        self.publish_pins(interval)
        self.publish_pin_job = self.bk_scheduler.add_job(self.publish_pins, 'interval', seconds=interval, args=(interval,))

    def start_job_update_shopify_data(self, interval=7200):
        # 定时更新shopify数据
        logger.info("start_job_update_shopify_data")
        self.update_shopify_data()
        self.shopify_job = self.bk_scheduler.add_job(self.update_shopify_data, 'interval', seconds=interval)

    def start_all(self, rule_interval=120, publish_pin_interval=240, pinterest_update_interval=3800, shopify_update_interval=3800):
        logger.info("TaskProcessor start all work.")
        # self.start_job_analyze_rule_job(rule_interval)
        # self.start_job_publish_pin_job(publish_pin_interval)
        # self.start_job_update_pinterest_data(pinterest_update_interval)
        self.start_job_update_shopify_data(shopify_update_interval)

    def stop_all(self):
        logger.warning("TaskProcessor stop_all work.")
        self.bk_scheduler.remove_all_jobs()

    def pause(self):
        logger.info("TaskProcessor pause work.")
        if self.bk_scheduler.running:
            self.bk_scheduler.pause()

    def resume(self):
        logger.info("TaskProcessor resume.")
        self.bk_scheduler.resume()

    def update_pinterest_data(self, specific_account_id=-1):
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
            if specific_account_id >= 0:
                cursor.execute('''
                        select id, token, account, nickname from `pinterest_account` where id=%s''', (specific_account_id))
                accounts = cursor.fetchall()
                if not accounts:
                    logger.info("accounts is empty!")
                    return False
            else:
                authorized = 1
                account_state = 0
                cursor.execute('''
                        select id, token, account, nickname from `pinterest_account` where state=%s and authorized=%s
                        ''', (account_state, authorized))
                accounts = cursor.fetchall()
                if not accounts:
                    logger.info("accounts is empty!")
                    return True

            # 拿到所有已经存在的board
            cursor.execute('''
                    select id, uuid, pinterest_account_id from `board` where id>=0''')
            exist_boards = cursor.fetchall()
            exist_boards_dict = {}
            if exist_boards:
                for exb in exist_boards:
                    exist_boards_dict[exb[1]] = "{}/{}".format(exb[0], exb[2])

            cursor.execute('''
                    select id, uuid, board_id from `pin` where id>=0''')
            exist_pins = cursor.fetchall()
            exist_pins_dict = {}
            if exist_pins:
                for exp in exist_pins:
                    exist_pins_dict[exp[1]] = "{}/{}".format(exp[0], exp[2])

            for account in accounts:
                account_id, token, account_uuid, nickname = account
                if not token:
                    logger.warning("pinterest account token is None, account={}".format(account_uuid))
                    if specific_account_id > 0:
                        return False
                    continue

                logger.info("start update pinterest account={} infomations".format(account_uuid))
                p_api = PinterestApi(access_token=token)
                ret = p_api.get_user_info()
                if ret['code'] == 1:
                    account_info = ret.get("data", {})
                    if account_info:
                        time_now = datetime.datetime.now()
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
                        img_url = account_info.get("image", {}).get("60x60", {}).get("url", "")
                        account_thumbnail = ""
                        if img_url:
                            account_thumbnail = self.image_2_base64(img_url, is_thumb=True, size=(60, 60))
                        cursor.execute('''update `pinterest_account` set nickname=%s, description=%s, type=%s, create_time=%s, boards=%s, pins=%s, followings=%s, followers=%s, uuid=%s, update_time=%s, thumbnail=%s where id=%s''',
                                       (user_name, bio, account_type, create_at, boards, pins, account_followings, account_followers, account_uuid, time_now, account_thumbnail, account_id))
                        conn.commit()
                    else:
                        logger.warning("get pinterest account info empty! account={}, token={}".format(account_uuid, token))
                else:
                    logger.error("get user info failed, account={}, token={}, ret={}".format(account_uuid, token, ret))
                    # 如果是授权失败，后面的不用执行了
                    err_msg = ret.get("msg", "")
                    if "Authentication failed" in err_msg or 'Authorization failed.' in err_msg:
                        logger.error("get user info failed, because {}".format(err_msg))
                        if specific_account_id > 0:
                            return False
                        continue

                # 获取该账号下的所有board,并刷新数据库
                ret = p_api.get_user_boards()
                if ret["code"] == 1:
                    boards = ret["data"]
                    if boards:
                        time_now = datetime.datetime.now()

                        # 因为在测试过程发现user info中的boards数量与实际不符，所以在此再次更新一下boards数量
                        cursor.execute(
                            '''update `pinterest_account` set boards=%s, update_time=%s where id=%s''', (len(boards), time_now, account_id))
                        conn.commit()

                        for board in boards:
                            uuid = board.get("id", "")
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
                            # 如果board　uuid 已经存在，且属于同一个账号，　则进行更新即可
                            if uuid in exist_boards_dict.keys() and account_id == int(exist_boards_dict[uuid].split("/")[1]):
                                board_id = int(exist_boards_dict[uuid].split("/")[0])
                                cursor.execute(
                                    '''update `board` set name=%s, description=%s, state=%s, update_time=%s, pins=%s, followers=%s, collaborators=%s where id=%s''',
                                    (name, description, state, update_time, board_pins, board_followers,
                                     board_collaborators, board_id))
                            else:
                                cursor.execute('''insert into `board` (`uuid`, `name`, `create_time`, `description`, `state`, 
                                `add_time`, `update_time`, `pinterest_account_id`, `url`, `pins`, `followers`, `collaborators`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ''',
                                               (uuid, name, create_time, description, state, add_time, update_time,
                                                account_id, url, board_pins, board_followers, board_collaborators))
                                board_id = cursor.lastrowid
                            conn.commit()

                            cursor.execute(
                                '''insert into `pinterest_history_data` (`board_uuid`, `board_name`, `board_followers`, 
                                `board_id`, `pinterest_account_id`, `update_time`, `account_followings`, 
                                `account_followers`, `account_views`, `pin_likes`, `pin_comments`, `pin_saves`, `account_name`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                (uuid, name, board_followers, board_id, account_id, time_now, 0, 0, 0, 0, 0, 0, nickname))

                            conn.commit()
                else:
                    logger.error(
                        "update boards get_user_boards error, account={} token={}, ret={}".format(account_uuid, token,
                                                                                                  ret))

                # 获取该账号下的所有pins, 并刷新数据库
                ret = p_api.get_user_pins()
                if ret["code"] == 1:
                    pins = ret["data"]
                    if pins:
                        time_now = datetime.datetime.now()
                        cursor.execute(
                            '''update `pinterest_account` set pins=%s, update_time=%s where id=%s''', (len(pins), time_now, account_id))
                        conn.commit()
                        pin_uuids = []
                        for pin in pins:
                            uuid = pin.get("id", "")
                            create_time = datetime.datetime.strptime(pin["created_at"], "%Y-%m-%dT%H:%M:%S")
                            update_time = time_now
                            url = pin.get("url", "")
                            media_type = pin.get("media", {}).get("type", 'image')
                            note = pin.get("note", "")
                            link = pin.get("link", "")
                            original_link = pin.get("original_link", "")
                            board_url = pin.get("board", {}).get("url", "")
                            board_uuid = pin.get("board", {}).get("id", "")
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

                            # 如果pin　uuid 已经存在,且属于同一个board，则进行更新即可
                            if uuid in exist_pins_dict.keys() and board_id == int(exist_pins_dict[uuid].split("/")[1]):
                                # , saves = % s, comments = % s
                                pin_id = int(exist_pins_dict[uuid].split("/")[0])
                                cursor.execute(
                                    '''update `pin` set note=%s, update_time=%s, saves=%s, comments=%s, likes=%s where id=%s''',
                                    (note, update_time, pin_saves, pin_comments, pin_likes, pin_id))
                                conn.commit()
                            else:
                                if uuid in pin_uuids:
                                    # 测试发现，pinterest可能会给出重复数据,如果这一把已经更新过，则不再更新
                                    continue

                                board_id = None
                                product_id = None
                                # 通过uuid找到对应的board
                                cursor.execute("select id from `board` where uuid=%s", board_uuid)
                                board = cursor.fetchone()
                                if board:
                                    board_id = board[0]

                                # 通过pin背后的链接，找到他对应的产品
                                cursor.execute("select id from `product` where url_with_utm=%s", original_link)
                                product = cursor.fetchone()
                                product_id = -1
                                if product:
                                    product_id = product[0]

                                if product_id >= 0:
                                    cursor.execute('''insert into `pin` (`uuid`, `url`, `note`, `origin_link`, 
                                        `thumbnail`, `publish_time`, `update_time`, `board_id`, `product_id`, `saves`, 
                                        `comments`, `likes`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ''',
                                                   (uuid, url, note, original_link, pin_thumbnail, create_time, update_time,
                                                    board_id, product_id, pin_saves, pin_comments, pin_likes))
                                else:
                                    cursor.execute('''insert into `pin` (`uuid`, `url`, `note`, `origin_link`, 
                                        `thumbnail`, `publish_time`, `update_time`, `board_id`, `saves`, 
                                        `comments`, `likes`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ''',
                                                   (uuid, url, note, original_link, pin_thumbnail, create_time, update_time,
                                                    board_id, pin_saves, pin_comments, pin_likes))
                                pin_id = cursor.lastrowid

                                # 先合入，因为下面的历史表中有外键关联
                                conn.commit()
                                pin_uuids.append(uuid)

                                # 　更新历史数据表
                                if product_id >= 0:
                                    cursor.execute(
                                        '''insert into `pinterest_history_data` (`pin_uuid`, `pin_note`, `pin_thumbnail`, 
                                        `pin_likes`, `pin_comments`, `pin_saves`, `update_time`, `board_id`, 
                                        `pin_id`, `pinterest_account_id`, `product_id`, `account_followings`, 
                                        `account_followers`, `account_views`, `board_followers`, `board_uuid`, `board_name`) 
                                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                        (uuid, note, pin_thumbnail, pin_likes, pin_comments, pin_saves,
                                         update_time, board_id, pin_id, account_id, product_id, 0, 0, 0, 0, "", ""))
                                else:
                                    cursor.execute(
                                        '''insert into `pinterest_history_data` (`pin_uuid`, `pin_note`, `pin_thumbnail`, 
                                        `pin_likes`, `pin_comments`, `pin_saves`, `update_time`, `board_id`, 
                                        `pin_id`, `pinterest_account_id`, `account_followings`, 
                                        `account_followers`, `account_views`, `board_followers`, `board_uuid`, `board_name`) 
                                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                        (uuid, note, pin_thumbnail, pin_likes, pin_comments, pin_saves,
                                         update_time, board_id, pin_id, account_id, 0, 0, 0, 0, "", ""))

                                conn.commit()
                else:
                    logger.error(
                        "update pins get_user_pins error, account={} token={}, ret={}".format(account_uuid, token, ret))
            return True
        except Exception as e:
            logger.exception("update_pinterest_data exception e={}".format(e))
            return False
        finally:
            cursor.close() if cursor else 0
            conn.close() if conn else 0

    def update_shopify_data(self, specific_sotre_uri=""):
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

            if specific_sotre_uri:
                cursor.execute('''select id, name, url, token, user_id, store_view_id from `store` where url=%s''', (specific_sotre_uri,))
            else:
                cursor.execute('''select id, name, url, token, user_id, store_view_id from `store` where id>=0''')
            stores = cursor.fetchall()

            # 取中已经存在的所有products, 只需更新即可
            cursor.execute('''select id, uuid from `product` where id>=0''')
            exist_products = cursor.fetchall()
            exist_products_dict = {}
            for exp in exist_products:
                exist_products_dict[exp[1]] = exp[0]

            # 遍历数据库中的所有store
            for store in stores:
                store_id, store_name, store_url, store_token, user_id, store_view_id = store
                if not all([store_url, store_token]):
                    logger.warning("store url or token is invalid, store id={}".format(store_id))
                    continue

                # 更新店铺信息
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
                    shop_currency = shop.get("currency", "USD")
                    # shop_myshopify_domain = shop.get("myshopify_domain", "")
                    cursor.execute('''update `store` set url=%s, uuid=%s, name=%s, timezone=%s, email=%s, owner_name=%s, 
                    owner_phone=%s, country=%s, city=%s, store_create_time=%s, store_update_time=%s, currency=%s where id=%s''',
                                   (shop_domain, shop_uuid, shop_name, shop_timezone, shop_email, shop_owner, shop_phone,
                                    shop_country_name, shop_city, datetime.datetime.strptime(created_at[0:-6], "%Y-%m-%dT%H:%M:%S"),
                                    datetime.datetime.strptime(updated_at[0:-6], "%Y-%m-%dT%H:%M:%S"), shop_currency, store_id))
                    conn.commit()
                else:
                    logger.warning("get shop info failed. ret={}".format(ret))

                # 获取店铺里的所有产品
                #
                gapi = GoogleApi(view_id=store_view_id, ga_source=SHOPIFY_CONFIG.get("utm_source", "pinbooster"), json_path=os.path.join(os.path.dirname(sys.path[0]), "sdk//googleanalytics//client_secrets.json"))
                # 拿到所有的ga数据
                reports = gapi.get_report(key_word="", start_time="1daysAgo", end_time="today")
                ret = papi.get_all_products()
                if ret["code"] == 1:
                    time_now = datetime.datetime.now()
                    products = ret["data"].get("products", [])
                    for pro in products:
                        pro_uuid = str(pro.get("id", ""))
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
                        if pro_uuid in exist_products_dict.keys():
                            pro_id = exist_products_dict[pro_uuid]
                            cursor.execute('''update `product` set url=%s, name=%s, price=%s, tag=%s, update_time=%s where id=%s''',
                                           (pro_url, pro_title, pro_price, pro_tags, time_now, pro_id))
                        else:
                            # pro_create_time = datetime.datetime.strptime(pro.get("created_at"), "%Y-%m-%dT%H:%M:%S")
                            pro_publish_time = datetime.datetime.strptime(pro.get("published_at", "")[0:-6], "%Y-%m-%dT%H:%M:%S")
                            pro_image = pro.get("image", {}).get("src", "")
                            thumbnail = self.image_2_base64(pro_image)
                            cursor.execute(
                                "insert into `product` (`sku`, `url`, `name`, `image_url`,`thumbnail`, `price`, `tag`, `create_time`, `update_time`, `store_id`, `publish_time`, `uuid`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (pro_sku, pro_url, pro_title, pro_image, thumbnail, pro_price, pro_tags, time_now,
                                 time_now, store_id, pro_publish_time, pro_uuid))
                            pro_id = cursor.lastrowid

                        conn.commit()
                        if not store_view_id:
                            logger.warning("this product have no store view id, product id={}, store id={}".format(pro_id, store_id))
                            continue

                        # pro_uuid = "google" # 测试
                        # ga_data = gapi.get_report(key_word=pro_uuid, start_time="1daysAgo", end_time="today")
                        time_now = datetime.datetime.now()
                        if reports.get("code", 0) == 1:
                            data = reports.get("data", {})
                            pro_report = data.get(pro_uuid, {})
                            pv = int(pro_report.get("page_view", 0))
                            uv = int(pro_report.get("unique_view", 0))
                            hits = int(pro_report.get("hits", 0))
                            transactions = int(pro_report.get("transactions", 0))
                            transactions_revenue = float(pro_report.get("transaction_revenue", 0))
                            cursor.execute('''insert into `product_history_data` (`product_visitors`, `product_new_visitors`, `product_clicks`, `product_scan`, `product_sales`, `product_revenue`, `update_time`, `product_id`, `store_id`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ''', (uv, uv, hits, pv, transactions, transactions_revenue, time_now, pro_id, store_id))
                        else:
                            logger.warning("get GA data failed, store view id={}, key_words={}".format(store_view_id, pro_uuid))

                        conn.commit()
                    return True
                else:
                    logger.warning("get shop products failed. ret={}".format(ret))

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
                                limit_interval = int(schedule["interval"])
                                limit_interval = 1800 if limit_interval<1800 else limit_interval
                                beg += datetime.timedelta(seconds=limit_interval)

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
                    conn.commit()

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

    def get_records(self,  status=0, execute_beg=None, execute_end=None):
        """
        获取执行时间在某一段时间内的发布记录, 数据来源PublishRecord表
        :param execute_beg: 执行时间范围起点, datetime类型
        :param execute_end: 执行时间范围终点, datetime类型
        :param status: 发布状态　record ((0, '待发布'), (1, '已发布'), (2, '暂停中'), (3, '发布失败'), (4, "已取消"), (5, "已删除"))
        :return: list
        """
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False

            # 先拿到所有状态为status, 执行时间在指定范围内的record
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
                               (status, ))

            records = cursor.fetchall()
            if not records:
                return []

            target_records = []
            # 遍历每一个record, 收集发布所需的所有参数
            for record in records:
                record_id, execute_time, board_id, product_id, rule_id = record

                # 取到待发布的pin所隶属的board信息
                cursor.execute('''
                        select uuid, name, pinterest_account_id, state from `board` where id=%s
                        ''', board_id)
                board = cursor.fetchone()
                board_uuid, board_name, pinterest_account_id, board_state = board

                # 取到待发布的pin所隶属的账号信息，　主要是token
                cursor.execute('''
                        select account, state, token from `pinterest_account` where id=%s
                        ''', pinterest_account_id)
                account = cursor.fetchone()

                account, account_state, token = account

                # 取到待发布的pin所关联的产品信息
                cursor.execute('''
                        select sku, url, name, image_url, price, tag, uuid from `product` where id=%s
                        ''', product_id)
                product = cursor.fetchone()
                sku, product_url, name, image_url, price, tag, product_uuid = product
                pending_record = {"id": record_id,
                                  "execute_time": execute_time,
                                  "board_id": board_id,
                                  "board_uuid": board_uuid,
                                  "board_name": board_name,
                                  "board_state": board_state,
                                  "account_id": pinterest_account_id,
                                  "account": account,
                                  "account_state": account_state,
                                  "token": token,
                                  "product_id": product_id,
                                  "product_uuid": product_uuid,
                                  "product_link": product_url,
                                  "product_img_url": image_url,
                                  "product_name": name,
                                  "product_sku": sku,
                                  "rule_id": rule_id}

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
        records = self.get_records(0, datetime.datetime.now()-datetime.timedelta(seconds=int(period/2+10)), datetime.datetime.now()+datetime.timedelta(seconds=int(period/2+10)))
        if not records:
            logger.info("there have no record for publishing.")
            return True
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False

            for record in records:
                pin_api = PinterestApi(access_token=record["token"])
                rule_id = record["rule_id"]
                product_name = record["product_name"]
                utm_format = SHOPIFY_CONFIG.get("utm_format", "")
                url_suffix = utm_format.format(pinterest_account=record["account"], board_name=record["board_name"], product_id=record["product_uuid"])
                link_with_utm = record["product_link"] + url_suffix
                board_id = record["board_id"]
                product_id = record["product_id"]
                logger.info("publish pin board name={}, product name={}".format(record["board_name"], product_name))
                ret = pin_api.create_pin(board_id=record["board_uuid"], note=product_name, image_url=record["product_img_url"], link=link_with_utm)
                time_now = datetime.datetime.now()
                if ret["code"] == 1:
                    data = json.loads(ret[1])["data"]
                    pin_uuid = data["id"]
                    url = data["url"]
                    # site_url = data["original_link"]
                    thumbnail = self.image_2_base64(record["img_url"])
                    cursor.execute('''insert into `pin` (`uuid`, `url`, `description`, `origin_link`, `thumbnail`, `publish_time`, `update_time`, `board_id`, `product_id`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (pin_uuid, url, product_name, link_with_utm, thumbnail, time_now, time_now, board_id, product_id))
                    pin_id = cursor.lastrowid
                    conn.commit()
                    # rule (-1, '新建'), (0, '待执行'), (1, '运行中'), (2, '暂停中'), (3, '已完成'), (4, '已过期'), (5, '已删除')
                    # record ((0, '待发布'), (1, '已发布'), (2, '暂停中'), (3, '发布失败'), (4, "已取消"), (5, "已删除"))
                    record_state = 1
                    remark = "success"
                    update_time = finished_time = time_now

                    # 发布成功后，更新record表
                    cursor.execute(
                        '''update `publish_record` set state=%s, remark=%s, finished_time=%s, pin_id=%s, update_time=%s where id=%s''',
                        (record_state, remark, finished_time, pin_id, update_time, record["id"]))
                    conn.commit()
                    # 将格式化后的url更新到产品数库表中
                    cursor.execute('''update `product` set url_with_utm=%s where id=%s''', (link_with_utm, product_id))
                    conn.commit()

                else:
                    # 发布失败
                    record_state = 3
                    remark = ret.get("msg", "")
                    update_time = finished_time = time_now
                    cursor.execute('''
                            update `publish_record` set state=%s, remark=%s, finished_time=%s, update_time=%s where id=%s
                            ''', (record_state, remark, finished_time, update_time, record["id"]))
                    conn.commit()

                # 再更新rule表,如果rule还是待运行状态(0)，则修改为正在运行状态(1)
                rule_state = 1
                cursor.execute('''update `rule` set state=%s, update_time=%s where id=%s and state=0''', (rule_state, update_time, rule_id))
                conn.commit()

                # 如果某一个规则下的所有record都已经发布完毕（无论是否全部成功）或被人为取消或删除，　而且该rule目前是运行中状态，则将该rule更新为已完成状（3）
                cursor.execute('''select rule_id from `publish_record` where (state=0 or state=2) and rule_id=%s''', (rule_id, ))
                rule_pending_records = cursor.fetchall()
                if not rule_pending_records:
                    # 如果当前rule处理运行状态，但是它的所有record中没有待执行和暂停中的，那代表这个rule已经被完成了
                    cursor.execute('''update `rule` set state=%s, update_time=%s where id=%s and state=1''', (rule_state, update_time, rule_id))
                    conn.commit()
        except Exception as e:
            logger.exception("publish_pins exception e={}".format(e))
            return False
        finally:
            cursor.close() if cursor else 0
            conn.close() if conn else 0

        return True

    def image_2_thumbnail(self, image_src, image_thumb, size=(70, 70)):
        if not os.path.exists(image_src):
            response = requests.get(image_src)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_src)

        image.thumbnail(size).save(image_thumb)
        return True

    def image_2_base64(self, image_src, is_thumb=True, size=(70, 70), format='png'):
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
            if "jp" in image_src[-4:]:
                format = "JPEG"
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


def test():
    tsp = TaskProcessor()
    # thu = tsp.image_2_base64(image_src="https://i.pinimg.com/60x60_RS/df/5c/53/df5c53facea5fd63d5796334b43f036d.jpg", format="jpeg")

    tsp.start_all(rule_interval=60, publish_pin_interval=120, pinterest_update_interval=3800, shopify_update_interval=3800)

    while 1:
        time.sleep(1)


def main():
    tsp = TaskProcessor()
    tsp.start_all(rule_interval=120, publish_pin_interval=240, pinterest_update_interval=3800, shopify_update_interval=3800)
    while 1:
        time.sleep(1)


if __name__ == '__main__':
    # test()
    main()