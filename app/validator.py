#!/usr/bin/env python
# -*- coding: utf-8 -*-


from multiprocessing import Queue, Process, cpu_count

import gevent
import requests

from app import logger
from settings import config


class Validator(object):
    def __init__(self):
        self.target = config['target']
        self.timeout = config['timeout']
        self.thread_num = config['thread_num']

    def run(self, proxies):
        q = Queue()
        chunks = self.slice(proxies, len(proxies) / cpu_count() + 1)
        process = []

        for chunk in chunks:
            p = Process(target=self.proc, args=(q, chunk))
            p.start()
            process.append(p)

        result = {}
        for _ in process:
            result.update(q.get())

        for p in process:
            p.join()

        return result

    @staticmethod
    def slice(items, num):
        return [items[i:i + num] for i in range(0, len(items), num)]

    def proc(self, q, proxies):
        jobs = [gevent.spawn(self.validate, proxies) for _ in range(self.thread_num)]
        gevent.joinall(jobs)

        result = {}
        for job in jobs:
            result.update(job.value)

        q.put(result)

    def validate(self, proxies):
        result = {}
        while proxies:
            proxy = proxies.pop()
            latency = self._validate(proxy)
            if latency:
                result[proxy] = latency

        return result

    def _validate(self, proxy):
        try:
            r = requests.get(self.target, proxies={"http": "http://%s" % proxy}, timeout=self.timeout)
            if r.status_code == requests.codes.ok and r.text == 'true':
                logger.info("Valid proxy: %r, latency:%s", proxy, r.elapsed)
                return r.elapsed

        except Exception as e:
            logger.error("Exception: %s", e)

        return None
