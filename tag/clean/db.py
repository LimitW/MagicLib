#coding=utf-8
import sys
import random
import os

reload(sys)
sys.setdefaultencoding('utf-8')

import MySQLdb

db = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='magic', charset='utf8')
cursor = db.cursor()
sql = ''' update tb_en_book_pub set categories = '%s' where id = %d '''
cursor.execute(sql)
res = cursor.fetchall()
db.commit()
db.close()
f = open('shop_category', 'wb')
for i in res:
    try:
        f.write(str(i[0]) + '\t' + i[1] + '\n')
    except Exception as e:
        print e
