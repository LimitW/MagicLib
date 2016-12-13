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
f = open('scholastic.json').read()
data = json.loads(f)

keys = ['name', 'authors', 'publisher', 'isbn', 'url',
'img_address', 'price', 'summary', 'datePubed', 'format',
'pagenum', 'categories', 'series']

def write_to_db(dic):
	db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='en_magic', charset='utf8')
	cursor = db.cursor()
	for v in keys:
		if dic.get(v) == None:
			dic[v] = ''
	try:
		pre_sql = "select id from tb_book_pub where url = '%s'" % dic['isbn']
		if cursor.execute(pre_sql) == 0:
			sql = "insert into tb_book_pub( \
				name, authors, publisher, \
				isbn, url, img_address, \
				price, summery, datePubed, \
				language, format, age_range, \
				pagenum, categories, series) \
				values ('%s', '%s', '%s', \
				'%s', '%s', '%s', \
				'%s', '%s', '%s', \
				'%s', '%s', '%s', \
				'%s', '%s', '%s')" \
				% (dic['name'], dic['authors'], dic['publisher'], \
				dic['isbn'], dic['url'], dic['img_address'], \
				dic['price'], dic['summary'], dic['datePubed'], \
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
		response = requests.get(item)
		response.encoding = 'utf-8'
		html = response.text
		#print html
		bf = BeautifulSoup(html, 'lxml')
		dic = {}
		dic['age_range'] = age_range
		dic['url'] = item
		try:
			img_tag = bf.find_all('div', class_='product-image')[0]
			img_tag = img_tag.find_all('a')[0]
			dic['img_address'] = img_tag.get('href')
		except Exception as e:
			print e
		try:
			name_div = bf.find_all('div', id='product-title')[0]
			name_tag = name_div.find_all('span', attrs={"itemprop":"name"})[0]
			dic['name'] = name_tag.get_text().strip()
		except Exception as e:
			print e
		try: #authors
			name_div = bf.find_all('div', id='product-title')[0]
			authors = name_div.find_all('h2')[0].find_all('a')
			authors_v = [];
			for author in authors:
				authors_v.append(author.get_text().strip())
			dic['authors'] = ','.join(authors_v)
		except Exception as e:
			print e
		try: #summary
			summary_tag = bf.find_all('div', attrs={"itemprop":"description"})[0]
			dic['summary'] = summary_tag.get_text()
		except Exception as e:
			print e
		try: #price
			price_tag = bf.find_all('span', attrs={"itemprop":"price"})[0]
			priceCurrency = bf.find_all('span', attrs={"itemprop":"priceCurrency"})[0]
			dic['price'] = price_tag.get_text().strip() + priceCurrency.get_text().strip()
		except Exception as e:
			print e
		try: #categories
			cat_tag = bf.find_all('div', class_='categories')[0].find_all("ul")[0]
			cats = cat_tag.find_all("li")
			cats_v = []
			for cat in cats:
				cats_v.append(cat.get_text())
			dic['categories'] = ','.join(cats_v)
		except Exception as e:
			print e
		details_tag = bf.find_all('div', class_='product-details')[0]
		try: #format
			format_tag = details_tag.find_all(text='Format')[0]
			forma = format_tag.parent
			forma = forma.find_next_sibling('p')
			dic['format'] = forma.get_text().strip()
		except Exception as e:
			print e
		try: #ISBN
			isbn_tag = details_tag.find_all(text='ISBN')[0]
			isbn = isbn_tag.parent
			isbn = isbn.find_next_sibling('p')
			dic['isbn'] = isbn.get_text().strip()
		except Exception as e:
			print e
		try: #publisher
			pub_tag = details_tag.find_all(text='Publisher')[0]
			pub = pub_tag.parent
			pub = pub.find_next_sibling('p')
			dic['publisher'] = pub.get_text().strip()
		except Exception as e:
			print e
		try: #pagenum
			pagenum_tag = details_tag.find_all(text='Other details')[0]
			pagenum = pagenum_tag.parent
			pagenum = pagenum.find_next_sibling('ul')
			dic['pagenum'] = pagenum.get_text().strip()
		except Exception as e:
			print e
		try: #datePubed
			date_tag = details_tag.find_all(text='Date published')[0]
			date = date_tag.parent
			date = date.find_next_sibling('p')
			dic['datePubed'] = date.get_text().strip()
		except Exception as e:
			print e
		try: #series
			series_tag = details_tag.find_all(text='Series')[0]
			series = series_tag.parent
			series = series.find_next_sibling('p')
			dic['series'] = series.get_text().strip()
		except Exception as e:
			print e
		write_to_db(dic)
