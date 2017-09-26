# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time
import logging
import MySQLdb
from scrapy_redis.connection import get_redis_from_settings
from scrapy.exceptions import DropItem

class MagicPipeline(object):
    logger = logging.getLogger(__name__)

    def __init__(self, server, key, mysql=None):
        self.server = server
        self.mysql = mysql
        self.key = key
        self.isupdate= False
        self.mysqldb = MySQLdb.connect(
            host=mysql['host'],
            user=mysql['user'],
            passwd=mysql['passwd'],
            db=mysql['db'],
            charset='utf8'
        )
        self.cursor = self.mysqldb.cursor()

    def update_isbn_from_mysql(self):
        self.logger.info('ISBN UPDATE START')

        select_isbn ='''select isbn from %s where isbn is not null''' % self.mysql['table']
        self.cursor.execute(select_isbn)
        has_isbn = self.cursor.fetchall()
        self.mysqldb.commit()

        for isbn in has_isbn:
            try:
                isbn = str(isbn[0]).strip()
                if isbn == '':
                    continue
            except Exception as e:
                self.logger.info('ISBN LOAD ERROR' + isbn[0])
                continue
            self.server.sadd(self.key, isbn)

        self.logger.info('ISBN UPDATE DONE')

    def isbn_seen(self, isbn):
        return isbn is not None and self.server.sadd(self.key, isbn) == 0

    @classmethod
    def from_settings(cls, settings):

        key = 'isbnfilter:%(timestamp)s' % {'timestamp': int(time.time())}
        server = get_redis_from_settings(settings)

        mysql = {}
        mysql['host'] = settings.get('MYSQL_HOST')
        mysql['user'] = settings.get('MYSQL_USER')
        mysql['passwd'] = settings.get('MYSQL_PASSWD')
        mysql['db'] = settings.get('MYSQL_DB')
        mysql['table'] = settings.get('MYSQL_TABLE')

        return cls(server=server, key=key, mysql=mysql)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def close_spider(self, spider):
        self.mysqldb.close()
        self.server.delete(self.key)

    def process_item(self, item, spider):

        if not self.isupdate:
            self.update_isbn_from_mysql()
            self.isupdate = True

        if dict(item).has_key('isbn') and self.isbn_seen(item['isbn']):
            raise DropItem("Duplicate item found: %s" % item['isbn'])

        qmarks = ', '.join(['%s'] * len(item))
        cols = ', '.join(item.keys())
        insert_sql = '''
            insert into %s (%s) values (%s)
        ''' % (self.mysql['table'], cols, qmarks)

        self.cursor.execute(insert_sql, item.values())
        self.mysqldb.commit()

        return item
