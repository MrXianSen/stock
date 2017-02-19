# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
#以json的形式存储
class StocknumPipeline(object):

    def __init__(self):
        self.file = codecs.open("stocknum.json", mode="wb", encoding='utf-8')
        self.file.write('{"hah"' + ':[')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + ","
        self.file.write(line.decode("unicode_escape"))

        return item

#将数据存储到mysql数据库
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
class MySQLStorePipeline(object):
    #数据库参数
    def __init__(self):
        dbargs = dict(
             host = '127.0.0.1',
             db = 'stock',
             user = 'root',
             passwd = '',
             cursorclass = MySQLdb.cursors.DictCursor,
             charset = 'utf8',
             use_unicode = True
            )
        self.dbpool = adbapi.ConnectionPool('MySQLdb',**dbargs)

    '''
    The default pipeline invoke function
    '''
    def process_item(self, item,spider):
        res = self.dbpool.runInteraction(self.insert_into_table,item)
        return item
    #插入的表，此表需要事先建好    目前表还未建
    def insert_into_table(self,conn,item):
            conn.execute('insert into stock_base(stockCode, stockName) values(%s,%s)', (
                item['stockCode'][0],
                item['stockName'][0],
            ))