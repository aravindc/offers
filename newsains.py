# -*- coding: utf-8 -*-
import requests
import math
import logging
import time
from datetime import datetime
from messageq import openConnection
from messageq import sendMessage
from messageq import messageToFile
from lxml import html
from urllib.parse import urlparse, urlsplit, parse_qs
from conxn import Conxn

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

logging.basicConfig(level=logging.INFO)
LOG_FILE = '/opt/offers/logs/SAINS_' + datetime.now().strftime("%Y%m%d") + '.log'
hdlr = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(hdlr)

FILE_NAME = '/opt/offers/SAINS_' + datetime.now().strftime("%Y%m%d") + '.json'
exchangeName = 'SAINS'
queueName = '{0}_{1}'.format(exchangeName, datetime.now().strftime("%Y%m%d"))

# http_proxy = "http://localhost:8118"
# https_proxy = "https://localhost:8118"

# proxyDict = {
#     "http": http_proxy,
#     "https": https_proxy,
# }

c = Conxn()
# Changed Dairy, eggs & chilled
# 428374
# Changed hard-coded category to be generated through genCategoryArray function
# categories = [
#     {"id": 410380, "name": "Special Offers"},
#     {"id": 12518, "name": "Fruit & vegetables"},
#     {"id": 13343, "name": "Meat & fish"},
#     {"id": 428374, "name": "Dairy, eggs & juice"},
#     {"id": 12320, "name": "Bakery"},
#     {"id": 218831, "name": "Frozen"},
#     {"id": 12422, "name": "Food cupboard"},
#     {"id": 340854, "name": "Beer, wine & spirits"},
#     {"id": 281806, "name": "Home & outdoor"},
#     {"id": 12192, "name": "Drinks"},
#     {"id": 12448, "name": "Health & beauty"},
#     {"id": 11651, "name": "Baby & toddler"},
#     {"id": 12564, "name": "Household"},
#     {"id": 12298, "name": "Pet"},
#     {"id": 281806, "name": "Homeware & garden"}
# ]


def genCategoryArray():
    grocery_html = requests.get(
        url='https://www.sainsburys.co.uk/shop/gb/groceries')
    grocery_sub_nav_links = '//div[@class="subNav jsHide"]/ul/li/a/@href'
    data = html.fromstring(grocery_html.text)
    category_links = data.xpath(grocery_sub_nav_links)
    category_array = []
    sains_base_url = 'https://www.sainsburys.co.uk'
    for category_link in category_links:
        print(category_link)
        catJson = {}
        r = requests.get(category_link)
        catData = html.fromstring(r.text)
        catOffLink = catData.xpath('//li/a[contains(text(),"offer")]/@href')
        if len(catOffLink) <= 1:
            continue 
        print(len(catOffLink))
        print(catOffLink[0] if catOffLink[0].startswith(sains_base_url) else sains_base_url+catOffLink[0])
        r1 = requests.get(catOffLink[0] if catOffLink[0].startswith(sains_base_url) else sains_base_url+catOffLink[0])
        linkData = html.fromstring(r1.text)
        print(linkData)
        linkOffLink = linkData.xpath(
            '//div[@class="filterCollapseBar"]/div/a[@class="repressive"]/@href')
        print(linkOffLink)
        categoryId = parse_qs(urlparse(linkOffLink[0]).query)[
            'top_category'][0]
        categoryName = urlparse(category_link).path.split('/')[4]
        catJson['id'] = categoryId
        catJson['name'] = categoryName
        print(catJson)
        category_array.append(catJson)
        #break
    return category_array

def getSainsStartUrl(categories):
    sains_start_url = []
    urlstring = 'https://www.sainsburys.co.uk/shop/gb/groceries/home/' \
                'CategorySeeAllView?langId=44&storeId=10151&catalogId=' \
                '10123&pageSize=120&facet=88&categoryId={0}&' \
                'categoryFacetId1={1}&beginIndex={2}'
    for n in categories:
        #logger.info("Working on {0}".format(urlstring % (n['id'], n['id'], 0)))
        logger.info("Working on {0}".format(urlstring.format(n['id'],n['id'],0)))
        #r = c.getUrlContent(url = urlstring % (n['id'], n['id'], 0))
        r = requests.get(url=urlstring.format(n['id'], n['id'], 0))
        data = html.fromstring(r.text)
        output = data.xpath('//h1[@class="resultsHeading"]/text()')
        print(output)
        itemcount = output[0].replace('  ', '') \
                                .replace('\r\n', '') \
                                .split('(')[1].split(' ')[0]
        for i in range(0, math.ceil(int(itemcount.replace(',', ''))/108)):
            sains_start_url.append(
                {"category": n['name'], "url": urlstring.format(n['id'], n['id'], i*108)})
            #break
        #break
    logger.info(sains_start_url)
    return sains_start_url

def getProduct(offertag, category):
    offer = {}
    product_id_tag = './/div[@class="productInfo"]//div[@class=' \
        '"promotion"]//a/@href'
    offer_desc_tag = './/div[@class="productInfo"]//div[@class=' \
        '"promotion"]//a/text()'
    product_url = './/div[@class="productInfo"]//h3/a/@href'
    product_desc_tag = './/div[@class="productInfo"]//h3/a/text()'
    product_imgsrc_tag = './/div[@class="productInfo"]//h3/a/img/@src'
    price_unit_tag = './/div[@class="pricing"]/p[@class="pricePerUnit"]' \
        '/text()[1]'
    try:
        offer['productid'] = parse_qs(urlsplit(offertag
                                           .xpath(product_id_tag)[0])
                                  .query)['productId'][0]
    except:
        print(offertag.xpath(product_id_tag))
    offer['imgsrcl'] = offertag.xpath(product_imgsrc_tag)[0]
    offer['productdesc'] = offertag.xpath(product_desc_tag) \
        [0].replace('  ', '') \
        .replace('\r\n', '') \
        .replace('Â£', '£')
    offer['offerdesc'] = offertag.xpath(offer_desc_tag) \
        [0].replace('  ', '') \
        .replace('\r\n', '') \
        .replace('Â£', '£')
    offer['producturl'] = offertag.xpath(product_url)[0]
    offer['priceunit'] = offertag.xpath(price_unit_tag)[0] \
        .replace('  ', '') \
        .replace('\r\n', '') \
        .replace('\n', '') \
        .replace('Â£','£')
    offer['category'] = category
    logger.info(offer)
    return offer

def getProducts(urls):
    channel, connection = openConnection(exchangeName, queueName)
    product_grid = '//div[@id="productsContainer"]/div[@id="product' \
                       'Lister"]/ul[contains(@class,"productLister")]' \
                       '//li[@class="gridItem"]'
    for url in urls:
        time.sleep(10)
        #r = c.getUrlContent(url = url['url'])
        r = requests.get(url = url['url'])
        tree = html.fromstring(r.content)
        products = tree.xpath(product_grid)
        for product in products:
            sendMessage(exchangeName, queueName, getProduct(product,url['category']), channel)
            logger.debug(getProduct(product, url['category']))
            #break
        #break
    connection.close()
    return None


if __name__ == '__main__':
    categories = genCategoryArray()
    urls = getSainsStartUrl(categories)
    getProducts(urls)
    channel, connection = openConnection(exchangeName, queueName)
    messageToFile(queueName, fileName=FILE_NAME)
    connection.close()
