#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta

import requests
from bs4 import BeautifulSoup

from app import logger


class Proxy(object):
    anonymity = {
        u'透明': 3,
        u'匿名': 2,
        u'高匿': 1,
        3: u'透明',
        2: u'匿名',
        1: u'高匿',
        0: u'未知'
    }

    def __init__(self, ip, port, anonymity):
        self.ip = ip
        self.port = port
        self.anonymity = anonymity

    def __str__(self):
        return '%s:%s' % (self.ip, self.port)

    def __repr__(self):
        return '[%s]%s:%s' % (self.anonymity, self.ip, self.port)

    def __hash__(self):
        return hash((self.ip, self.port))


class Site(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.urls = []
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.0.2564.82 Chrome/48.0.2564.82 Safari/537.36'
        }

    def fetch(self):
        proxies = []
        for s in self.get():
            proxies.extend(self.parse(s))

        logger.info('Get %s ip addresses from %s', len(proxies), self)

        return proxies

    def get(self, encoding=None):
        """
        :param encoding: requests parameter
        :return: BeautifulSoup list
        """
        soups = []
        for url in self.urls:
            logger.info('GET: %s', url)
            try:
                r = requests.get(url, headers=self.headers)
                if encoding:
                    r.encoding = encoding

                if r.status_code == requests.codes.ok:
                    soups.append(BeautifulSoup(r.text, 'lxml'))
                else:
                    logger.error('Error: %s' % r.status_code)

            except Exception as e:
                logger.error('GET: %s', e)

        return soups

    def parse(self, soup):
        raise NotImplementedError()


class Xici(Site):
    def __init__(self):
        """
        nn: 国内高匿代理
        nt: 国内普通代理
        wn: 国外高匿代理
        wt: 国外普通代理

        仅获取前两页
        """
        super(Xici, self).__init__()
        self.urls = ['http://www.xicidaili.com/%s/%s' % (sub, str(page))
                     for page in range(1, 3)
                     for sub in ['nn', 'nt']]

    def parse(self, soup):
        proxy_list = []
        for tr in soup.find(id='ip_list').find_all('tr')[1:]:
            try:
                td = tr.find_all('td')
                proxy = Proxy(td[2].string, td[3].string, Proxy.anonymity.get(td[5].string, 0))
                proxy_list.append(proxy)

            except Exception as e:
                logger.error('Exception: %s', e)

        return proxy_list


class CNproxy(Site):
    def __init__(self):
        super(CNproxy, self).__init__()
        self.urls = ['http://cn-proxy.com']

    def parse(self, soup):
        proxy_list = []
        for tbody in soup.find_all('tbody'):
            for tr in tbody.find_all('tr'):
                try:
                    td = tr.find_all('td')
                    proxy_list.append(Proxy(td[0].string, td[1].string, 0))

                except Exception as e:
                    logger.error('Exception: %s', e)

        return proxy_list
