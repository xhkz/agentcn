#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing

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

    def run(self, proxies):
        q = multiprocessing.Queue()
        size = len(proxies) / self.process_num + 1
        chunks = self.slice(proxies, size)
        process = []

        for chunk in chunks:
            p = multiprocessing.Process(target=self.proc, args=(q, chunk))
            p.start()
            process.append(p)

        result = {}
        for p in process:
            p.join()
            result.update(q.get())

        return result

    def slice(self, proxies, size):
        if proxies:
            return [proxies[i:i + size] for i in range(0, len(proxies), size)]

        return []

    def proc(self, q, proxies):
        jobs = [gevent.spawn(self.validate, proxies) for _ in range(self.thread_num)]
        gevent.joinall(jobs)

        result = {}
        for job in jobs:
            result.update(job.value)

        q.put(result)

    def validate(self, proxies):
        result = {}
        while len(proxies) > 0:
            proxy = proxies.pop()
            try:
                r = requests.get(self.target, proxies={"http": "http://%s" % proxy}, timeout=self.timeout)
                if r.status_code == requests.codes.ok:
                    result[proxy] = r.elapsed
                    logger.info("Valid proxy: %r, speed:%s", proxy, r.elapsed)

            except Exception as e:
                logger.error("Exception: %s", e)

        return result
