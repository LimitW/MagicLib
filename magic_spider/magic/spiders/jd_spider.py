#coding=utf-8
import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
import re
import json
from magic.items import MagicItem

class JDSpider(scrapy.Spider):

    dict_url = re.compile('.*list\.jd\.com.*')
    item_url = re.compile('.*item\.jd\.com.*')

    name = 'jd_spider'
    start_urls = [
        'http://book.jd.com/booksort.html'
    ]

    def parse(self, response):
        new_tags = response.css('.mc a::attr(href)').re('.*list\.jd\.com.*')
        for new_tag in new_tags:
            url = new_tag
            if new_tag[0:2] == '//':
                url = 'http:' + new_tag
            yield Request(url, callback=self.parse_dict)

    def parse_dict(self, response):
        if self.dict_url.match(response.url) == None:
            return

        new_tags = response.css('.p-name a::attr(href)').re('.*item\.jd\.com.*')
        for new_tag in new_tags:
            url = new_tag
            if new_tag[0:2] == '//':
                url = 'http:' + new_tag
            yield Request(url, callback=self.parse_item, priority=1)

        next_page = response.css('a.fp-next::attr(href)').extract_first()
        if next_page == None:
            return
        if next_page[0] == '/':
            next_page = 'http://list.jd.com' + next_page

        yield Request(next_page, callback=self.parse_dict)

    def parse_item(self, response):

        if self.item_url.match(response.url) == None:
            self.logger.error('error leaf url: ' + response.url)
            return

        item = MagicItem()

        try:
            item['name'] = response.xpath('//*[@id="name"]/h1/text()').extract_first()
        except Exception as e:
            return

        item['url'] = response.url

        try:
            item['authors'] = response.xpath('//*[@id="p-author"]')[0].xpath('string(.)').extract_first()
        except Exception as e:
            pass

        try:
            item['categories'] = response.xpath('//*[@id="root-nav"]/div/div')[0].xpath('string(.)').extract_first()
        except Exception as e:
            pass

        try:
            item['image'] = response.css('#spec-n1 img::attr(src)').extract_first()
            if item['image'][0:2] == '//':
                item['image'] = 'http:' + item['image']
        except Exception as e:
            pass

        try:
            item['summery'] = ''.join(response.css('.book-detail-content::text').extract())
        except Exception as e:
            pass

        try:
            detail = response.xpath('//*[@id="parameter2"]')[0].xpath('string(.)')[0]
            try:
                item['format'] = detail.re(u'包装：[\t\n\s]*[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff.0-9]+')[0][3:]
            except Exception as e:
                pass
            try:
                item['isbn'] = detail.re(u'ISBN：[\t\n\s]*[0-9]+')[0][5:]
            except Exception as e:
                pass
            try:
                item['dimension'] = detail.re(u'开本：[\t\n\s]*[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff.0-9]+')[0][3:]
            except Exception as e:
                pass
            try:
                item['datePubed'] = detail.re(u'出版时间：[\t\n\s]*[0-9\-\\\/]+')[0][5:]
            except Exception as e:
                pass
            try:
                item['language'] = detail.re(u'正文语种：[\t\n\s]*[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff.]+')[0][5:]
            except Exception as e:
                pass
            try:
                item['pagenum'] = detail.re(u'页数：[\t\n\s]*[0-9]+')[0][3:]
            except Exception as e:
                pass
            try:
                item['publisher'] = detail.re(u'出版社：[\t\n\s]*[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff.]+')[0][4:]
            except Exception as e:
                pass
            try:
                item['series'] = detail.re(u'丛书名：[\t\n\s]*[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff.0-9]+')[0][4:]
            except Exception as e:
                pass
            #item['age_range'] = None
        except Exception as e:
            pass

        for v in item:
            if item[v] != None:
                item[v] = item[v].replace(' ', '')
                item[v] = item[v].replace('\t', '')
                item[v] = item[v].replace('\n', '')

        return item
 
        match = re.match(r'.*item\.jd\.com\/([0-9]+).*', response.url)
        if not match:
            return item
        skuid = match.group(1)
        price_url = '''http://p.3.cn/prices/mgets?skuIds=J_%s''' % skuid

        return Request(price_url, callback=self.parse_price, meta={'item': item}, priority = 10)

    def parse_price(self, response):
        item = response.meta['item']
        try:
            detail = json.loads(response.body)
            item['price'] = detail[0]['p']
        except Exception as e:
            pass
        return item
