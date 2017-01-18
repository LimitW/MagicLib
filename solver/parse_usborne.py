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

language = 'English'
f = open('../data/usborne.json').read()
data = json.loads(f)

root_url = 'https://usborne.com'
keys = ['name', 'authors', 'publisher', 'isbn', 'url',
'img_address', 'price', 'summary', 'format',
'pagenum', 'categories', 'series', 'datePubed', 'age_range']

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
			isbn, url, img_address, \
			price, datePubed, \
			language, format, age_range, \
			pagenum, categories, series) \
			values ('%s', '%s', '%s', \
			'%s', '%s', '%s', \
			'%s', '%s', \
			'%s', '%s', '%s', \
			'%s', '%s', '%s')" \
			% (dic['name'], dic['authors'], dic['publisher'], \
			dic['isbn'], dic['url'], dic['img_address'], \
			dic['price'], dic['datePubed'], \
			language, dic['format'], dic['age_range'],
			dic['pagenum'], dic['categories'], dic['series'])
		cursor.execute(sql)
		db.commit()
	except Exception as e:
		print e
		db.rollback()
	db.close()

for age_range in data:
	ls = data[age_range]
	for item in ls:
		try:
			item = root_url + item
			response = requests.get(item)
			response.encoding = 'utf-8'
			html = response.text
			bf = BeautifulSoup(html, 'lxml')
			dic = {}
			dic['publisher'] = 'Usborne'
			dic['age_range'] = age_range
			dic['url'] = item
		except Exception as e:
			print e
			continue
		try:
			detail_tag = bf.find_all('dl', class_='bookInfo')[0]
		except Exception as e:
			print 'no detail', e
			continue
		try:
			img_tag = bf.find_all('div', class_='bookImage')[0]
			img_tag = img_tag.find_all('img')[0]
			dic['img_address'] = img_tag.get('src')
		except Exception as e:
			print 'img_address', e
		try:
			name_tag = bf.find_all('h1', attrs={"itemprop":"name"})[0]
			dic['name'] = name_tag.get_text().strip()
		except Exception as e:
			print 'name', e
		#try: #summary
		#	summary_tag = bf.find_all('div', attrs={"itemprop":"description"})[0]
		#	dic['summary'] = summary_tag.get_text().strip()
		#except Exception as e:
		#	print 'summary', e
		try: #price
			price_tag = bf.find_all('p', class_='formatDetails')[0]
			dic['price'] = price_tag.get_text().strip()
		except Exception as e:
			print 'price', e
		try: #series
			series_tag = bf.find_all('a', class_='series')[0]
			dic['series'] = series_tag.get_text().strip()
		except Exception as e:
			print 'series', e
		try: #categories
			cat_tag = bf.find_all('nav', id='breadcrumb')[0]
			cats = cat_tag.find_all('a')
			cats_v = []
			for cat in cats:
				cats_v.append(cat.get_text())
			dic['categories'] = '>'.join(cats_v)
		except Exception as e:
			print 'categories', e
		try: #format
			format_tag = detail_tag.find_all('dt', class_='fullWidth')[0]
			dic['format'] = format_tag.get_text().strip()
		except Exception as e:
			print 'format', e
		try: #ISBN, PAGENUM
			detail_ls = detail_tag.get_text().strip().split('\n')
			for i in range(0, len(detail_ls)):
				detail_ls[i] = detail_ls[i].strip()
				if detail_ls[i] == '':
					continue
				detail_ls[i] = detail_ls[i].split(':')
				if len(detail_ls[i]) < 2:
					continue
				if detail_ls[i][0] == 'ISBN':
					dic['isbn'] = detail_ls[i][1].strip()
				if detail_ls[i][0] == 'Extent':
					dic['pagenum'] = detail_ls[i][1].strip()
		except Exception as e:
			print 'isbn', e
		try: #authors
			author_tag = detail_tag.find_all(text='Author/Editor')[0]
			author_tag = author_tag.parent.find_next_sibling('dd')
			dic['authors'] = author_tag.get_text() + '(Author/Editor)'
			try:
				illus_tag = detail_tag.find_all(text='Illustrator')[0]
				illus_tag = illus_tag.parent.find_next_sibling('dd')
				dic['authors'] += ',' + illus_tag.get_text() + ('(Illustrator)')
			except Exception as e:
				print 'Illustrator', e
		except Exception as e:
			print 'authors', e
		write_to_db(dic)
