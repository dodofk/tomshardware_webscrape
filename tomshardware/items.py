import scrapy
from scrapy import Field


class TomshardwareItem(scrapy.Item):
    tag = Field()
    title = Field()
    author = Field()
    content = Field()
    dates = Field()
    url = Field()


class WCCFItem(scrapy.Item):
    tag = Field()
    title = Field()
    author = Field()
    content = Field()
    dates = Field()
    url = Field()


class NewsUrlItem(scrapy.Item):
    news_url = Field()
