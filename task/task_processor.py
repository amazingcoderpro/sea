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

    def image_2_base64(self, image_src, is_thumb=True, size=(100, 100)):
        if not os.path.exists(image_src):
            response = requests.get(image_src)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_src)

        if is_thumb:
            image.thumbnail(size)

        output_buffer = BytesIO()
        image.save(output_buffer, format='JPEG')
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

    def get_records(self, status=0):
        """
        获取所有待发布的pins记录, 数据来源PublishRecord表
        :param status: 发布状态　0－－未发布，１－－已发布
        :return: list
        """
        con = DBUtil().get_instance()
        cursor = con.cursor()
        cursor.execute('''
                select id, execute_time, board_id, product_id, rule_id from `publish_record` where state=%s and execute_time between %s and %s
                ''', (status, datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=120)))
        records = cursor.fetchall()

        for record in records:
            record_id, execute_time, board_id, product_id, rule_id = record
            cursor.execute('''
                    select board_uri, name, pinterest_account_id, state from `board` where id=%s
                    ''', board_id)
            board = cursor.fetchone()
            board_uri, board_name, pinterest_account_id, state = board

            cursor.execute('''
                    select account_uri, state, token from `pinterest_account` where id=%s
                    ''', pinterest_account_id)
            account = cursor.fetchone()
            account_uri, state, token = account
            pin_api = PinterestApi(access_token="ArVPxolYdQAXgzr0-FFoRGAF682xFaDsz-o3I1FF0n-lswCyYAp2ADAAAk1KRdOSuUEgxv0AAAAA")
            boards = pin_api.get_user_boards()
            note = ""
            link = ""
            image_url = "https://img-blog.csdn.net/20180509111334917"
            ret = pin_api.create_pin(board_id="753790125070471656", note="123", image_url=image_url, link=link)
            print(ret)

            if ret[0] in [200, 201]:
                data = json.loads(ret[1])["data"]
                pin_uri = data["id"]
                url = data["url"]
                description = note
                site_url = data["original_link"]
                thumbnail = ""
                board_id = board_id
                product_id = product_id
                time_now = datetime.datetime.now()
                cursor.execute('''insert into `pin` (`pin_uri`, `url`, `description`, `site_url`, `thumbnail`, `publish_time`, `update_time`, `board_id`, `product_id`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (pin_uri, url, description, site_url, thumbnail, time_now, time_now, board_id, product_id))
                pin_id = cursor.lastrowid

                state = 1
                remark = ""
                update_time = finished_time = time_now

                cursor.execute('''
                        update `publish_record` set state=%s, remark=%s, finished_time=%s, pin_id=%s, update_time=%s where id=%s
                        ''', (state, remark, finished_time, pin_id, update_time, record_id))

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
        ''', datetime.datetime.now()-datetime.timedelta(days=5))
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
                insert into `publish_record` (`execute_time`, `board_id`, `product_id`, `rule_id`, `create_time`, `update_time`) values (%s, %s, %s, %s, %s, %s)''', (exe_time, board_id, product_id, rule_id, time_now, time_now))
            con.commit()


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

    # pt.get_records()
    base64_str = pt.image_2_base64("https://www.theadultman.com/wp-content/uploads/2016/08/Things-Every-Man-Should-Own-1-1.jpg", is_thumb=False)
    pt.base64_2_image(base64_str, "123.jpg")

if __name__ == '__main__':
    test_pinterest_opt()