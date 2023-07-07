import scrapy
from tomshardware.items import TomshardwareItem, NewsUrlItem


class TomshardwareSpider(scrapy.Spider):
    name = "tomshardware"
    # start_urls = []

    def start_requests(self):
        domain = "https://www.tomshardware.com/archive"
        years = [str(year) for year in range(2020, 2023)]
        months = [str(month) for month in range(1, 13)]

        urls = [f"{domain}/{year}/{month.zfill(2)}" for year in years for month in months]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        article_urls = response.css("li.day-article a::attr(href)").getall()
        for article_url in article_urls:
            yield NewsUrlItem(
                news_url=article_url,
            )
            yield scrapy.Request(url=article_url, callback=self.parse_article)

    def parse_article(self, response):
        tags = response.css(".tag::text").getall()
        contents = response.xpath(
            '//div[@id="article-body"]/p/text() | //div[@id="article-body"]/ul/li//text()'
        ).getall()

        yield TomshardwareItem(
            tag=[tag + "\n" for tag in tags],
            title=response.css("h1::text").get(),
            author=response.xpath('//*[@id="slice-container-authorByline"]/div/div/span/a/text()').get(),
            dates=response.xpath('//time[@class="relative-date"]/@datetime').get(),
            content=" ".join(contents),
            url=response.url,
        )
