import logging
import json
from datetime import datetime
import os
import requests
import io

# Initialize logger
logging.basicConfig(level=logging.INFO)
LOG_FILE = '/opt/offers/logs/MORRI_' + \
    datetime.now().strftime("%Y%m%d") + '.log'
hdlr = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(hdlr)

FILE_NAME = '/opt/offers/MORRI_' + datetime.now().strftime("%Y%m%d") + '.json'

morris_urls = {
    "base_url": "https://www.ocado.com/webshop/api/v1/browse?tags=19998",
    "img_base": "https://www.ocado.com/productImages/{3}/{0}_0_{1}x{2}.jpg",
    "prod_base": "https://www.ocado.com/webshop/product/{0}/{1}",
    "promo_base": "https://www.ocado.com/webshop/promotion/{0}/{1}"
}


def getOffers():
    response = requests.get(morris_urls['base_url'])
    json_obj = json.loads(response.text)
    logger.info(len(json_obj['mainFopCollection']['sections'][0]['fops']))
    full_data = []
    for obj in json_obj['mainFopCollection']['sections'][0]['fops']:
        json_data = {}
        logger.info(obj)
        loc_sku = obj['product']['sku']
        loc_name = obj['product']['name']
        loc_price = obj['product']['price']['current']
        loc_unit_price = obj['product']['price']['unit']['price']
        loc_unit = obj['product']['price']['unit']['per']
        loc_category = obj['product']['mainCategory']
        repl_chars = '£ ,!"^&*()%'
        loc_offtext = obj['product']['offer']['text'].lower()
        for char in repl_chars:
            loc_offtext = loc_offtext.replace(char, '-')
        loc_offtext = loc_offtext.replace('--', '-')
        loc_offid = obj['product']['offer']['id']
        logger.info(loc_sku)
        json_data['prod_sku'] = loc_sku
        json_data['prod_name'] = loc_name
        json_data['prod_url'] = morris_urls['prod_base'].format(
            loc_name.replace(' ', '-'), loc_sku)
        json_data['promo_url'] = morris_urls['promo_base'].format(
            loc_offtext, loc_offid)
        json_data['prod_150_img'] = morris_urls['img_base'].format(
            loc_sku, 150, 150, loc_sku[:3])
        json_data['prod_640_img'] = morris_urls['img_base'].format(
            loc_sku, 640, 640, loc_sku[:3])
        json_data['prod_price'] = loc_price
        json_data['prod_unit_price'] = loc_unit_price
        json_data['prod_unit'] = loc_unit
        json_data['category'] = loc_category
        json_data['ins_dt'] = datetime.now().strftime("%Y%m%d")
        full_data.append(json_data)
        logger.info(full_data)
        return full_data


if __name__ == "__main__":
    offerProducts = getOffers()
    try:
        os.remove(FILE_NAME)
    except OSError:
        pass
    with io.open(FILE_NAME, 'w+', encoding='utf-8') as outfile:
        json.dump(offerProducts, outfile, ensure_ascii=False)
