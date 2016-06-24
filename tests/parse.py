from BeautifulSoup import BeautifulSoup
import urllib2
import re
import urlparse
import os
import urllib
import socket
import threading
import Queue
import time

MAX_PAGE_NUM = 30
FILENAME = 'target_list.txt'

def valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s

def get_page(page):
    time.sleep(0.5)
    try:
        content=urllib2.urlopen(page,timeout=10).read()
        return content
    except:
        #print 'There is an error.'
        return []

def get_all_links(content, page):
    if content==[]:
        return []
    links = []
    tempset=set()
    try:
        soup=BeautifulSoup(content)
        for i in soup.findAll('a',{'href':re.compile(('^http|^/'))}):
            end = i['href'].find('/',7)
            if end != -1:
                tempset.add(i['href'][:end])
        for i in tempset:
            links.append(urlparse.urljoin(page,i))        
    except:
        pass
    return links

def working():
    global page_num
    page_num = 0
    while page_num<MAX_PAGE_NUM:
        print page_num
        page = q.get()
        if page not in crawled:
            print page
            content = get_page(page)
            outlinks = get_all_links(content,page)
            if outlinks==[]:
                continue
            for link in outlinks:
                q.put(link)
            if varLock.acquire():
                f = open(FILENAME,'a')
                f.write(page)
                f.write('\n')
                f.close()
                page_num+=1
                crawled.append(page)
                varLock.release()
                q.task_done()

num = 2
crawled = []
graph = {}
varLock = threading.Lock()
q = Queue.Queue()
q.put('http://site.baidu.com')
for i in range(num):
    t=threading.Thread(target=working)
    t.setDaemon(True)
    t.start()
t.join()

#working()
