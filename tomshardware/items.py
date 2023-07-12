import scrapy
from scrapy import Field


class NewsItem(scrapy.Item):
    tag = Field()
    title = Field()
    author = Field()
    content = Field()
    dates = Field()
    url = Field()


# the following class are used to specify the item class for each feed
class TomshardwareItem(NewsItem):
    pass

class WCCFItem(NewsItem):
    pass


class TechspotItem(NewsItem):
    subtitle = Field()


class VideocardzItem(NewsItem):
    pass


class AnandtechItem(NewsItem):
    pass


class NewsUrlItem(scrapy.Item):
    news_url = Field()
