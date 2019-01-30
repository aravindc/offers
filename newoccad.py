import logging
import json
from datetime import datetime
import os
import requests
import io
import time
from messageq import *

# Initialize logger
logging.basicConfig(level=logging.INFO)
LOG_FILE = '/opt/offers/logs/OCCAD_' + \
    datetime.now().strftime("%Y%m%d") + '.log'
hdlr = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(hdlr)

FILE_NAME = '/opt/offers/OCCAD_' + datetime.now().strftime("%Y%m%d") + '.json'
exchangeName = 'Occado'
queueName = '{0}-{1}'.format(exchangeName, datetime.now().strftime("%Y%m%d"))

occado_urls = {
    "base_url": "https://www.ocado.com/webshop/api/v1/browse?tags=19998",
    "img_base": "https://www.ocado.com/productImages/{3}/{0}_0_{1}x{2}.jpg",
    "prod_base": "https://www.ocado.com/webshop/product/{0}/{1}",
    "promo_base": "https://www.ocado.com/webshop/promotion/{0}/{1}",
    "sku_base": "https://www.ocado.com/webshop/api/v1/products?skus={0}"
}


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def getSkuUrls(skus):
    sku_urls = []
    for sku in chunker(skus, 20):
        sku_urls.append(occado_urls['sku_base'].format(
            ",".join(str(x) for x in sku)))
    return sku_urls


def getOffers(skuUrls, channel):

    for skuUrl in skuUrls:
        response = requests.get(skuUrl)
        json_obj = json.loads(response.text)
        full_data = []
        missing_data = []
        for obj in json_obj:
            json_data = {}
            logger.info(obj)

            if 'name' not in obj and 'product' not in obj:
                missing_data.append(obj)
                continue

            if 'product' in obj:
                loc_sku = obj['product']['sku']
                loc_name = obj['product']['name']
                loc_price = obj['product']['price']['current']
                if 'unit' in obj['product']['price']:
                    loc_unit_price = obj['product']['price']['unit']['price']
                    loc_unit = obj['product']['price']['unit']['per']
                else:
                    loc_unit_price = "N/A"
                    loc_unit = "N/A"
                loc_category = obj['product']['mainCategory']
                repl_chars = '£ ,!"^&*()%'
                loc_offtext = obj['product']['offer']['text'].lower()
                for char in repl_chars:
                    loc_offtext = loc_offtext.replace(char, '-')
                loc_offtext = loc_offtext.replace('--', '-')
                loc_offid = obj['product']['offer']['id']
            else:
                loc_sku = obj['sku']
                loc_name = obj['name']
                loc_price = obj['price']['current']
                if 'unit' in obj['price']:
                    loc_unit_price = obj['price']['unit']['price']
                    if 'per' in obj['price']['unit']:
                        loc_unit = obj['price']['unit']['per']
                    else:
                        loc_unit = 'N/A'
                else:
                    loc_unit_price = 'N/A'
                    loc_unit = 'N/A'
                loc_category = obj['mainCategory']
                repl_chars = '£ ,!"^&*()%'
                loc_offtext = obj['offer']['text'].lower()
                for char in repl_chars:
                    loc_offtext = loc_offtext.replace(char, '-')
                loc_offtext = loc_offtext.replace('--', '-')
                if 'id' in obj['offer']:
                    loc_offid = obj['offer']['id']
                else:
                    loc_offid = ''

            logger.info(loc_sku)
            json_data['prod_sku'] = loc_sku
            json_data['prod_name'] = loc_name
            json_data['prod_url'] = occado_urls['prod_base'].format(
                loc_name.replace(' ', '-'), loc_sku)
            json_data['promo_url'] = occado_urls['promo_base'].format(
                loc_offtext, loc_offid)
            json_data['prod_150_img'] = occado_urls['img_base'].format(
                loc_sku, 150, 150, loc_sku[:3])
            json_data['prod_640_img'] = occado_urls['img_base'].format(
                loc_sku, 640, 640, loc_sku[:3])
            json_data['prod_price'] = loc_price
            json_data['prod_unit_price'] = loc_unit_price
            json_data['prod_unit'] = loc_unit
            json_data['category'] = loc_category
            json_data['ins_dt'] = datetime.now().strftime("%Y%m%d")
            sendMessage(exchangeName, queueName, json_data, channel)
            full_data.append(json_data)
        time.sleep(3)
    logger.debug(missing_data)
    logger.debug(full_data)
    return full_data


def getSkuList():
    response = requests.get(occado_urls['base_url'])
    json_obj = json.loads(response.text)
    logger.info(len(json_obj['mainFopCollection']['sections'][0]['fops']))
    sku_list = []
    for obj in json_obj['mainFopCollection']['sections'][0]['fops']:
        sku_list.append(obj['sku'])
    return sku_list


def genOutputFile(offerProducts):
    try:
        os.remove(FILE_NAME)
    except OSError:
        pass
    with io.open(FILE_NAME, 'w+', encoding='utf-8') as outfile:
        json.dump(offerProducts, outfile, ensure_ascii=False)


if __name__ == "__main__":
    channel, connection = openConnection(exchangeName, queueName)
    skuList = getSkuList()
    skuUrls = getSkuUrls(skuList)
    offerProducts = getOffers(skuUrls, channel)
    messageToFile(queueName, fileName=FILE_NAME)
    connection.close()
