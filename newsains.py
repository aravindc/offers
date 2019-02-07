import requests
import lxml.html
import math
import logging
from datetime import datetime
from messageq import openConnection
from messageq import sendMessage
from messageq import messageToFile

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

http_proxy = "http://localhost:8123"
https_proxy = "https://localhost:8123"

proxyDict = {
    "http": http_proxy,
    "https": https_proxy,
}

categories = [
    {"id": 410380, "name": "Special Offers"},
    {"id": 12518, "name": "Fruit & vegetables"},
    {"id": 13343, "name": "Meat & fish"},
    {"id": 387873, "name": "Dairy, eggs & juice"},
    {"id": 267397, "name": "Chilled"},
    {"id": 12320, "name": "Bakery"},
    {"id": 218831, "name": "Frozen"},
    {"id": 12422, "name": "Food cupboard"},
    {"id": 340854, "name": "Beer, wine & spirits"},
    {"id": 281806, "name": "Home & outdoor"},
    {"id": 12192, "name": "Drinks"},
    {"id": 12448, "name": "Health & beauty"},
    {"id": 11651, "name": "Baby & toddler"},
    {"id": 12564, "name": "Household"},
    {"id": 12298, "name": "Pet"}
]

def getSainsStartUrl():
        sains_start_url = []
        # Added BWS category code to the list
        # Dairy code changed from 267396 to Dairy, Eggs & Juice -  387873
        # Added Special offers - 410380
        # categoryId = [410380, 12518, 13343, 387873, 267397, 12320, 218831, 12422, 340854,
        #              12192, 12448, 11651, 12564, 12298, 281806]
        # categoryId=[12518]
        # categoryId=[12518,13343,12422]
        urlstring = 'https://www.sainsburys.co.uk/shop/gb/groceries/home/' \
                    'CategorySeeAllView?langId=44&storeId=10151&catalogId=' \
                    '10123&pageSize=108&facet=88&categoryId=%d&' \
                    'categoryFacetId1=%d&beginIndex=%d'
        for n in categories:
            print("Working on {0}".format(urlstring % (n['id'], n['id'], 0)))
            r = requests.get(urlstring %
                             (n['id'], n['id'], 0), proxies=proxyDict)
            print(r)
            data = lxml.html.fromstring(r.text)
            output = data.xpath('//h1[@class="resultsHeading"]/text()')
            # item = output[0].replace('  ', '')
            # .replace('\r\n', '').split('(')[0]
            itemcount = output[0].replace('  ', '') \
                                 .replace('\r\n', '') \
                                 .split('(')[1].split(' ')[0]
            for i in range(0, math.ceil(int(itemcount.replace(',', ''))/108)):
                sains_start_url.append({"category":n['name'],"url":urlstring % (n['id'], n['id'], i*108)})
            break
        logger.info(sains_start_url)
        return sains_start_url



if __name__ == '__main__':
    getSainsStartUrl()
