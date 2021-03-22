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


headers = {'User-Agent': 'PostmanRuntime/7.25.0',
           'Accept': '*/*',
           'Cache-Control': 'no-cache',
           'Host': 'www.tesco.com',
           'Accept-Encoding': 'gzip, deflate, br',
           'Connection': 'keep-alive',
           'Cookie': 'bm_sz=04919BE521C5C4D8ADF4617D5250A484~YAAQrpxkX+b8IYVyAQAA/VQr0QgTg5gDEXUmuUfa0qqtHv0QHHZjtL4gcSJ9RA7hoaEXJOTp1DYPb9xCrGwP37BrvtUY2kCKB7PqvVLXAXnfrt9F0ZiEPj10SiSVXZRZj8klW46ZA7Ho/0XtWlsO2aFX1MPkmD2/C10cDH6E1PgeO9EUNkZi9uPu109p4DE=; _abck=5621BD87FE69A39458BD0AB267BB9A81~-1~YAAQrpxkX+f8IYVyAQAA/VQr0QTSvxcBlxnRsND9THtPksH0EbfK/A3XkW0xT9oCk0Bj1ewbVDXr3PqtBjR7hHO6h6IXMvC2XID5RrAk0gVEKGwm9RDyBWyvp6hnPzicHMH6tTUIZdYLmssjIBAJ2WnpBkKUuF0YbX45V4H8d3m6u8FOhyqZewFyT1+Yvh14NDHwmDw4Yb4hQkLPglrkzt8LV39SpfSjjGkWMjyX4l967aCe+SHK5hjcTIz9bjSAoOQNqFWR5ATMnfBDSLOfaAQ4Dic=~-1~-1~-1; atrc=48693e75-78d9-4fce-85d0-9a0a50232644; _csrf=2wH2UKiamS-tjvd4hERekcG2',
           'Referer': 'http://www.tesco.com/'}


# c = Conxn()
# Removed getTescoStartUrl and replaced with genCategoryUrlArray
# This function provides starturl along with its category
# def getTescoStartUrl():
#     tesco_start_url = []
#     ##r = c.getUrlContent(
#     ##    'https://www.tesco.com/groceries/en-GB/promotions/alloffers')
#     r = requests.get('https://www.tesco.com/groceries/en-GB/promotions/alloffers')
#     logger.debug(r.text)
#     data = lxml.html.fromstring(r.text)
#     # changed class name from "items-count__filter-caption" to "items-count__container"
#     output = data.xpath(
#         '//div[@class="items-count__filter-caption"]//text()')
#     logger.info(output)
#     if (len(output) == 0):
#         output = data.xpath(
#             '//span[@class="items-count__filter-caption"]/text()')
#         itemcount = output[0].split(' ')
#     else:
#         itemcount = output[3].split(' ')
#         # itemcount = output[0].split(' ')
#     logger.info(math.ceil(int(itemcount[0]) / 48))
#     # Changed item count size from 24 to 48
#     maxpage = math.ceil(int(itemcount[0]) / 48)
#     tescourl = 'https://www.tesco.com/groceries/en-GB/promotions/alloffers?count=48&page={0}'
#     for i in range(1, maxpage):
#         tesco_start_url.append(tescourl.format(i))
#         logger.info(tesco_start_url)
#         break
#     return tesco_start_url


def genCategoryUrlArray():
    tesco_start_url = []
    base_url = 'https://www.tesco.com'
    tesc_cat_format_url = '/all?viewAll=promotion&promotion=offers&count=48&page={0}'
    grocery_html = requests.get(
        url='https://www.tesco.com/groceries/en-GB/shop/', headers=headers, timeout=10)
    grocery_sub_nav_links = '//div[@class="current"]/ul[@class="list"]/li/a/@href'
    grocery_html_data = html.fromstring(grocery_html.text)
    category_links = grocery_html_data.xpath(grocery_sub_nav_links)
    for category_link in category_links:
        transform_url = category_link.replace('?include-children=true', '')
        category = transform_url.split('/')[4]
        cat_link = transform_url + format(tesc_cat_format_url, '1')
        r = requests.get(base_url+cat_link, timeout=10)
        data = html.fromstring(r.text)
        output = data.xpath(
            '//div[@class="items-count__filter-caption"]//text()')
        try:
            if (len(output) == 0):
                output = data.xpath(
                    '//span[@class="items-count__filter-caption"]/text()')
                itemcount = output[0].split(' ')
            else:
                itemcount = output[3].split(' ')
            maxpage = math.ceil(int(itemcount[0]) / 48)
            for i in range(1, maxpage+1):
                jsonObj = {}
                jsonObj['category'] = category
                jsonObj['category_offer_url'] = base_url + \
                    transform_url + tesc_cat_format_url.format(i)
                tesco_start_url.append(jsonObj)
                break
        except Exception as e:
            pass
    return tesco_start_url


def getProduct(Offertag, Category):
    offer = {}
    # XPath Tags

    # product_list_base_tag = './/div[@class = "product-lists"]//ul[@class = "product-list grid"]/li[contains(@class, "product-list--list-item")]/div/div/div/div/div/div/'
    # product_id_tag = './/div[@class="product-tile--wrapper"]//div[@class="tile-content"]/a/@href'
    # product_imgsrc_tag = './/img/@src'
    # product_desc_tag = './/div[@class="product-details--wrapper"]//a/text()'
    # offer_desc_tag = './/div[@class = "product-lists"]//ul[@class = "product-list grid"]/li[contains(@class, "product-list--list-item")]/div/div/div/div/div/div//div/span[@class = "offer-text"]/text()'
    # validity_desc_tag = './/div[@class = "product-lists"]//ul[@class = "product-list grid"]/li[contains(@class, "product-list--list-item")]/div/div/div/div/div/div//div/span[@class = "dates"]/text()'

    product_list_base_tag = './div/div/div/div/'
    product_id_tag = product_list_base_tag + \
        '/div[@class="tile-content"]/a/@href'
    product_imgsrc_tag = product_list_base_tag + '/img/@src'
    product_desc_tag = product_list_base_tag + '/h3/a/text()'
    offer_desc_tag = product_list_base_tag + \
        '/div/span[@class = "offer-text"]/text()'
    validity_desc_tag = product_list_base_tag + \
        '/div/span[@class = "dates"]/text()'

    logger.info(product_id_tag)
    logger.info(Offertag.xpath(product_id_tag))
    offer['productid'] = Offertag.xpath(product_id_tag)[0].replace("/groceries/en-GB/products/", "")
    offer['category'] = Category
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
    # channel, connection = openConnection(exchangeName, queueName)
    product_grid = '//div[@class="product-lists"]//ul[@class="product-list grid"]/li'
    for url in Urls:
        # time.sleep(10)
        r = requests.get(url['category_offer_url'], headers=headers, timeout=10)
        tree = html.fromstring(r.content)
        products = tree.xpath(product_grid)
        for product in products:
            # sendMessage(exchangeName, queueName, getProduct(product,url['category']), channel)
            logger.info(product)
            # logger.info(getProduct(product, url['category']))
            break
        break
    # connection.close()
    return None


if __name__ == '__main__':
    urls = genCategoryUrlArray()
    getOffers(urls)
    channel, connection = openConnection(exchangeName, queueName)
    # messageToFile(queueName, fileName=FILE_NAME)
    connection.close()    
