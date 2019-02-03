import json
import requests
import time


http_proxy = "http://localhost:8123"
https_proxy = "https://localhost:8123"

proxyDict = {
    "http": http_proxy,
    "https": https_proxy,
}

url = 'https://www.rightmove.co.uk/api/_search?locationIdentifier=REGION%5E61537&numberOfPropertiesPerPage=24&radius=0.0&sortType=2&index={0}&includeSSTC=false&viewType=LIST&channel=BUY&areaSizeUnit=sqft&currencyCode=GBP&isFetching=false&viewport='

def proxyRequest(url):
    time.sleep(5)
    return requests.get(url, proxies=proxyDict)


def getCount():
    response = proxyRequest(url.format(0))
    json_obj1 = json.loads(response.text)
    total_count = json_obj1['resultCount']
    return int(total_count.replace(',', ''))


def createOutput(total_count):
    for i in range(0, total_count, 24):
        response = proxyRequest(url.format(i))
        json_obj = json.loads(response.text)
        if 'properties' not in json_obj:
            print(json_obj)
            print(i)
            break
        for redbprop in json_obj['properties']:
            #print('{0}|{1}|{2}|{3}|{4}|{5}|{6}'.format(
            #    redbprop['id'],redbprop['bedrooms'],redbprop['price']['amount'],
            #    redbprop['location']['latitude'],redbprop['location']['longitude'],
            #redbprop['propertySubType'],redbprop['displayAddress']))
            with open('redbridge.csv', 'a+') as f:
                f.write('{0}|{1}|{2}|{3}|{4}|{5}|{6}\n'.format(
                    redbprop['id'], redbprop['bedrooms'], redbprop['price']['amount'],
                    redbprop['location']['latitude'], redbprop['location']['longitude'],
                    redbprop['propertySubType'], redbprop['displayAddress'].replace('\r\n', ' ')))

if __name__ == '__main__':
    createOutput(getCount())
