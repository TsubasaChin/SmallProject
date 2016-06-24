import os, time, random
from subprocess import Popen,PIPE
import json
import sys

CONFIG_FILE = '../config/sys_config.json'
#TARGET_LIST_FILE = '../target_list.txt'
#TIMEOUT_IN_SECONDS = 30

input = sys.argv[1]
if not input:
    sys.stderr.write("Usage: %s [TIMEOUT_IN_SECONDS]\n" % sys.argv[0])
else:
    TIMEOUT_IN_SECONDS = float(input)

def get_sys_config(config_file):
    try:
        with open(config_file) as data_file:
            config = json.load(data_file)
        return config
    except:
        raise RuntimeError("Something wrong with the config file.")

def run(command):
    p = Popen(command, shell=True,stdin=PIPE, stdout=PIPE, stderr=PIPE)
    time.sleep(0.5)
    p.terminate()

if __name__=='__main__':
    print 'Start scheduling all modules to work.'
    timeout = TIMEOUT_IN_SECONDS
    kill_command = 'ssh -oStrictHostKeyChecking=no %s "pkill -f ebay"'
    print 'Timeout value is %.1fs.' % timeout
    p = {}
    config = get_sys_config(CONFIG_FILE)
    
    host_list = []
#    for pulisher in config['publisher']:
#        host_list.append(pulisher['host'])
#        command_string = "ssh -oStrictHostKeyChecking=no %s \"%s\"" %(pulisher['host'],pulisher['command'])
#        run(command_string)
    for producer in config['producer']:
        host_list.append(producer['host'])
        command_string = "ssh -oStrictHostKeyChecking=no %s \"%s\"" %(producer['host'],producer['command'])
        run(command_string)
        for consumer in producer['consumer']:
            host_list.append(consumer['host'])
            command_string = "ssh -oStrictHostKeyChecking=no %s \"%s\"" %(consumer['host'],consumer['command'])
            run(command_string)

    time.sleep(timeout)
    for host in host_list:
        os.system(kill_command % host)
        time.sleep(2)

    print 'All Jobs done.'

