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

f = open('usborne.json', 'wb')
#1320/age-0-2-years
magic_number = 1320
root_url = 'https://usborne.com/browse-books/catalogue/custom-search/'
age_range = ['0-2', '3-5', '5-7', '7-11', '11-13']
url_pool = {
    '0-2': [],
    '3-5': [],
    '5-7': [],
    '7-11': [],
    '11-13': [],
    '14-18': []
}

def build_targets():
    for i in range(0, len(age_range)):
        cnt_age = 0
        age = age_range[i]
        print 'catch age ' + age
        list_url = root_url + str(magic_number+i) + '/age-%s-years/' % age
        response = requests.get(list_url)
        response.encoding = 'utf-8'
        data = response.text
        bf = BeautifulSoup(data, 'lxml')
        lt = bf.find_all('div', class_='tListContent')
        print 'catch %d lines' % len(lt)
        for li in lt:
            a_tag = li.find_all('p', class_='tListBookLink')[0].find_all('a')[0]
            target = a_tag.get('href')
            if target == None or len(str(target)) < 5:
                continue
            print 'get %s' % target
            url_pool[age].append(target)
            cnt_age += 1
        print 'age %s done, count %d' % (age, cnt_age)

build_targets()
f.write(json.dumps(url_pool))
