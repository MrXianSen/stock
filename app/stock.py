# !stock/app/stock.py
# -*- coding:UTF-8 -*-

import json             # json
import os
import logging          # 日志
import datetime         # 统计代码运行时间用到

from db import createTable
from db import insert_many
from db import query
from file import read_file
from sqlalchemy import create_engine
import tushare as ts

# STATIC PARAMETERS
QUERY_COUNT = 500   # 每次查询数据的条数
DEFAULT_DATE = '2016-10-01' # 进行tushare的初始日期

#-- 创建股票基础数据表 --
def create_stock_base():
    tbName = 'stock'
    paramsDic = {'id': 'INT AUTO_INCREMENT PRIMARY KEY', 'stockCode': 'varchar(32) not null', 'stockName': 'varchar(64) not null'}
    try:
        createTable(tbName, paramsDic)
        print 'Success:' % tbName
    except Exception, e:
        print 'Error: %s' % tbName + e.message
    pass

#-- 插入基础数据 --
LOCAL_SQL = 'INSERT INTO %s(%s) VALUES(%s);\n'
def insert_stock_base():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    path = unicode(path, 'utf8')
    json_str = read_file(path + '/stocknum.json')
    stocks = json.loads(json_str)['hah']
    sql = ''
    startTime = datetime.datetime.now()
    logging.info("拼装插入股票基础数据sql语句开始:" + str(startTime))
    sql = LOCAL_SQL % ('stock', 'stockCode, stockName', '%s, %s')
    values = []
    for i in xrange(0, len(stocks)):
        stock = stocks[i]
        temp = (stock['stockCode'], stock['stockName'])
        values.append(temp)
        pass
    endTime = datetime.datetime.now()
    logging.info("拼装插入股票基础数据结束:" + str(endTime) + ", 共耗时：" + str((endTime - startTime).seconds))
    insert_many(sql, tuple(values))
    pass

#-- 创建存储经过tushare处理后的数据表res_tushare
def create_res_tushare(tbName='stock_data'):
    paramsDic = {
                 'date': 'VARCHAR(16)',
                 'open': 'DOUBLE',
                 'high': 'DOUBLE',
                 'close': 'DOUBLE',
                 'low': 'DOUBLE',
                 'volume': 'DOUBLE',
                 'price_change': 'DOUBLE',
                 'p_change': 'DOUBLE',
                 'ma5': 'DOUBLE',
                 'ma10': 'DOUBLE',
                 'ma20': 'DOUBLE',
                 'v_ma5': 'DOUBLE',
                 'v_ma10': 'DOUBLE',
                 'v_ma20': 'DOUBLE',
                 'turnover': 'DOUBLE'}
    try:
        createTable(tbName, paramsDic)
        print 'Success: %s ' % tbName
    except Exception, e:
        print 'Error: %s, cause: %s' % (tbName, e.message)
    pass

#-- 创建记录股票涨跌情况的表
def create_stock_compare(tbName='stock_compare'):
    paramsDic = {
        'date': 'VARCHAR(16)',
        'high': 'INT',
        'close': 'INT',
        'low': 'INT',
        'volume': 'INT',
        'ma5': 'INT',
        'ma10': 'INT',
        'ma20': 'INT',
        'v_ma5': 'INT',
        'v_ma10': 'INT',
        'v_ma20': 'INT',
        'turnover': 'INT',
        'p_change': 'VARCHAR(4)'}
    try:
        createTable(tbName, paramsDic)
        print 'Success: %s ' % tbName
    except Exception, e:
        print 'Error: %s, cause: %s' % (tbName, e.message)
    pass

#-- 处理基础数据并将处理后的而数据保存到表[res_tushare]中
def generate_tushare_res(startDate=DEFAULT_DATE, endDate=None):
    index = 1       # 200条数据为一组，表示需要查询多少组数据
    start = 0       # 查询的起始位置
    amount = query('stock', 'COUNT(*)')[0][0] # 获取【stock】表中的数据条数
    if amount > QUERY_COUNT:
        if(amount % QUERY_COUNT) == 0:
            index = amount / QUERY_COUNT
        if(amount / QUERY_COUNT) != 0:
            index = amount / QUERY_COUNT + 1
    for i in xrange(index):
        tempDatas = get_base_data(start, QUERY_COUNT)
        start += QUERY_COUNT
        save_res_tushare(tempDatas, startDate, endDate)

def save_res_tushare(tempDatas, start, end):
    # 创建连接数据库的引擎
    engine = create_engine('mysql://root:123456@127.0.0.1/stock?charset=utf8')
    for stock in tempDatas:
        stockCode = stock[0]
        code = stockCode[2:]
        tushareDataframe = ts.get_hist_data(code, start=start, end=end)
        if(type(tushareDataframe) == type(None)):
            continue
        tbName = 'stock_data' + code
        #create_res_tushare(tbName)                                   # 先自己创建数据库，接口中创建会报错
        tushareDataframe.to_sql(tbName, engine, if_exists='append')    # 将数据插入到数据库中

def get_base_data(start, count):
    return query('stock', 'stockCode, stockName', where=None, start=start, count=count)

def compare_stock_data():
    index = 1  # 200条数据为一组，表示需要查询多少组数据
    start = 0  # 查询的起始位置
    amount = query('stock', 'COUNT(*)')[0][0]  # 获取【stock】表中的数据条数
    if amount > QUERY_COUNT:
        if (amount % QUERY_COUNT) == 0:
            index = amount / QUERY_COUNT
        if (amount / QUERY_COUNT) != 0:
            index = amount / QUERY_COUNT + 1
    for i in xrange(index):
        tempDatas = get_base_data(start, QUERY_COUNT)
        start += QUERY_COUNT
        save_stock_compare(tempDatas)

def save_stock_compare(tempDatas):
    for stock in tempDatas:
        stockCode = stock[0]
        code = stockCode[2:]
        tbName = 'stock_compare' + code # 查询的表名
        stockDatas = get_stock_data(tbName) # 获取@tbName中的数据集合

def get_stock_data(tbName):
    return query(tbName, '*', where='ORDER BY date')
