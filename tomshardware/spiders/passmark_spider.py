import scrapy
from tomshardware.items import PassMarkCpuItem, PassMarkGpuItem


class PassmarkSpider(scrapy.Spider):
    name = "passmark"

    def __init__(self, segment="cpu", *args, **kwargs):
        super(PassmarkSpider, self).__init__(*args, **kwargs)
        assert segment in ["cpus", "gpus"], "segment must be either cpu or gpu"
        self.segment = segment

    def start_requests(self):
        levels = [
            "high_end",
            "mid_range",
            "midlow_range",
            "low_end",
        ]

        for level in levels:
            if self.segment == "cpus":
                url = f"https://www.cpubenchmark.net/{level}_cpus.html"
            elif self.segment == "gpus":
                url = f"https://www.videocardbenchmark.net/{level}_gpus.html"
            else:
                url = None
            yield scrapy.Request(
                url=url, callback=self.parse, cb_kwargs={"level": level}
            )

    def parse(self, response, level):
        if self.segment == "cpus":
            for row in response.xpath('//div[@id="mark"]//ul[@class="chartlist"]/li'):
                details = row.xpath("span/@onclick").get()

                details = details.split("(")[1].split(",")[1:]
                rank = details[0].strip()
                samples = details[1].strip()
                cores = int(details[2].strip())
                threads = int(details[3].strip()) * cores

                if details[-2].strip() != "null":
                    add_cores = int(eval(details[-2].strip()))
                    add_threads = int(eval(details[-1].split(")")[0].strip()))

                    cores += add_cores
                    threads += add_threads * add_cores

                yield PassMarkCpuItem(
                    name=row.xpath('a/span[@class="prdname"]/text()').get(),
                    level=level,
                    segment=self.segment,
                    rank=rank,
                    sample=samples,
                    cores=cores,
                    threads=threads,
                    score=row.xpath('a/span[@class="count"]/text()').get(),
                    price=row.xpath('a/span[@class="price-neww"]/text()').get(),
                )
        elif self.segment == "gpus":
            for row in response.xpath('//div[@id="mark"]//ul[@class="chartlist"]/li'):
                details = row.xpath("span/@onclick").get()

                details = details.split("(")[1].split(",")[1:]
                rank = details[0].strip()
                g2dmark = details[2].strip()
                samples = details[3].strip()
                maxtdp = details[-1].split(")")[0].strip()

                yield PassMarkGpuItem(
                    name=row.xpath('a/span[@class="prdname"]/text()').get(),
                    level=level,
                    segment=self.segment,
                    rank=rank,
                    g2dmark=g2dmark,
                    sample=samples,
                    score=row.xpath('a/span[@class="count"]/text()').get(),
                    maxtdp=maxtdp,
                    price=row.xpath('a/span[@class="price-neww"]/text()').get(),
                )
