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
f = open('hmhco.json').read()
data = json.loads(f)

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
	try:
		pre_sql = "select id from current where url = '%s'" % dic['isbn']
		if cursor.execute(pre_sql) == 0:
			sql = "insert into tb_book_pub( \
                name, authors, publisher, \
                isbn, pagenum, url, \
                price, summery, datePubed, \
                language, format, age_range) \
			    values ('%s', '%s', '%s', \
                '%s', '%s', '%s', \
                '%s', '%s', '%s', \
                '%s', '%s', '%s')" \
                % (dic['name'], dic['authors'], cur_publisher, \
                dic['isbn'], dic['pagenum'], dic['url'], \
                dic['price'], dic['summary'], dic['datePubed'], \
                language, dic['format'], dic['age_range'])
			cursor.execute(sql)
		db.commit()
	except Exception as e:
	    print e
	    db.rollback()
	db.close()
write_to_db({})
for age_range in data:
    ls = data[age_range]
    for item in ls:
        item = root_url + item
        response = requests.get(item)
        response.encoding = 'utf-8'
        html = response.text
        print html
        bf = BeautifulSoup(html, 'lxml')
        dic = {}
        dic['age_range'] = age_range
        dic['url'] = item
        try: #name
            name_tag = bf.find_all('h1', id='body1_0_headerText')[0]
            dic['name'] = name_tag.get_text().strip()
        except Exception as e:
            print e
		try:
			img_tag = bf.find_all('img', id='body1_0_bookImage')[0]
			dic['img_address'] = root_url + img_tag.get('src')
		except Exception as e:
			print e
        try: #authors
            authors = bf.find_all('p', class_='writer')[0]
            authors = authors.find_all('a')
            authors_v = [];
            for author in authors:
                authors_v.append(author.get_text().strip())
            dic['authors'] = ','.join(authors_v)
        except Exception as e:
            print e
        try: #summary
            summary_tag = bf.find_all('div', id='productDescrip')[0]
            ps = summary_tag.find_all('p', recursive=False)
            summary = ''
            for p in ps:
                summary += p.get_text().strip()
            dic['summary'] = summary
        except Exception as e:
            print e
        try: #price
            price_tag = bf.find_all('p', class_='product-item-price')[0]
            spans = price_tag.find_all('span', recursive=False)
            price = ''
            for span in spans:
                price += span.get_text().strip()
            dic['price'] = price
        except Exception as e:
            print e
        try: #format
            format_tag = bf.find_all('li', id='body1_0_formatSpan')[0]
            forma = format_tag.get_text().split(':')[1].strip()
            dic['format'] = forma
        except Exception as e:
            print e
        try: #ISBN
            isbn_tag = bf.find_all('li', id='body1_0_isbn13Span')[0]
            isbn = isbn_tag.get_text().split(':')[1].strip()
            dic['isbn'] = isbn
        except Exception as e:
            print e
        try: #pagenum
            pagenum_tag = bf.find_all('li', id='body1_0_noOfPagesSpan')[0]
            pagenum = pagenum_tag.get_text().split(':')[1].strip()
            dic['pagenum'] = pagenum
        except Exception as e:
            print e
        try: #datePubed
            date_tag = bf.find_all('li', id='body1_0_publicationDateSpan')[0]
            date = date_tag.get_text().split(':')[1].strip()
            dic['datePubed'] = date
        except Exception as e:
            print e
        print dic
        write_to_db(dic)
