#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey

from app.crawler import Crawler
from app.sniffer import Sniffer

monkey.patch_all()


def main():
    proxies = Crawler.run()
    Sniffer(proxies).verify()


if __name__ == "__main__":
    main()
