# SmallProject
A small monitor

## Requirements
In this project,we use RabbitMQ as the middleware,take Centos 7 as an example,the installation process is as follows:

    yum install -y rabbitmq-server
    rabbitmq-plugins enable rabbitmq_management
    systemctl enable rabbitmq-server
    systemctl restart rabbitmq-server
    
By now,you may visit http://<host-ip>:15672 to check whether the installation is successful.More detailed instruction is available on 

		http://www.rabbitmq.com/download.html
		
We also use pika.
Pika is a pure-Python implementation of the AMQP 0-9-1 protocol that tries to stay fairly independent of the underlying network support library,which is also recommended by RabbitMQ.
It can be installed via pip and if you haven't installed pip in your environment,run the first commmand first.

		yum install -y python-pip
		pip install pika
		
Since monitor via SSH method is included in this project,before we get started,we need to setting up SSH trust between each two server in the environment.
Reference script can be found under the "tests" directory   

## Description
SmallProject is a bunch of Python scripts. To get the code, execute the following:

    ca /data
    mkdir ebay && cd ebay
    git clone git://github.com/pivotal/projectmonitor.git

The target of this project is to monitor a list of hosts within a given SLA time,via different methods.
So as input,we must provide a text file containing all the hosts and a SLA time.Take monitoring each host as a job,we dispatch jobs to different workers simultaneously.
After each job is done,the result will be published to backends.Different backends may have their own filters to satisfy different needs.
We mainly have producer,consumer,publisher and schduler,four modules.
The producer is responsible for dispatching jobs,while the consumer module acts as a worrker.Then we have publisher to publish results to different backends.
The scheduler works on scheduling other modules to acheive the time-limit goal. 


## Configuration
To make things easy,we take "/data/ebay" as the working directory.
1,Write a configuration json file as a holder of the modules' info and put it under "/data/ebay/config" where we already have a configure sample.

2,Put all the monitor targets' ip or hostname in the "/data/ebay/target_list.txt",line by line.

3,Configure your RabbitMQ server IP in each script under the "/data/ebay/bin" directory.

4,Configure things you wanna to print out in each script under the "/data/ebay/bin" directory.

## Get started

After all the configuration mentioned above,you may run the following code to get started:

		1,On the host where you wanna to see the result on a console:
		cd /data/ebay/bin
		sh ./start_publisher_console.sh
		
		2,On the host where the scheduler dwells:
		cd /data/ebay/bin
		python scheduler.py <SLA timeout_in_seconds>


## Tests
1,Tests on Monitor via SSH method
Since I don't have that many host,I picked up single host and changed the /usr/bin/uptime file.Each time I ssh to that host and execute the uptime command,
I will get random results(failure or different uptime value).

2,Tests on Monitor via HTTP method and PING method
Run the parse.py script under "tests" directory and get a bunch of urls.Then take them as the test targets.

3,HA
With RabbitMQ cluster,messages published to the queue are replicated to all slave nodes.Sudden interruption didn't cause data loss.

4,Scalability
As the number of monitor targets increased,change the configure file and start more processes or even add more nodes into the cluster to guarantee all jobs finished within the given time limit.
