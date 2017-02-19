# !stock/test/db_test.py
# -*- coding:UTF-8 -*-

from app.db import insert_many
from app.db import query

def test_insert(sql, tmp):
    insert_many(sql, tmp)
    pass

def test_query():
    query('stock', 'count(*)', where=None, start=None, end=None)

if __name__ == '__main__':
    test_query()