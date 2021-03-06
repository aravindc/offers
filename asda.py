import requests
import json
import logging
import time
import math
import re
import os
import io
import urllib.parse as urlparse
from datetime import datetime
from messageq import openConnection
from messageq import sendMessage
from messageq import messageToFile

logging.basicConfig(level=logging.INFO)
LOG_FILE = '/opt/offers/logs/ASDA_' + datetime.now().strftime("%Y%m%d") + '.log'
hdlr = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(hdlr)

FILE_NAME = '/opt/offers/ASDA_' + datetime.now().strftime("%Y%m%d") + '.json'
exchangeName = 'ASDA'
queueName = '{0}_{1}'.format(exchangeName, datetime.now().strftime("%Y%m%d"))

http_proxy = "http://localhost:8123"
https_proxy = "https://localhost:8123"

proxyDict = {
    "http": http_proxy,
    "https": https_proxy,
}

asda_urls = {
    "base_url": "https://groceries.asda.com",
    "entry_url": "https://groceries.asda.com/cmscontent/json/pages/" +
                 "special-offers/all-offers?storeId=4565&shipDate=" +
                 str(int(time.time())*1000),
    "item_url": "https://groceries.asda.com/cmscontent/json/pages/" +
                "special-offers/all-offers/by-category?storeId=4565&" +
                "N={}&Nrpp=60&No={}&shipDate="+str(int(time.time())*1000),
    "item_detail_url": "https://groceries.asda.com/api/items/view?" +
                       "storeid=4565&shipdate=" + str(int(time.time())*1000) +
                       "&itemid={}"
    }

all_urls = json.loads(json.dumps(asda_urls))


# https://groceries.asda.com/special-offers/all-offers/by-category/103099
# https://groceries.asda.com/cmscontent/json/pages/special-offers/all-offers/by-category?Endeca_user_segments=anonymous%7Cstore_4565%7Cwapp%7Cvp_XXL%7CZero_Order_Customers%7CDelivery_Pass_Older_Than_12_Months%7Cdp-false%7C1007%7C1019%7C1020%7C1023%7C1024%7C1027%7C1038%7C1041%7C1042%7C1043%7C1047%7C1053%7C1055%7C1057%7C1059%7C1067%7C1070%7C1082%7C1087%7C1097%7C1098%7C1099%7C1100%7C1102%7C1105%7C1107%7C1109%7C1110%7C1111%7C1112%7C1116%7C1117%7C1119%7C1123%7C1124%7C1126%7C1128%7C1130%7C1140%7C1141&storeId=4565&shipDate=1528074000000&N=103099&Nrpp=60&No=0&requestorigin=gi&_=1528125877201

# URL to get 60 ItemIds per category
# https://groceries.asda.com/cmscontent/json/pages/special-offers/all-offers/by-category?storeId=4565&N=103099&Nrpp=60&No=0&requestorigin=gi&shipDate=1528074000000

# URL for contents
# https://ui.assets-asda.com/g/v5/258/216/5054781258216_130_IDShot_4.jpeg

# URL to get Item Level Details (Restrict to 15 items per call)
# https://groceries.asda.com/api/items/view?itemid=910002016369,13852532,910002352739,910001311986,910001004396,910000273987,31847,910001518216,910000993334,9831156,910002849510,910002523180,910000273752,910001053016,910002871253&storeid=4565&shipdate=currentDate


def proxyRequest(url):
    time.sleep(5)
    return requests.get(url, proxies=proxyDict)
    # return requests.get(url)


def getCategories():
    # r = requests.get('https://groceries.asda.com/cmscontent/
    #   json/pages/special-offers/all-offers')
    # r = requests.get('https://groceries.asda.com/cmscontent/
    # json/pages/special-offers/all-offers?Endeca_user_segments=anonymous|
    # store_4565|wapp|vp_XXL|Zero_Order_Customers|
    # Delivery_Pass_Older_Than_12_Months|dp-false|1007|1019|1020|1023|1024|
    # 1027|1038|1041|1042|1043|1047|1053|1055|1057|1059|1067|1070|1082|1087|
    # 1097|1098|1099|1100|1102|1105|1107|1109|1110|1111|1112|1116|1117|1119|
    # 1123|1124|1126|1128|1130&storeId=4565&shipDate=1526605200000&
    # requestorigin=gi&_=1526659177596')
    r = proxyRequest(all_urls['entry_url'])
    json_obj = json.loads(r.text)
    json_data = []
    refinements = json_obj['contents'][0]['mainContent'][0]['refinements']
    for refinement in refinements:
        tmp_data = {}
        tmp_data['category'] = refinement['label']
        tmp_data['count'] = refinement['count']
        tmp1 = 'http://www.test.com/' + refinement['navigationState']
        parsed = urlparse.urlparse(tmp1)
        tmp_data['categoryId'] = urlparse.parse_qs(parsed.query)['N'][0]
        json_data.append(tmp_data)
    logger.debug(json_data)
    return json_data


