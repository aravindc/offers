import os
import scrapy
import requests
import lxml.html
import math
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.item import Field
from urllib.parse import urlsplit, parse_qs
from datetime import datetime
from messageq import openConnection
from messageq import sendMessage
from messageq import messageToFile


#  Initialize logger
#  logging.basicConfig(level=logging.INFO)
#  logger = logging.getLogger(__name__)


class SainsburysOfferItem(scrapy.Item):
    productid = Field()
    imgsrcl = Field()
    productdesc = Field()
    offerdesc = Field()
    producturl = Field()
    priceunit = Field()

# Listed all product categories
# 410380 - Special Offers
# 12518 - Fruit & vegetables
# 13343 - Meat & fish
# 387873 - Dairy, eggs & juice
# 267397 - Chilled 
# 12320 - Bakery
# 218831 - Frozen
# 12422 - Food cupboard
# 340854 - Beer, wine & spirits
# 281806 - Home & outdoor 
# 12192 - Drinks
# 12448 - Health & beauty
# 11651 - Baby & toddler
# 12564 - Household 
# 12298 - Pet


exchangeName = 'SAINS'
queueName = '{0}_{1}'.format(exchangeName, datetime.now().strftime("%Y%m%d"))

class MySpider(scrapy.Spider):
    def getSainsStartUrl(self):
        sains_start_url = []
        # Added BWS category code to the list
        # Dairy code changed from 267396 to Dairy, Eggs & Juice -  387873
        # Added Special offers - 410380
        categoryId = [410380, 12518, 13343, 387873, 267397, 12320, 218831, 12422, 340854, 
                      12192, 12448, 11651, 12564, 12298, 281806]
        # categoryId=[12518]
        # categoryId=[12518,13343,12422]
        urlstring = 'https://www.sainsburys.co.uk/shop/gb/groceries/home/' \
                    'CategorySeeAllView?langId=44&storeId=10151&catalogId=' \
                    '10123&pageSize=108&facet=88&categoryId=%d&' \
                    'categoryFacetId1=%d&beginIndex=%d'
        for n in categoryId:
            print("Working on {0}".format(urlstring % (n,n,0)))
            r = requests.get(urlstring % (n, n, 0))
            data = lxml.html.fromstring(r.text)
            output = data.xpath('//h1[@id="resultsHeading"]/text()')
            print(output)
            # item = output[0].replace('  ', '')
            # .replace('\r\n', '').split('(')[0]
            itemcount = output[0].replace('  ', '') \
                                 .replace('\r\n', '') \
                                 .split('(')[1].split(' ')[0]
            for i in range(0, math.ceil(int(itemcount.replace(',', ''))/108)):
                sains_start_url.append(urlstring % (n, n, i*108))
        return sains_start_url

    def sendMessageToQ(self, offer):
        channel, connection = openConnection(exchangeName, queueName)
        sendMessage(exchangeName, queueName, offer, channel)
        connection.close()

    name = "sainsoffer"  # Name of the spider, to be used when crawling
    allowed_domains = ["sainsburys.co.uk"]  # Where the spider is allowed to go   
    start_urls = getSainsStartUrl()

    def parse(self, response):
        hxs = Selector(response)  # The XPath selector
        product_grid = '//div[@id="productsContainer"]/div[@id="product' \
                       'Lister"]/ul[contains(@class,"productLister")]' \
                       '//li[@class="gridItem"]'
        product_id_tag = './/div[@class="productInfo"]//div[@class=' \
                         '"promotion"]//a/@href'
        offer_desc_tag = './/div[@class="productInfo"]//div[@class=' \
                         '"promotion"]//a/text()'
        product_url = './/div[@class="productInfo"]//h3/a/@href'
        product_desc_tag = './/div[@class="productInfo"]//h3/a/text()'
        product_imgsrc_tag = './/div[@class="productInfo"]//h3/a/img/@src'
        price_unit_tag = './/div[@class="pricing"]/p[@class="pricePerUnit"]' \
                         '/text()[1]'
        offertags = hxs.xpath(product_grid)
        sainsoffers = []

        for offertag in offertags:
            offer = SainsburysOfferItem()
            offer['productid'] = parse_qs(urlsplit(offertag
                                          .xpath(product_id_tag).extract()[0])
                                          .query)['productId'][0]
            offer['imgsrcl'] = offertag.xpath(product_imgsrc_tag).extract()[0]
            offer['productdesc'] = offertag.xpath(product_desc_tag) \
                                           .extract()[0].replace('  ', '') \
                                           .replace('\r\n', '')
            offer['offerdesc'] = offertag.xpath(offer_desc_tag) \
                                         .extract()[0].replace('  ', '') \
                                         .replace('\r\n', '')
            offer['producturl'] = offertag.xpath(product_url).extract()[0]
            offer['priceunit'] = offertag.xpath(price_unit_tag).extract()[0] \
                                         .replace('  ', '') \
                                         .replace('\r\n', '') \
                                         .replace('\n', '')
            sainsoffers.append(offer)
            sendMessageToQ(offer)
        return sainsoffers


FILE_NAME = '/opt/offers/SAINS_' + datetime.now().strftime("%Y%m%d")+'.json'
LOG_FILE_NAME = '/opt/offers/logs/SAINS_'+datetime.now().strftime("%Y%m%d") + \
                '.log'

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
process.crawl(MySpider)
process.start()

# TODO: create function to insert data into MariaDB
