#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time,datetime
import os,sys
import socket
import subprocess
import re
import urllib2, httplib

PING_TTL = "5"
SSH_CONNECTTIMEOUT = "5"

class Job:
    def __init__(self,config):
        '''config should be a dict'''
        try:
            self.job_id = config['job_id']
            self.job_target = config['target']
            self.job_type = config['job_type']
	    #self.job_command = config['command']
	    self.auto_recover_command = ''
	except:
            raise RuntimeError("Required configuration fields missing")

        if self.job_id == '':
            raise RuntimeError("missing job_id")
        if self.job_target == '':
            raise RuntimeError("missing job target")
        if self.job_type == '':
            raise RuntimeError("missing job type")

    def execute(self):
        """Override this method to perform the test."""
        raise NotImplementedError

    def set_auto_recover(self,recover_command):
        self.auto_recover_command = recover_command

    def recover(self):
        if self.auto_recover_command != '':
            try:
                p = subprocess.Popen(self.auto_recover_command, shell=True)
                p.wait()
                recover_message = "Command executed and returned %d" % p.returncode
            except Exception, e:
                recover_message = "Unable to run command: %s" % e
            print recover_message
        return
 
class PingJob(Job):

    def __init__(self,config):
        Job.__init__(self,config)
        try:
            ping_ttl = config['ping_ttl']
        except:
            ping_ttl = PING_TTL
            
        self.ping_command = "ping -c1 -W" + ping_ttl + " %s 2> /dev/null"
        self.ping_flag = "bytes from"
        self.time_flag = "min/avg/max/mdev = [\d.]+/(?P<ms>[\d.]+)/"

    def execute(self):
        r1 = re.compile(self.ping_flag)
        r2 = re.compile(self.time_flag)
        time_used = 0.0
        is_Success = False

        try:
            p = os.popen(self.ping_command % self.job_target)
            for response_line in p:
                if r1.search(response_line):
                    is_Success = True
                else:
                    if r2.search(response_line):
                        time_used = r2.search(response_line).group("ms")
            if (not is_Success) or (time_used == 0.0):
                message = "Host %s is not reachable." % self.job_target
            else:
                message = "Host %s is reachable and the average ping time is %s." % (self.job_target,time_used)
        except Exception,e:
            message = e
        return is_Success,message
     

class SshJob(Job):

    def __init__(self,config):
        Job.__init__(self,config)
        try:
            connect_timeout = config["connect_timeout"]
        except:
            connect_timeout = SSH_CONNECTTIMEOUT

        self.ssh_command = "ssh -o ConnectTimeout=" + connect_timeout + " %s uptime 2> /dev/null"
        self.uptime_flag = "up"
        self.days_flag = "days"
    
    def execute(self):
        r1 = re.compile(self.uptime_flag)
        up_days = 0.0
        is_Success = False

        try:
            p = os.popen(self.ssh_command % self.job_target)
            for response_line in p:
                if r1.search(response_line):
                    is_Success = True
                    start = re.search(self.uptime_flag,response_line).start()+3
                    end = re.search(self.days_flag,response_line).start()-1
                    up_days = response_line[start:end]
            message = "Host %s is up for %s days." % (self.job_target,up_days)
        except Exception,e:
            message = e
        return is_Success,message

class HttpJob(Job):

    def __init__(self,config):
        Job.__init__(self,config)

    def execute(self):
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(5)
        start_time = time.time()
        end_time = None
        status = None
        time_used = 0.0
        is_Success = False

        try:
            u = urllib2.urlopen(self.job_target)
            end_time = time.time()
            time_used = float(end_time - start_time)
            status = "200 OK"
            if hasattr(u,"status") and u.status != "":
                status = u.status
            if status == "200 OK":
                is_Success = True
                message = "Http request to %s got status '200 OK' and the load time was %0.2fs." % (self.job_target,time_used)
            else:
                message = "Http request to %s got status '%s' instead of 200 OK" % (self.job_target,status)
        except urllib2.HTTPError, e:
            status = "%s %s" % (e.code, e.reason)
            message = "HTTP error(%s) when sending request to URL %s" % (status,self.job_target)
        except Exception, e:
            message = "Exception while trying to open URL %s: %s" % (self.job_target,e)

        return  is_Success,message
                

        
        
