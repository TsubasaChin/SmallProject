#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pika
import sys
import logging

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='/data/ebay/log/monitor.log',
                filemode='a+')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


#MQ_IP = '20.26.20.70'
EXCHANGE_NAME = 'backend_publish'
EXCHANGE_TYPE = 'direct'

input = sys.argv[1:]
if (not input) or (len(input)<2):
    sys.stderr.write("Usage: %s [MQ_IP][INFO] [WARNING][ERROR]\n" % sys.argv[0])
    sys.exit(1)
else:
    MQ_IP = input[0]



class Publisher():
    def __init__(self):
        print "This is a backend publisher"
        

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_IP))
        self.channel = self.connection.channel()

    def exchange(self,exchange_name,exchange_type):
        self.channel.exchange_declare(exchange=exchange_name,
                                      type=exchange_type)

    def queue_declare(self):
        result = self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        return queue_name

    def binding(self,exchange_name,queue_name,routing_key):
        self.channel.queue_bind(exchange=exchange_name,
                                queue=queue_name,
                                routing_key=routing_key)
    
    def callback(self,ch,method,properties,body):
        #log_info=body.split('\t')[-1]
        is_Success,message = body.split('\t')
        is_Success = bool(is_Success)
        if is_Success:
            logging.info(message)
        else:
            logging.error(message)


    def consume(self,queue_name):
        self.channel.basic_consume(self.callback,
                                   queue=queue_name,
                                   no_ack=True) 
        print(' [*] Waiting for log to publish to backend. To exit press CTRL+C')
        self.channel.start_consuming()

    def disconnect(self):
        self.connection.close()

    def run(self):
        self.connect()
        self.exchange(EXCHANGE_NAME,EXCHANGE_TYPE)
        queue_name = self.queue_declare()
        for item in input[1:]:
            self.binding(EXCHANGE_NAME,queue_name,item)
        self.consume(queue_name)
        self.disconnect()


if __name__ == "__main__":
    publisher = Publisher()
    publisher.run()
