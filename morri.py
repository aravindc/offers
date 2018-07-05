import scrapy
import requests
from scrapy.crawler import CrawlerProcess
from scrapy.item import Field
from scrapy.selector import Selector
# import logging
import json
from datetime import datetime
import os

# Initialize logger
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


class MorrisonsOfferItem(scrapy.Item):
    imgsrcl = Field()
    productdesc = Field()
    offerdesc = Field()
    producturl = Field()
    offerurl = Field()
    productprice = Field()
    unitprice = Field()


class MorrisonsSpider(scrapy.Spider):
    def getChildCatUrls():
        categories = [
            '104268', '102210', '104162', '102705', '103644', '103120',
            '102063', '166274', '103497', '102838', '166275', '103423',
            '102207', '150516', '153052'
        ]
        # categories = ['104268', '104162']
        # categories = [104268]
        base_url = 'https://groceries.morrisons.com'
        base_cat_url = base_url + '/webshop/subNavigation?catalogueType= \
                                   OFFER_PRODUCTS&tags=|105651|19998|%s'

        cat_url = {}
        starturls = []

        for category in categories:
            response = requests.get(base_cat_url % category)
            json_obj = json.loads(response.text)
            # logger.debug(json_obj)
            for lvl1 in json_obj['categories']:
                if 'children' in lvl1:
                    for child1 in lvl1['children']:
                        if 'children' in child1:
                            for child2 in child1['children']:
                                # logger.debug(child2['name'])
                                cat_url[
                                    lvl1['name'] + '->' + child1['name'] +
                                    '->' +
                                    child2['name']] = base_url + child2['url']
                                starturls.append(base_url + child2['url'])
                        else:
                            # logger.debug(child1['name'])
                            cat_url[lvl1['name'] + '->' +
                                    child1['name']] = base_url + child1['url']
                            starturls.append(base_url + child1['url'])
                else:
                    # logger.debug(lvl1['name'])
                    cat_url[lvl1['name']] = base_url + lvl1['url']
                    starturls.append(base_url + lvl1['url'])
        # logger.info(json.dumps(cat_url))
        # logger.info(starturls)
        return starturls

    name = "morrioffer"    # Name of the spider, to be used when crawling
    allowed_domains = ["morrisons.com"]    # Where the spider is allowed to go
    # start_urls = ['https://groceries.morrisons.com/webshop/
    # getOfferProducts.do?tags=|105651|19998|104268|113925|113955&Asidebar=2']
    start_urls = getChildCatUrls()

    def parse(self, response):
        hxs = Selector(response)
        product_grid = '//div[@id="js-productPageFops"]/ul/li'
        img_src = './/div[@class="fop-item"]//img/@src'
        prod_desc = './/div[@class="fop-item"]//div[@class= \
                    "fop-description"]/h4[contains(@class,"fop-title")]/text()'
        prod_url = './/div[@class="fop-item"]//div[contains(@class, \
                   "fop-content-wrapper")]/a/@href'
        promo_desc = './/div[@class="fop-item"]//a[contains(@class, \
                     "fop-row-promo")]/span/text()'
        promo_url = './/div[@class="fop-item"]//a[contains(@class, \
                    "fop-row-promo")]/@href'
        price = './/div[@class="fop-item"]//div[@class= \
                "price-group-wrapper"]/h5[contains(@class,"fop-price")]/text()'
        unit_price = './/div[@class="fop-item"]//div[@class= \
                     "price-group-wrapper"]/span[@class= \
                     "fop-unit-price"]/text()'
        offertags = hxs.xpath(product_grid)

        morrioffers = []
        base_url = 'https://groceries.morrisons.com'
        for offertag in offertags:
            if(offertag.xpath(img_src).extract_first() is not None):
                offer = MorrisonsOfferItem()
                offer['imgsrcl'] = base_url + offertag.xpath(
                    img_src).extract_first()
                offer['productdesc'] = offertag.xpath(
                    prod_desc).extract_first().replace('  ', '').replace(
                        '\r\n', '').replace('\n', '')
                offer['offerdesc'] = offertag.xpath(
                    promo_desc).extract_first().replace('  ', '').replace(
                        '\r\n', '').replace('\n', '')
                offer['producturl'] = base_url + offertag.xpath(
                    prod_url).extract_first()
                offer['offerurl'] = base_url + offertag.xpath(
                    promo_url).extract_first()
                offer['productprice'] = offertag.xpath(
                    price).extract_first().replace('  ', '').replace('\r\n',
                                                                     '').replace(
                                                                         '\n', '')
                offer['unitprice'] = offertag.xpath(unit_price).extract_first()
                morrioffers.append(offer)
            else:
                print(offertag.extract())

        return morrioffers


FILE_NAME = '/opt/offers/MORRI_' + datetime.now().strftime("%Y%m%d") + '.json'
LOG_FILE_NAME = '/opt/offers/logs/MORRI_' + datetime.now().strftime(
    "%Y%m%d") + '.log'
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
    'DOWNLOAD_DELAY': '2',
    'LOG_LEVEL': 'INFO',
    'LOG_FILE': LOG_FILE_NAME,
    'LOG_ENABLED': False
}

process = CrawlerProcess(SETTINGS)
process.crawl(MorrisonsSpider)
process.start()
