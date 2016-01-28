#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import time

import gevent
import requests
from gevent import monkey

from app import logger
from settings import config

monkey.patch_all()


class Validator(object):
    def __init__(self):
        self.target = config['target']
        self.timeout = config['timeout']
        self.process_num = config['process_num']
        self.thread_num = config['thread_num']

    def run_in_multiprocess(self, proxy_list):
        """ 多进程 """
        result_queue = multiprocessing.Queue()
        proxy_partitions = self.partite_proxy(proxy_list)
        process = []
        for partition in proxy_partitions:
            p = multiprocessing.Process(target=self.process_with_gevent, args=(result_queue, partition))
            p.start()
            process.append(p)

        for p in process:
            p.join()

        result = {}
        for p in process:
            result.update(result_queue.get())

        return result

    def partite_proxy(self, proxy_list):
        """ 按process_num数对proxy_list进行分块 """
        if len(proxy_list) == 0:
            return []

        result = []
        step = len(proxy_list) / self.process_num + 1
        for i in range(0, len(proxy_list), step):
            result.append(proxy_list[i:i + step])

        return result

    def process_with_gevent(self, result_queue, proxy_list):
        """ 采用gevent进行处理 """
        jobs = [gevent.spawn(self.validate_job, proxy_list) for i in range(self.thread_num)]
        gevent.joinall(jobs)
        result = {}
        for job in jobs:
            result.update(job.value)

        result_queue.put(result)

    def validate_job(self, proxy_list):
        result = {}
        while len(proxy_list) > 0:
            ip_port = proxy_list.pop()
            is_valid, speed = self.validate(ip_port)
            if is_valid:
                result[ip_port] = speed
                logger.info("got an valid ip: %s, time:%s", ip_port, speed)

        return result

    def validate(self, ip_port):
        proxies = {
            "http": "http://%s" % ip_port,
        }
        try:
            start = time.time()
            r = requests.get(self.target, proxies=proxies, timeout=self.timeout)
            if r.status_code == requests.codes.ok and r.text == 'true':
                speed = time.time() - start
                logger.debug('validating %s, success, time:%ss', ip_port, speed)
                return True, speed

        except Exception as e:
            logger.debug("validating %s, fail: %s", ip_port, e)

        return False, 0
