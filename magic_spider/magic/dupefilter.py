import logging
import time

from scrapy.dupefilters import BaseDupeFilter

from scrapy_redis import defaults
from scrapy_redis.connection import get_redis_from_settings

from scrapy.utils.python import to_bytes
from w3lib.url import canonicalize_url
import hashlib
import mmh3

import MySQLdb


logger = logging.getLogger(__name__)

domains = {
 'scho_spider': 'shop.scholastic.co.uk',
 'hmhco_spider': 'hmhco.com',
 'bd_spider' : 'bookdepository.com',
 'jd_spider' : 'jd.com',
 'usborne_spider' : 'usborne.com'
}

class GenHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = mmh3.hash(value, self.seed)
        return (self.cap - 1) & ret

class BloomDupeFilter(BaseDupeFilter):
    """Redis-based request duplicates filter.

    This class can also be used with default Scrapy's scheduler.

    """

    logger = logger

    def __init__(self, server, key, debug=False, mysql=None, spider_name=None):
        """Initialize the duplicates filter.

        Parameters
        ----------
        server : redis.StrictRedis
            The redis server instance.
        key : str
            Redis key Where to store fingerprints.
        debug : bool, optional
            Whether to log filtered requests.

        """
        self.server = server
        self.key = key
        self.debug = debug
        self.mysql = mysql
        self.logdupes = True
        self.spider_name = spider_name
        self.bitsize = 1 << 32
        self.seeds = [5, 7, 11, 13, 31, 37, 61, 67, 71, 73]
        self.hashfunc = []
        for seed in self.seeds:
            self.hashfunc.append(GenHash(self.bitsize, seed))
        self.mysqlupdate = False

    def update_bloom_from_mysql(self):
        self.logger.info("FILTER UPDATE START");

        db = MySQLdb.connect(
            host=self.mysql['host'],
            user=self.mysql['user'],
            passwd=self.mysql['passwd'],
            db=self.mysql['db'],
            charset='utf8'
        )
        cursor = db.cursor()

        select_url = '''select url from %s where url like '%%%s%%' ''' % (self.mysql['table'], domains[self.spider_name])
        self.logger.info(select_url)
        cursor.execute(select_url)
        has_urls = cursor.fetchall()
        db.commit()
        db.close()

        for url in has_urls:
            try:
                url = str(url[0]).strip()
                if url == '':
                    continue
            except Exception as e:
                self.logger.info("URL LOAD ERROR: " + url[0])
                continue
            for hf in self.hashfunc:
                self.server.setbit(self.key, hf.hash(url), 1)

        self.logger.info("FILTER UPDATE DONE")

    @classmethod
    def from_settings(cls, settings):
        """Returns an instance from given settings.

        This uses by default the key ``dupefilter:<timestamp>``. When using the
        ``scrapy_redis.scheduler.Scheduler`` class, this method is not used as
        it needs to pass the spider name in the key.

        Parameters
        ----------
        settings : scrapy.settings.Settings

        Returns
        -------
        RFPDupeFilter
            A RFPDupeFilter instance.


        """
        server = get_redis_from_settings(settings)

        # XXX: This creates one-time key. needed to support to use this
        # class as standalone dupefilter with scrapy's default scheduler
        # if scrapy passes spider on open() method this wouldn't be needed
        # TODO: Use SCRAPY_JOB env as default and fallback to timestamp.
        key = defaults.DUPEFILTER_KEY

        debug = settings.getbool('DUPEFILTER_DEBUG')

        mysql = {}
        mysql['host'] = settings.get('MYSQL_HOST')
        mysql['user'] = settings.get('MYSQL_USER')
        mysql['passwd'] = settings.get('MYSQL_PASSWD')
        mysql['db'] = settings.get('MYSQL_DB')
        mysql['table'] = setting.get('MYSQL_TABLE')

        return cls(server, key=key, debug=debug, mysql=mysql)

    @classmethod
    def from_crawler(cls, crawler):
        """Returns instance from crawler.

        Parameters
        ----------
        crawler : scrapy.crawler.Crawler

        Returns
        -------
        RFPDupeFilter
            Instance of RFPDupeFilter.

        """
        return cls.from_settings(crawler.settings)

    def request_seen(self, request):
        """
        Return True if url has been seen.

        """
        if not self.mysqlupdate:
            self.update_bloom_from_mysql()
            self.mysqlupdate = True
        ret = 1
        locs = []
        url = request.url
        for hf in self.hashfunc:
            locs.append(hf.hash(url))
            ret = ret & self.server.getbit(self.key, locs[-1])

        if not ret:
            for loc in locs:
                self.server.setbit(self.key, loc, 1)
        return ret

    def request_fingerprint(self, request):
        """
        Return the url fingerprint.

        """
        url = request.url
        fp = hashlib.sha1()
        fp.update(to_bytes(canonicalize_url(url)))
        fp = fp.hexdigest()
        return fp

    def close(self, reason=''):
        """Delete data on close. Called by Scrapy's scheduler.

        Parameters
        ----------
        reason : str, optional

        """
        self.clear()

    def clear(self):
        """Clears fingerprints data."""
        self.server.delete(self.key)

    def log(self, request, spider):
        """Logs given request.

        Parameters
        ----------
        request : scrapy.http.Request
        spider : scrapy.spiders.Spider

        """
        if self.debug:
            msg = "Filtered duplicate request: %(request)s"
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
        elif self.logdupes:
            msg = ("Filtered duplicate request %(request)s"
                   " - no more duplicates will be shown"
                   " (see DUPEFILTER_DEBUG to show all duplicates)")
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
            self.logdupes = False
