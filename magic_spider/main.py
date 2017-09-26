#coding=utf-8

import os
import signal

spider_lists = [
  'jd_spider',
  'scho_spider',
  'hmhco_spider',
  'usborne_spider',
  'bd_spider',
#  'jd_spider',
]

def spider_gen():
  for spider in spider_lists:
    os.system('scrapy crawl ' + spider)

if __name__ == '__main__':
  spider_gen()
