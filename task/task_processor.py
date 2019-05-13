#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-05-11
# Function:
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from config import logger
from sea_app.models import PublishRecord, Pin, Board, Account


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


if __name__ == '__main__':
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