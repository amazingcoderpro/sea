#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-05-11
# Function:
import datetime
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from config import logger
# from sea_app.models import PublishRecord, Pin, Board, PinterestAccount
from PIL import Image
import pymysql
import json
import requests
from io import BytesIO
import base64
import re
from sdk.pinterest.pinterest_api import PinterestApi
import os

class DBUtil:
    def __init__(self, host="47.112.113.252", port=3306, db="sea", user="sea", password="sea@orderplus.com"):
        self.conn_pool = {}
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.pwd = password

    def get_instance(self):
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

        return self.conn_pool[name]


class PinterestOpt:

    def image_2_thumbnail(self, image_src, image_thumb, size=(100, 100)):
        if not os.path.exists(image_src):
            response = requests.get(image_src)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_src)

        image.thumbnail(size).save(image_thumb)
        return True

    def image_2_base64(self, image_src, is_thumb=True, size=(100, 100), format='png'):
        if not os.path.exists(image_src):
            response = requests.get(image_src)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_src)

        if is_thumb:
            image.thumbnail(size)

        output_buffer = BytesIO()
        image.save(output_buffer, format='png')
        byte_data = output_buffer.getvalue()
        base64_str = base64.b64encode(byte_data)
        base64_str = base64_str.decode("utf-8")
        return base64_str

    def base64_2_image(self, base64_str, image_path):
        base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
        byte_data = base64.b64decode(base64_data)
        image_data = BytesIO(byte_data)
        img = Image.open(image_data)
        img.save(image_path)
        return True

    def get_pending_records(self, status=0):
        """
        获取所有待发布的pins记录, 数据来源PublishRecord表
        :param status: 发布状态　0－－未发布，１－－已发布
        :return: list
        """
        con = DBUtil().get_instance()
        cursor = con.cursor()

        # 先拿到所有状态为0的record
        cursor.execute('''
                select id, execute_time, board_id, product_id, rule_id from `publish_record` where state=%s and execute_time between %s and %s
                ''', (status, datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(seconds=3000)))
        records = cursor.fetchall()

        pending_records = []
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

            pending_records.append(pending_record)

        return pending_records

    def create_pins(self, records):
        con = DBUtil().get_instance()
        cursor = con.cursor()
        utm_params = ""
        for record in records:
            #"ArVPxolYdQAXgzr0-FFoRGAF682xFaDsz-o3I1FF0n-lswCyYAp2ADAAAk1KRdOSuUEgxv0AAAAA"
            pin_api = PinterestApi(access_token=record["token"])
            # image_url = "https://img-blog.csdn.net/20180509111334917"
            # # "753790125070471656"

            note = record["note"]
            link = record["link"] + utm_params
            board_id = record["board_id"]
            product_id = record["product_id"]
            ret = pin_api.create_pin(board_id=record["board_uri"], note=record["note"], image_url=record["img_url"], link=link)
            print(ret)

            if ret[0] in [200, 201]:
                data = json.loads(ret[1])["data"]
                pin_uri = data["id"]
                url = data["url"]
                # site_url = data["original_link"]
                thumbnail = self.image_2_base64(record["img_url"])
                time_now = datetime.datetime.now()
                cursor.execute('''insert into `pin` (`pin_uri`, `url`, `description`, `origin_link`, `thumbnail`, `publish_time`, `update_time`, `board_id`, `product_id`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (pin_uri, url, note, link, thumbnail, time_now, time_now, board_id, product_id))
                pin_id = cursor.lastrowid

                state = 1
                remark = ""
                update_time = finished_time = time_now

                cursor.execute('''
                        update `publish_record` set state=%s, remark=%s, finished_time=%s, pin_id=%s, update_time=%s where id=%s
                        ''', (state, remark, finished_time, pin_id, update_time, record["id"]))

                con.commit()



    """
    {"data": {"attribution": null, "creator": {"url": "https://www.pinterest.com/hellomengxiaoning/", "first_name": "meng", "last_name": "xiaoning", "id": "753790193789717834"}, "url": "https://www.pinterest.com/pin/753790056365083517/", "media": {"type": "image"}, "created_at": "2019-05-22T06:24:00", "original_link": "http://www.baidu.com/", "note": "123", "color": null, "link": "https://www.pinterest.com/r/pin/753790056365083517/5031224083375764064/7e49259acd505d1254fb158b65c676e47f492703bd27058c24dcbf999d6c5930", "board": {"url": "https://www.pinterest.com/hellomengxiaoning/xiaoning/", "id": "753790125070471656", "name": "xiaoning"}, "image": {"original": {"url": "https://i.pinimg.com/originals/98/ea/d8/98ead8f36c30abff7cfe53c56ec7a55a.jpg", "width": 0, "height": 0}}, "counts": {"saves": 0, "comments": 0}, "id": "753790056365083517", "metadata": {}}}
    """
    def produce_records_by_rule(self):
        """
        根据发布规则生成待发布数据
        :return:
        """
        con = DBUtil().get_instance()
        cursor = con.cursor()
        cursor.execute('''
        select id,product_list,update_time,board_id,start_time,end_time from `rule` where update_time>%s
        ''', datetime.datetime.now()-datetime.timedelta(days=100))
        rules = cursor.fetchall()

        for rule in rules:
            rule_id, product_list, update_time, board_id, rule_start_time, rule_end_time = rule
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
            while rule_start_time < rule_end_time:
                for schedule in schedule_list:
                    if rule_start_time.weekday() == schedule["weekday"]:
                        beg = rule_start_time + schedule["beg"]
                        end = rule_start_time + schedule["end"]
                        while beg < end:
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
                insert into `publish_record` (`execute_time`, `board_id`, `product_id`, `rule_id`, `create_time`, `update_time`, `state`) values (%s, %s, %s, %s, %s, %s, %s)''', (exe_time, board_id, product_id, rule_id, time_now, time_now, 0))
            con.commit()

    def update_pins(self):
        pass

    def update_boards(self, account_state=0):
        """
        拉取所有pinteres 正常账号下的所有board, 并增量式的插入数据库，有则更新，无则插入
        :return:
        """

        # 拉取所有账号
        con = DBUtil().get_instance()
        cursor = con.cursor()
        cursor.execute('''
        select id, token from `pinterest_account` where state=%s
        ''', account_state)
        accounts = cursor.fetchall()

        # 拿到所有已经存在的board
        cursor.execute('''
        select id, board_uri from `board` where id>=0''')
        exist_boards = cursor.fetchall()
        exist_boards_dict = {}
        for exb in exist_boards:
            exist_boards_dict[exb[1]] = exb[0]

        cursor.execute('''
        select id, pin_uri from `pin` where id>=0''')
        exist_pins = cursor.fetchall()
        exist_pins_dict = {}
        for exp in exist_pins:
            exist_pins_dict[exp[1]] = exp[0]

        for account in accounts:
            account_id, token = account
            if not token:
                logger.warning("pinterest account token is None")
                continue

            p_api = PinterestApi(access_token=token)
            ret = p_api.get_user_boards()

            if ret["code"] == 1:
                boards = ret["data"]
                print(boards)
                if boards:
                    time_now = datetime.datetime.now()
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
                            cursor.execute('''update `board` set name=%s, description=%s, state=%s, update_time=%s, pins=%s, followers=%s, collaborators=%s''',
                                           (name, description, state, update_time, board_pins, board_followers, board_collaborators))
                        else:
                            cursor.execute('''insert into `board` (`board_uri`, `name`, `create_time`, `description`, `state`, 
                    `add_time`, `update_time`, `pinterest_account_id`, `url`, `pins`, `followers`, `collaborators`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ''',
                                           (uri, name, create_time, description, state, add_time, update_time, account_id, url, board_pins, board_followers, board_collaborators))
                            board_id = cursor.lastrowid

                        cursor.execute('''insert into `pinterest_history_data`　
                        (`board_uri`, `board_name`, `board_followers`, `board_id`, `pinterest_account_id`, `update_time`) 
                        values (%s, %s, %s, %s, %s, %s)''', (uri, name, board_followers, board_id, account_id, time_now))

                    con.commit()
            else:
                logger.error("update boards get_user_boards error, account token={}, ret={}".format(token, ret))

            ret = p_api.get_user_pins()

            if ret["code"] == 1:
                pins = ret["data"]["data"]
                if pins:
                    time_now = datetime.datetime.now()
                    for pin in pins:
                        uri = pin.get("id", "")
                        create_time = datetime.datetime.strptime(pin["created_at"], "%Y-%m-%dT%H:%M:%S")
                        update_time = time_now
                        url = pin.get("url", "")
                        media_type = pin.get("media",{}).get("type", 'image')
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
                        pin_like = 0
                        pin_views = 0
                        pin_clicks = 0

                        # 如果pin　uri 已经存在，则进行更新即可
                        if uri in exist_pins_dict.keys():
                            # , saves = % s, comments = % s
                            pin_id = exist_pins_dict[uri]
                            cursor.execute(
                                '''update `pin` set description=%s, update_time=%s''',
                                (note, update_time))
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
                        `thumbnail`, `publish_time`, `update_time`, `board_id`, `product_id`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s) ''',
                                           (uri, url, note, original_link, pin_thumbnail, create_time, update_time, board_id, product_id))
                            pin_id = cursor.lastrowid

                        con.commit()

                        #　更新历史数据表
                        cursor.execute('''insert into `pinterest_history_data` (`pin_uri`, `pin_note`, `pin_thumbnail`, `pin_likes`, `pin_comments`, `pin_saves`, `pin_views`, `pin_clicks`, `update_time`, `board_id`, `pin_id`, `pinterest_account_id`, `product_id`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                       (uri, note, pin_thumbnail, pin_like, pin_comments, pin_saves, pin_views, pin_clicks,
                                    update_time, board_id, pin_id, account_id, product_id))

                        con.commit()
            else:
                logger.error("update pins get_user_pins error, account token={}, ret={}".format(token, ret))


