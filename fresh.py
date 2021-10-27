from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from langdetect import detect, DetectorFactory
from retrying import retry
import pandas as pd
import time
import random
import requests
import logging
import uuid
import argparse
import json
import mysql.connector
import fresh_models as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import UUIDType
from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
from urllib3.util import Retry
from publishers_headers import *
from extractor import extract_information
import threading
from threading import Thread, Lock
from multiprocessing import Process, Pool
from urllib.request import urlopen
from pymongo import MongoClient
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from url_list import *

DetectorFactory.seed = 0
# logging.basicConfig(filename='new_crawling.log',
#                     format='%(asctime)s %(levelname)-8s %(message)s',
#                     level=logging.INFO,
#                     datefmt='%Y-%m-%d %H:%M:%S')

# logging.basicConfig(filename='temp.log',
#                     format='%(asctime)s %(levelname)-8s %(message)s',
#                     level=logging.INFO,
#                     datefmt='%Y-%m-%d %H:%M:%S')

headers_main = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'}

proxies_ip_list = [
                   "https://ishjoatt-1:lrm30lf8w0dg@p.webshare.io:80",
                   "https://ishjoatt-2:lrm30lf8w0dg@p.webshare.io:80",
                   "https://ishjoatt-3:lrm30lf8w0dg@p.webshare.io:80",
                   "https://ishjoatt-4:lrm30lf8w0dg@p.webshare.io:80",
                   "https://ishjoatt-5:lrm30lf8w0dg@p.webshare.io:80"
]

client = MongoClient()
mydb = client['cms_major']
raw_articles_mongodb = mydb.data

my_connect = mysql.connector.connect(
  host='localhost',
  user='db',
  passwd='newzer@',
  database='cms_major'
)


session_factory = sessionmaker(bind = db.get_dbEngine())
Session = scoped_session(session_factory)


def requests_retry_session(
    retries=3,
    backoff_factor=0.15,
    status_forcelist=(400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 414, 415, 416, 417, 418, 421,
                      422, 423, 424, 425, 426, 428, 429, 431, 451, 500, 501, 502, 503, 504, 505, 506, 507, 508, 510,
                      511),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


# pip install latest-user-agents
from latest_user_agents import get_latest_user_agents, get_random_user_agent
@retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000, wait_exponential_max=32000)
def make_requests(url, header):
    header['User-Agent'] = get_random_user_agent()
    try:
        response = requests.get(url, timeout=4, verify=False,
                                headers=header,
                                proxies={
                                    "http": "http://ishjoatt-rotate:lrm30lf8w0dg@p.webshare.io:80/",
                                    "https": "http://ishjoatt-rotate:lrm30lf8w0dg@p.webshare.io:80/"
                                })
    except:
        pass
    if response.status_code != 200:
        raise ValueError("Error with request")
    return response


class BaseCrawler:
    def _crawl_page(self, url):
        retries = 1
        for i in range(100):
            logging.info("Try No.:: {}, URL:: {}".format(i, url))
            print("Try No.:: {}, URL:: {}".format(i, url))
            try:
                response = make_requests(url, headers_main)
                # response = requests.get(url, timeout=2, verify=False, headers=headers_main)
                status = response.status_code
                if status == 200:
                    return response.content
                logging.info("Got the response code: {}".format(status))
            except Exception as exception:
                logging.info(
                    "EXCEPTION {} occurred for this url while getting the html for archive: {}"
                    .format(exception, url))
                time.sleep(0.5)
                retries += 1
        return ""


