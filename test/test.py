# !stock/test/test.py
# -*- coding:UTF-8 -*-

import tushare as ts
from app.db import query
from app.db import insert_many
from app.stock import create_stock_compare
import MySQLdb

#-- 数据库连接信息 --
host='localhost'
port = 3306
user='root'
passwd='123456'
db ='stock'

#-- 获取一个数据库连接 --
def connect(host, port, user, passwd, db):
    return MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')

def test_tushare(code, start, end=None):
    result = ts.get_hist_data(code, start=start, end=end)
    print result
    # engine = create_engine('mysql://root:123456@127.0.0.1/stock?charset=utf8')
    # result.to_sql('stock' + code, engine, if_exists='append')
   # pd.io.sql.to_sql(result, 'stock_data' + code, connect(host, port, user, passwd, db), flavor='mysql', if_exists='append', index=False, chunksize=200)

def test_binary():
    tbName = 'stock_data000033'
    create_stock_compare('stock_compare000033')
    stockDatas = query(tbName,
                       'date, high, close, low, volume, ma5, ma10, ma20, v_ma5, v_ma10, v_ma20, turnover, p_change',
                       'ORDER BY date')
    sql = 'INSERT INTO ' \
          'stock_compare000033(date, high, close, low, volume, ma5, ma10, ' \
          'ma20, v_ma5, v_ma10, v_ma20, turnover, p_change) ' \
          'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    values = []
    for i in xrange(len(stockDatas)):
        if i == 0:
            continue
        j = i-1
        yes = stockDatas[j]
        to = stockDatas[i]
        high = 0
        close = 0
        low = 0
        volume = 0
        ma5 = 0
        ma10 = 0
        ma20 = 0
        v_ma5 = 0
        v_ma10 = 0
        v_ma20 = 0
        turnover = 0
        p_change = 'no'
        if yes[1] < to[1]:
            high = 1
        if yes[2] < to[2]:
            close = 1
        if yes[3] < to[3]:
            low = 1
        if yes[4] < to[4]:
            volume = 1
        if yes[5] < to[5]:
            ma5 = 1
        if yes[6] < to[6]:
            ma10 = 1
        if yes[7] < to[7]:
            ma20 = 1
        if yes[8] < to[8]:
            v_ma5 = 1
        if yes[9] < to[9]:
            v_ma10 = 1
        if yes[10] < to[10]:
            v_ma20 = 1
        if yes[11] < to[11]:
            turnover = 1
        if to[12] > 0:
            p_change = 'yes'
        value = (to[0], high, close, low, volume, ma5, ma10, ma20, v_ma5, v_ma10, v_ma20, turnover, p_change)
        values.append(value)
    insert_many(sql, values)

def test_tree():
    datas = query('stock_compare000033',
                  'date, high, close, low, volume, ma5, ma10, ma20, v_ma5, v_ma10, v_ma20, turnover, p_change')
    dataSet = []
    for data in datas:
        curr = [
            data[1], data[2], data[3], data[4],
            data[5], data[6], data[7], data[8],
            data[9], data[10], data[11], data[12]
        ]
        dataSet.append(curr)
    labels = [
        'high', 'close', 'low', 'volume',
        'ma5', 'ma10', 'ma20', 'v_ma5',
        'v_ma5', 'v_ma10', 'v_ma20', 'p_change']
    return dataSet, labels

if __name__ == '__main__':
    test_tree()