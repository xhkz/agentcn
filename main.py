#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()

from app.crawler import Crawler
from app.sniffer import Sniffer


def main():
    proxies = Crawler.run()
    Sniffer(proxies).verify()


if __name__ == "__main__":
    main()
