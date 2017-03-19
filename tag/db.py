#coding=utf-8
import sys
import random
import os

reload(sys)
sys.setdefaultencoding('utf-8')

import MySQLdb

db = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='magic', charset='utf8')
cursor = db.cursor()
sql = ''' select id, isbn from tb_en_book_pub where url like '%hmhco%' or url like '%shop.scholastic%' or url like '%usborne.com%' '''
cursor.execute(sql)
res = cursor.fetchall()
db.commit()

for i in res:
    img = 'img_22/' + str(i[0]) + '@' + i[1] + '.jpg'
    print img
    sql = ''' update tb_en_book_pub set img_address = '%s' where id = %d ''' % (img, i[0])
    cursor.execute(sql)
    db.commit()

db.close()
