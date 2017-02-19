# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#封装要爬取字段

class StocknumItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    stockCode = scrapy.Field()
    stockName = scrapy.Field()
pass
