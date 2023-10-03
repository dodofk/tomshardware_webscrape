import scrapy
import logging


class SeekingAlphaSpider(scrapy.Spider):
    name = "seekingalpha"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/80.0.3987.149 Safari/537.36"
        }

    # i want to crawl the earnings call part
    def start_requests(self):
        companys = [
            "amd",
            "intc",
            "nvda",
        ]

        for company in companys:
            logging.log(logging.DEBUG, f"Requesting url for {company} transcript")

            url = f"https://seekingalpha.com/symbol/{company}/earnings/transcripts?page=1"

            yield scrapy.Request(
                url=url,
                callback=self.parse_company_urls,
                meta={
                    "company": company,

                },
            )

    def parse_company_urls(self, response):
        if response.xpath("//div[@data-test-id='empty-state-message']"):
            return
        urls = response.xpath(
            "//a[@data-test-id='post-list-item-title']/@href"
        ).getall()
        titles = response.xpath(
            "//a[@data-test-id='post-list-item-title']/text()"
        ).getall()
        dates = response.xpath(
            "//span[@data-test-id='post-list-date']/text()"
        ).getall()

        for (url, title, date) in zip(urls, titles, dates):
            yield scrapy.Request(
                url=f"https://seekingalpha.com{url}",
                callback=self.parse_transcript,
                meta={
                    "company": response.meta["company"],
                    "title": title,
                    "date": date,
                },
            )

    def parse_transcript(self, response):
        company_participants_path = response.xpath("//p[strong='Company Participants']")
        followings = company_participants_path.xpath(
            "following-sibling::p"
        )

        company_participants = list()
        for idx, following in enumerate(followings):
            if following.xpath("strong[normalize-space(.)='Conference Call Participants']"):
                followings = followings[idx + 1:]
                break
            company_participants.append(following.xpath("normalize-space()").get())

        call_participants = list()
        for idx, following in enumerate(followings):
            if following.xpath("strong"):
                followings = followings[idx: ]
                break
            call_participants.append(following.xpath("normalize-space()").get())

        company_content = list()
        for idx, following in enumerate(followings):
            if following.xpath("strong[normalize-space(.)='Question-and-Answer Session']"):
                followings = followings[idx + 1:]
                break
            company_content.append(following.xpath("normalize-space()").get())

        company_qa = list()
        speaker, content = "", ""
        for idx, following in enumerate(followings):
            if following.xpath("strong"):
                company_qa.append((speaker, content))
                speaker, content = "", ""
                speaker = following.xpath("normalize-space()").get()
            else:
                if content == "":
                    content = following.xpath("normalize-space()").get()
                else:
                    content += following.xpath("normalize-space()").get()

        company_qa.append((speaker, content))
        company_qa = [f"({speaker},{content})" for speaker, content in company_qa if speaker != ""]
        yield {
            "url": response.url,
            "company": response.meta["company"],
            "company_participants": company_participants,
            "other_participants": call_participants,
            "CONT_CO": " ".join(
                company_content
            ),
            "CONT_QA": ",".join(
                company_qa
            ),
            "title": response.meta["title"],
            "date": response.meta["date"],
        }
