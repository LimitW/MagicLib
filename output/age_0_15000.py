#coding=utf-8

import sys
import MySQLdb
import os

reload(sys)
sys.setdefaultencoding('utf-8')

db = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='magic', charset='utf8')
cursor = db.cursor()

for l in [0, 5000, 10000]:
    r = l + 5000 - 1
    print l, r
    f = open('successlist' + str(l) + '-' + str(r))
    lines = f.readlines()
    for line in lines:
        idx, age_range = line.split(' ')
        idx = int(idx.strip())
        age_range = age_range.strip()
        print idx, age_range
        sql = ''' update tb_en_book_pub set age_range='%s' where id=%d ''' % (age_range, idx)
        print sql
        cursor.execute(sql)
        db.commit()
db.close()
