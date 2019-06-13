#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-06-06
# Function: 
import time
from task.task_processor import TaskProcessor


def main():
    tsp = TaskProcessor()
    tsp.start_all(rule_interval=120, publish_pin_interval=240, pinterest_update_interval=3600*4, shopify_update_interval=3600*5, update_new=120)
    while 1:
        time.sleep(1)


if __name__ == '__main__':
    main()
