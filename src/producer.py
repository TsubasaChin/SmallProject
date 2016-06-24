#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import pika

input = sys.argv[1:]
if (not input) or (len(input)<3):
    sys.stderr.write("Usage: %s [TARGET_LIST_FILE][MQ_IP][JOB_TYPE]" % sys.argv[0])
    sys.exit(1)
else:
    target_list_file = input[0]
    MQ_IP = input[1]
    JOB_TYPE = input[2]
    f = open(target_list_file,'r')
    MONITOR_TARGETS = f.read().splitlines()
QUEUE_NAME = 'to_do_queue'

class Producer:
    
    def __init__(self,target_list):
        self.target_list = MONITOR_TARGETS
        self.queue_name = QUEUE_NAME
        
    def connect(self):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_IP))
            self.channel = self.connection.channel()
        except:
            raise RuntimeError("Cannot connect to the RabbitMQ server,is the IP correct?")
    
    def queue_declare(self):
        self.channel.queue_declare(queue=self.queue_name,durable=True) 

    def publish(self,body_content,console_feedback_info,exchange_name=''):
        self.channel.basic_publish(exchange=exchange_name,
                              routing_key=self.queue_name,
                              body=body_content,
                              properties=pika.BasicProperties(
                                 delivery_mode=2, # make body_content persitent
                              ))
        print(console_feedback_info)
    
    def disconnect(self):
        self.connection.close()

    def run(self):
        self.connect()
        self.queue_declare()
        job_id = 0
        for target in self.target_list:
            job_id += 1
            body_content = str(job_id)+'\t'+target+'\t'+str(JOB_TYPE)
            console_feedback_info = "[x] Publishing Job %s to Queue %s" % (job_id,self.queue_name)
            self.publish(body_content,console_feedback_info)
        self.disconnect()

if __name__ == "__main__":
    producer = Producer(MONITOR_TARGETS)
    producer.run()
