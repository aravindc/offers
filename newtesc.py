import os
import logging
import requests
import lxml.html
import math
import time
from datetime import datetime
from messageq import openConnection
from messageq import sendMessage
from messageq import messageToFile
from lxml import html

logging.basicConfig(level=logging.INFO)
LOG_FILE = '/opt/offers/logs/TESC_' + datetime.now().strftime("%Y%m%d") + '.log'
hdlr = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(hdlr)

FILE_NAME = '/opt/offers/TESC_' + datetime.now().strftime("%Y%m%d") + '.json'
exchangeName = 'TESC'
queueName = '{0}_{1}'.format(exchangeName, datetime.now().strftime("%Y%m%d"))

#c = Conxn()

def getTescoStartUrl():
    tesco_start_url = []
    ##r = c.getUrlContent(
    ##    'https://www.tesco.com/groceries/en-GB/promotions/alloffers')
    r = requests.get('https://www.tesco.com/groceries/en-GB/promotions/alloffers')
    logger.debug(r.text)
    data = lxml.html.fromstring(r.text)
    # changed class name from "items-count__filter-caption" to "items-count__container"
    output = data.xpath(
        '//div[@class="items-count__filter-caption"]//text()')
    logger.info(output)
    if (len(output) == 0):
        output = data.xpath(
            '//span[@class="items-count__filter-caption"]/text()')
        itemcount = output[0].split(' ')
    else:
        itemcount = output[3].split(' ')
        # itemcount = output[0].split(' ')
    logger.info(math.ceil(int(itemcount[0]) / 48))
    # Changed item count size from 24 to 48
    maxpage = math.ceil(int(itemcount[0]) / 48)
    tescourl = 'https://www.tesco.com/groceries/en-GB/promotions/alloffers?count=48&page={0}'
    for i in range(1, maxpage):
        tesco_start_url.append(tescourl.format(i))
        logger.info(tesco_start_url)
        break
    return tesco_start_url

def getProduct(Offertag):
    offer = {}
    # XPath Tags
    
    product_id_tag = './/div[@class="product-tile-wrapper"]//div[@class="tile-content"]/a/@href'
    product_imgsrc_tag = './/img/@src'
    product_desc_tag = './/div[@class="product-details-wrapper"]//a/text()'
    offer_desc_tag = './/li[@class="product-promotion"]//span[@class="offer-text"]/text()'
    validity_desc_tag = './/li[@class="product-promotion"]//span[@class="dates"]/text()'

    offer['productid'] = Offertag.xpath(product_id_tag)[0].replace("/groceries/en-GB/products/", "")
    if Offertag.xpath(product_imgsrc_tag):
        offer['imgsrc225'] = Offertag.xpath(product_imgsrc_tag)[0]
        offer['imgsrc110'] = Offertag.xpath(product_imgsrc_tag)[0].replace('225x225', '110x110')
        offer['imgsrc90'] = Offertag.xpath(product_imgsrc_tag)[0].replace('225x225', '90x90')
        offer['imgsrc540'] = Offertag.xpath(product_imgsrc_tag)[0].replace('225x225', '540x540')
    else:
        offer['imgsrc90'] = ""
        offer['imgsrc540'] = ""
        offer['imgsrc110'] = ""
        offer['imgsrc225'] = ""
    if Offertag.xpath(product_desc_tag):
        offer['productdesc'] = Offertag.xpath(product_desc_tag)[0]
    else:
        offer['productdesc'] = ""
    if Offertag.xpath(offer_desc_tag):
        offer['offerdesc'] = Offertag.xpath(offer_desc_tag)[0]
    else:
        offer['offerdesc'] = ""
    if Offertag.xpath(validity_desc_tag):
        offer['validitydesc'] = Offertag.xpath(validity_desc_tag)[0]
    else:
        offer['validitydesc'] = ""    
    return offer

def getOffers(Urls):
    channel, connection = openConnection(exchangeName, queueName)
    product_grid = '//div[@class="product-lists"]//ul[@class="product-list grid"]/li'
    for url in Urls:
        time.sleep(10)
        r = requests.get(url)
        tree = html.fromstring(r.content)
        products = tree.xpath(product_grid)
        for product in products:
            sendMessage(exchangeName, queueName, getProduct(product), channel)
            logger.info(getProduct(product))
            #break
        #break
    connection.close()
    return None

if __name__ == '__main__':
    urls = getTescoStartUrl()
    getOffers(urls)
    channel, connection = openConnection(exchangeName, queueName)
    messageToFile(queueName, fileName=FILE_NAME)
    connection.close()    