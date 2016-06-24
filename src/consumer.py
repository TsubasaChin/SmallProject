#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,time
import pika
from job import *

QUEUE_NAME = 'to_do_queue'
EXCHANGE_NAME = 'backend_publish'
EXCHANGE_TYPE = 'direct'

input = sys.argv[1:]
if (not input) or (len(input)<2):
    sys.stderr.write("Usage: %s [MQ_IP][INFO] [WARNING] [ERROR]\n" % sys.argv[0])
    sys.exit(1)
else:
    MQ_IP = input[0]
    severity = input[1]

class Consumer:
    def __init__(self):
        self.queue_name = QUEUE_NAME

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_IP))
        self.channel = self.connection.channel()

    def queue_declare(self):
        self.channel.queue_declare(queue=self.queue_name)

    def exchange(self,exchange_name,exchange_type):
        self.channel.exchange_declare(exchange=exchange_name,
                                      type=exchange_type)
        
    def publish(self,body_content,console_feedback_info,routing_key,exchange_name=''):
        self.channel.basic_publish(exchange=exchange_name,
                              routing_key=routing_key,
                              body=body_content)
        print(console_feedback_info)
    
    def job_execution(self,body):
        job_info = body.split('\t')
        job_id = job_info[0]
        target = job_info[1]
        job_type = job_info[2]
        config = {'job_id':job_id,'target':target,'job_type':job_type}
        if job_type == 'SSH':
            job = SshJob(config)
        elif job_type == 'PING':
            job = PingJob(config)
        elif job_type == 'HTTP':
            job = HttpJob(config)
        else:
            raise RuntimeError("Wrong job type.")

        self.exchange(EXCHANGE_NAME,EXCHANGE_TYPE)
        try:
            is_Success,message = job.execute()
            console_feedback_info = "[x] Publishing Job %s(SUCCEEDED) to EXCHANGE %s" % (job_id,EXCHANGE_NAME)
            print(message)
            #time.sleep(5)
            #body_content = str(job_id)+'\t'+target+'\t'+message
            #body_content = ' '.join(sys.argv[2:]) or 'Hello World!'
            body_content = str(is_Success) + '\t' + message
            self.publish(body_content,console_feedback_info,severity,EXCHANGE_NAME)
        except:
            console_feedback_info = "[x] Publishing Job %s(FAILED) to EXCHANGE %s" % (job_id,EXCHANGE_NAME)
            #body_content = str(job_id)+'\t'+target+'\t'+message
            message = 'Job %s failed' % job.job_id
            body_content = str(is_Success) + '\t' + message
            self.publish(body_content,console_feedback_info,EXCHANGE_NAME)

    def callback(self,ch,method,properties,body):
        self.job_execution(body)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def consume(self):
        self.channel.basic_qos(prefetch_count=1) # not to give more than one job to a worker at a time
        self.channel.basic_consume(self.callback,
                                   queue=self.queue_name)
        print(' [*] Waiting for jobs. To exit press CTRL+C')
        self.channel.start_consuming()

    def disconnect(self):
        self.connection.close()

    def run(self):
        self.connect()
        #self.queue_declare()
        self.consume()
        self.disconnect()

if __name__ == "__main__":
    consumer = Consumer()
    consumer.run()
