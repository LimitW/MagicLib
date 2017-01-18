#coding=utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import MySQLdb

def init_db():
    db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='en_magic', charset='utf8')
    cursor = db.cursor()
    sql = ''' select id, name, isbn, url, img_address from tb_book_pub where id > 3011044 '''
    cursor.execute(sql)
    res = cursor.fetchall()
    db.close()
    return res

import urllib2

def solver(res):
    for i in range(850, len(res)):
        line  = res[i]
        print i, line
        cur_img = line[-1]
        file_type = cur_img.split('.')[-1]
        cur_file_name = str(line[0]) + '@' + line[2] + '.' + file_type
        print cur_file_name
        url = line[3]
        if url.find('https://shop.scholastic.co.uk/') != -1:
            cur_img = 'https:' + cur_img
        print cur_img
	try:
       		cur_file = urllib2.urlopen(cur_img)
        	with open(cur_file_name, 'wb') as output:
            		output.write(cur_file.read())
	except Exception as e:
		print e

solver(init_db())
