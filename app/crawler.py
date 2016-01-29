#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gevent

from proxy import Site


class Crawler(object):
    def __init__(self):
        pass

    @staticmethod
    def _run(site):
        return site().fetch()

    @staticmethod
    def run():
        ip_list = []
        sites = Site.__subclasses__()

        jobs = [gevent.spawn(Crawler._run, site) for site in sites]
        gevent.joinall(jobs)

        for job in jobs:
            ip_list.extend(job.value)

        return ip_list
