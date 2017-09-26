#coding=utf-8
import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
import re
from magic.items import MagicItem

class BDSpider(scrapy.Spider):
    name = 'bd_spider'
    allowed_domain = ['bookdepository.com']
    root_url = 'https://www.bookdepository.com'
    start_urls = [
        'https://www.bookdepository.com/'
    ]
    def parse(self, response):
        '''
        categories_tags = response.css('ul.category-dropdown-list a::attr(href)').extract()

        for tag in categories_tags:
            url = self.root_url + tag + '/browse/viewmode/all'
        #    self.logger.info("new dict url: " + url)
            yield Request(url, callback=self.parse_dict)
        '''

        age_tags = response.css('ul.age-range-dropdown-list a::attr(href)').extract()
        for tag in age_tags:
            age_range = '-'.join(tag.split('-')[-2:])
            url = self.root_url + tag
            self.logger.info("new age range %s url %s" % (age_range, url))
            yield Request(url, callback=self.parse_dict, meta={'age_range': age_range}, priority=2)

    def parse_dict(self, response):
        new_items = response.css('div.item-info .title a::attr(href)').extract()
        for item in new_items:
            url = self.root_url + item
            yield Request(url, callback=self.parse_item, priority=1, meta=response.meta)

        next_page = response.css('#next-top a::attr(href)').extract_first()
        if next_page == None:
            return
        next_page = self.root_url + next_page

        yield Request(next_page, callback=self.parse_dict, meta=response.meta, priority=2)

    def parse_item(self, response):

        item = MagicItem()

        try:
            item['name'] = response.css('div.item-info h1::text').extract_first().strip()
        except Exception as e:
            return

        item['url'] = response.url

        try:
            item['authors'] = ','.join(response.css('.author-info a::text').extract())
        except Exception as e:
            pass

        try:
            item['categories'] = '>'.join(response.css('.breadcrumb a::text').extract()).strip()
        except Exception as e:
            pass

        try:
            item['image'] = response.css('.item-img-content img::attr(src)').extract_first().strip()
        except Exception as e:
            pass

        try:
            item['summery'] =  response.css('.item-excerpt::text').extract_first().strip()
        except Exception as e:
            pass

        try:
            item['language'] = response.css('a[itemprop="inLanguage"]::text').extract_first().strip()
        except Exception as e:
            pass

        try:
            item['pagenum'] = response.css('span[itemprop="numberOfPages"]::text').extract_first().split(' ')[0].strip()
        except Exception as e:
            pass

        try:
            item['isbn'] = response.css('span[itemprop="isbn"]::text').extract_first().strip()
        except Exception as e:
            pass

        try:
            item['publisher'] = response.css('a[itemprop="publisher"]::text').extract_first().strip()
        except Exception as e:
            pass

        try:
            item['datePubed'] = response.css('span[itemprop="datePublished"]::text').extract_first().strip()
        except Exception as e:
            pass

        try:
            detail = response.css('.biblio-info').xpath('string(.)')
            try:
                dim_raw = detail.re('Dimensions([\n\s\tA-Za-z0-9]*)')[0]
                dim_raw = dim_raw.replace(' ', '')
                dim_raw = dim_raw.replace('\t', '')
                dim_raw = dim_raw.replace('\n', '')
                item['dimension'] = dim_raw
            except Exception as e:
                pass

            try:
                format_raw = detail.re('Format([\n\s\tA-Za-z]*)')[0]
                format_raw = format_raw.replace(' ', '')
                format_raw = format_raw.replace('\t', '')
                format_raw = format_raw.replace('\n', '')
                item['format'] = format_raw
               
            except Exception as e:
                pass
        except Exception as e:
            pass

        if response.meta.has_key('age_range'):
            item['age_range'] = response.meta['age_range']

        return item
