import os
import scrapy
import logging
import requests
import lxml.html
import math
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.item import Field
from datetime import datetime


class TescoOfferItem(scrapy.Item):
    productid = Field()
    imgsrc90 = Field()
    imgsrc110 = Field()
    imgsrc540 = Field()
    imgsrc225 = Field()
    productdesc = Field()
    offerdesc = Field()
    validitydesc = Field()
    offerStart = Field()
    offerEnd = Field()


class TescoOfferSpider(scrapy.Spider):
    def getTescoStartUrl():
        tesco_start_url = []
        r = requests.get(
            'https://www.tesco.com/groceries/en-GB/promotions/alloffers')
        data = lxml.html.fromstring(r.text)
        # changed class name from "items-count__filter-caption" to "items-count__container"
        # changed class name back to items-count__filter-caption
        output = data.xpath(
            '//div[@class="items-count__filter-caption"]//text()')
        print(output)
        if (len(output) == 0):
            output = data.xpath(
                '//span[@class="items-count__filter-caption"]/text()')
            itemcount = output[0].split(' ')
        else:
            itemcount = output[3].split(' ')
            #itemcount = output[0].split(' ')
        print(math.ceil(int(itemcount[0]) / 24))
        #    return math.ceil(int(itemcount[0])/24)
        maxpage = math.ceil(int(itemcount[0]) / 24)
        tescourl = 'https://www.tesco.com/groceries/en-GB/promotions/alloffers?page=%d'
        for i in range(1, maxpage):
            tesco_start_url.append(tescourl % i)
        return tesco_start_url

        # output = data.xpath('//span[@class="items-count-filter-caption"]
        # /text()')
        output = data.xpath(
            '//div[@class="items-count__filter-caption"]//text()')
        logging.info(output)
        itemcount = output[3].split(' ')
        print(math.ceil(int(itemcount[0]) / 24))
        #    return math.ceil(int(itemcount[0])/24)
        maxpage = math.ceil(int(itemcount[0]) / 24)
        tescourl = 'https://www.tesco.com/groceries/en-GB/promotions/alloffers?page=%d'
        for i in range(1, maxpage):
            tesco_start_url.append(tescourl % i)
        return tesco_start_url

    name = "tescooffer"    # Name of the spider, to be used when crawling
    allowed_domains = ["tesco.com"]    # Where the spider is allowed to go
    start_urls = getTescoStartUrl()

    # start_urls = ['https://www.tesco.com/groceries/en-GB/promotions/alloffers
    # ?page=1']

    def parse(self, response):
        hxs = Selector(response)    # The XPath selector

        # XPath Tags
        productlist_tag = '//div[@class="product-lists"]//ul[@class="product-list grid"]/li'
        product_id_tag = './/div[@class="product-tile-wrapper"]//div[@class="tile-content"]/a/@href'
        product_imgsrc_tag = './/img/@src'
        product_desc_tag = './/div[@class="product-details-wrapper"]//a/text()'
        offer_desc_tag = './/li[@class="product-promotion"]//span[@class="offer-text"]/text()'
        validity_desc_tag = './/li[@class="product-promotion"]//span[@class="dates"]/text()'
        offertags = hxs.xpath(productlist_tag)
        ###

        tescooffers = []
        for offertag in offertags:
            offer = TescoOfferItem()
            offer['productid'] = offertag.xpath(product_id_tag).extract()[0].replace("/groceries/en-GB/products/", "")
            if offertag.xpath(product_imgsrc_tag).extract():
                offer['imgsrc225'] = offertag.xpath(product_imgsrc_tag).extract()[0]
                offer['imgsrc110'] = offertag.xpath(product_imgsrc_tag).extract()[0].replace('225x225', '110x110')
                offer['imgsrc90'] = offertag.xpath(product_imgsrc_tag).extract()[0].replace('225x225', '90x90')
                offer['imgsrc540'] = offertag.xpath(product_imgsrc_tag).extract()[0].replace('225x225', '540x540')
            else:
                offer['imgsrc90'] = ""
                offer['imgsrc540'] = ""
                offer['imgsrc110'] = ""
                offer['imgsrc225'] = ""
            if offertag.xpath(product_desc_tag).extract():
                offer['productdesc'] = offertag.xpath(product_desc_tag).extract()[0]
            else:
                offer['productdesc'] = ""
            if offertag.xpath(offer_desc_tag).extract():
                offer['offerdesc'] = offertag.xpath(offer_desc_tag).extract()[0]
            else:
                offer['offerdesc'] = ""
            if offertag.xpath(validity_desc_tag).extract():
                offer['validitydesc'] = offertag.xpath(validity_desc_tag).extract()[0]
            else:
                offer['validitydesc'] = ""
            tescooffers.append(offer)
        return tescooffers    # To be changed later


FILE_NAME = '/opt/offers/TESC_' + datetime.now().strftime("%Y%m%d") + '.json'
LOG_FILE_NAME = '/opt/offers/logs/TESC_' + datetime.now().strftime("%Y%m%d") + '.log'
try:
    os.remove(FILE_NAME)
except OSError:
    pass
os.environ["http_proxy"] = "http://localhost:8123"
SETTINGS = {
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_EXPORT_ENCODING': 'utf-8',
    'FEED_URI': FILE_NAME,
    'FEED_FORMAT': 'json',
    'DOWNLOAD_DELAY': '5',
    'LOG_LEVEL': 'INFO',
    'LOG_FILE': LOG_FILE_NAME
}

process = CrawlerProcess(SETTINGS)
process.crawl(TescoOfferSpider)
process.start()
