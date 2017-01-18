#coding=utf-8
import sys
import random
import urllib2
import cookielib
import time
from bs4 import BeautifulSoup
import gzip
import StringIO
import zlib
from multiprocessing.dummy import Pool
import os

reload(sys)
sys.setdefaultencoding('utf-8')

import socket

_dnscache = {}

def _setDNSCache():
    """
    Makes a cached version of socket._getaddrinfo to avoid subsequent DNS requests.
    """
    def _getaddrinfo(*args, **kwargs):
        global _dnscache
        if args in _dnscache:
            #print str(args)+" in cache"
            return _dnscache[args]
        else:
            #print str(args)+" not in cache"
            _dnscache[args] = socket._getaddrinfo(*args, **kwargs)
            return _dnscache[args]

    if not hasattr(socket, '_getaddrinfo'):
        socket._getaddrinfo = socket.getaddrinfo
        socket.getaddrinfo = _getaddrinfo

uagent = [
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0',
    'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
]

def gzip_decoder(page):
    encoding = page.info().get("Content-Encoding")
    if encoding in ('gzip', 'x-gzip', 'deflate'):
        content = page.read()
        if encoding == 'deflate':
            data = StringIO.StringIO(zlib.decompress(content))
        else:
            data = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(content))
        return data.read()
    return page.read()

success_list = []
error_list = []

def parser(line):

    global success_list
    global error_list

    try:
        idx, url = line.split(' ')
        idx = int(idx.strip())
        url = url.strip()
        if url[0:7] == 'http://':
            url = 'https' + url[4:]
    except Exception as e:
        print 'line error: idx %d, url %s' % (idx, url)
        error_list.append([idx, url])
        return

    try:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', uagent[random.randint(0,len(uagent)-1)]), ('Accept-Encoding', 'gzip,deflate')]
        time1 = time.time()
        r = opener.open(url, timeout=3)
        time2 = time.time()
        print 'get cost %fs' % (time2 - time1)
    except Exception as e:
        print e
        error_list.append([idx, url])
        return

    try:
        html = gzip_decoder(r)
        time3 = time.time()
        print 'gzip read cost %fs' % (time3 - time2)
        opener.close()
    except Exception as e:
        print 'gzip read error or opener close fail:', e
        error_list.append([idx, url])
        return

    try:
        bf = BeautifulSoup(html, 'lxml')
        detail_tag = bf.find_all('ul', class_='biblio-info')
        detail_tag = detail_tag[0]
        age_tag = detail_tag.find_all('li', recursive=False)
        age_tag = age_tag[0]
        label_tag = age_tag.find_all('label')
        label_tag = label_tag[0]
        label = label_tag.get_text().strip()
        if label != 'For ages':
            print 'parse error: NO AGE RANGE, FIRST IS %s' % (label)
            error_list.append([idx, url])
            return
        val = age_tag.find_all('span')[0]
        age_range = val.get_text().strip()
        success_list.append([idx, age_range])
        sys.stdout.flush()
    except Exception as e:
        print 'parse error:', e
        error_list.append([idx, url])

fail = 0

def outputer(st, ed):
    global success_list
    global error_list
    global fail
    if len(error_list) == 5000:
        print 'from %d to %d fail' % (st, ed)
        fail = 1
        return
    try:
        print '%d lines success' % (len(success_list))
        success_save = open('output/successlist' + str(st) + '-' + str(ed-1) + '.txt', 'wb')
        for i in success_list:
            success_save.write(str(i[0]) + ' ' + i[1] + '\n')
        success_save.close()
        print '%d lines error' % (len(error_list))
        error_save = open('output/errorlist' + str(st) + '-' + str(ed-1) + '.txt', 'wb')
        for i in error_list:
            error_save.write(str(i[0]) + ' ' + i[1] + '\n')
        error_save.close()
    except Exception as e:
        print 'from %d to %d ans write error:' % (st, ed), e
    success_list = []
    error_list = []

def solver(data, st, ed):
    try:
        data = data[st:ed]
    except Exception as e:
        print 'from %d to %d data load error:' % (st, ed), e
    try:
        pool = Pool(24)
        pool.map(parser, data)
        pool.close()
        pool.join()
    except Exception as e:
        print 'pool error:', e
    outputer(st, ed)

mod = 5000
st = 100000 
ed = 200000 

if __name__ == "__main__":
    _setDNSCache()
    f = open('data').readlines()
    ranges = [st]
    for i in range(1, ed):
        if st + i * mod < ed:
             ranges.append(st + i * mod)
        else:
            ranges.append(ed)
            break
    time1_ = time.time()
    for i in range(1, len(ranges)):
        if fail:
            break
        time1 = time.time()
        solver(f, ranges[i-1], ranges[i])
        time2 = time.time()
        print 'from %d to %d cost %fmin' % (ranges[i-1], ranges[i]-1, (time2 - time1)/60)
    time2_ = time.time()
    print 'total %fmin' % ((time2_ - time1_) / 60)
