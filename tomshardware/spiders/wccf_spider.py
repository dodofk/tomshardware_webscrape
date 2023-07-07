import scrapy
from tomshardware.items import WCCFItem


class WCCFSpider(scrapy.Spider):
    name = "wccftech"

    # custom_settings = {
    #     'DOWNLOAD_DELAY': 3,
    # }

    custom_user_agents = (
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    )

    def start_requests(self):
        domain = "https://wccftech.com/category/news/page"
        page = list(range(1, 500))

        headers = {
            "User-Agent": self.custom_user_agents,
        }
        urls = [f"{domain}/{p}/" for p in page]

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
