import scrapy
from tomshardware.items import WCCFItem
from datetime import datetime
import feedparser


# feed : https://wccftech.com/feed/
# for wccf, it can just run a daily scheduled time without issue
class WCCFSpider(scrapy.Spider):
    name = "wccftech"

    custom_user_agents = (
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    )

    def __init__(self, strategy="all", *args, **kwargs):
        super(WCCFSpider, self).__init__(*args, **kwargs)
        assert strategy in ["all", "update"], "strategy must be all or update"

        self.strategy = strategy


    def start_requests(self):
        if self.strategy == "all":

            headers = {
                "User-Agent": self.custom_user_agents,
            }

            yield scrapy.Request(
                url="https://wccftech.com/category/news/page/2/",
                headers=headers,
                callback=self.parse_pages,
            )
        elif self.strategy == "update":
            feed = feedparser.parse("https://wccftech.com/feed/")

            urls = []
            for entry in feed.entries:
                urls.append(entry.link)

            headers = {
                "User-Agent": self.custom_user_agents,
            }

            for url in urls:
                yield scrapy.Request(url=url, headers=headers, callback=self.parse_article)

    def parse_pages(self, response):
        last_page = response.xpath('//div[@class="pagination-last"]/a/span/text()').get()
        domain = "https://wccftech.com/category/news/page"
        pages = list(range(1, int(last_page) + 1))

        headers = {
            "User-Agent": self.custom_user_agents,
        }

        urls = [f"{domain}/{p}/" for p in pages]
        for url in urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response):
        article_urls = response.css("h3 a::attr(href)").getall()
        headers = {
            "User-Agent": self.custom_user_agents,
        }

        for article_url in article_urls:
            yield scrapy.Request(
                url=article_url, headers=headers, callback=self.parse_article
            )

    def parse_article(self, response):
        yield WCCFItem(
            tag=response.xpath(
                '//div[@class="badge gradient-primary"]/span/a/text()'
            ).get(),
            title=response.css("h1::text").get(),
            author=response.xpath('//meta[@name="author"]/@content').get(),
            content=" ".join(
                response.xpath(
                    '//div[@class="post"]/p/text() | //div[@class="post"]/p/em/text() |'
                    ' //div[@class="post"]/p/a/text() | //div[@class="post"]/p/strong/text()'
                ).getall()
            ),
            dates=response.xpath('//div[@class="meta"]/time/text()').get(),
            url=response.url,
        )
