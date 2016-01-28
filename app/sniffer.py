#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator
from itertools import groupby

from app import logger, app_name
from proxy import Proxy
from settings import config
from validator import Validator


class Sniffer(object):
    def __init__(self, proxies):
        self.proxies = sorted(proxies, key=lambda x: x.anonymity)
        self.validator = Validator()

    def verify(self):
        result = {}
        for level in config['anonymity']:
            proxies = ['%s:%s' % (p.ip, p.port) for p in self.classify().get(level, [])]

            logger.info('Sniffer [%s], total: %s', Proxy.anonymity.get(level), len(proxies))
            result[level] = self.validator.run_in_multiprocess(proxies)

            logger.info('Sniffer [%s], valid: %s', Proxy.anonymity.get(level), len(result[level]))

        if config['save']:
            try:
                self.save(result)
            except Exception as e:
                logger.error("Exception: %s", e)

    def save(self, result):
        for level, proxies in result.iteritems():
            with open('./out/%s-%s.txt' % (app_name, level), 'wb') as f:
                f.writelines(['%s\t%s\n' % (line[0], line[1]) for line in sorted(proxies.items(), key=operator.itemgetter(1))])

    def classify(self):
        group = {}
        for k, v in groupby(self.proxies, key=lambda x: x.anonymity):
            group[k] = list(set(v))

        return group
