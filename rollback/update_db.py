#coding=utf-8
import sys
import MySQLdb
import json

reload(sys)
sys.setdefaultencoding('utf-8')

def update_db(dic):
	db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='en_magic', charset='utf8')
	cursor = db.cursor()
	try:
		pre_sql = "select id from tb_book_pub where url = '%s'" % dic['url']
		if cursor.execute(pre_sql) == 0:
			db.close()
			return
		this_id = cursor.fetchall()
		if len(this_id) != 1:
			print this_id, 'multiple'
			return
		this_id = this_id[0][0]
		sql = ''' update tb_book_pub set img_address = '%s' where id = %d ''' % (dic['img_address'], this_id)
		cursor.execute(sql)
		db.commit()
	except Exception as e:
		print e
		db.rollback()
	db.close()

f = open('hmhco.log').readlines()
for line in range(0, len(f)):
	try:
		line = eval(f[line])
		update_db(line)
	except Exception as e:
		print e
