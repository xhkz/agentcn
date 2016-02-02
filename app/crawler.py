#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

        for site in Site.__subclasses__():
            ip_list.extend(Crawler._run(site))

        # jobs = [gevent.spawn(Crawler._run, site) for site in sites]
        # gevent.joinall(jobs)
        #
        # for job in jobs:
        #     ip_list.extend(job.value)

        return ip_list
