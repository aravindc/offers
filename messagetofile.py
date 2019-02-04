# -*- coding: utf-8 -*-
import logging
import pika
import requests
import json
from dbconfig import read_rabbit_config
from messageq import messageToFile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    rabbit_config = read_rabbit_config()
    print(rabbit_config)
    base_url = 'http://{0}:{1}@{2}:15672'.format(rabbit_config['user'],rabbit_config['pass'],rabbit_config['host'])
    response = requests.get(base_url+'/api/queues')
    json_queues = json.loads(response.text)
    for json_queue in json_queues:
        queue_name = json_queue['name']
        logger.info(queue_name)
        if json_queue['messages_ready']:
            messageToFile(queue_name,'c:/opt/offers/{0}.json'.format(queue_name))
        else:
            logger.info('{} is empty'.format(queue_name))
            continue
