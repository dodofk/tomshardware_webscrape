import scrapy
from scrapy import Field


class TomshardwareItem(scrapy.Item):
    tag = Field()
    title = Field()
    author = Field()
    content = Field()
