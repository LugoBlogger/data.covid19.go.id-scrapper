import time
import sys
import bs4
import json
import argparse
import textwrap

from bs4 import BeautifulSoup
from selenium import webdriver
from pathlib import Path
from threading import Thread
from multiprocessing import Process, Manager


class WorkerTask(object):
    def __init__(self, queue_dict):
        self.queue_dict = queue_dict


    def worker(self):
        base_site = "https://data.covid19.go.id/public/index.html"
        
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",
                                  options=options)
        driver.get(base_site)
        
        soup_page = BeautifulSoup(driver.page_source, parser="lxml",
                                  features="lxml")

        # multiprocessing.Manager() cannot handle complex data type 
        # e.g: bs4.BeautifulSoup
        # so we convert it to string (primitive data type)
        self.queue_dict[0] = str(soup_page)
        

class ProgressTask(object):
    def __init__(self):
        self._running = True

    
    def terminate(self):
        self._running = False


    def print_point(self):
        while self._running:
            # Using print doesn't work in Ubuntu terminal
            #print(".", end="")
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1)


def get_page_covid19_go_id():
    queue_dict = Manager().dict()
    #print(queue_dict.values())

    progress_ins = ProgressTask()
    progress_proc = Thread(target=progress_ins.print_point)
    progress_proc.start()

    # signal termination
    worker_ins = WorkerTask(queue_dict)
    worker_proc = Process(target=worker_ins.worker)
    worker_proc.start()
    worker_proc.join()

    if not worker_proc.is_alive():
        progress_ins.terminate()
        progress_proc.join()

    # revert back soup_page to bs4.BeautifulSoup
    soup_page = BeautifulSoup(queue_dict.values()[0], parser="lxml",
                              features="lxml")

    return soup_page


def extract_time_stamp(soup_page):
    return [data.get_text().split()[-1] 
            for data in soup_page.\
                        find_all('span', attrs={'class': 'pull-right'}) 
                if 'Tanggal' in data.get_text()]

    
def extract_headlines(soup_page):
    headlines = [[headline_data.find('h3').string] \
                    + [data.string for data in headline_data.find_all('b')] 
                 for headline_data in soup_page\
                                      .find_all('div', 
                                                attrs={'class': 'col-md-3'})]
                                      
    return {label.lower(): [total_case, increment.lower()] 
            for total_case, label, increment in headlines}


def extract_provinces_data(soup_page):
    return {data.find('b').get_text().strip().lower()\
                :data.find('span').string[15:] 
            for data in soup_page.\
                        find_all('div', attrs={'class': 'wrapDetailInfo'})}


def get_clean_data(filename, download_again=False):
    path_to_file = Path.cwd() / Path(filename)

    if not path_to_file.is_file() or download_again:

        print("Start scrapping page of data.covid19.go.id/public/index.html")
        soup_page = get_page_covid19_go_id()
        print("\nScrapping data.covid19.go.id finished.")
        
        data = {"time_stamp": extract_time_stamp(soup_page),
                "headlines": extract_headlines(soup_page),
                "provinces_data": extract_provinces_data(soup_page)}
        print("Extraction finished.")

        with open(filename, "w") as f:
            f.write(json.dumps(data, indent=2))

    else:
        with open(path_to_file, "r") as f:
            data = f.read()
        
        data = json.loads(data)

    return data 


def user_input_parser():
    parser = argparse.ArgumentParser(
                prog=sys.argv[0],
                formatter_class=argparse.RawDescriptionHelpFormatter,
                description=textwrap.dedent("""\
                    scrapping data.covid19.go.id
                    ----------------------------
                        examples: 
                        1) Specify filename, force the program to scrap again
                           instead to read the previously saved JSON File, and 
                           print only the headlines
                        
                             $ python web-scrapping.py -f dump.json -d True
                   
                        2) Specify the data in a specific province and the headline
                        
                             $ python web-scrapping.py -p "Jawa Timur"

                    """))
    parser.add_argument("-f", type=str, default="covid19.json", 
                        help="the name of JSON file")
    parser.add_argument("-d", type=bool, default=False, 
                        help="whether to scrap the data again or not")
    parser.add_argument("-p", type=str, default=None,
                        help="select specific province's data")

    args = parser.parse_args()

    # access input variables by [args.f, args.d, args.p]
    return args


def print_ts_and_headline(data):
    time_stamp = data["time_stamp"]
    print("-"*29)
    print(f" Last updated at: {time_stamp[0]}")
    print("-"*29)
    
    for label, val in data["headlines"].items():
        print(f"{label:>16s}: {val[0]:>7s} orang ({val[1]})")


def print_province(data, province):
    province = province.lower()
    print("")
    print(" "*4, end="")
    print(f"{province.capitalize()}: {data[province]}")



if __name__ == "__main__":

    args = user_input_parser()
    data = get_clean_data(args.f, download_again=args.d)
    print_ts_and_headline(data)

    if args.p:
        print_province(data["provinces_data"], args.p)
