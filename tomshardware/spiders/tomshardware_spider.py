import scrapy
from tomshardware.items import TomshardwareItem


class TomshardwareSpider(scrapy.Spider):
    name = "tomshardware"
    # start_urls = []

    def start_requests(self):
        domain = "https://www.tomshardware.com/archive"
        years = ["2023"]
        months = ["1", "2", "3", "4", "5"]

        urls = [f"{domain}/{year}/{month.zfill(2)}" for year in years for month in months]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        article_urls = response.css("li.day-article a::attr(href)").getall()
        for article_url in article_urls:
            yield scrapy.Request(url=article_url, callback=self.parse_article)


    def parse_article(self, response):
        tags = response.css(".tag::text").getall()

        content_sections = response.css(".content-wrapper")
        content_paragraphs = content_sections.css("p::text").getall()

        yield TomshardwareItem(
            tag=[tag + "\n" for tag in tags],
            title=response.css("h1::text").get(),
            author=response.xpath('//*[@id="slice-container-authorByline"]/div/div/span/a/text').get(),
            content="\n".join(content_paragraphs),
        )
