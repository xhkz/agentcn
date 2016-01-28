#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import logger
from proxy import Site


class Crawler(object):
    def __init__(self):
        pass

    @staticmethod
    def run():
        ip_list = []
        for proxy in Site.__subclasses__():
            ips = proxy().fetch()
            ip_list.extend(ips)
            logger.info('Get %s ip addresses from %s', len(ips), proxy)

        return ip_list
