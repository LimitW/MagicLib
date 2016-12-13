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

f = open('hmhco.json', 'wb')

root_url = 'http://www.hmhco.com/at-home/shop-by-age/'
age_range = ['0-2', '3-5', '6-8', '9-12']
page_range = [15, 78, 111, 67]
url_pool = {
    '0-2': [],
    '3-5': [],
    '6-8': [],
    '9-12': []
}

def build_targets():
    for i in range(0, len(age_range)):
        cnt_age = 0
        age = age_range[i]
        page = page_range[i]
        print 'catch age ' + age
        for cur_page in range(1, page+1):
            cnt_page = 0
            list_url = root_url + age + '/page=' + str(cur_page)
            print 'catch page %d' % cur_page
            response = requests.get(list_url)
            response.encoding = 'utf-8'
            data = response.text
            bf = BeautifulSoup(data, 'lxml')
            lt = bf.find_all('section', class_='product-widget')[0]
            lt = lt.find_all('a')
            for a_tag in lt:
                target = a_tag.get('href')
                if target == None or len(str(target)) < 5:
                    continue
                cnt_page += 1
                print 'get %s' % target
                url_pool[age].append(target)
            cnt_age += cnt_page
            print 'page %d done, count %d' % (cur_page, cnt_page)
        print 'age %s done, count %d' % (age, cnt_age)

build_targets()

f.write(json.dumps(url_pool))
