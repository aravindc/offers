import requests
import json
import logging
import time
import uuid
import math
import hashlib
from lxml import html
from fake_useragent import UserAgent
from datetime import datetime
from messageq import openConnection
from messageq import sendMessage
from messageq import messageToFile


# Global variables
ua = UserAgent()
user_agent = str(ua.chrome)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
supercats = [
    'fresh-food', 'bakery',
    'frozen-food','food-cupboard',
    'drinks', 'baby',
    'health-and-beauty', 'pets',
    'household', 'home-and-ents'
    ]
resourcesUrl = 'https://www.tesco.com/groceries/en-GB/resources'
exchangeName = 'TESCO_PROD'
queueName = '{0}_{1}'.format(exchangeName, datetime.now().strftime("%Y%m%d"))

# Get CSRF Token
def getCsrfToken(clientSession):
    URL = 'https://www.tesco.com/groceries/en-GB/shop/fresh-food/all'
    header_data = {'User-Agent': user_agent}
    logger.debug(header_data)
    response = clientSession.get(URL, headers=header_data)
    totalhtml = html.fromstring(response.text)
    return totalhtml.xpath('//body/@data-csrf-token')[0]

# Generate Unique Hash using UUID
def generateHash():
    return str(uuid.uuid4().int)[0:16]

def getCategoryCount(clientSession, categoryName):
    header_data = {'x-csrf-token': getCsrfToken(
       clientSession), 'User-Agent': user_agent, 'Content-Type': 'application/json'}
    post_data = generateBodyData(categoryName, 1)
    response = clientSession.post(resourcesUrl, json=post_data, headers=header_data)
    jsonObj = json.loads(response.text)
    print(jsonObj['productsByCategory'])
    jsonProductCount = jsonObj['productsByCategory']['data']['results']['pageInformation']['totalCount']
    return jsonProductCount


def getProducts(clientSession):
    productArray = []
    header_data = {'x-csrf-token': getCsrfToken(
       clientSession), 'User-Agent': user_agent, 'Content-Type': 'application/json'}    
    for supercat in supercats:
        categoryCount = getCategoryCount(clientSession, supercat)
        logger.info(categoryCount)
        maxpage = math.ceil(int(categoryCount) / 48)
        for i in range(1, maxpage):
            bodyData = generateBodyData(supercat, i)
            response = clientSession.post(resourcesUrl, json=bodyData, headers=header_data)
            jsonObj = json.loads(response.text)
            jsonProductArray = jsonObj['productsByCategory']['data']['results']['productItems']
            for jsonProductItem in jsonProductArray:
                productArray.append(jsonProductItem)
                sendMessage(exchangeName, queueName, jsonProductItem, channel)
                logger.debug(jsonProductItem)
            time.sleep(5)
            #break
        #break
    return productArray

# Generate Body data based on categoryName
def generateBodyData(categoryName, pageNum):
    post_data = {"resources":[{"type":"trolleyContents", "params":{},"hash":generateHash()},
    {"type":"productsByCategory",
    "params":{"query":{"page": pageNum, "count": "48"},
    "superdepartment": categoryName},
    "hash":generateHash()}]}
    logger.debug(post_data)
    return post_data


if __name__ == '__main__':
    clientSession = requests.Session()
    channel, connection = openConnection(exchangeName, queueName)
    getProducts(clientSession)


    #header_data = {'x-csrf-token': getCsrfToken(
    #   clientSession), 'User-Agent': user_agent, 'Content-Type': 'application/json'}
    #logger.debug(header_data)
    #totalCount = 0
    #for supercat in supercats:
    #    post_data = generateBodyData(supercat, 1)
    #    response = clientSession.post(resourcesUrl, json=post_data, headers=header_data)
    #    jsonObj = json.loads(response.text)
    #    with open('/tmp/jsonfile.json', 'w') as myf:
    #        myf.write(json.dumps(jsonObj))
    #    logger.info(jsonObj['productsByCategory']['data']['results'])
    #    jsonProductCount = jsonObj['productsByCategory']['results']['pageInformation']['totalCount']
    #    jsonProductItems = jsonObj['productsByCategory']['results']['productItems']
    #    logger.info('{0} - {1}'.format(supercat, jsonProductCount))
    #    totalCount = totalCount +  int(jsonProductCount)
    #    time.sleep(5)
    #    logger.debug(jsonProductItems)
    #    break
    #logger.info("Total Items: {}".format(totalCount))