def getItemIds(categories):
    json_objs = json.loads(json.dumps(categories))
    allCat = []
    for json_obj in json_objs:
        itemIds = {}
        itemIds['category'] = json_obj['category']
        itemIds['sku_repoId'] = []
        logger.info('Working on {}'.format(itemIds['category']))
        catItems = []
        for i in range(0, json_obj['count'], 60):
            time.sleep(5)
            logger.debug(all_urls['item_url'].format(json_obj['categoryId'], i))
            item_resp = proxyRequest(all_urls['item_url'].format(json_obj['categoryId'], i))
            sku_records = json.loads(item_resp.text)['contents'][0]['mainContent'][3]['dynamicSlot']['contents'][0]['mainContent'][0]['records']
            for sku_record in sku_records:
                if(sku_record['attributes']['sku.repositoryId'][0] not in itemIds['sku_repoId']):
                    itemIds['sku_repoId'].append(sku_record['attributes']['sku.repositoryId'][0])
                    logger.debug(sku_record['attributes']['sku.repositoryId'])
            #break
        allCat.append(itemIds)
        catItems.append(itemIds)
        getItemDetails(catItems)
        #break
    logger.debug(allCat)
    return allCat


def getItemDetails(allCat):
    regx = re.compile('[^a-zA-Z0-9 ]')
    totalItems = []
    channel, connection = openConnection(exchangeName, queueName)
    for category in allCat:
        time.sleep(60)
        logger.debug(category['category'] + ': ' + str(len(category['sku_repoId'])))
        logger.debug(category['sku_repoId'])
        for i in range(0, math.ceil(len(category['sku_repoId']) / 15)):
            start = i*15
            end = start + 15
            itemString = ','.join(map(str, category['sku_repoId'][start:end]))
            logger.debug('Start: '+str(start)+' : End: '+str(end))
            logger.debug(itemString)
            logger.info(all_urls['item_detail_url'].format(itemString))
            itemDetail_Output = proxyRequest(all_urls['item_detail_url'].format(itemString))
            items = json.loads(itemDetail_Output.text)['items']
            for item in items:
                tmpItem = {}
                tmpItem['category'] = category['category'] if 'category' in category else ''
                tmpItem['id'] = item['id'] if 'id' in item else ''
                tmpItem['deptName'] = item['deptName'] if 'deptName' in item else ''
                tmpItem['brandName'] = item['brandName'] if 'brandName' in item else ''
                tmpItem['name'] = item['name'] if 'name' in item else ''
                tmpItem['promoDetailFull'] = item['promoDetailFull'] if 'promoDetailFull' in item else ''
                tmpItem['shelfId'] = item['shelfId'] if 'shelfId' in item else ''
                tmpItem['shelfName'] = item['shelfName'] if 'shelfName' in item else ''
                tmpItem['promoDetail'] = item['promoDetail'] if 'promoDetail' in item else ''
                tmpItem['price'] = item['price'] if 'price' in item else ''
                tmpItem['wasPrice'] = item['wasPrice'] if 'wasPrice' in item else ''
                tmpItem['deptId'] = item['deptId'] if 'deptId' in item else ''
                tmpItem['imageURL'] = item['imageURL'] if 'imageURL' in item else ''
                tmpItem['pricePerUOM'] = item['pricePerUOM'] if 'pricePerUOM' in item else ''
                shelfName = regx.sub('', tmpItem['shelfName']).replace('  ', ' ').replace(' ', '-').lower()
                prodName = regx.sub('', tmpItem['name']).replace('  ', ' ').replace(' ', '-').lower()
                tmpItem['productURL'] = 'https://groceries.asda.com/product/' + shelfName + '/' + prodName + '/' + item['id']
                tmpItem['scene7AssetId'] = item['scene7AssetId'] if 'scene7AssetId' in item else ''
                if 'images' in item:
                    tmpItem['thumbnailImage'] = item['images']['thumbnailImage'] if 'thumbnailImage' in item['images'] else ''
                    tmpItem['largeImage'] = item['images']['largeImage'] if 'largeImage' in item['images'] else ''
                else:
                    tmpItem['thumbnailImage'] = ''
                    tmpItem['largeImage'] = ''
                tmpItem['ins_ts'] = datetime.now().strftime("%Y-%m-%d")
                sendMessage(exchangeName, queueName, tmpItem, channel)
                totalItems.append(tmpItem)
    #logger.debug(totalItems)
    connection.close()
    return totalItems


def genOutputFile(offerProducts):
    try:
        os.remove(FILE_NAME)
    except OSError:
        pass
    with io.open(FILE_NAME, 'w+', encoding='utf-8') as outfile:
        json.dump(offerProducts, outfile, ensure_ascii=False)

if __name__ == '__main__':
    #channel, connection = openConnection(exchangeName, queueName)
    categories = getCategories()
    itemIds = getItemIds(categories)
    #offerProducts = getItemDetails(itemIds, channel)
    messageToFile(queueName, fileName=FILE_NAME)
    #connection.close()
