#!db.py
# -*- coding:UTF-8 -*-
'''
数据库处理的相关工具方法定义
'''
import MySQLdb
import logging
import datetime

from Exception.exception_level import DB_EXECUTE_SQL_ERROR
from Exception.exception_level import DB_INSERT_ERROR

#-- 数据库连接信息 --
host='localhost'
port = 3306
user='root'
passwd='123456'
db ='stock'

#-- 创建数据库语句
CREATE_TABLE = 'CREATE TABLE %s(%s)'
INSERT_TABLE_SQL = 'INSET INTO %s VALUES(%s) %s'
SELECT_SQL = 'SELECT %s FROM %s '

#-- 获取一个数据库连接 --
def connect(host, port, user, passwd, db):
    return MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
    pass

#-- 执行批量插入操作
def insert_many(sql, tmp):
    conn = connect(host, port, user, passwd, db)
    curr = conn.cursor()
    startTime = datetime.datetime.now()
    print ('insert base data start time:' + str(startTime))
    try:
        curr.executemany(sql, tmp)
        conn.commit()
    except Exception,e:
        print('insert base data error' + str(e))
    finally:
        curr.close()
        conn.close()
    endTime = datetime.datetime.now()
    print("insert base data end time:" + str(endTime) + ", total：" + str((endTime - startTime).seconds))

#-- 执行传入的sql语句 --
def execute(sql):
    startTime = datetime.datetime.now()
    logging.info("execute sql start：" + str(startTime))
    conn = connect(host, port, user, passwd, db)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        pass
    except Exception, e:
        conn.rollback()
        raise Exception(e)
    finally:
        cur.close()
        conn.close()
    endTime = datetime.datetime.now()
    logging.info("execute sql end：" + str(endTime) + ", total：" + str((endTime - startTime).seconds))
    pass

'''
创建数据库表
tableName 表名
paramsDic 表字段名
primaryKey 主键设置字符串
foreignKey 外键设置字段
'''
def createTable(tableName, paramsDic, foreignKey=''):
    sql = CREATE_TABLE % (tableName, dic2Str(paramsDic))
    if foreignKey != '':
        sql += ', ' + foreignKey
        pass
    try:
        execute(sql)
        pass
    except Exception, e:
        raise Exception(e)
    pass

'''
插入数据
tableName 表名
values 插入数据
where 筛选条件
'''
def insert_data(tableName, values, where=''):
    sql = INSERT_TABLE_SQL % (tableName, values, where)
    try:
        execute(sql)
    except Exception,e:
        print 'insert data failed [%s], caused: %s' % (sql, e.message)
    pass

'''
数据库查询
 :parameter tbName 表名
 :parameter what 查询结果集中包含的内容
 :parameter where 查询条件
 :parameter count 查询数据条数
'''
def query(tbName, what, where=None, start=None, count=None):
    results = None
    sql = SELECT_SQL % (what, tbName)
    if where:
        sql += where + ' '
    if start != None:
        sql += 'LIMIT %s, %s' % (start, count)
    conn = connect(host, port, user, passwd, db)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except Exception, e:
        print ('get data from %s failed: %s' % (tbName, e.message))
    finally:
        cursor.close()
        conn.close()
    return results

#-- 字符串拼接
def dic2Str(paramsDic):
    res = ''
    for key in paramsDic:
        res += key + ' ' + paramsDic[key] + ','
        pass
    str_list = list(res)
    str_list.pop()
    return "".join(str_list)
    pass



#修改查询条件的数据
#cur.execute("update student set class='3 year 1 class' where name = 'Tom'")

#删除查询条件的数据
#cur.execute("delete from student where age='9'")
