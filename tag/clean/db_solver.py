#coding=utf-8
import sys
import random
import os

reload(sys)
sys.setdefaultencoding('utf-8')

import MySQLdb

f = open('shop_category', 'r')
z = f.readlines()
db = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='magic', charset='utf8')
cursor = db.cursor()

for line in z:
    idx, cat = line.split('\t')
    cat = cat.strip()
    cat = cat.replace(MySQLdb.escape_string('\n'), '')
    if len(cat) < 1:
        continue
    idx = int(idx)
    print idx, cat
    sql = ''' update tb_en_book_pub set categories = '%s' where id = %d ''' % (cat, idx)
    print sql
    cursor.execute(sql)
    db.commit()

db.close()
