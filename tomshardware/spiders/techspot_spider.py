import scrapy
import xml.etree.ElementTree as ET
from tomshardware.items import TechspotItem
import gzip
import requests
import datetime


class TechspotSpider(scrapy.Spider):
    name = "techspot"

    # For strategy 'all', the spider will crawl all the data
    def __init__(self, strategy="all", update_date=None, *args, **kwargs):
        super(TechspotSpider, self).__init__(*args, **kwargs)
        assert strategy in [
            "all",
            "update",
        ], "strategy must be one of ['all', 'update']"
        self.strategy = strategy
        self.start_year = 2010
        self.end_year = datetime.date.today().year

        if update_date is None:
            self.update_date = str(datetime.date.today())
        else:
            self.update_date = update_date

    def start_requests(self):
        if self.strategy == "all":
            # years = [str(year) for year in range(self.start_year, self.end_year)]
            url_list = []
            # for year in years:
            #     url = f"https://www.techspot.com/sitemap/news_{year}.xml.gz"
            #     url_list.append(url)
            #
            # url_list.append("https://www.techspot.com/sitemap/news_this_year.xml.gz")
            # url_list.append("https://www.techspot.com/sitemap/reviews_all.xml.gz")

            namespaces = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            for _url in url_list:
                r = requests.get(_url)
                # print(_url)
                # print(r)
                # print(r.content)
                gz_file = gzip.decompress(r.content)
                root = ET.fromstring(gz_file)
                loc_elements = root.findall(".//ns:url/ns:loc", namespaces)
                urls = [loc.text for loc in loc_elements]

                for url in urls:
                    if "/downloads/" in url:
                        self.logger.info("Error in bad url: ", _url, url)
                        continue
                    yield scrapy.Request(url=url, callback=self.parse_article)

            # r = requests.get("https://www.techspot.com/sitemap/features_category.xml.gz")
            # gz_file = gzip.decompress(r.content)
            # root = ET.fromstring(gz_file)
            # loc_elements = root.findall(".//ns:url/ns:loc", namespaces)
            # urls = [loc.text for loc in loc_elements]
            #
            # for url in urls:
            #     if url == "https://www.techspot.com/features/":
            #         continue
            #     yield scrapy.Request(url=url, callback=self.parse_feature)

            r = requests.get("https://www.techspot.com/sitemap/drivers_all.xml.gz")
            gz_file = gzip.decompress(r.content)
            root = ET.fromstring(gz_file)
            loc_elements = root.findall(".//ns:url/ns:loc", namespaces)
            urls = [loc.text for loc in loc_elements]

            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse_driver)

            r = requests.get("https://www.techspot.com/sitemap/downloads_all.xml.gz")
            gz_file = gzip.decompress(r.content)
            root = ET.fromstring(gz_file)
            loc_elements = root.findall(".//ns:url/ns:loc", namespaces)
            urls = [loc.text for loc in loc_elements]

            for url in urls:
                # print("hi")
                yield scrapy.Request(url=url, callback=self.parse_download)
        elif self.strategy == "update":
            yield self.start_requests_update()

    def start_requests_update(self):
        pass

    # Since feature doesnot have entirely sitemap, it only have sitemap of urls
    # Therefore, we need to crawl the feature page and get the urls
    def parse_feature(self, response):
        urls = response.css("h3 a::attr(href)").getall()
        for url in urls:
            if "/downloads/" in url:
                self.logger.info("Error in bad url: ", response.url, url)
                continue
            yield scrapy.Request(url=url, callback=self.parse_article)

    def parse_article(self, response):
        yield TechspotItem(
            tag="\n".join(
                response.xpath('//ul[@class="category-chicklets"]/li/a/text()').getall()
            ),
            title=response.xpath('//section[@class="title-group"]/h1/text()')
            .get()
            .replace("\xa0", " ")
            if response.xpath('//section[@class="title-group"]/h1/text()')
            else "",
            subtitle=response.xpath('//section[@class="title-group"]/h2/text()')
            .get()
            .replace("\xa0", " ")
            if response.xpath('//section[@class="title-group"]/h2/text()')
            else "",
            author=response.xpath('//a[@id="author"]/text()').get()
            if response.xpath('//a[@id="author"]/text()').get()
            else response.xpath('//a[@rel="author"]/text()').get(),
            content=" ".join(
                response.xpath('//div[@class="articleBody"]/p//text()').getall()
            ),
            dates=response.xpath('//time[@pubdate="pubdate"]/@datetime').get(),
            url=response.url,
        )

    def parse_download(self, response):
        yield TechspotItem(
            tag="\n".join(
                response.xpath('//ul[@class="category-chicklets"]/li/a/text()').getall()
            ),
            title=response.xpath('//h1/text()')
            .get()
            .strip(),
            content=" ".join(
                response.xpath(
                    '//div[@itemprop="releaseNotes"]//p//text()'
                    '| //div[@itemprop="releaseNotes"]//ul/li//text()'
                    '| //div[@itemprop="releaseNotes"]//ul/li/strong//text()'
                    '| //div[@itemprop="releaseNotes"]//p/strong//text()'
                    '| //div[@itemprop="releaseNotes"]//h2//text()'
                    '| //div[@itemprop="releaseNotes"]//h3//text()'
                    '| //div[@itemprop="releaseNotes"]/text()'
                ).getall()
            ),
            dates=response.xpath('//time[@itemprop="dateModified"]/@datetime').get(),
            url=response.url,
        )

    def parse_driver(self, response):
        yield TechspotItem(
            tag="\n".join(
                response.xpath('//ul[@class="category-chicklets"]/li/a/text()').getall()
            ),
            title=response.xpath('//h1/text()')
            .get()
            .strip()
            .replace("\xa0", " "),
            content=" ".join(
                response.xpath(
                    '//div[@class="ps-item publisher-description"]//p//text() '
                    '| //div[@class="ps-item publisher-description"]//ul/li/text()'
                    '| //div[@class="ps-item publisher-description"]//p/strong//text()'
                    '| //div[@itemprop="releaseNotes"]/text()'
                ).getall()
            ),
            dates=response.xpath('//time[@itemprop="dateModified"]/@datetime').get(),
            url=response.url,
        )
