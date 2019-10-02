import requests
import json
from lxml import html
from fake_useragent import UserAgent
import logging
import uuid

ua = UserAgent()
user_agent = str(ua.chrome)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def getCsrfToken(clientSession):
    URL = 'https://www.tesco.com/groceries/en-GB/shop/fresh-food/all'
    header_data = {'User-Agent': user_agent}
    logger.info(header_data)
    response = clientSession.get(URL, headers=header_data)
    totalhtml = html.fromstring(response.text)
    return totalhtml.xpath('//body/@data-csrf-token')[0]

def generateHash():
    return str(uuid.uuid4().int)[0:16]

def getProducts(clientSession):
    return None

if __name__ == '__main__':
    supercats = ['fresh-food','bakery','frozen-food','food-cupboard',
    'drinks','baby','health-and-beauty','pets','household','home-and-ents']
    clientSession = requests.Session()
    header_data = {'x-csrf-token': getCsrfToken(
       clientSession), 'User-Agent': user_agent, 'Content-Type': 'application/json'}
    logger.info(header_data)
    post_data = {"resources":[{"type":"trolleyContents", "params":{},"hash":generateHash()},
    {"type":"productsByCategory",
    "params":{"query":{"page":"1", "count": "48"},
    "superdepartment":"fresh-food"},
    "hash":generateHash()}]}
    logger.info(post_data)
    fin_url = 'https://www.tesco.com/groceries/en-GB/resources'
    response = clientSession.post(fin_url, json=post_data, headers=header_data)
    jsonObj = json.loads(response.text)
    jsonProductCount = jsonObj['productsByCategory']['results']['pageInformation']['totalCount']
    jsonProductItems = jsonObj['productsByCategory']['results']['productItems']
    logger.info(jsonProductCount)
    logger.info(jsonProductItems)

