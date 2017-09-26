#coding=utf-8
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from magic.items import MagicItem

class UsborneSpider(CrawlSpider):
    name = 'usborne_spider'
    allowed_domain = ['usborne.com']
    root_url = 'https://usborne.com/browse-books'
    start_urls = [
        'https://usborne.com/browse-books'
    ]

    rules = (
        Rule(LinkExtractor(allow=('.*/browse-books/catalogue/product/.*')), follow=False, callback='parse_item'),
        Rule(LinkExtractor(allow=('.*/browse-books/catalogue/.*'))),
    )

    def parse_item(self, response):

        item = MagicItem()

        try:
            item['name'] = response.css('h1[itemprop="name"]::text').extract_first()
        except Exception as e:
            return 

        item['url'] = response.url
        item['language'] = 'English'
        item['publisher'] = 'usborne'

        try:
            item['series'] = response.css('a.series::text').extract_first().strip()
        except Exception as e:
            pass

        try:
            item['authors'] = response.css('p.seriesAndOrAuthor a::text')[-1].extract().strip()
        except Exception as e:
            pass

        try:
            item['categories'] = '>'.join(response.css('nav#breadcrumb a::text').extract()[3:]).strip()
        except Exception as e:
            pass

        try:
            item['image'] = response.css('img[itemprop="image"]::attr(src)').extract_first()
        except Exception as e:
            pass

        try:
            item['summery'] = ''.join(response.css('div[itemprop="description"] p::text').extract()).strip()
        except Exception as e:
            pass

        try:
            item['price'] = response.css('p.formatDetails strong::text').extract_first()
        except Exception as e:
            pass

        try:
            detail = response.css('dl.bookInfo')
            d_key = detail.css('dt::text')
            d_val = detail.css('dd')
            for i in range(0, len(d_key)):
                key = d_key[i]
                t_key = key.extract().strip()
                if t_key == 'Age':
                    item['age_range'] = d_val[i].css('::text').extract_first()
                elif len(d_val[i].css('span')) > 0:
                    try:
                        item['format'] = d_key[i].extract().strip()
                    except Exception as e:
                        pass
                    try:
                        item['isbn'] = d_val[i].re('ISBN:[\n\r\t\s]*([0-9]+)')[0]
                    except Exception as e:
                        pass
                    try:
                        item['pagenum'] = d_val[i].re('Extent:[\n\r\t\s]*([0-9\t\sa-z]+)')[0]
                    except Exception as e:
                        pass
                    try:
                        item['dimension'] = d_val[i].re('Dimensions:[\n\r\t\s]*([0-9a-z\t\s]+)')[0]
                    except Exception as e:
                        pass
        except Exception as e:
            pass

        return item
