import scrapy
import xml.etree.ElementTree as ET
from tomshardware.items import VideocardzItem
import gzip
import requests


# need to crawl news, press-release, posts
class VideoCardz_Spider(scrapy.Spider):
    name = "videocardz"

    def start_requests(self):
        # Get the sitemap info of news from start_year to end_year
        sitemap_url = "https://videocardz.com/sitemap.xml"
        r = requests.get(sitemap_url)
        root = ET.fromstring(r.content)
        loc_elements = root.findall("{*}sitemap/{*}loc")
        urls = [loc.text for loc in loc_elements]

        for url in urls:
            if "pt-newz" in url or "pt-press_release" in url or "pt-post" in url:
                article_r = requests.get(url)
                article_root = ET.fromstring(article_r.content)
                article_loc_elements = article_root.findall("{*}url/{*}loc")
                article_urls = [loc.text for loc in article_loc_elements]

                for article_url in article_urls:
                    yield scrapy.Request(url=article_url, callback=self.parse_article)

    def parse_article(self, response):
        # print(response.url)
        authors = response.xpath(
            '//div[@class="socialbar clearfix"]/div/text()'
        ).getall()

        while " " in authors:
            authors.remove(" ")

        content = response.xpath(
            '//article[@id="videocardz-article"]//p//text() | //article[@id="videocardz-article"]/h2/text() '
            '|//article[@id="videocardz-article"]/ul/li//text() | //article[@id="videocardz-article"]/h3/text()'
        ).getall()

        while " " in content:
            content.remove(" ")

        yield VideocardzItem(
            tag="\n".join(
                [response.xpath('//div[@class="section-class"]/a/div/text()').get()]
                + response.xpath('//div[@class="topic-class"]/a/div/text()').getall()
            ),
            title=response.css("h1::text").get(),
            dates=response.xpath('//div[@id="lastupdate"]/text()')
            .get()
            .split(": ")[1]
            .replace(" \xa0", ""),
            author="\n".join(authors),
            content=" ".join(content),
            url=response.url,
        )
