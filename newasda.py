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
from messageq import deleteQueue
from conxn import Conxn

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
catQueue = 'ASDA_CAT_QUEUE'
itemQueue = 'ASDA_ITEM_QUEUE'

c = Conxn()

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
    r = c.getUrlContent(url = all_urls['entry_url'])
    json_obj = json.loads(r.text)
    json_data = []
    refinements = json_obj['contents'][0]['mainContent'][0]['refinements']
    channel, connection = openConnection(exchangeName, catQueue)
    deleteQueue(catQueue, channel)
    channel.close()
    connection.close()
    channel, connection = openConnection(exchangeName, catQueue)
    for refinement in refinements:
        tmp_data = {}
        tmp_data['category'] = refinement['label']
        tmp_data['count'] = refinement['count']
        tmp1 = 'http://www.test.com/' + refinement['navigationState']
        parsed = urlparse.urlparse(tmp1)
        tmp_data['categoryId'] = urlparse.parse_qs(parsed.query)['N'][0]
        json_data.append(tmp_data)
        sendMessage(exchangeName, catQueue, tmp_data, channel)
    logger.debug(json_data)
    channel.close()
    connection.close()
    return json_data

def getItemIds(categories):
    json_objs = json.loads(json.dumps(categories))
    allCat = []
    channel, connection = openConnection(exchangeName, itemQueue)
    deleteQueue(catQueue, channel)
    channel.close()    
    channel, connection = openConnection(exchangeName, itemQueue)
    for json_obj in json_objs:
        itemIds = {}
        itemIds['category'] = json_obj['category']
        itemIds['sku_repoId'] = []
        logger.info('Working on {}'.format(itemIds['category']))
        catItems = []
        for i in range(0, json_obj['count'], 60):
            time.sleep(5)
            logger.debug(all_urls['item_url'].format(json_obj['categoryId'], i))
            item_resp = c.getUrlContent(url = all_urls['item_url'].format(json_obj['categoryId'], i))
            sku_records = json.loads(item_resp.text)['contents'][0]['mainContent'][3]['dynamicSlot']['contents'][0]['mainContent'][0]['records']
            for sku_record in sku_records:
                if(sku_record['attributes']['sku.repositoryId'][0] not in itemIds['sku_repoId']):
                    itemIds['sku_repoId'].append(sku_record['attributes']['sku.repositoryId'][0])
                    logger.debug(sku_record['attributes']['sku.repositoryId'])
                break
            #break
        allCat.append(itemIds)
        catItems.append(itemIds)
        logger.info(itemIds)
        #getItemDetails(catItems)
        #break
        channel, connection = openConnection(exchangeName, itemQueue)
        sendMessage(exchangeName, itemQueue, itemIds, channel)
        channel.close()
        connection.close()
    logger.debug(allCat)
    return allCat    

if __name__ == '__main__':
    categories = getCategories()
    getItemIds(categories)