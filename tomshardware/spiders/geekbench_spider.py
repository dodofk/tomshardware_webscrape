import scrapy
from tomshardware.items import GeekBenchItem


class GeekBench_Spider(scrapy.Spider):
    name = "geekbench"

    def start_requests(self):
        url = "https://browser.geekbench.com/processor-benchmarks"
        yield scrapy.Request(url=url + "#single-core", callback=self.parse)

    def parse(self, response):
        for row in response.xpath('//div[@id="single-core"]//table[@class="table benchmark-chart-table"]/tbody/tr'):

            yield GeekBenchItem(
                name=row.xpath('td[@class="name"]/a/text()').get().strip(),
                frequency=row.xpath('td[@class="name"]/div[@class="description"]/text()').get().split("(")[0],
                bench_type="single_core",
                num_cores=row.xpath('td[@class="name"]/div[@class="description"]/text()').get().split("(")[0],
                score=row.xpath('td[@class="score"]/text()').get().strip(),
            )

        for row in response.xpath('//div[@id="multi-core"]//table[@class="table benchmark-chart-table"]/tbody/tr'):
            yield GeekBenchItem(
                name=row.xpath('td[@class="name"]/a/text()').get().strip(),
                frequency=row.xpath('td[@class="name"]/div[@class="description"]/text()').get().split("(")[0],
                bench_type="multi_core",
                num_cores=row.xpath('td[@class="name"]/div[@class="description"]/text()').get().split("(")[0],
                score=row.xpath('td[@class="score"]/text()').get().strip(),
            )
