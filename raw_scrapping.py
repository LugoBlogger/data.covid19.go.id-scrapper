import bs4
import sys
import time

from threading import Thread
from multiprocessing import Process, Manager

from bs4 import BeautifulSoup

from selenium import webdriver

#sys.setrecursionlimit(1000)

class WorkerTask(object):
    def __init__(self, queue_dict):
        self.queue_dict = queue_dict
        
    def worker(self):
        base_site = "https://data.covid19.go.id/public/index.html"
        
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=options)
        driver.get(base_site)
        
        soup_page = BeautifulSoup(driver.page_source, parser="html5lib", features="lxml")
        
        self.queue_dict[0] = str(soup_page)
        #time.sleep(3)
        
        
class ProgressTask: 
    def __init__(self): 
        self._running = True
      
    def terminate(self): 
        self._running = False
      
    def print_point(self): 
        while self._running: 
            sys.stdout.write(".") 
            sys.stdout.flush()
            time.sleep(1) 


def scrap_covid19_go_id():
    queue_dict = Manager().dict()
    print(queue_dict.values())

    progress_ins = ProgressTask() 
    progress_proc = Thread(target=progress_ins.print_point) 
    progress_proc.start() 
    #print(os.getpid())
    
    # Signal termination 
    worker_ins = WorkerTask(queue_dict)
    worker_proc = Process(target=worker_ins.worker)
    worker_proc.start()
    worker_proc.join()
    
    if not worker_proc.is_alive():
        progress_ins.terminate()
        progress_proc.join()

    #print(queue_dict.values())
    soup_page = BeautifulSoup(queue_dict.values()[0], parser="lxml", features="lxml")
    
    return soup_page

            
if __name__ == '__main__':
    soup_page = scrap_covid19_go_id()
    #print(soup_page.prettify())
    #print(type(soup_page))
