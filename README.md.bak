# SmallProject

A small monitor

### Prerequisities

1,In this project,we use RabbitMQ as the middleware,take Centos 7 as an example,the installation process is as follows:

```
yum install -y rabbitmq-server
rabbitmq-plugins enable rabbitmq_management
systemctl enable rabbitmq-server
systemctl restart rabbitmq-server
```
By now,you may visit http://MQ_IP:15672 to check whether the installation is successful.

More detailed instructions are available on http://www.rabbitmq.com/download.html

2,We also use pika.

```
yum install -y python-pip
pip install pika
```
3,Setting up SSH trust between each two servers in the environment.

### Description

SmallProject is a bunch of Python scripts.

The target of this project is to monitor a list of hosts within a given SLA time,via different methods.

We mainly have producer,consumer,publisher and schduler--four modules.

* Producer - responsible for dispatching jobs
* Consumer - acting as workers
* Publisher - publishing results to different backends.
* Scheduler - arranging other modules to acheive the time-limit goal

To get the code, execute the following:

```
ca /data
mkdir ebay && cd ebay
git clone git://github.com/pivotal/projectmonitor.git
```

## Configuration

To make things easy,we take "/data/ebay" as the working directory.

* Write a configuration json file as a holder of the modules' info and put it under "/data/ebay/config" where we already have a configuration sample.
* Put all the monitor targets' ip or hostnames into the "/data/ebay/target_list.txt",line by line.
* Configure your RabbitMQ server IP in each script under the "/data/ebay/bin" directory.
* Configure things you wanna to print out in each script under the "/data/ebay/bin" directory.

## Get started

After all the configuration mentioned above,you may run the following code to get started:

```
#On the host where you wanna to see the result on a console:
cd /data/ebay/bin
sh ./start_publisher_console.sh
```
```
#On the host where the scheduler dwells:
cd /data/ebay/bin
python scheduler.py <SLA timeout_in_seconds>
```

## Tests

### Tests on Monitor via SSH method

Since I don't have that many hosts,I picked up single host and changed its /usr/bin/uptime file.Each time I ssh to that host and execute the uptime command,I will get random results(failure or different uptime values).

### Tests on Monitor via HTTP method and PING method

Run the parse.py script under "tests" directory and get a bunch of urls.Then take them as the test targets.

### HA

With RabbitMQ cluster,messages published to the queue are replicated to all slave nodes.Sudden interruption didn't cause data loss.

### Scalability

As the number of monitor targets increased,change the configure file and start more processes or even add more nodes into the cluster to guarantee all jobs finished within the given time limit.

## Others

### Add new monitor method

```
#!/usr/bin/env python
from job import Job

class NewJob(Job):
    def __init__(self,config):
        Job.__init__(self,config)
        
        ## parameters to add
        
    def execute(self):
        
        ## new job description
        
        return message

```

### Publish results to another backend

Add another new queue,filter and consumer in the config file and scripts
