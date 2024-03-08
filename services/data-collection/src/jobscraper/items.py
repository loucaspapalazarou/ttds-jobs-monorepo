# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
import re
from urllib.parse import urlparse

TAG_RE = re.compile(r"<[^>]+>")


def mark_eurojobs(value):
    return "eurojobs-" + value


def url_to_id(url: str):
    parsed_url = urlparse(url)
    sld = parsed_url.netloc.split(".")[1]
    job_id = parsed_url.path.split("-")[-1]
    return f"{sld}-{job_id}"


def preprocess_text(value: str):
    return " ".join(
        TAG_RE.sub(" ", value)
        .replace("&nbsp;", " ")
        .replace("\xa0", " ")
        .replace("\t", "")
        .replace("\r", "")
        .replace("\n", "")
        .strip()
        .split()
    )


def string_to_date(s: str):
    return " ".join(s[s.find(",") + 1 :].split()[:2])


def link_to_location(url: str):
    domain_to_location = {
        "s1jobs.com": "Scotland",
        "y1jobs.com": "Yorkshire",
        "ne1jobs.com": "Northeast England",
        "l1jobs.com": "Liverpool",
        "se1jobs.com": "Southeast England",
        "sw1jobs.com": "Southwest England",
        "wm1jobs.com": "West Midlands",
        "w1jobs.com": "Wales",
        "em1jobs.com": "East Midlands",
        "ea1jobs.com": "East Anglia",
        "ox1jobs.com": "Oxfordshire",
        "jobs24.co.uk": "England & Wales",
    }
    domain = url.split("//")[-1].split("/")[0].removeprefix("www.")
    if domain in domain_to_location:
        return domain_to_location[domain]
    else:
        return ""


class Jobs24Item(scrapy.Item):
    job_id = scrapy.Field(
        input_processor=MapCompose(url_to_id),
        output_processor=TakeFirst(),
    )
    link = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    title = scrapy.Field(
        input_processor=MapCompose(preprocess_text),
        output_processor=TakeFirst(),
    )
    company = scrapy.Field(
        input_processor=MapCompose(preprocess_text),
        output_processor=TakeFirst(),
    )
    date_posted = scrapy.Field(
        input_processor=MapCompose(preprocess_text, string_to_date),
        output_processor=TakeFirst(),
    )
    location = scrapy.Field(
        input_processor=MapCompose(link_to_location),
        output_processor=TakeFirst(),
    )
    description = scrapy.Field(
        input_processor=MapCompose(preprocess_text),
        output_processor=TakeFirst(),
    )


class EurojobsItem(scrapy.Item):
    job_id = scrapy.Field(
        input_processor=MapCompose(mark_eurojobs),
        output_processor=TakeFirst(),
    )
    link = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    title = scrapy.Field(
        input_processor=MapCompose(preprocess_text),
        output_processor=TakeFirst(),
    )
    company = scrapy.Field(
        input_processor=MapCompose(preprocess_text),
        output_processor=TakeFirst(),
    )
    location = scrapy.Field(
        input_processor=MapCompose(preprocess_text),
        output_processor=TakeFirst(),
    )
    description = scrapy.Field(
        input_processor=MapCompose(preprocess_text),
        output_processor=TakeFirst(),
    )
    date_posted = scrapy.Field(
        input_processor=MapCompose(preprocess_text),
        output_processor=TakeFirst(),
    )
