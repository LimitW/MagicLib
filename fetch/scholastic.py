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
#search[age_end]=2 search[age_start]=0 search[age_id]=
root_url = 'https://shop.scholastic.co.uk/search/search?'
age_range = [[0, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12], [13, 18]]
page_range = [9, 49, 136, 172, 103, 77, 30]
url_pool = {
    '0-2': [],
    '3-4': [],
    '5-6': [],
    '7-8': [],
    '9-10': [],
    '11-12': [],
    '13-18': []
}

f = open('scholastic.json', 'wb')

def build_targets():
    for i in range(0, len(age_range)):
        cnt_age = 0
        age_start, age_end = age_range[i]
        page = page_range[i]
        age = str(age_start) + '-' + str(age_end)
        print 'catch age %s' % age
        for cur_page in range(1, page+1):
            cnt_page = 0
            url_params = 'search%5Bage_start%5D=' + str(age_start)
            url_params += '&search%5Bage_end%5D=' + str(age_end)
            url_params += '&page=%d' % cur_page
            list_url = root_url + url_params
            print 'catch page %d' % cur_page
            response = requests.get(list_url)
            response.encoding = 'utf-8'
            data = response.text
            bf = BeautifulSoup(data, 'lxml')
            lt = bf.find_all('ul', class_='result-list')[0]
            lt = lt.find_all('a', class_='product-cover-image')
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
