from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import Jobs24Item
from scrapy.loader import ItemLoader


class Jobs24Spider(CrawlSpider):
    name = "jobs24"
    allowed_domains = [
        "www.jobs24.co.uk",
        "www.nw1jobs.com",
        "www.y1jobs.com",
        "www.ne1jobs.com",
        "www.l1jobs.com",
        "www.se1jobs.com",
        "www.sw1jobs.com",
        "www.wm1jobs.com",
        "www.w1jobs.com",
        "www.em1jobs.com",
        "www.ea1jobs.com",
        "www.ox1jobs.com",
        "www.s1jobs.com",
    ]
    start_urls = [
        "https://www.jobs24.co.uk/jobs/",
        "https://www.nw1jobs.com/jobs/",
        "https://www.y1jobs.com/jobs/",
        "https://www.ne1jobs.com/jobs/",
        "https://www.l1jobs.com/jobs/",
        "https://www.se1jobs.com/jobs/",
        "https://www.sw1jobs.com/jobs/",
        "https://www.wm1jobs.com/jobs/",
        "https://www.w1jobs.com/jobs/",
        "https://www.em1jobs.com/jobs/",
        "https://www.ea1jobs.com/jobs/",
        "https://www.ox1jobs.com/jobs/",
        "https://www.s1jobs.com/jobs/",
    ]

    rules = (
        Rule(LinkExtractor(allow=(r"page="))),
        Rule(LinkExtractor(allow=(r"/jobs/"))),
        Rule(LinkExtractor(allow=(r"/job/")), callback="parse_item"),
    )

    def parse_item(self, response):
        l = ItemLoader(item=Jobs24Item(), response=response)
        l.add_value("job_id", response.url)
        l.add_value("link", response.url)
        l.add_css("title", "h1.jobDetails__title")
        l.add_css("company", "p.jobDetails")
        l.add_css("date_posted", "p.small")
        l.add_value("location", response.url)
        l.add_css("description", "div.jobDescription")
        return l.load_item()
