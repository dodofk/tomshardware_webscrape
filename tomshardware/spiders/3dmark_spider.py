# schema: product name
#   rank starrating msrpprice 3dmarkgraphic score popularity

# url: benchmarks.ul.com/compare/best-gpus
import scrapy
from tomshardware.items import Mark3DItem


class Mark3D_Spider(scrapy.Spider):
    name = "3dmark"

    def start_requests(self):
        url = "https://benchmarks.ul.com/compare/best-gpus"

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for row in response.xpath(
            '//table[@class="navigationtable performancechart"]/tbody/tr'
        ):
            yield Mark3DItem(
                name=row.xpath('td/a[@class="OneLinkNoTx"]/text()').get(),
                rank=row.xpath('td[@class="order-cell"]/text()').get(),
                star=len(
                    row.xpath(
                        'td/div[@class="starRating clearfix"]/span[@class="icon-starConverted full"]'
                    ).getall()
                ),
                msrpprice=row.xpath('td[@class="list-tiny-none"]/span/div/text()')
                .get()
                .strip()
                if row.xpath('td[@class="list-tiny-none"]/span/div/text()').get()
                else None,
                score=row.xpath('td[@class="small-pr1"]/div/div/span/text()')
                .get()
                .strip()
                if row.xpath('td[@class="small-pr1"]/div/div/span/text()').get()
                else None,
                popularity=row.xpath(
                    'td[@class="list-medium-none"]/div/div/span/text()'
                ).get(),
            )
