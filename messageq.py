# -*- coding: utf-8 -*-
import pika
import json
import os
import io
import hashlib


def openConnection(exchangeName, queueName):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchangeName, passive=False,
                             durable=True, exchange_type='direct')
    channel.queue_declare(
        queue=queueName, durable=True,
        arguments={"x-message-deduplication": True,
                   "x-cache-persistence": "disk"})
    channel.queue_bind(queue=queueName,
                       exchange=exchangeName, routing_key=queueName)
    return channel, connection


def sendMessage(exchangeName, queueName, jsonData, channel):
    header = hashlib.md5(str(jsonData).encode()).hexdigest()
    print(header)
    channel.basic_publish(exchange=exchangeName,
                          routing_key=queueName, body=json.dumps(jsonData),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                              headers={'x-deduplication-header': header},
                              ))


def deleteQueue(queueName, channel):
    channel.queue_delete(queue=queueName)


def messageToFile(queueName, fileName):
    print("Starting to Read Messages")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    queueHandler = channel.queue_declare(queueName, durable=True)
    queueSize = queueHandler.method.message_count
    jsonOutput = []
    for i in range(0, queueSize):
        m, h, b = channel.basic_get(queueName)
        jsonOutput.append(json.loads(b.decode('utf8')))
        # channel.basic_ack(m.delivery_tag)
        print(i)
        print(m)
        print(h)
    try:
        os.remove(fileName)
    except OSError:
        pass
    with io.open(fileName, 'w+', encoding='utf-8') as outfile:
        json.dump(jsonOutput, outfile, ensure_ascii=False,
                  sort_keys=True, indent=0)


def on_message(channel, method_frame, header_frame, body):
    print(method_frame.delivery_tag)
    print(body)
    print(channel.basic_ack(delivery_tag=method_frame.delivery_tag))