class ShopifyOpt:
    def update_products(self):
        pass


class TaskProcessor:
    def __init__(self, scan_interval):
        self.bk_scheduler = BackgroundScheduler()
        self.bk_scheduler.start()
        self.pinterest = None
        self.scan_job = None
        self.scan_interval = scan_interval

    def get_all_new_pins(self):
        time_now = datetime.datetime.now()
        error_time = int(self.scan_interval/2)+1
        lte_time = time_now + datetime.timedelta(seconds=error_time)
        gte_time = time_now + datetime.timedelta(seconds=error_time)
        all_jobs = PublishRecord.objects.filter(state=False, execute_time__lte=gte_time, execute_time__gte=lte_time).all()
        return all_jobs

    def scan_new_pins(self):
        waiting_pins = self.get_all_new_pins()
        logger.info("scan_new_pins be triggered.")
        for wp in waiting_pins:
            logger.info("create pin info={}".format(wp))
            # self.pinterest.create_pin(wp)

    def update_pins(self):
        all_pins = Pin.objects.filter().all()

    def start(self):
        logger.info("TaskProcessor start work.")
        self.scan_job = self.bk_scheduler.add_job(self.scan_new_pins, 'interval', seconds=self.scan_interval)

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

def test_task_pro():
    tsp = TaskProcessor(6)
    tsp.start()
    import time
    time.sleep(15)
    # tsp.pause()
    # time.sleep(20)
    tsp.resume()
    # time.sleep(20)
    tsp.stop()
    time.sleep(2)
    tsp.start()
    time.sleep(20)

def test_pinterest_opt():
    pt = PinterestOpt()
    # pt.produce_records_by_rule()

    # records = pt.get_pending_records()
    # if records:
    #     print(records)
    #     pt.create_pins(records)
    pt.update_boards()

    # base64_str = pt.image_2_base64("https://www.theadultman.com/wp-content/uploads/2016/08/Things-Every-Man-Should-Own-1-1.jpg", is_thumb=False)
    # pt.base64_2_image(base64_str, "123.jpg")
    # pt.update_boards()

if __name__ == '__main__':
    test_pinterest_opt()