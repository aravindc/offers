import pika
import requests
import json
from dbconfig import read_rabbit_config

if __name__ == "__main__":
    rabbit_config = read_rabbit_config()
    print(rabbit_config)
    base_url = 'http://{0}:{1}@{2}:15672'.format(rabbit_config['user'],rabbit_config['pass'],rabbit_config['host'])
    response = requests.get(base_url+'/api/queues')
    print(json.loads(response.text))