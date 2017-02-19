# !stock/start.py
# -*- coding:UTF-8 -*-
'''
操作指南：
    命令： python start.py 【parameter】
1. 创建股票基础数据表
    :parameter：create_tb_base
2. 插入股票基础数据参数
    :parameter：insert_stock_base
'''

import sys
from app.stock import create_stock_base
from app.stock import insert_stock_base
from app.stock import generate_tushare_res

ARGV_CTEATE_TB_STOCK_BASE = "create_tb_base"
ARGV_INSERT_STOCK_BASE = "insert_stock_base"
ARGV_GENERATE_RES_TUSHARE = 'generate_res_tushare'

def dispatch():
    if len(sys.argv) < 2:
        print "请输入两个参数\n"
        print __doc__
        return
    args = sys.argv[1]
    if args == ARGV_CTEATE_TB_STOCK_BASE: # 创建股票基础数据表【stock】
        create_stock_base()
    if args == ARGV_INSERT_STOCK_BASE:
        insert_stock_base()
    if args == ARGV_GENERATE_RES_TUSHARE:
        start = None    # 进行tushare的开始时间
        end = None      # 进行tushare的结束时间
        if len(sys.argv) == 3:
            start = sys.argv[2]
            if len(sys.argv) == 4:
                end = sys.argv[3]
                generate_tushare_res(start, end) #设定起始起始日期和结束日期
            generate_tushare_res(start) #输入参数中只设定了起始日期
        generate_tushare_res() #未设定起始结束日期

if __name__ == '__main__':
    dispatch()