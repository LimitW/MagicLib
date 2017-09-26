#coding=utf-8
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from magic.items import MagicItem

class SchoSpider(CrawlSpider):
    name = 'scho_spider'
    allowed_domain = ['shop.scholastic.co.uk']
    root_url = 'https://shop.scholastic.co.uk/'
    start_urls = [
        'https://shop.scholastic.co.uk/'
    ]

    rules = (
        Rule(LinkExtractor(allow=('.*/products/*')),
                follow=False,
                callback='parse_item'
        ),
        Rule(LinkExtractor(allow=('.*/search/search.*'))
        ),
    )

    def parse_item(self, response):

        item = MagicItem()

        try:
            item['name'] = response.css('span[itemprop="name"]::text').extract_first()
        except Exception as e:
            return

        item['url'] = response.url
        item['language'] = 'English'

        try:
            item['authors'] = ','.join(response.css('div#product-title h2 a::text').extract()).strip()
        except Exception as e:
            pass

        try:
            cates = response.css('div.categories a::text').extract()
            undup_cates = list(set(cates))
            item['categories'] = ','.join(undup_cates)
        except Exception as e:
            pass

        try:
            item['image'] = response.css('div.product-image a::attr(href)').extract_first()
        except Exception as e:
            pass

        try:
            item['summery'] = response.css('div[itemprop="description"] p::text').extract_first()
        except Exception as e:
            pass

        try:
            currency = response.css('span[itemprop="priceCurrency"]::text').extract_first()
            price = response.css('span[itemprop="price"]::text').extract_first()
            item['price'] = currency + price
        except Exception as e:
            pass

        try:
            item['age_range'] = response.css('p.age-rating a::text').re('[0-9]+[^a-zA-Z0-9]*[0-9]*').strip()
        except Exception as e:
            pass

        try:
            detail = response.css('div.product-details')
            d_key = detail.css('h6::text')
            d_val = detail.css('p')
            mapper = {'Format':'format', 'ISBN':'isbn', 'Publisher': 'publisher', 'Date published': 'DatePubed'}
            for i in range(0, len(d_key)):
                key = d_key[i]
                t_key = key.extract().strip()
                if mapper.has_key(t_key):
                    try:
                        item[mapper[t_key]] = d_val[i].css('::text').extract_first().strip()
                    except Exception as e:
                        pass
        except Exception as e:
            pass

        return item
