#coding=utf-8
import requests
import re
import urllib
import sys
import datetime as dt
from datetime import datetime
import time
from bs4 import BeautifulSoup
import MySQLdb
import json

reload(sys)
sys.setdefaultencoding('utf-8')

cur_publisher = 'Houghton Mifflin Harcourt'
language = 'English'

root_url = 'http://www.hmhco.com'

keys = ['name', 'authors', 'publisher', 'isbn', 'url',
'img_address', 'price', 'summary', 'datePubed', 'format',
'pagenum']

def write_to_db(dic):
	db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='en_magic', charset='utf8')
	cursor = db.cursor()
	for v in keys:
		if dic.get(v) == None:
			dic[v] = ''
		else:
			dic[v] = MySQLdb.escape_string(dic[v])
	print 'start'
	print dic
	try:
		pre_sql = "select id from tb_book_pub where isbn = '%s'" % dic['isbn']
		if dic['isbn'] == '':
			pre_sql = "select id from tb_book_pub where url = '%s'" % dic['url']
		if cursor.execute(pre_sql) != 0:
			db.close()
			return
		sql = "insert into tb_book_pub( \
				name, authors, publisher, \
				isbn, pagenum, url, \
				price, datePubed, \
				language, format, age_range) \
		values ('%s', '%s', '%s', \
				'%s', '%s', '%s', \
				'%s', '%s', \
				'%s', '%s', '%s')" \
				% (dic['name'], dic['authors'], cur_publisher, \
				dic['isbn'], dic['pagenum'], dic['url'], \
				dic['price'], dic['datePubed'], \
				language, dic['format'], dic['age_range'])
		cursor.execute(sql)
		db.commit()
		print done
	except Exception as e:
		print e
		db.rollback()
	db.close()

f = open('hmhco.log').readlines()
for line in range(1078, len(f)):
	line = f[line]
	write_to_db(eval(line))
