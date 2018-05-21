import requests
import json
import logging
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

asda_urls = {
    "base_url": "https://groceries.asda.com",
    "entry_url": "https://groceries.asda.com/cmscontent/json/pages/" +
                 "special-offers/all-offers?storeId=4565&shipDate=" +
                 str(int(time.time())*1000)
    }


def testFunction():
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
    url1 = json.loads(json.dumps(asda_urls))
    logger.info(url1)
    r = requests.get(url1['entry_url'])
    json_obj = json.loads(r.text)
    json_data = []
    refinements = json_obj['contents'][0]['mainContent'][0]['refinements']
    for refinement in refinements:
        tmp_data = {}
        tmp_data['label'] = refinement['label']
        tmp_data['count'] = refinement['count']
        tmp_data['navigationState'] = refinement['navigationState']
        json_data.append(tmp_data)
    logger.info(json_data)
    return json_data


if __name__ == '__main__':
    testFunction()

#1526605200000
#1526855938000