class SimpleCrawler:
    _results = {}

    @staticmethod
    def fetch_url(url, timeout=2, crawl_type=None, publisher="EconomicTimes"):
        html, status_code = SimpleCrawler._fetch_url(url, timeout=timeout, crawl_type=crawl_type, publisher=publisher)
        return html, status_code

    @staticmethod
    def _fetch_url(url, timeout=None, crawl_type=None, publisher="EconomicTimes"):
        logging.info("==> Entered _fetch_urls:: {}".format(url))
        print("==> Entered _fetch_urls:: {}".format(url))
        html = ""
        status = 404
        response = None
        if publisher == "EconomicTimes":
            headers_to_use = headers_list_ET
        if publisher == "TimesofIndia":
            headers_to_use = headers_list_TOI
        if publisher == "NDTV":
            headers_to_use = headers_list_NDTV
        if publisher == "DeccanHerald":
            headers_to_use = headers_list_DH
        if publisher == "Independent":
            headers_to_use = headers_list_Independent
        if publisher == "EveningStandard":
            headers_to_use = headers_list_EveningStandard
        if publisher == "NewYorkPost":
            headers_to_use = headers_list_NewYorkPost
        if publisher == "Express":
            headers_to_use = headers_list_Express
        if publisher == "DailyMail":
            headers_to_use = headers_list_DailyMail
        if publisher == "IndiaToday":
            headers_to_use = headers_list_IndiaToday
        if publisher == "OneIndia":
            headers_to_use = headers_list_OneIndia
        if publisher == "ScrollNews":
            headers_to_use = headers_list_ScrollNews
        if publisher == "CNBCWorld":
            headers_to_use = headers_list_CNBC
        if publisher == "TheIndianExpress":
            headers_to_use = headers_list_IndianExpress
        if publisher == "ThePioneer":
            headers_to_use = headers_list_ThePioneer
        if publisher == "TheFinancialExpress":
            headers_to_use = headers_list_FinancialExpress
        if publisher == "EuroNews":
            headers_to_use = headers_list_EuroNews
        if publisher == "ESPNCricInfo":
            headers_to_use = headers_list_ESPNCricInfo
        if publisher == "NYTimes":
            headers_to_use = headers_list_NYTimes
        if publisher == "BusinessStandard":
            headers_to_use = headers_list_BusinessStandard
        for i in range(5):    # default 10, made 5 for NDTV
            retries = 1
            logging.info("Try to fetch the html: {}, url:: {}".format(i, url))
            try:
                # if publisher == "USAToday":
                #     response = requests_retry_session().get(url, timeout=2, verify=False,
                #                                             proxies={"http": random.choice(proxies_ip_list)})
                # if publisher == "HinduBusinessLine":
                #     response = requests_retry_session().get(url, timeout=2, verify=False,
                #                                             headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
                #                                                     'Referer': 'https://www.thehindubusinessline.com/'},
                #                                             proxies={"http": random.choice(proxies_ip_list)})
                # if publisher in ("TheIndianExpress"):
                #     response = requests_retry_session().get(url, timeout=2, verify=False,
                #                                             headers=random.choice(headers_to_use))

                # response = requests.get(url, timeout=2, verify=False, headers=random.choice(headers_to_use), proxies={"http": random.choice(proxies_ip_list)})    # For Express only
                response = make_requests(url, random.choice(headers_to_use))
                status = response.status_code
                time_taken = response.elapsed.total_seconds()
                logging.info("{}  || time_taken = {}".format(url, time_taken))
                if status == 200:
                    logging.info("[Successful]:: {}".format(url))
                    html = response.text
                    break
            except Exception as exception:
                logging.info(
                    "EXCEPTION {} occurred for this url while getting the html for this archive article:: {}"
                    .format(exception, url))
                time.sleep(0.5)
                retries += 1
            # break
        # except Exception as exception:
        #     logging.info("EXCEPTION {} occurred for this url while getting the html for this archive article:: {}".format(exception, url))
        #     # time.sleep(0.5)
        #     time.sleep(round(random.uniform(1, 1.5),3))
        #     # retries += 1
            '''
            time_taken = response.elapsed.total_seconds()
            logging.info("{}  || time_taken = {}".format(url, time_taken))
            if response.status_code == 200:
                logging.info("Definitely a 200")
                break
            time.sleep(round(random.uniform(0.1, 0.3),3))
            '''

            # break
            # except Exception as e:
            #     logging.info("Retry #{} ===> EXCEPTION {} occurred for this url while getting the html for this archive article:: {}".format(retries, e, url))
            #     print("Retry #{} ===> EXCEPTION {} occurred for this url while getting the html for this archive article:: {}".format(retries, e, url))
            #     # logging.exception("the error: ", e)
            #     # wait = retries * 2
            #     # time.sleep(wait)
            #     # time.sleep(0.75)  # 1.5 default
            #     retries += 1
        if html == "":
            logging.exception("[Error] Could not get the html file for this article url: {}".format(url))
            print("[Error] Could not get the html file for this article url: {}".format(url))
        time.sleep(round(random.uniform(0.1, 0.3),3))
        return html, status


class TheHinduCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            urls.append('https://www.thehindu.com/archive/web/' + dt.strftime("%Y/%m/%d/"))
        logging.info("Generating {} urls for TheHindu".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                logging.info("Try: {}".format(i))
                soup = BeautifulSoup(page)
                soup.find('div', {'id':'subnav-tpbar-latest'}).decompose()
                section = soup.find('div', {'class':'tpaper-container'})
                for a in section.find_all('a'):
                    href = a.get('href')
                    if "crossword.thehindu.com" not in str(href):
                        if href is not None and href.endswith(".ece"):
                            if href not in urls:
                                urls.append(href)
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in The Hindu, url is {}".format(page_url))
        return urls

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return urls


class EconomicTimesCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        def excel_date(date1):
            date1 = datetime.strptime(date1, "%Y-%m-%d")
            temp = datetime(1899, 12, 30)
            delta = date1 - temp
            return delta.days
        for dt in pd.date_range(self.start_date, self.end_date):
            dt_year = str(dt)[:4]
            dt_month = str(dt).split("-")[1].lstrip("0")
            urls.append('https://economictimes.indiatimes.com/archivelist/year-' + dt_year + ",month-" + dt_month + ",starttime-" + str(excel_date(str(dt)[:10])) + ".cms")
        logging.info("Generating {} urls for EconomicTimes".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                soup = BeautifulSoup(page, 'html5lib')
                section = soup.find('table', {'cellpadding': '0', 'cellspacing': '0', 'border': '0', 'width': '100%'})
                for a in section.find_all('a'):
                    href = a.get('href')
                    urls.append('https://economictimes.indiatimes.com' + href)
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in EconomicTimes, url is {}".format(page_url))
        return urls

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class TimesOfIndiaCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        # self.retries = 5

    # @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        def excel_date(date1):
            date1 = datetime.strptime(date1, "%Y-%m-%d")
            temp = datetime(1899, 12, 30)
            delta = date1 - temp
            return delta.days
        for dt in pd.date_range(self.start_date, self.end_date):
            dt_year = str(dt)[:4]
            dt_month = str(dt).split("-")[1].lstrip("0")
            dt_day = datetime.strptime(str(dt)[:10], "%Y-%m-%d").strftime("%d").lstrip("0")
            urls.append('https://timesofindia.indiatimes.com/' + dt_year + "/" + dt_month + "/" + dt_day + "/" + "archivelist/year-" + dt_year + ",month-" + dt_month + ",starttime-" + str(excel_date(str(dt)[:10])) +".cms")
        logging.info("Generating {} urls for TimesofIndia".format(len(urls)))
        return urls

    # @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        # for i in range(self.retries):
        page = self._crawl_page(page_url)
        try:
            soup = BeautifulSoup(page, 'html5lib')
            section = soup.find('div', {'style': "font-family:arial ;font-size:12;font-weight:bold; color: #006699"})
            for a in section.find_all('a'):
                if "ads.indiatimes.com" in a.get('href'):
                    continue
                if "timesofindia.indiatimes.com" in a.get('href'):
                    urls.append(a.get('href'))
                if a.get('href')[0] == '/':
                    urls.append('http://timesofindia.indiatimes.com' + a.get('href'))
            # break
        except Exception as e:
            logging.exception("Exception occurred while fetching the links in TimesofIndia, url is {}".format(page_url))
        return urls

    # @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class NDTVCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        all_days_YM = []
        all_days_total = []
        page_urls = []
        article_urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            if dt.strftime("%Y-%m") not in all_days_YM:
                all_days_YM.append(dt.strftime("%Y-%m"))
            all_days_total.append(dt.strftime("%d %B %Y"))
        for instance in all_days_YM:
            page_urls.append("https://archives.ndtv.com/articles/" + instance + ".html")
        for page_url in page_urls:
            r = requests_retry_session().get(page_url, timeout=2, verify=False,
                                             headers=random.choice(headers_list_NDTV),
                                             proxies={"http": random.choice(proxies_ip_list)})
            soup = BeautifulSoup(r.content, 'html5lib')
            for h3 in soup.find_all('h3'):
                for all_day_total in all_days_total:
                    if all_day_total == h3.text:
                        for li in h3.find_next('ul').find_all('li'):
                            article_text = li.a.get_text()
                            article_link = li.a.get('href')
                            article_urls.append(article_link)
        tup = ('khabar.ndtv.com', 'swirlster.ndtv.com', 'hotdeals360.com', '/bengali/', '/tamil/', '/hindi/', 'hindi.', 'tamil.', 'bengali.')
        new_lis = [x for x in article_urls if not any(y in x for y in tup)]
        return list(set(new_lis))



class DeccanHeraldCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            r = requests.post("https://www.deccanherald.com/getarchive", data = {'arcDate': dt.strftime("%Y/%m/%d")})
            soup = BeautifulSoup(r.content, 'html5lib')
            links = soup.find_all('a')
            for link in links:
                final_link = "https://www.deccanherald.com{}".format(link.get('href'))
                if final_link not in urls:
                    urls.append(final_link)
        return list(set(urls))


class IndependentCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            urls.append("https://www.independent.co.uk/archive/{}".format(dt.strftime("%Y-%m-%d")))
        logging.info("Generating {} urls for Independent".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            # page = requests_retry_session().get(page_url, timeout=3, verify=False,
            #                                     headers=random.choice(headers_list_Independent),
            #                                     proxies={'http':random.choice(proxies_ip_list)})
            page = make_requests(page_url, random.choice(headers_list_Independent))
            try:
                soup = BeautifulSoup(page.content, 'html5lib')
                h1 = soup.find('h1', {'class': 'withDate'})
                ul = h1.find_next('ul')
                for link in ul.find_all('a'):
                    urls.append("https://www.independent.co.uk" + link.get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in Independent, url is {}".format(page_url))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class EveningStandardCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            urls.append("https://www.standard.co.uk/archive/{}".format(dt.strftime("%Y-%m-%d").replace("-0", "-")))
        logging.info("Generating {} urls for EveningStandard".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                soup = BeautifulSoup(page, 'html5lib')
                h1 = soup.find('h1', {'class': 'withDate'})
                ul = h1.find_next('ul')
                for a in ul.find_all('a'):
                    urls.append("https://www.standard.co.uk" + a.get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in EveningStandard, url is {}".format(page_url))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class NewYorkPostCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            urls.append("https://nypost.com/{}".format(dt.strftime("%Y/%m/%d/")))
        logging.info("Generating {} urls for NewYorkPost".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                soup = BeautifulSoup(page, 'html5lib')
                for h3 in soup.find_all('h3', {'class': 'entry-heading'}):
                    urls.append(h3.find_next('a').get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in NewYorkPost, url is {}".format(page_url))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class ExpressCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            urls.append('https://www.express.co.uk/sitearchive/' + dt.strftime('%Y/%m/%d').replace("/0", "/"))
        logging.info("Generating {} urls for Express".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                soup = BeautifulSoup(page, 'html5lib')
                mydivs = soup.find_all('ul', {'class': 'section-list'})
                for div in mydivs:
                    for link in div.find_all('a'):
                        urls.append('https://www.express.co.uk' + link.get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in Express, url is {}".format(page_url))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class USATodayCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            for i in range(1, 50):
                page = "https://www.usatoday.com/sitemap/{}?page={}".format(dt.strftime("%Y/%B/%d/").lower(), i)
                r = requests_retry_session().get(page, timeout=3, verify=False,
                                                 headers=random.choice(headers_list_USAToday),
                                                 proxies={"http": random.choice(proxies_ip_list)})
                # r = make_requests(page, random.choice(headers_list_USAToday))    # USAToday doesn't extract correct #articles with make_requests
                soup = BeautifulSoup(r.content, 'html5lib')
                for ul in soup.find_all(lambda tag: tag.name=='ul' and tag.get('class') == ['sitemap-list'] and tag.next_element['class'] == ['sitemap-list-item']):
                    for a in ul.find_all('a'):
                        urls.append(a.get('href'))
        logging.info("Generating {} urls for USAToday".format(len(urls)))
        return list(set(urls))


class DailyMailCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            urls.append('https://www.dailymail.co.uk/home/sitemaparchive/day_' + dt.strftime("%Y%m%d") + '.html')
        logging.info("Generating {} urls for DailyMail".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                soup = BeautifulSoup(page, 'html5lib')
                section = soup.find('ul', {'class': 'archive-articles debate link-box'})
                for a in section.find_all('a'):
                    urls.append('https://www.dailymail.co.uk' + a.get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in DailyMail, url is {}".format(page_url))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class IndiaTodayCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            for num in range(0, 300):
                url_scaffold = "https://www.indiatoday.in/archives/story/{}?bundle_name=Story&hash=itbxf0&ds_changed={}&page={}"
                page = url_scaffold.format(dt.strftime("%d-%m-%Y"), dt.strftime("%Y-%m-%d"), num)
                # r = requests_retry_session().get(page, timeout=2, verify=False,
                #                                  headers=random.choice(headers_list_IndiaToday),
                #                                  proxies = {"http": random.choice(proxies_ip_list)})
                r = make_requests(page, random.choice(headers_list_IndiaToday))
                soup = BeautifulSoup(r.content, 'html5lib')
                if "No Record Found !" not in soup.text:
                    urls.append(page)
                else:
                    break
        logging.info("Generating {} urls for IndiaToday".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            # page = self._crawl_page(page_url)
            r = make_requests(page_url, random.choice(headers_list_IndiaToday))
            try:
                soup = BeautifulSoup(r.content, 'html5lib')
                mydivs = soup.find_all('div', {'class': 'views-field views-field-nothing-1'})
                for division in mydivs:
                    article_link = division.find('a')
                    urls.append('https://www.indiatoday.in' + article_link.get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in IndiaToday, url is {}".format(page_url))
        return list(set(urls))

    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class OneIndiaCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            urls.append('https://www.oneindia.com/' + dt.strftime('%Y/%m/%d/'))
        logging.info("Generating {} urls for OneIndia".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                soup = BeautifulSoup(page, 'html5lib')
                sections = soup.find('div', {'class': 'content clearfix'}).find_all('ul')
                for section in sections:
                    for li in section.find_all('li'):
                        href = li.a.get('href')
                        urls.append('https://www.oneindia.com' + href)
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in OneIndia, url is {}".format(page_url))
        return urls

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class HinduBusinessLineCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            urls.append('https://www.thehindubusinessline.com/archive/web/' + dt.strftime('%Y/%m/%d/'))
        logging.info("Generating {} urls for HinduBusinessLine".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                soup = BeautifulSoup(page, 'html5lib')
                mydivs = soup.find_all('ul', {'class': 'archive-list'})
                for div in mydivs:
                    for link in div.find_all('a'):
                        urls.append(link.get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in HinduBusinessLine, url is {}".format(page_url))
        tup = ('www.thehindubusinessline.com/tamil/')
        final_lis = [x for x in urls if not any(y in x for y in tup)]
        return final_lis

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class ScrollNewsCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            for num in range(1, 25):
                page = 'https://scroll.in/archives/{}/page/{}'.format(dt.strftime("%Y/%m/%d"), num)
                r = requests.get(page, timeout=2, verify=False,
                                 headers=random.choice(headers_list_ScrollNews),
                                 proxies={"http": random.choice(proxies_ip_list)})
                soup = BeautifulSoup(r.content, 'html5lib')
                if soup.find('li', {'class': 'row-story'}):
                    urls.append(page)
                else:
                    break
        logging.info("Generating {} urls for ScrollNews".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                soup = BeautifulSoup(page, 'html5lib')
                mydivs = soup.find_all('li', {'class': 'row-story'})
                for div in mydivs:
                    urls.append(div.find('a').get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in ScrollNews, url is {}".format(page_url))
        return urls

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class CNBCCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            urls.append("https://www.cnbc.com/site-map/{}".format(dt.strftime("%Y/%B/%d/").replace("/0", "/")))
        logging.info("Generating {} urls for CNBC".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                soup = BeautifulSoup(page, 'html5lib')
                div = soup.find('div', {'class': 'SiteMapArticleList-articleData'})
                for link in div.find_all('a', {'class': 'SiteMapArticleList-link'}):
                    urls.append(link.get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in CNBC, url is {}".format(page_url))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class TheIndianExpressCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            urls.append('http://archive.indianexpress.com/archive/news/' + dt.strftime("%d/%m/%Y").replace("/0", "/").lstrip("0"))
        logging.info("Generating %s urls for TheIndianExpress", len(urls))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                soup = BeautifulSoup(page, 'html5lib')
                section = soup.find('div', {'id': 'box_left' , 'style': 'display:block'})
                for a in section.find_all('a'):
                    if "indianexpress.com" not in a.get('href'):
                        urls.append("http://archive.indianexpress.com" + a.get('href'))
                    else:
                        urls.append(a.get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in TheIndianExpress, url is ", page_url)
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return urls


class ThePioneerCrawler(BaseCrawler):
    """
    This publisher has month-wise article dumps, so when starting jobs for this,
    use the first date of the month as both start_date and end_date.
    e.g. to crawl Jan 2020 articles, start_date = end_date = 2020-01-01
    """
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        urls = []
        article_urls = []
        se = set()
        for dt in pd.date_range(self.start_date, self.end_date):
            se.add("yr={}&mn={}".format(dt.strftime("%Y"), dt.strftime("%m").lstrip("0")))
        se = list(se)
        for element in se:
            for i in range(1, 1000):
                url = "https://www.dailypioneer.com/searchlist.php?{}&page={}".format(element, i)
                page = self._crawl_page(url)
                soup = BeautifulSoup(page, 'html5lib')
                try:
                    highlightedNews = soup.find('div', {'class': 'highLightedNews'})
                    if highlightedNews:
                        if url not in urls:
                            print(url)
                            try:
                                HN = soup.find('div', {'class': 'highLightedNews'})
                                for a in HN.find_all('a'):
                                    if ".html" in a.get('href'):
                                        url = "https://www.dailypioneer.com" + a.get('href')
                                        if url not in article_urls:
                                            article_urls.append(url)
                                INL = soup.find('div', {'class': 'innerNewsList'})
                                for h2 in INL.find_all('h2'):
                                    article_urls.append("https://www.dailypioneer.com" + h2.a.get('href'))
                            except Exception as e:
                                logging.exception("Exception occurred while fetching the links in ThePioneer, url is {}".format(page_url))
                    else:
                        break            
                except:
                    break
        logging.info("Generating {} urls for ThePioneer".format(len(urls)))
        return list(set(article_urls))
    
    def get_article_urls(self):
        return self._get_page_urls()
    
    '''  # This code is inoptimal
    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        se = set()
        for dt in pd.date_range(self.start_date, self.end_date):
            se.add("yr={}&mn={}".format(dt.strftime("%Y"), dt.strftime("%m").lstrip("0")))
        se = list(se)
        for element in se:
            for i in range(1, 1000):
                url = "https://www.dailypioneer.com/searchlist.php?{}&page={}".format(element, i)
                r = requests.get(url, timeout=3)
                soup = BeautifulSoup(r.content, 'html5lib')
                try:
                    highlightedNews = soup.find('div', {'class': 'highLightedNews'})
                    if highlightedNews:
                        if url not in urls:
                            print(url)
                            urls.append(url)
                    else:
                        break
                except:
                    break
        logging.info("Generating {} urls for ThePioneer".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        page = self._crawl_page(page_url)
        try:
            soup = BeautifulSoup(page, 'html5lib')
            HN = soup.find('div', {'class': 'highLightedNews'})
            for a in HN.find_all('a'):
                if ".html" in a.get('href'):
                    url = "https://www.dailypioneer.com" + a.get('href')
                    if url not in urls:
                        urls.append(url)
            INL = soup.find('div', {'class': 'innerNewsList'})
            for h2 in INL.find_all('h2'):
                urls.append("https://www.dailypioneer.com" + h2.a.get('href'))
        except Exception as e:
            logging.exception("Exception occurred while fetching the links in ThePioneer, url is {}".format(page_url))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))
    '''


class FinancialExpressCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = set()
        se = set()
        for dt in pd.date_range(self.start_date, self.end_date):
            se.add(dt.strftime("%Y/%m"))
        se = sorted(list(se))
        for element in se:
            for i in range(1, 100):
                url = "https://www.financialexpress.com/archive/{}/?page={}".format(element, i)
                request = urlopen(url)
                soup = BeautifulSoup(request.read(), 'html5lib')
                next_page = soup.find('li', {'class': 'next disabled'})
                if url not in urls:
                    urls.add(url)
                if next_page:
                    break
        logging.info("Generating {} urls for FinancialExpress".format(len(urls)))
        print("Generating {} urls for FinancialExpress".format(len(urls)))
        return list(urls)

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = set()
        for i in range(self.retries):
            page = urlopen(page_url)
            try:
                soup = BeautifulSoup(page.read(), 'html5lib')
                news_section = soup.find('div', {'class': 'news'})
                for article in news_section.find_all('a'):
                    if "www.financialexpress.com" in article.get('href'):
                        urls.add(article.get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in FinancialExpress, url is {}".format(page_url))
        return list(urls)

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class EuroNewsCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            for num in range(1, 50):
                page = 'https://www.euronews.com/{}?p={}'.format(dt.strftime('%Y/%m/%d'), num)
                r = requests.get(page, timeout=3)
                soup = BeautifulSoup(r.content, 'html5lib')
                if soup.find('article', {'class': True}):
                    urls.append(page)
                else:
                    break
        logging.info("Generating %s urls for EuroNews", len(urls))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        for i in range(self.retries):
            page = self._crawl_page(page_url)
            try:
                soup = BeautifulSoup(page, 'html5lib')
                mydivs = soup.find_all('div', {'class': 'm-object__body'})
                for div in mydivs:
                    for link in div.find_all('a', {'class': 'm-object__title__link'}):
                        urls.append('https://www.euronews.com' + link.get('href'))
                break
            except Exception as e:
                logging.exception("Exception occurred while fetching the links in EuroNews, url is ", page_url)
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class ESPNCricInfoCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d+%b+%Y")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d+%b+%Y")
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for i in range(1, 30):
            url_scaffold = "https://www.espncricinfo.com/ci/content/story/data/index.json?datefrom={}&dateupto={};;type=7;page={}"
            page = url_scaffold.format(self.start_date, self.end_date, i)
            r = requests.get(page, timeout=3)
            soup = BeautifulSoup(r.content, 'html5lib')
            body = json.loads(soup.find('body').text, strict=False)
            if body == []:
                break
            else:
                for x in body:
                    urls.append("https://www.espncricinfo.com/ci/content/story/{}.html".format(x['object_id']))
        logging.info("Generating %s urls for ESPNCricInfo", len(urls))
        return list(set(urls))


class NYTimesCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5
    
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            urls.append('https://www.nytimes.com/sitemap/{}/'.format(dt.strftime("%Y/%m/%d")))
        return urls
    
    def _get_article_urls(self, page_url):
        urls = []
        page = self._crawl_page(page_url)
        try:
            soup = BeautifulSoup(page, 'html5lib')
            main_content = soup.find('main', {'id': 'site-content'})
            list_of_articles = main_content.find_all('li')
            for article in list_of_articles:
                urls.append(article.a.get('href'))
        except Exception as e:
            logging.exception("Exception occurred while fetching the links in NYTimes, url is {}".format(page_url))
        tup = ('/issue/todayspaper', '/issue/todaysheadlines', '/issue/todaysinyt', '/espanol/')
        final_lis = [x for x in urls if not any(y in x for y in tup)]
        return final_lis
    
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))

    '''  ## This is code for old archive format (month-wise article dump)
    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        se = set()
        for dt in pd.date_range(self.start_date, self.end_date):
            for i in range(0, 10):
                se.add("https://spiderbites.nytimes.com/{}/articles_{}_0000{}.html".format(dt.strftime("%Y"),
                                                                                           dt.strftime("%Y_%m"),
                                                                                            i))
        se = sorted(list(se))
        for link in se:
            response = requests.get(link, timeout=3, verify=False)
            soup = BeautifulSoup(response.content, 'html5lib')
            try:
                if soup.find('ul', {'id': 'headlines'}):
                    urls.append(link)
            except:
                break
        logging.info("Generating {} urls for NYTimes".format(len(urls)))
        print("Generating {} urls for NYTimes".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = []
        page = self._crawl_page(page_url)
        try:
            soup = BeautifulSoup(page, 'html5lib')
            articles_list = soup.find('ul', {'id': 'headlines'})
            for li in articles_list.find_all('li'):
                urls.append(li.a.get('href'))
            # break
        except Exception as e:
            logging.exception("Exception occurred while fetching the links in NYTimes, url is {}".format(page_url))
        urls = [x for x in urls if x != '']
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))
    '''


class BusinessStandardCrawler(BaseCrawler):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_page_urls(self):
        urls = []
        for dt in pd.date_range(self.start_date, self.end_date):
            day, month, year = (dt.strftime("%d"), dt.strftime("%m"), dt.strftime("%Y"))
            latest_news = "https://www.business-standard.com/latest-news?print_dd={}&print_mm={}&print_yy={}".format(day, month, year)
            general_news = "https://www.business-standard.com/general-news?print_dd={}&print_mm={}&print_yy={}".format(day, month, year)
            todays_paper = "https://www.business-standard.com/todays-paper?print_dd={}&print_mm={}&print_yy={}".format(day, month, year)
            urls.append(latest_news)
            urls.append(general_news)
            urls.append(todays_paper)
        logging.info("Generating {} urls for Business Standard".format(len(urls)))
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _get_article_urls(self, page_url):
        urls = set()
        # r = requests.get(page_url, timeout=3, verify=False,
        #                  headers=random.choice(headers_list_BusinessStandard))
        r = make_requests(page_url, random.choice(headers_list_BusinessStandard))    # for BS, this successfully crawls articles compared to simple requests.get()
        try:
            soup = BeautifulSoup(r.content, 'html5lib')
            lists = soup.find_all('ul', {'class': 'aticle-txt'})
            for li in lists:
                for a in li.find_all('a'):
                    urls.add("https://www.business-standard.com" + a.get('href'))
        except Exception as e:
            logging.exception("Exception occurred while fetching the links in Business Standard, url is {}".format(page_url))
        urls = list(urls)
        return urls

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def get_article_urls(self):
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


def handler(publisher, start_date, end_date):
    crawler = None
    if publisher == "TheHindu":
        crawler = TheHinduCrawler(start_date, end_date)
    if publisher == "EconomicTimes":
        crawler = EconomicTimesCrawler(start_date, end_date)
    if publisher == "TimesofIndia":
        crawler = TimesOfIndiaCrawler(start_date, end_date)
    if publisher == "DeccanHerald":
        crawler = DeccanHeraldCrawler(start_date, end_date)
    if publisher == "NDTV":
        crawler = NDTVCrawler(start_date, end_date)
    if publisher == "Independent":
        crawler = IndependentCrawler(start_date, end_date)
    if publisher == "EveningStandard":
        crawler = EveningStandardCrawler(start_date, end_date)
    if publisher == "NewYorkPost":
        crawler = NewYorkPostCrawler(start_date, end_date)
    if publisher == "Express":
        crawler = ExpressCrawler(start_date, end_date)
    if publisher == "USAToday":
        crawler = USATodayCrawler(start_date, end_date)
    if publisher == "DailyMail":
        crawler = DailyMailCrawler(start_date, end_date)
    if publisher == "IndiaToday":
        crawler = IndiaTodayCrawler(start_date, end_date)
    if publisher == "OneIndia":
        crawler = OneIndiaCrawler(start_date, end_date)
    if publisher == "HinduBusinessLine":
        crawler = HinduBusinessLineCrawler(start_date, end_date)
    if publisher == "ScrollNews":
        crawler = ScrollNewsCrawler(start_date, end_date)
    if publisher == "CNBCWorld":
        crawler = CNBCCrawler(start_date, end_date)
    if publisher == "TheIndianExpress":
        crawler = TheIndianExpressCrawler(start_date, end_date)
    if publisher == "ThePioneer":
        crawler = ThePioneerCrawler(start_date, end_date)
    if publisher == "TheFinancialExpress":
        crawler = FinancialExpressCrawler(start_date, end_date)
    if publisher == "EuroNews":
        crawler = EuroNewsCrawler(start_date, end_date)
    if publisher == "ESPNCricInfo":
        crawler = ESPNCricInfoCrawler(start_date, end_date)
    if publisher == "NYTimes":
        crawler = NYTimesCrawler(start_date, end_date)
    if publisher == "BusinessStandard":
        crawler = BusinessStandardCrawler(start_date, end_date)
    urls = crawler.get_article_urls()
    return list(set(urls))

'''
# @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
def archives(url, publisher):
    S = SimpleCrawler()
    # try:
    html, status = S.fetch_url(url, crawl_type="Archives", publisher=publisher)
    return html, status
    # except Exception as e:
    #     logging.exception("[Error] Exception occurred while getting the html for the article ---> {}".format(url))
    #     return ""
'''


publisher_id_mapping = {
    'ScrollNews':          uuid.UUID('7e5375ad-17b7-4598-bebb-4ec8ed3506bd'),
    'OneIndia':            uuid.UUID('4af27ab5-becb-4fe2-9dce-87c2b6a6551d'),
    'HinduBusinessLine':   uuid.UUID('499d177b-56c6-489b-b607-88840d31b3cd'),
    'NDTV':                uuid.UUID('8704135c-0498-49c0-b47c-2cd355bbdbc4'),
    'DeccanHerald':        uuid.UUID('805089cf-8e22-474f-b14d-0b67edbfee44'),
    'IndiaToday':          uuid.UUID('8fa2fd28-3a27-449f-becd-36424435abe5'),
    'EconomicTimes':       uuid.UUID('108a4fd3-06ad-424c-baa0-5c63c86d2a07'),
    'TimesofIndia':        uuid.UUID('cb992884-bd4e-40a9-ad08-c820abc1f360'),
    'CNBCWorld':           uuid.UUID('975d774d-9cf3-4b21-9526-e8c432f19932'),
    'NewYorkPost':         uuid.UUID('99b9b40f-851e-45b6-9e7b-a08f9edf9b8e'),
    'EveningStandard':     uuid.UUID('09dd0b00-a0b0-423d-8735-90df98252cdc'),
    'Independent':         uuid.UUID('89dfb81e-3fdb-4ea2-a16c-d571bf051e4c'),
    'USAToday':            uuid.UUID('3dd68f6d-fa18-489b-9589-5f821c1698a6'),
    'DailyMail':           uuid.UUID('19a4b6ec-0f8c-44a3-842e-169a7746fd6b'),
    'Express':             uuid.UUID('b2d56c7e-4e7b-45d4-8674-c1432ee9edcc'),
    'ThePioneer':          uuid.UUID('88ac62c4-72a6-4ef3-842d-6ba133c4ef60'),
    'TheIndianExpress':    uuid.UUID('31e281cb-65f2-4aaa-bff3-6fe2d7092b21'),
    'TheFinancialExpress': uuid.UUID('9a688b63-b12b-4a71-a6dd-ce8861b0c99d'),
    'EuroNews':            uuid.UUID('e3c569fa-fa85-4852-b171-5d4829157e20'),
    'ESPNCricInfo':        uuid.UUID('bf0ad581-35d2-4735-b654-884f62215613'),
    'NYTimes':             uuid.UUID('7586b7fd-45d3-4d2f-a40a-8e541f03ef48'),
    'BusinessStandard':    uuid.UUID('1f308812-0a38-4d0b-98b9-55d70ad36332')
}

count_crawl_success = 0
count_crawl_fail = 0

def get_and_save_htmls(data):
    S = SimpleCrawler()
    raw_articles = []
    mongo_data = []
    row = []
    if len(data) == 0:
        return
    logging.info("get_and_save_htmls() START || {}, {}, {}, {} ===> {}, {}, {}, {}".format(threading.current_thread().ident, data[0][0], data[0][1], data[0][2],
                                                                                           threading.current_thread().ident, data[0][0], data[-1][1], data[-1][2]))
    for article_url, publisher, date_crawled in data:
        # html, status_code = archives(article_url, publisher)    # original
        html, status_code = S.fetch_url(article_url, crawl_type="Archives", publisher=publisher)
        id_ = uuid.uuid1()
        param = db.globalID(resource_type=db.ResourceType.ARTICLE,
                            resource_id=db.UUIDConversion.uuid_to_bin(id_, 1))
        
        logging.info("URL = {}, STATUS_CODE = {}".format(article_url, status_code))
        global count_crawl_success, count_crawl_fail
        if str(html) == '' or status_code != 200:
            count_crawl_fail += 1
        else:
            count_crawl_success += 1
        row.append(param)

        if str(html) == '':
            raw_articles.append(db.rawArticles(resource_id=db.UUIDConversion.uuid_to_bin(id_, 1),
                                               publisher=db.PublishersType[publisher],
                                               url=article_url,
                                               date_crawled=date_crawled,
                                               state=db.ArticleState.CRAWL_FAIL,
                                               publisher_id=db.UUIDConversion.uuid_to_bin(publisher_id_mapping[publisher], 1)))
        else:
            raw_articles.append(db.rawArticles(resource_id=db.UUIDConversion.uuid_to_bin(id_, 1),
                                               publisher=db.PublishersType[publisher],
                                               url=article_url,
                                               date_crawled=date_crawled,
                                               state=db.ArticleState.CRAWL_SUCCESS,
                                               publisher_id=db.UUIDConversion.uuid_to_bin(publisher_id_mapping[publisher], 1)))
        mongo_data.append((db.UUIDConversion.mongodb_uuid(id_), str(html)))
    
    try:
        raw_articles_mongodb.insert_many([{
            '_id': resource_id,
            'html_body': html_body
        } for resource_id, html_body in mongo_data])
    except Exception as exception:
        logging.exception(
            "EXCEPTION occurred while saving data to MongoDB collection ===> %s",
            exception)
        print("EXCEPTION occurred while saving data to MongoDB collection ===> {}".format(exception))
    session = Session()
    session.add_all(row)
    session.add_all(raw_articles)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logging.exception(e)
        print(e)
    session.close()
    time.sleep(0.1)
    logging.info("get_and_save_htmls() END || {}, {}, {}, {} ===> {}, {}, {}, {}".format(threading.current_thread().ident, data[0][0], data[0][1], data[0][2],
                                                                                         threading.current_thread().ident, data[0][0], data[-1][1], data[-1][2]))

total_num_articles = 0
subdata_length = 0

def per_day_thread(publisher, startdate):
    logging.info("per_day_thread() START ===> {}, {}, {}".format(threading.current_thread().ident, publisher, startdate))
    PER_DAY = 30  # 375 def
    article_urls = handler(publisher, startdate, startdate)
    logging.info("Date = {}    Total articles = {}".format(startdate, len(article_urls)))
    print("Date = {}    Total articles = {}".format(startdate, len(article_urls)))
    global total_num_articles, subdata_length
    total_num_articles += len(article_urls)
    # if startdate == '2014-12-18':
    #     article_urls = dec_18
    # elif startdate == '2014-12-19':
    #     article_urls = dec_19
    # elif startdate == '2014-12-20':
    #     article_urls = dec_20
    # elif startdate == '2014-12-21':
    #     article_urls = dec_21
    # elif startdate == '2014-12-22':
    #     article_urls = dec_22
    # elif startdate == '2014-12-23':
    #     article_urls = dec_23
    # elif startdate == '2014-12-24':
    #     article_urls = dec_24
    # elif startdate == '2014-12-25':
    #     article_urls = dec_25
    # elif startdate == '2014-12-26':
    #     article_urls = dec_26
    # elif startdate == '2014-12-27':
    #     article_urls = dec_27
    '''
    if startdate == '2014-12-28':
        article_urls = dec_28
    elif startdate == '2014-12-29':
        article_urls = dec_29
    elif startdate == '2014-12-30':
        article_urls = dec_30
    elif startdate == '2014-12-31':
        article_urls = dec_31
    '''

    import math
    article_per_process = math.ceil(len(article_urls) / PER_DAY)  # int() default
    # article_per_process += 1
    article_index = 0

    threads = []
    for _ in range(PER_DAY):
        subdata = []
        end_index = min(article_index + article_per_process, len(article_urls))
        for url in article_urls[article_index:end_index]:
            subdata.append([url, publisher, startdate])
            subdata_length += 1
        article_index += article_per_process
        threads.append(Thread(target=get_and_save_htmls, args=(subdata,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    logging.info("per_day_thread() END ===> {}, {}, {}".format(threading.current_thread().ident, publisher, startdate))


if __name__ == '__main__':
    '''
    url_skeleton = "https://www.indiatoday.in/archives/story/25-11-2020?bundle_name=Story&hash=itbxf0&ds_changed=2020-11-25&page={}"
    urls = []
    for i in range(0,53):
        urls.append(url_skeleton.format(i))
    urls = []
    urls.append(url_skeleton)
    articles_to_crawl = []
    for url in urls:
        r = make_requests(url, random.choice(headers_list_IndiaToday))
        soup = BeautifulSoup(r.content, 'html5lib')
        mydivs = soup.find_all('div', {'class': 'views-field views-field-nothing-1'})
        for division in mydivs:
            article_link = division.find('a')
            articles_to_crawl.append('https://www.indiatoday.in' + article_link.get('href'))
        print("Collected articles for url ===> {}\n".format(url))
    publisher = 'IndiaToday'
    date_crawled = '2020-11-25'
    for url in articles_to_crawl:
        get_and_save_htmls([(url, publisher, date_crawled)])
    '''
    # publisher = 'IndiaToday'
    # date_crawled = '2019-12-10'
    # urls = []
    # for url in urls:
    #     get_and_save_htmls([(url, publisher, date_crawled)])

    initial_doc_count = raw_articles_mongodb.estimated_document_count()
    parser = argparse.ArgumentParser()
    parser.add_argument("-P", "--publisher", help="publisher name", default="ScrollNews")
    parser.add_argument("-S", "--startdate", help="Start Date - format YYYY-MM-DD", default=date.today())
    parser.add_argument("-E", "--enddate", help="End Date - format YYYY-MM-DD")
    args = parser.parse_args()
    publisher, startdate, enddate = args.publisher, args.startdate, args.enddate
    if enddate is None:
        enddate = startdate + timedelta(days=1)
    
    logging.basicConfig(filename='{}_entire.log'.format(publisher),
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')

    all_dates = []
    for dt in pd.period_range(startdate, enddate, freq="D"):
        all_dates.append(dt.strftime("%Y-%m-%d"))

    # Checks if MongoDB server is ON, and proceeds only if it is
    if client.server_info()['ok'] == 1.0:
        threads = [Thread(target=per_day_thread, args=(publisher, d)) for d in all_dates]
        DAYS_AT_A_TIME = 10
        for batch_index in range(0, len(threads), DAYS_AT_A_TIME):
            logging.info("Starting 10 days batch from {}".format(all_dates[batch_index]))
            for t in threads[batch_index:batch_index + DAYS_AT_A_TIME]:
                t.start()
            for t in threads[batch_index:batch_index + DAYS_AT_A_TIME]:
                t.join()
    
        with open("{}_crawl_status.txt".format(publisher), 'a') as filex:
            logging.info("Startdate = {}  Enddate = {}".format(startdate, enddate))
            logging.info("Length of subdata = {}".format(subdata_length))
            logging.info("Total #CRAWL_SUCCESS = {}".format(count_crawl_success))
            logging.info("Total #CRAWL_FAIL = {}".format(count_crawl_fail))
            logging.info('\n\nTotal num articles = {}'.format(total_num_articles))
            filex.write("Startdate = {}  Enddate = {}\n".format(startdate, enddate))
            if subdata_length == count_crawl_success:
                filex.write("TRUE\n")
            filex.write("Length of subdata = {}\n".format(subdata_length))
            filex.write("Total #CRAWL_SUCCESS = {}\n".format(count_crawl_success))
            filex.write("Total #CRAWL_FAIL = {}\n".format(count_crawl_fail))
            filex.write('Total num articles = {}\n'.format(total_num_articles))
            print("Length of subdata = {}".format(subdata_length))
            print("Total #CRAWL_SUCCESS = {}".format(count_crawl_success))
            print("Total #CRAWL_FAIL = {}".format(count_crawl_fail))
            print('\n\nTotal num articles = {}'.format(total_num_articles))
    else:
        print("Connection to MongoDB server can't be made. Exiting program")

    docs_added_count = raw_articles_mongodb.estimated_document_count() - initial_doc_count
    print("\n{} documents added to database\n".format(docs_added_count))

    stats_sql_query = "select date_crawled, state, count(*) from `raw-articles` where publisher='{}' and date_crawled between '{}%' and '{}%' and t_create like '{}%' group by date_crawled, state".format(publisher, startdate, enddate, datetime.today().strftime("%Y-%m-%d"))
    stats = pd.read_sql(stats_sql_query, my_connect)
    print(stats)

    import sys
    sys.exit()
