#!stock/app/file.py
# -*- coding:UTF-8 -*-
import codecs
from Exception.exception_level import FILE_OPEN_ERROR

def read_file(filePath):
    file = codecs.open(filePath, 'r', 'utf-8')
    try:
        json_str = file.read()
        return json_str
    except Exception, e:
        raise Exception('打开文件%s失败' % (filePath), FILE_OPEN_ERROR)
    finally:
        file.close()