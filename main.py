#!/usr/bin/env python
# -*- coding: utf-8 -*-

from crawler import Crawler
from sniffer import Sniffer


def main():
    proxies = Crawler.run()

    Sniffer(proxies).verify()


if __name__ == "__main__":
    main()
