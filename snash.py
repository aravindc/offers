import requests
import json
import math
import time
import logging
from datetime import datetime
from messageq import openConnection
from messageq import sendMessage
from conxn import Conxn

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

items = []
exchangeName = 'SNASH'
queueName = '{0}_{1}'.format(exchangeName, datetime.now().strftime("%Y%m%d"))
us_body = json.dumps({"binary": "web-ecom", "binary_version": "2.11.27-hotfix", "is_retina": "false",
                      "os_version": "Win32", "pixel_density": "1.0", "push_token": "", "screen_height": 1080, "screen_width": 1920})

c = Conxn()


def getSessionToken():
    header_data = {"Content-type": "application/json"}
    response = c.postUrlContent( 
        'https://www.shopthefastlane.com/api/v2/user_sessions', header_data, us_body)
    json_output = json.loads(response.text)
    print(json_output)
    return json_output['session_token']

def getUser(session_token):
    header_data = {"Authorization": "Bearer {0}".format(session_token)}
    response = c.postUrlContent('https://www.shopthefastlane.com/api/v2/users', header_data, None)
    logger.info(response.text)
    json_output = json.loads(response.text)
    return json_output['session_token']

def getItemCount(session_token):
    header_data = {"Authorization": "Bearer {0}".format(session_token)}
    response = c.getUrlContent(url = 
        'https://www.shopthefastlane.com/api/v2/store_products?limit=1&offset=0&sort=alpha&tags=on_sale', header=header_data)
    logger.info(response.text)
    json_output = json.loads(response.text)
    return json_output['item_count']

def getCrawlUrls(item_count):
    url_string = 'https://www.shopthefastlane.com/api/v2/store_products?limit=60&offset={0}&sort=alpha&tags=on_sale'
    urls = []
    for i in range(0, math.ceil(item_count/60)):
        urls.append(url_string.format(i*60))
    return urls

def getPromoProducts(session_token, urls):
    header_data = {"Authorization": "Bearer {0}".format(session_token)}
    for snash_url in urls:
        response = c.getUrlContent(url=snash_url, header=header_data)
        json_output = json.loads(response.text)
        for item in json_output['items']:
            sendMessage(exchangeName, queueName, item, channel)
            items.append(item)
    return items

if __name__ == "__main__":
    channel, connection = openConnection(exchangeName, queueName)
    s_token1 = getSessionToken()
    s_token2 = getUser(s_token1)
    itemCount = getItemCount(s_token2)
    Urls = getCrawlUrls(itemCount)
    getPromoProducts(s_token2, Urls)
    connection.close()
