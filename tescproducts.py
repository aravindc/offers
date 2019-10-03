import requests
import json
from lxml import html
from fake_useragent import UserAgent
import logging
import time
import uuid

ua = UserAgent()
user_agent = str(ua.chrome)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def getCsrfToken(clientSession):
    URL = 'https://www.tesco.com/groceries/en-GB/shop/fresh-food/all'
    header_data = {'User-Agent': user_agent}
    logger.debug(header_data)
    response = clientSession.get(URL, headers=header_data)
    totalhtml = html.fromstring(response.text)
    return totalhtml.xpath('//body/@data-csrf-token')[0]

def generateHash():
    return str(uuid.uuid4().int)[0:16]

def getProducts(clientSession):
    return None


def generateBodyData(categoryName):
    post_data = {"resources":[{"type":"trolleyContents", "params":{},"hash":generateHash()},
    {"type":"productsByCategory",
    "params":{"query":{"page":"1", "count": "48"},
    "superdepartment": categoryName},
    "hash":generateHash()}]}
    logger.debug(post_data)
    return post_data


if __name__ == '__main__':
    supercats = [
        {'category':'fresh-food', 'catCount': 0},
        {'category':'bakery', 'catCount': 0},
        {'category':'frozen-food', 'catCount': 0},
        {'category':'food-cupboard', 'catCount': 0},
        {'category':'drinks', 'catCount': 0},
        {'category':'baby', 'catCount': 0},
        {'category':'health-and-beauty', 'catCount': 0},
        {'category':'pets', 'catCount': 0},
        {'category':'household', 'catCount': 0},
        {'category':'home-and-ents', 'catCount': 0}
        ]
    clientSession = requests.Session()
    header_data = {'x-csrf-token': getCsrfToken(
       clientSession), 'User-Agent': user_agent, 'Content-Type': 'application/json'}
    logger.debug(header_data)
    fin_url = 'https://www.tesco.com/groceries/en-GB/resources'

    totalCount = 0

    for supercat in supercats:
        post_data = generateBodyData(supercat['category'])
        response = clientSession.post(fin_url, json=post_data, headers=header_data)
        jsonObj = json.loads(response.text)
        jsonProductCount = jsonObj['productsByCategory']['results']['pageInformation']['totalCount']
        jsonProductItems = jsonObj['productsByCategory']['results']['productItems']
        logger.info('{0} - {1}'.format(supercat['category'], jsonProductCount))
        totalCount = totalCount +  int(jsonProductCount)
        time.sleep(5)
        logger.debug(jsonProductItems)
    logger.info("Total Items: {}".format(totalCount))

