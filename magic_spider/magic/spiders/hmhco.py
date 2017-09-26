#coding=utf-8
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from magic.items import MagicItem

class HmhcoSpider(CrawlSpider):
    name = 'hmhco_spider'
    allowed_domain = ['hmhco.com']
    root_url = 'http://www.hmhco.com'
    start_urls = [
        'http://www.hmhco.com/at-home/shop-by-age/',
        'https://www.hmhco.com/at-home/shop-by-category/browse-all-categories/'
    ]

    rules = (
        Rule(LinkExtractor(allow=('.*/shop/books/.*')),
                follow=False,
                callback='parse_item'
        ),
        Rule(LinkExtractor(allow=('.*/at-home/shop-by-age/.*'))),
        Rule(LinkExtractor(allow=('.*/at-home/shop-by-category/.*'))),
    )

    def parse_item(self, response):

        item = MagicItem()

        try:
            item['name'] = response.css('h1#body1_0_headerText::text').extract_first()
        except Exception as e:
            return 

        item['url'] = response.url
        item['language'] = 'English'
        item['publisher'] = 'hmhco'

        r = re.match(r'.*shop/books/.*/([0-9]{13}).*', response.url)
        if r != None:
            item['isbn'] = r.group(1)

        try:
            item['format'] = response.css('li#body1_0_formatSpan::text').extract_first().split(':')[-1].strip()
        except Exception as e:
            pass

        try:
            item['pagenum'] = response.css('li#body1_0_noOfPagesSpan::text').extract_first().split(':')[-1].strip()
        except Exception as e:
            pass

        try:
            item['datePubed'] = response.css('li#body1_0_publicationDateSpan::text').extract_first().split(':')[-1].strip()
        except Exception as e:
            pass

        try:
            item['age_range'] = response.css('li#body1_0_ageRangeSpan::text').extract_first().split(':')[-1].strip()
        except Exception as e:
            pass

        try:
            item['authors'] = ','.join(response.css('p.writer a::text').extract())
        except Exception as e:
            pass

        try:
            item['categories'] = ','.join(response.css('div#body1_0_subjectDiv a::text').extract())
        except Exception as e:
            pass

        try:
            item['image'] = root_url + response.css('img#body1_0_bookImage::attr(src)').extract_first()
        except Exception as e:
            pass

        try:
            item['summery'] = ''.join(response.css('div#productDescrip div')[-1].css('::text').extract()).strip()
        except Exception as e:
            pass

        try:
            item['price'] = ''.join(response.css('.product-item-price span::text').extract()).strip()
        except Exception as e:
            pass

        return item
