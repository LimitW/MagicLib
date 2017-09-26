# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MagicItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    authors = scrapy.Field()
    publisher = scrapy.Field()
    isbn = scrapy.Field()
    categories = scrapy.Field()
    series = scrapy.Field()
    pagenum = scrapy.Field()
    image = scrapy.Field()
    url = scrapy.Field()
    summery = scrapy.Field()
    datePubed = scrapy.Field()
    price = scrapy.Field()
    language = scrapy.Field()
    dimension = scrapy.Field()
    format = scrapy.Field()
    age_range = scrapy.Field()
