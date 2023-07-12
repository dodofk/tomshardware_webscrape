import scrapy
from tomshardware.items import AnandtechItem
import json


class Anandtech_Spider(scrapy.Spider):
    name = "anandtech"

    def __init__(self, strategy="all", n=20000, *args, **kwargs):
        super(Anandtech_Spider, self).__init__(*args, **kwargs)
        assert strategy in ["all", "update"], "strategy must be all or update"

        with open("meta.json", "r") as f:
            self.meta = json.load(f)
            self.news_id = self.meta["anandtech"]

        if strategy == "all":
            self.start_id = 1
            self.end_id = n
            self.high_id = 0
        # we assume our data update daily
        elif strategy == "update":
            self.start_id = self.news_id + 1
            self.end_id = self.news_id + 100
            self.high_id = self.news_id

    def start_requests(self):
        for i in range(self.start_id, self.end_id):
            yield scrapy.Request(
                url=f"https://www.anandtech.com/show/{i}",
                callback=self.parse,
                meta={"id": i},
            )
        #
        # start_url = f"https://www.anandtech.com/show/{self.news_id}"
        # yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response):
        if (
            response.xpath('//div[@class="generic_cont general_form"]/h2/text()').get()
            == "Sorry, the content you requested was not found."
        ):
            return

        if response.url == "https://www.anandtech.com/":
            return

        yield AnandtechItem(
            tag="\n".join(
                response.xpath('//div[@class="blog_top_left"]/ul/li//text()').getall()[
                    1:
                ]
            ),
            title=response.css("h1::text").get(),
            author=response.xpath(
                '//div[@class="blog_top_left"]/span/a[@class="b"]/text()'
            ).get(),
            content=" ".join(
                response.xpath('//div[@class="articleContent"]//text()').getall()
            ),
            dates=response.xpath('//div[@class="blog_top_left"]//em/text()').get(),
            url=response.url,
        )
        self.high_id = response.meta["id"]

    def closed(self, reason):
        if reason == "finished":
            self.meta["anandtech"] = self.high_id
            with open("meta.json", "w") as f:
                json.dump(self.meta, f, indent=4)
