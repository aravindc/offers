from datetime import date, timedelta, datetime
from dbconfig import read_rabbit_config
import logging
import requests
import json
import pika

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    oneWeekPrior = datetime.today() - timedelta(7)
    print(oneWeekPrior)
    clientQueues = [
        'SAINS',
        'ASDA',
        'MORRI',
        'OCCAD',
        'SNASH'
    ]
    rabbit_config = read_rabbit_config()
    logger.info(rabbit_config)
    base_url = 'http://{0}:{1}@{2}:15672'.format(rabbit_config['user'],
                                                 rabbit_config['pass'],
                                                 rabbit_config['host'])
    vhost = '%2F'
    response = requests.get(base_url+'/api/queues/{}'.format(vhost))
    logger.info(response)
    logger.info(response.text)
    json_queues = json.loads(response.text)
    for json_queue in json_queues:
        clientName = json_queue['name'].split('_')[0]
        queueDate = datetime.strptime(json_queue['name'].split('_')[1], '%Y%m%d')
        if queueDate <= oneWeekPrior and clientName in clientQueues:
            response = requests.delete(base_url+'/api/queues/{}/{}'.format(vhost, json_queue['name']))
            logger.info(response.text)
            logger.info(json_queue['name'])
