"""Crawling code for Archive-Crawling Service."""

import argparse
import json
import logging
import math
import random
import sys
import threading
import time
import uuid
# pylint: disable=too-many-lines
# file deepcode ignore C0412: imports from threading and requests libraries aren't grouped together by isort
from datetime import date, datetime, timedelta
from threading import Thread
from urllib.request import urlopen

import pandas as pd
import requests
import urllib3
# file deepcode ignore TLSCertVerificationDisabled: setting verify=False in requests.get() results in lower exceptions.
# file deepcode ignore W1201: This isn't an error
from bs4 import BeautifulSoup
from latest_user_agents import get_random_user_agent
from pymongo import MongoClient
from requests.adapters import HTTPAdapter
from retrying import retry
from sqlalchemy.orm import scoped_session, sessionmaker
from urllib3.util import Retry
import mysql.connector

import python.services.archive_crawling.models as db
from python.services.archive_crawling.config import (DAYS_AT_A_TIME, DBNAME,
                                                     HEADERS_MAIN, HOST,
                                                     MONGODB_DATABASE,
                                                     PASSWORD, PER_DAY, USER,
                                                     proxies_ip_list)
from python.services.archive_crawling.publishers_headers import (
    headers_list_BusinessStandard, headers_list_CNBC, headers_list_DailyMail,
    headers_list_DH, headers_list_ESPNCricInfo, headers_list_ET,
    headers_list_EuroNews, headers_list_EveningStandard, headers_list_Express,
    headers_list_FinancialExpress, headers_list_Independent,
    headers_list_IndianExpress, headers_list_IndiaToday, headers_list_NDTV,
    headers_list_NewYorkPost, headers_list_NYTimes, headers_list_OneIndia,
    headers_list_ScrollNews, headers_list_ThePioneer, headers_list_TOI,
    headers_list_USAToday)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(filename='crawling_log.log',
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

session_factory = sessionmaker(bind=db.get_db_engine())
Session = scoped_session(session_factory)

my_connect = mysql.connector.connect(host=HOST,
                                     user=USER,
                                     passwd=PASSWORD,
                                     database=DBNAME)

client = MongoClient()
mydb = client[MONGODB_DATABASE]
raw_articles_mongodb = mydb.data


def requests_retry_session(retries=3,
                           backoff_factor=0.15,
                           status_forcelist=(500, 502, 504, 403, 404, 408,
                                             429)):
    """Custom function to replace requests.get()"""
    with requests.Session() as session:
        retry_new = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry_new)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session


@retry(stop_max_attempt_number=5,
       wait_exponential_multiplier=1000,
       wait_exponential_max=32000)
def make_requests(url, header):
    """
    Wrapper function of vanilla requests.get()
    Gives benefit of working on publishers like Business-Standard, IndiaToday, where
    crawling using requests.get() or requests_retry_session() wasn't working.
    """
    header['User-Agent'] = get_random_user_agent()
    try:
        response = requests.get(
            url,
            timeout=4,
            verify=False,  # nosec
            headers=header,
            proxies={
                "http":
                "http://ishjoatt-rotate:lrm30lf8w0dg@p.webshare.io:80/",
                "https":
                "http://ishjoatt-rotate:lrm30lf8w0dg@p.webshare.io:80/"
            })
    except:  # pylint: disable=bare-except  # noqa: E722    # nosec
        pass
    if response.status_code != 200:
        raise ValueError("Error with request")
    return response


class BaseCrawler:
    """Fetches html of urls of archive pages."""
    def _crawl_page(self, url):  # pylint: disable=no-self-use
        """
        Function to collect all archive pages in a date range.
        E.g. For the EuroNews publisher, if the date range provided is 2021-01-01 to 2021-01-03,
        it should return the pages
        https://www.euronews.com/2021/01/01, https://www.euronews.com/2021/01/02, and
        https://www.euronews.com/2021/01/03

        A sleep of 20s b/w consecutive retries (total of 15) proved more effective
        than an exponential backoff of 2s with 5 retries.
        """
        retries = 1
        for i in range(15):
            logging.info("Try No.:: %d, URL:: %s" % (i, url))
            try:
                response = make_requests(url, HEADERS_MAIN)
                status = response.status_code
                if status == 200:
                    return response.content
                logging.info("Got the response code: %s", status)
            except Exception as exception:  # pylint: disable=broad-except
                logging.info(
                    "EXCEPTION %s occurred for this url while getting the html for archive: %s"
                    % (exception, url))
                time.sleep(20)
                retries += 1
        return ""


class SimpleCrawler:
    """Fetches the html of articles in archive pages."""
    _results = {}

    @staticmethod
    def fetch_url(url, publisher="ECONOMIC_TIMES"):
        """Calls _fetch_url."""
        html, status_code = SimpleCrawler._fetch_url(url, publisher=publisher)
        return html, status_code

    @staticmethod  # noqa: C901
    def _fetch_url(  # pylint: disable=too-many-branches
            url, publisher="ECONOMIC_TIMES"):
        """
        Given a url and the publisher it belongs to, _fetch_url returns the html string
        and status code.

        A sleep of 15s b/w consecutive retries (total of 15) proved more effective
        than an exponential backoff of 2s with 5 retries.
        """
        logging.info("==> Entered _fetch_urls:: %s", url)
        html = ""
        status = 404
        response = None
        if publisher == "ECONOMIC_TIMES":
            headers_to_use = headers_list_ET
        if publisher == "TIMES_OF_INDIA":
            headers_to_use = headers_list_TOI
        if publisher == "NDTV":
            headers_to_use = headers_list_NDTV
        if publisher == "DECCAN_HERALD":
            headers_to_use = headers_list_DH
        if publisher == "INDEPENDENT":
            headers_to_use = headers_list_Independent
        if publisher == "EVENING_STANDARD":
            headers_to_use = headers_list_EveningStandard
        if publisher == "NEW_YORK_POST":
            headers_to_use = headers_list_NewYorkPost
        if publisher == "EXPRESS":
            headers_to_use = headers_list_Express
        if publisher == "DAILY_MAIL":
            headers_to_use = headers_list_DailyMail
        if publisher == "INDIA_TODAY":
            headers_to_use = headers_list_IndiaToday
        if publisher == "ONE_INDIA":
            headers_to_use = headers_list_OneIndia
        if publisher == "SCROLL_NEWS":
            headers_to_use = headers_list_ScrollNews
        if publisher == "CNBC_WORLD":
            headers_to_use = headers_list_CNBC
        if publisher == "INDIAN_EXPRESS":
            headers_to_use = headers_list_IndianExpress
        if publisher == "THE_PIONEER":
            headers_to_use = headers_list_ThePioneer
        if publisher == "THE_FINANCIAL_EXPRESS":
            headers_to_use = headers_list_FinancialExpress
        if publisher == "EURO_NEWS":
            headers_to_use = headers_list_EuroNews
        if publisher == "ESPN_CRICINFO":
            headers_to_use = headers_list_ESPNCricInfo
        if publisher == "NEW_YORK_TIMES":
            headers_to_use = headers_list_NYTimes
        if publisher == "BUSINESS_STANDARD":
            headers_to_use = headers_list_BusinessStandard
        for i in range(15):
            retries = 1
            logging.info("Try to fetch the html: %d, url:: %s" % (i, url))
            try:
                if publisher == "USA_TODAY":
                    response = requests_retry_session().get(
                        url,
                        timeout=2,
                        verify=False,
                        proxies={"http":
                                 random.choice(proxies_ip_list)})  # nosec
                if publisher == "HINDU_BUSINESS_LINE":
                    response = requests_retry_session().get(
                        url,
                        timeout=2,
                        verify=False,
                        headers={
                            'User-Agent':
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
                            'Referer': 'https://www.thehindubusinessline.com/'
                        },
                        proxies={"http":
                                 random.choice(proxies_ip_list)})  # nosec
                if publisher == "INDIAN_EXPRESS":
                    response = requests_retry_session().get(
                        url,
                        timeout=2,
                        verify=False,
                        headers=random.choice(headers_to_use))  # nosec

                response = make_requests(
                    url, random.choice(headers_to_use))  # nosec
                status = response.status_code
                logging.info("URL:: %s, Status:: %d" % (url, status))
                if status == 200:
                    logging.info("[Successful]:: %s", url)
                    html = response.text
                    break
            except Exception as exception:  # pylint: disable=broad-except
                logging.info(
                    "EXCEPTION %s occurred for this url while getting the html for this archive article:: %s"
                    % (exception, url))
                time.sleep(0.5)
                retries += 1
        if html == "":
            if response is None:
                logging.exception(
                    "[Error] Could not get the html file for this article url: %s, response is NONE",
                    url)
            else:
                logging.exception(
                    "[Error] Could not get the html file for this article url: %s",
                    url)
        return html, status


class TheHinduCrawler(BaseCrawler):
    """
    Crawling code for The Hindu publisher.
    *   Extractors for this publisher haven't been written, as the number of articles per-date seemed to
        change frequently, even for archive pages from years ago.
    *   Crawling of this publisher isn't done as well.
    Sample archive page:   https://www.thehindu.com/archive/web/2021/04/12/
    """
    def __init__(self, start_date, end_date):
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date
        self.retries = 5

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            urls.append('https://www.thehindu.com/archive/web/' +
                        date_element.strftime("%Y/%m/%d/"))
        logging.info("Generating %d urls for The Hindu", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        for i in range(self.retries):  # pylint: disable=too-many-nested-blocks
            page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
            try:
                logging.info("Try: %d", i)
                soup = BeautifulSoup(page, 'html5lib')
                soup.find('div', {'id': 'subnav-tpbar-latest'}).decompose()
                section = soup.find('div', {'class': 'tpaper-container'})
                for link in section.find_all('a'):
                    href = link.get('href')
                    if "crossword.thehindu.com" not in str(href):
                        if href is not None and href.endswith(".ece"):
                            if href not in urls:
                                urls.append(href)
                break
            except Exception as exception:  # pylint: disable=broad-except
                logging.exception(
                    "Exception occurred while fetching the links in The Hindu, url is %s, exception ===> %s"
                    % (page_url, exception))
        return urls

    def get_article_urls(self):
        """Function to extract article urls from archive pages."""
        urls = []
        for page_url in self._get_page_urls():
            article_urls = self._get_article_urls(page_url)
            if article_urls is not None:
                urls.extend(article_urls)
        return list(set(urls))


class EconomicTimesCrawler(TheHinduCrawler):
    """
    Crawling code for Economic Times publisher.
    Sample archive page:   https://economictimes.indiatimes.com/archivelist/year-2021,month-3,starttime-44268.cms
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []

        def excel_date(date1):
            """Custom function to get an Excel date number for a given date."""
            date1 = datetime.strptime(date1, "%Y-%m-%d")
            temp = datetime(1899, 12, 30)
            delta = date1 - temp
            return delta.days

        for date_element in pd.date_range(self.start_date, self.end_date):
            dt_year = str(date_element)[:4]
            dt_month = str(date_element).split("-")[1].lstrip("0")
            urls.append(
                'https://economictimes.indiatimes.com/archivelist/year-' +
                dt_year + ",month-" + dt_month + ",starttime-" +
                str(excel_date(str(date_element)[:10])) + ".cms")
        logging.info("Generating %d urls for EconomicTimes", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            section = soup.find(
                'table', {
                    'cellpadding': '0',
                    'cellspacing': '0',
                    'border': '0',
                    'width': '100%'
                })
            for link in section.find_all('a'):
                href = link.get('href')
                urls.append('https://economictimes.indiatimes.com' + href)
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in EconomicTimes, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class TimesOfIndiaCrawler(TheHinduCrawler):
    """
    Crawling code for Times of India publisher.
    Sample archive page:   https://timesofindia.indiatimes.com/archivelist/year-2019,month-1,starttime-43476.cms
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []

        def excel_date(date1):
            """Custom function to get an Excel date number for a given date."""
            date1 = datetime.strptime(date1, "%Y-%m-%d")
            temp = datetime(1899, 12, 30)
            delta = date1 - temp
            return delta.days

        for date_element in pd.date_range(self.start_date, self.end_date):
            dt_year = str(date_element)[:4]
            dt_month = str(date_element).split("-")[1].lstrip("0")
            dt_day = datetime.strptime(str(date_element)[:10],
                                       "%Y-%m-%d").strftime("%d").lstrip("0")
            urls.append('https://timesofindia.indiatimes.com/' + dt_year +
                        "/" + dt_month + "/" + dt_day + "/" +
                        "archivelist/year-" + dt_year + ",month-" + dt_month +
                        ",starttime-" +
                        str(excel_date(str(date_element)[:10])) + ".cms")
        logging.info("Generating %d urls for TimesofIndia", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            section = soup.find(
                'div', {
                    'style':
                    "font-family:arial ;font-size:12;font-weight:bold; color: #006699"
                })
            for link in section.find_all('a'):
                if "ads.indiatimes.com" in link.get('href'):
                    continue
                if "timesofindia.indiatimes.com" in link.get('href'):
                    urls.append(link.get('href'))
                if link.get('href')[0] == '/':
                    urls.append('http://timesofindia.indiatimes.com' +
                                link.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in TimesofIndia, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class NDTVCrawler(BaseCrawler):
    """
    Crawling code for NDTV publisher.
    * Archive links for this publisher are month-wise.
    Sample archive page:   https://archives.ndtv.com/articles/2021-04.html
    """
    def __init__(self, start_date, end_date):
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def get_article_urls(self):
        """Function to extract article urls from archive pages."""
        all_days_year_month = []
        all_days_total = []
        page_urls = []
        article_urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            if date_element.strftime("%Y-%m") not in all_days_year_month:
                all_days_year_month.append(date_element.strftime("%Y-%m"))
            all_days_total.append(date_element.strftime("%d %B %Y"))
        for instance in all_days_year_month:
            page_urls.append("https://archives.ndtv.com/articles/" + instance +
                             ".html")
        for page_url in page_urls:
            response = requests_retry_session().get(
                page_url,
                timeout=2,
                verify=False,
                headers=random.choice(headers_list_NDTV),  # nosec
                proxies={"http": random.choice(proxies_ip_list)})  # nosec
            soup = BeautifulSoup(response.content, 'html5lib')
            for h3_element in soup.find_all('h3'):
                for all_day_total in all_days_total:
                    if all_day_total == h3_element.text:
                        for list_element in h3_element.find_next(
                                'ul').find_all('li'):
                            article_link = list_element.a.get('href')
                            article_urls.append(article_link)
        faulty_articles_tuple = ('khabar.ndtv.com', 'swirlster.ndtv.com',
                                 '/bengali/', '/tamil/', '/hindi/', 'hindi.',
                                 'tamil.', 'bengali.')
        correct_article_urls = [
            url for url in article_urls
            if not any(faulty_article in url
                       for faulty_article in faulty_articles_tuple)
        ]
        return list(set(correct_article_urls))


class DeccanHeraldCrawler(BaseCrawler):
    """
    Crawling code for Deccan Herald publisher.
    * Date-wise archive articles for this publisher are obtained by making a POST request to
    "https://www.deccanherald.com/getarchive", and 'arcDate' should be like 2021/04/13 (for 13 April, 2021)
    """
    def __init__(self, start_date, end_date):
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def get_article_urls(self):
        """Function to extract article urls from archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            response = requests.post(
                "https://www.deccanherald.com/getarchive",
                data={'arcDate': date_element.strftime("%Y/%m/%d")})
            soup = BeautifulSoup(response.content, 'html5lib')
            links = soup.find_all('a')
            for link in links:
                final_link = "https://www.deccanherald.com%s" % link.get(
                    'href')
                if final_link not in urls:
                    urls.append(final_link)
        return list(set(urls))


class IndependentCrawler(TheHinduCrawler):
    """
    Crawling code for Independent publisher.
    Sample archive page:   https://www.independent.co.uk/archive/2021-04-13
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            urls.append("https://www.independent.co.uk/archive/%s",
                        date_element.strftime("%Y-%m-%d"))
        logging.info("Generating %d urls for Independent", len(urls))
        return urls

    def _get_article_urls(self, page_url):  # pylint: disable=no-self-use
        """Returns a list of article urls."""
        urls = []
        page = make_requests(page_url,
                             random.choice(headers_list_Independent))  # nosec
        try:
            soup = BeautifulSoup(page.content, 'html5lib')
            header_one = soup.find('h1', {'class': 'withDate'})
            unordered_list = header_one.find_next('ul')
            for link in unordered_list.find_all('a'):
                urls.append("https://www.independent.co.uk" + link.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in Independent, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class EveningStandardCrawler(TheHinduCrawler):
    """
    Crawling code for Evening Standard publisher.
    Sample archive page:   https://www.standard.co.uk/archive/2021-04-13
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            urls.append("https://www.standard.co.uk/archive/%s",
                        date_element.strftime("%Y-%m-%d").replace("-0", "-"))
        logging.info("Generating %d urls for EveningStandard", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            header_one = soup.find('h1', {'class': 'withDate'})
            unordered_list = header_one.find_next('ul')
            for link in unordered_list.find_all('a'):
                urls.append("https://www.standard.co.uk" + link.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in EveningStandard, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class NewYorkPostCrawler(TheHinduCrawler):
    """
    Crawling code for New York Post publisher.
    Sample archive page:   https://nypost.com/2021/04/13/
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            urls.append("https://nypost.com/%s",
                        date_element.strftime("%Y/%m/%d/"))
        logging.info("Generating %d urls for NewYorkPost", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            for header_three in soup.find_all('h3',
                                              {'class': 'entry-heading'}):
                urls.append(header_three.find_next('a').get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in NewYorkPost, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class ExpressCrawler(TheHinduCrawler):
    """
    Crawling code for Express publisher.
    Sample archive page:   https://www.express.co.uk/sitearchive/2021/04/13
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            urls.append('https://www.express.co.uk/sitearchive/' +
                        date_element.strftime('%Y/%m/%d').replace("/0", "/"))
        logging.info("Generating %d urls for Express", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            mydivs = soup.find_all('ul', {'class': 'section-list'})
            for div in mydivs:
                for link in div.find_all('a'):
                    urls.append('https://www.express.co.uk' + link.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in Express, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class USATodayCrawler(BaseCrawler):
    """
    Crawling code for USA Today publisher.
    * Archive pages for this publisher are distributed across multiple pages.
    Sample archive page:   https://www.usatoday.com/sitemap/2021/april/13/?page=0
    """
    def __init__(self, start_date, end_date):
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def get_article_urls(self):
        """Returns a list of article urls."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            for i in range(1, 50):
                page = "https://www.usatoday.com/sitemap/%s?page=%d" % (
                    date_element.strftime("%Y/%B/%d/").lower(), i)
                response = requests_retry_session().get(
                    page,
                    timeout=3,
                    verify=False,
                    headers=random.choice(headers_list_USAToday),  # nosec
                    proxies={"http": random.choice(proxies_ip_list)})  # nosec
                # USAToday doesn't extract correct #articles with make_requests, thus requests_retry_session() is used
                soup = BeautifulSoup(response.content, 'html5lib')
                for unordered_list in soup.find_all(
                        lambda tag: tag.name == 'ul' and tag.get(
                            'class') == ['sitemap-list'] and tag.next_element[
                                'class'] == ['sitemap-list-item']):
                    for link in unordered_list.find_all('a'):
                        urls.append(link.get('href'))
        logging.info("Generating %d urls for USAToday", len(urls))
        return urls


class DailyMailCrawler(TheHinduCrawler):
    """
    Crawling code for Daily Mail publisher.
    Sample archive page:   https://www.dailymail.co.uk/home/sitemaparchive/day_20210413.html
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            urls.append(
                'https://www.dailymail.co.uk/home/sitemaparchive/day_' +
                date_element.strftime("%Y%m%d") + '.html')
        logging.info("Generating %d urls for DailyMail", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            section = soup.find('ul',
                                {'class': 'archive-articles debate link-box'})
            for link in section.find_all('a'):
                urls.append('https://www.dailymail.co.uk' + link.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in DailyMail, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class IndiaTodayCrawler(TheHinduCrawler):
    """
    Crawling code for India Today publisher.
    * Archive pages for this publisher are distributed across multiple pages.
    Sample archive page:   https://www.indiatoday.in/archives/story/13-04-2021?bundle_name=Story&hash=itbxf0&ds_changed=2021-04-13&page=0
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            for num in range(0, 50):
                url_scaffold = "https://www.indiatoday.in/archives/story/%s?bundle_name=Story&hash=itbxf0&ds_changed=%s&page=%d"  # noqa: E501
                page = url_scaffold % (date_element.strftime("%d-%m-%Y"),
                                       date_element.strftime("%Y-%m-%d"), num)
                response = make_requests(
                    page, random.choice(headers_list_IndiaToday))  # nosec
                soup = BeautifulSoup(response.content, 'html5lib')
                if "No Record Found !" not in soup.text:
                    urls.append(page)
                else:
                    break
        logging.info("Generating %d urls for IndiaToday", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        response = make_requests(
            page_url, random.choice(headers_list_IndiaToday))  # nosec
        try:
            soup = BeautifulSoup(response.content, 'html5lib')
            mydivs = soup.find_all(
                'div', {'class': 'views-field views-field-nothing-1'})
            for division in mydivs:
                article_link = division.find('a')
                urls.append('https://www.indiatoday.in' +
                            article_link.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in IndiaToday, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class OneIndiaCrawler(TheHinduCrawler):
    """
    Crawling code for One India publisher.
    Sample archive page:   https://www.oneindia.com/2021/04/13
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            urls.append('https://www.oneindia.com/' +
                        date_element.strftime('%Y/%m/%d/'))
        logging.info("Generating %d urls for OneIndia", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            sections = soup.find('div', {
                'class': 'content clearfix'
            }).find_all('ul')
            for section in sections:
                for list_element in section.find_all('li'):
                    href = list_element.a.get('href')
                    urls.append('https://www.oneindia.com' + href)
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in OneIndia, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class HinduBusinessLineCrawler(TheHinduCrawler):
    """
    Crawling code for Hindu Business Line publisher.
    Sample archive page:   https://www.thehindubusinessline.com/archive/web/2021/04/13/
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            urls.append('https://www.thehindubusinessline.com/archive/web/' +
                        date_element.strftime('%Y/%m/%d/'))
        logging.info("Generating %d urls for HinduBusinessLine", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            mydivs = soup.find_all('ul', {'class': 'archive-list'})
            for div in mydivs:
                for link in div.find_all('a'):
                    urls.append(link.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in HinduBusinessLine, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class ScrollNewsCrawler(TheHinduCrawler):
    """
    Crawling code for Scroll News publisher.
    * Archive pages for this publisher are distributed across multiple pages.
    Sample archive page:   https://scroll.in/archives/2021/04/13/page/1
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            for num in range(1, 25):
                page = 'https://scroll.in/archives/%s/page/%d' % (
                    date_element.strftime("%Y/%m/%d"), num)
                response = requests.get(
                    page,
                    timeout=2,
                    verify=False,  # nosec
                    headers=random.choice(headers_list_ScrollNews),  # nosec
                    proxies={"http": random.choice(proxies_ip_list)})  # nosec
                soup = BeautifulSoup(response.content, 'html5lib')
                if soup.find('li', {'class': 'row-story'}):
                    urls.append(page)
                else:
                    break
        logging.info("Generating %d urls for ScrollNews", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            mydivs = soup.find_all('li', {'class': 'row-story'})
            for div in mydivs:
                urls.append(div.find('a').get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in ScrollNews, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class CNBCCrawler(TheHinduCrawler):
    """
    Crawling code for CNBC World publisher.
    Sample archive page:   https://www.cnbc.com/site-map/articles/2021/April/13
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            urls.append("https://www.cnbc.com/site-map/%s",
                        date_element.strftime("%Y/%B/%d/").replace("/0", "/"))
        logging.info("Generating %d urls for CNBC", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            div = soup.find('div', {'class': 'SiteMapArticleList-articleData'})
            for link in div.find_all('a',
                                     {'class': 'SiteMapArticleList-link'}):
                urls.append(link.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in CNBC, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class TheIndianExpressCrawler(BaseCrawler):
    """Crawling code for The Indian Express publisher."""
    def get_article_urls(self, url):  # pylint: disable=no-self-use
        """
        Code to crawl articles from https://indianexpress.com/section/news-archive/
        * All 25,117 pages of this archive have already been crawled, so this
          function is just for reference.
        """
        urls = []
        response = requests.get(url, timeout=3)
        soup = BeautifulSoup(response.content, 'html5lib')
        logging.info("\nOn page %s \n", url.split("page/")[1].split("/")[0])
        div_articles = soup.find_all('div', {'class': 'articles'})
        for div_article in div_articles:
            header_two = div_article.find_next('h2')
            link = header_two.a.get('href')
            urls.append(link)
        return urls


class ThePioneerCrawler(TheHinduCrawler):
    """
    Crawling code for The Pioneer publisher.
    * Archive pages for this publisher are distributed across multiple pages.
    Sample archive page:   https://www.dailypioneer.com/searchlist.php?yr=2021&mn=4&page=1
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of article urls after crawling all archive pages of a month."""
        urls = []
        article_urls = []
        set_element = set()
        for date_element in pd.date_range(self.start_date, self.end_date):
            set_element.add("yr={}&mn={}".format(
                date_element.strftime("%Y"),
                date_element.strftime("%m").lstrip("0")))
        set_element = list(set_element)
        for element in set_element:  # pylint: disable=too-many-nested-blocks
            for i in range(1, 1000):
                url = "https://www.dailypioneer.com/searchlist.php?{}&page={}".format(
                    element, i)
                page = self._crawl_page(url)  # pylint: disable=too-many-function-args
                soup = BeautifulSoup(page, 'html5lib')
                try:
                    highlighted_news = soup.find('div',
                                                 {'class': 'highLightedNews'})
                    if highlighted_news:
                        if url not in urls:
                            try:
                                for link_element in highlighted_news.find_all(
                                        'a'):
                                    if ".html" in link_element.get('href'):
                                        url = "https://www.dailypioneer.com" + link_element.get(
                                            'href')
                                        if url not in article_urls:
                                            article_urls.append(url)
                                inner_news_list = soup.find(
                                    'div', {'class': 'innerNewsList'})
                                for h2_element in inner_news_list.find_all(
                                        'h2'):
                                    article_urls.append(
                                        "https://www.dailypioneer.com" +
                                        h2_element.a.get('href'))
                            except Exception as exception:  # pylint: disable=broad-except
                                logging.exception(
                                    "Exception occurred while fetching the links in ThePioneer, url is %s, exception ===> %s"
                                    % (url, exception))
                    else:
                        break
                except:  # pylint: disable=bare-except  # noqa: E722
                    break
        logging.info("Generating %d article urls for ThePioneer",
                     len(article_urls))
        return list(set(article_urls))

    def get_article_urls(self):
        return self._get_page_urls()


class FinancialExpressCrawler(TheHinduCrawler):
    """
    Crawling code for The Hindu publisher.
    * Archive pages for this publisher are distributed across multiple pages.
    Sample archive page:   https://www.financialexpress.com/archive/2014/11/?page=1
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = set()
        set_element = set()
        for date_element in pd.date_range(self.start_date, self.end_date):
            set_element.add(date_element.strftime("%Y/%m"))
        set_element = sorted(list(set_element))
        for element in set_element:
            for i in range(1, 100):
                url = "https://www.financialexpress.com/archive/%s/?page=%d" % (
                    element, i)
                request = urlopen(url)  # nosec
                soup = BeautifulSoup(request.read(), 'html5lib')
                next_page = soup.find('li', {'class': 'next disabled'})
                if url not in urls:
                    urls.add(url)
                if next_page:
                    break
        logging.info("Generating %d urls for FinancialExpress", len(urls))
        return list(urls)

    def _get_article_urls(self, page_url):  # pylint: disable=no-self-use
        """Returns a list of article urls."""
        urls = set()
        page = urlopen(page_url)  # nosec
        try:
            soup = BeautifulSoup(page.read(), 'html5lib')
            news_section = soup.find('div', {'class': 'news'})
            for article in news_section.find_all('a'):
                if "www.financialexpress.com" in article.get('href'):
                    urls.add(article.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in FinancialExpress, url is %s, exception ===> %s"
                % (page_url, exception))
        return list(urls)


class EuroNewsCrawler(TheHinduCrawler):
    """
    Crawling code for Euro News publisher.
    * Archive pages for this publisher are distributed across multiple pages.
    Sample archive page:   https://www.euronews.com/2021/04/13?p=1
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            for num in range(1, 50):
                page = 'https://www.euronews.com/%s?p=%d' % (
                    date_element.strftime('%Y/%m/%d'), num)
                response = requests.get(page, timeout=3)
                soup = BeautifulSoup(response.content, 'html5lib')
                if soup.find('article', {'class': True}):
                    urls.append(page)
                else:
                    break
        logging.info("Generating %s urls for EuroNews", len(urls))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            mydivs = soup.find_all('div', {'class': 'm-object__body'})
            for div in mydivs:
                for link in div.find_all('a',
                                         {'class': 'm-object__title__link'}):
                    urls.append('https://www.euronews.com' + link.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in EuroNews, url is %s, exception ===> %s"
                % (page_url, exception))
        return urls


class ESPNCricInfoCrawler(BaseCrawler):
    """
    Crawling code for ESPN CricInfo publisher.
    * Archive pages for this publisher are distributed across multiple pages.
    Sample archive page:   https://www.espncricinfo.com/ci/content/story/data/index.json?datefrom=09+May+2014&dateupto=09+May+2014;;type=7;page=2
    """
    def __init__(self, start_date, end_date):
        """Init function."""
        self.start_date = datetime.strptime(start_date,
                                            "%Y-%m-%d").strftime("%d+%b+%Y")
        self.end_date = datetime.strptime(end_date,
                                          "%Y-%m-%d").strftime("%d+%b+%Y")

    def get_article_urls(self):
        """Returns a list of article urls."""
        urls = []
        for i in range(1, 30):
            url_scaffold = "https://www.espncricinfo.com/ci/content/story/data/index.json?datefrom=%s&dateupto=%s;;type=7;page=%d"  # noqa: E501
            page = url_scaffold % (self.start_date, self.end_date, i)
            response = requests.get(page, timeout=3)
            soup = BeautifulSoup(response.content, 'html5lib')
            body = json.loads(soup.find('body').text)
            if body == []:
                break
            for element in body:
                urls.append(
                    "https://www.espncricinfo.com/ci/content/story/%s.html",
                    element['object_id'])
        logging.info("Generating %d urls for ESPNCricInfo", len(urls))
        return list(set(urls))


class NYTimesCrawler(TheHinduCrawler):
    """
    Crawling code for New York Times publisher.
    Sample archive page:   https://www.nytimes.com/sitemap/2020/12/31/
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            urls.append('https://www.nytimes.com/sitemap/{}/'.format(
                date_element.strftime("%Y/%m/%d")))
        return urls

    def _get_article_urls(self, page_url):
        """Returns a list of article urls."""
        urls = []
        page = self._crawl_page(page_url)  # pylint: disable=too-many-function-args
        try:
            soup = BeautifulSoup(page, 'html5lib')
            main_content = soup.find('main', {'id': 'site-content'})
            list_of_articles = main_content.find_all('li')
            for article in list_of_articles:
                urls.append(article.a.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in NYTimes, url is %s, exception ===> %s"
                % (page_url, exception))
        faulty_articles_tuple = ('/issue/todayspaper',
                                 '/issue/todaysheadlines', '/issue/todaysinyt',
                                 '/espanol/')
        correct_article_urls = [
            url for url in urls
            if not any(faulty_article in url
                       for faulty_article in faulty_articles_tuple)
        ]
        return list(set(correct_article_urls))


class BusinessStandardCrawler(TheHinduCrawler):
    """
    Crawling code for Business Standard publisher.
    *  For this publisher, we get all articles of a date from 3 distinct pages (Latest news, General news, and Today's paper)
       and return all distinct articles
    *  Many articles collected from the 3 pages are Premium, i.e. the code might not be able to crawl the entire data from them
    Sample archive page (Latest news):   https://www.business-standard.com/latest-news?print_dd=13&print_mm=04&print_yy=2021
    Sample archive page (General news):  https://www.business-standard.com/general-news?print_dd=13&print_mm=04&print_yy=2021
    Sample archive page (Today's paper): https://www.business-standard.com/todays-paper?print_dd=13&print_mm=04&print_yy=2021
    """
    def __init__(self, start_date, end_date):  # pylint: disable=super-init-not-called
        """Init function."""
        self.start_date = start_date
        self.end_date = end_date

    def _get_page_urls(self):
        """Returns a list of urls of archive pages."""
        urls = []
        for date_element in pd.date_range(self.start_date, self.end_date):
            day, month, year = (date_element.strftime("%d"),
                                date_element.strftime("%m"),
                                date_element.strftime("%Y"))
            latest_news = "https://www.business-standard.com/latest-news?print_dd=%s&print_mm=%s&print_yy=%s" % (
                day, month, year)
            general_news = "https://www.business-standard.com/general-news?print_dd=%s&print_mm=%s&print_yy=%s" % (
                day, month, year)
            todays_paper = "https://www.business-standard.com/todays-paper?print_dd=%s&print_mm=%s&print_yy=%s" % (
                day, month, year)
            urls.append(latest_news)
            urls.append(general_news)
            urls.append(todays_paper)
        logging.info("Generating %d urls for Business Standard", len(urls))
        return urls

    def _get_article_urls(self, page_url):  # pylint: disable=no-self-use
        """Returns a list of article urls."""
        urls = set()
        response = make_requests(
            page_url, random.choice(headers_list_BusinessStandard))  # nosec
        try:
            soup = BeautifulSoup(response.content, 'html5lib')
            lists = soup.find_all('ul', {'class': 'aticle-txt'})
            for list_element in lists:
                for link in list_element.find_all('a'):
                    urls.add("https://www.business-standard.com" +
                             link.get('href'))
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception occurred while fetching the links in Business Standard, url is %s, exception ===> %s"
                % (page_url, exception))
        urls = list(urls)
        return urls


def handler(publisher, start_date, end_date):  # pylint: disable=too-many-branches
    """
    Function which fetches article urls from archive pages of a range and
    returns them in a list.
    """
    crawler = None
    if publisher == "THE_HINDU":
        crawler = TheHinduCrawler(start_date, end_date)
    if publisher == "ECONOMIC_TIMES":
        crawler = EconomicTimesCrawler(start_date, end_date)
    if publisher == "TIMES_OF_INDIA":
        crawler = TimesOfIndiaCrawler(start_date, end_date)
    if publisher == "DECCAN_HERALD":
        crawler = DeccanHeraldCrawler(start_date, end_date)
    if publisher == "NDTV":
        crawler = NDTVCrawler(start_date, end_date)
    if publisher == "INDEPENDENT":
        crawler = IndependentCrawler(start_date, end_date)
    if publisher == "EVENING_STANDARD":
        crawler = EveningStandardCrawler(start_date, end_date)
    if publisher == "NEW_YORK_POST":
        crawler = NewYorkPostCrawler(start_date, end_date)
    if publisher == "EXPRESS":
        crawler = ExpressCrawler(start_date, end_date)
    if publisher == "USA_TODAY":
        crawler = USATodayCrawler(start_date, end_date)
    if publisher == "DAILY_MAIL":
        crawler = DailyMailCrawler(start_date, end_date)
    if publisher == "INDIA_TODAY":
        crawler = IndiaTodayCrawler(start_date, end_date)
    if publisher == "ONE_INDIA":
        crawler = OneIndiaCrawler(start_date, end_date)
    if publisher == "HINDU_BUSINESS_LINE":
        crawler = HinduBusinessLineCrawler(start_date, end_date)
    if publisher == "SCROLL_NEWS":
        crawler = ScrollNewsCrawler(start_date, end_date)
    if publisher == "CNBC_WORLD":
        crawler = CNBCCrawler(start_date, end_date)
    if publisher == "INDIAN_EXPRESS":
        crawler = TheIndianExpressCrawler(start_date, end_date)
    if publisher == "THE_PIONEER":
        crawler = ThePioneerCrawler(start_date, end_date)
    if publisher == "THE_FINANCIAL_EXPRESS":
        crawler = FinancialExpressCrawler(start_date, end_date)
    if publisher == "EURO_NEWS":
        crawler = EuroNewsCrawler(start_date, end_date)
    if publisher == "ESPN_CRICINFO":
        crawler = ESPNCricInfoCrawler(start_date, end_date)
    if publisher == "NEW_YORK_TIMES":
        crawler = NYTimesCrawler(start_date, end_date)
    if publisher == "BUSINESS_STANDARD":
        crawler = BusinessStandardCrawler(start_date, end_date)
    urls = crawler.get_article_urls()
    return urls


publisher_id_mapping = {
    'ScrollNews': uuid.UUID('7e5375ad-17b7-4598-bebb-4ec8ed3506bd'),
    'OneIndia': uuid.UUID('4af27ab5-becb-4fe2-9dce-87c2b6a6551d'),
    'HinduBusinessLine': uuid.UUID('499d177b-56c6-489b-b607-88840d31b3cd'),
    'NDTV': uuid.UUID('8704135c-0498-49c0-b47c-2cd355bbdbc4'),
    'DeccanHerald': uuid.UUID('805089cf-8e22-474f-b14d-0b67edbfee44'),
    'IndiaToday': uuid.UUID('8fa2fd28-3a27-449f-becd-36424435abe5'),
    'EconomicTimes': uuid.UUID('108a4fd3-06ad-424c-baa0-5c63c86d2a07'),
    'TimesofIndia': uuid.UUID('cb992884-bd4e-40a9-ad08-c820abc1f360'),
    'CNBCWorld': uuid.UUID('975d774d-9cf3-4b21-9526-e8c432f19932'),
    'NewYorkPost': uuid.UUID('99b9b40f-851e-45b6-9e7b-a08f9edf9b8e'),
    'EveningStandard': uuid.UUID('09dd0b00-a0b0-423d-8735-90df98252cdc'),
    'Independent': uuid.UUID('89dfb81e-3fdb-4ea2-a16c-d571bf051e4c'),
    'USAToday': uuid.UUID('3dd68f6d-fa18-489b-9589-5f821c1698a6'),
    'DailyMail': uuid.UUID('19a4b6ec-0f8c-44a3-842e-169a7746fd6b'),
    'Express': uuid.UUID('b2d56c7e-4e7b-45d4-8674-c1432ee9edcc'),
    'ThePioneer': uuid.UUID('88ac62c4-72a6-4ef3-842d-6ba133c4ef60'),
    'TheIndianExpress': uuid.UUID('31e281cb-65f2-4aaa-bff3-6fe2d7092b21'),
    'TheFinancialExpress': uuid.UUID('9a688b63-b12b-4a71-a6dd-ce8861b0c99d'),
    'EuroNews': uuid.UUID('e3c569fa-fa85-4852-b171-5d4829157e20'),
    'ESPNCricInfo': uuid.UUID('bf0ad581-35d2-4735-b654-884f62215613'),
    'NYTimes': uuid.UUID('7586b7fd-45d3-4d2f-a40a-8e541f03ef48'),
    'BusinessStandard': uuid.UUID('1f308812-0a38-4d0b-98b9-55d70ad36332')
}

COUNT_CRAWL_SUCCESS = 0
COUNT_CRAWL_FAIL = 0


def get_and_save_htmls(data):
    """
    Takes url of an article, its publisher, and date_crawled (archive date) as
    input, gets the html of the article and status_code from archives(), then
    adds all data into raw-articles table in MySQL, except html, which it adds to
    a MongoDB collection.

    If the data html is not '', then the article has a state of CRAWL_FAIL.
    Otherwise, it has a state of CRAWL_SUCCESS.
    """
    simple_crawler_object = SimpleCrawler()
    raw_articles = []
    mongo_data = []
    row = []
    if not data:
        return
    logging.info(
        "get_and_save_htmls() START || %s, %s, %s, %s ===> %s, %s, %s, %s" %
        (threading.current_thread().ident, data[0][0], data[0][1], data[0][2],
         threading.current_thread().ident, data[0][0], data[-1][1],
         data[-1][2]))
    for article_url, publisher, date_crawled in data:
        html, status_code = simple_crawler_object.fetch_url(
            article_url, publisher=publisher)
        id_ = uuid.uuid1()
        param = db.GlobalID(resource_type=db.ResourceType.ARTICLE,
                            resource_id=db.UUIDConversion.uuid_to_bin(id_, 1))
        logging.info("URL = {}, STATUS_CODE = {}".format(
            article_url, status_code))
        global COUNT_CRAWL_SUCCESS, COUNT_CRAWL_FAIL  # pylint: disable=global-statement
        if str(html) == '' or status_code != 200:
            COUNT_CRAWL_FAIL += 1
        else:
            COUNT_CRAWL_SUCCESS += 1
        row.append(param)

        if str(html) == '':
            raw_articles.append(
                db.RawArticles(resource_id=db.UUIDConversion.uuid_to_bin(
                    id_, 1),
                               publisher=db.Publishers[publisher],
                               url=article_url,
                               date_crawled=date_crawled,
                               state=db.ArticleState.CRAWL_FAIL,
                               publisher_id=db.UUIDConversion.uuid_to_bin(
                                   publisher_id_mapping[publisher], 1)))
        else:
            raw_articles.append(
                db.RawArticles(resource_id=db.UUIDConversion.uuid_to_bin(
                    id_, 1),
                               publisher=db.Publishers[publisher],
                               url=article_url,
                               date_crawled=date_crawled,
                               state=db.ArticleState.CRAWL_SUCCESS,
                               publisher_id=db.UUIDConversion.uuid_to_bin(
                                   publisher_id_mapping[publisher], 1)))
        mongo_data.append((db.UUIDConversion.mongodb_uuid(id_), str(html)))
    try:
        raw_articles_mongodb.insert_many([{
            '_id': resource_id,
            'html_body': html_body
        } for resource_id, html_body in mongo_data])
    except Exception as exception:  # pylint: disable=broad-except
        logging.exception(
            "EXCEPTION occurred while saving data to MongoDB collection ===> %s",
            exception)
    session = Session()
    session.add_all(row)
    session.add_all(raw_articles)
    try:
        session.commit()
    except Exception as exception:  # pylint: disable=broad-except
        session.rollback()
        logging.exception(
            "EXCEPTION occurred while saving data to MySQL ===> %s", exception)
    session.close()
    time.sleep(
        0.1)  # added to avoid sending too many requests to publisher server
    logging.info(
        "get_and_save_htmls() END || %s, %s, %s, %s ===> %s, %s, %s, %s" %
        (threading.current_thread().ident, data[0][0], data[0][1], data[0][2],
         threading.current_thread().ident, data[0][0], data[-1][1],
         data[-1][2]))


TOTAL_NUM_ARTICLES = 0
SUBDATA_LENGTH = 0


def per_day_thread(publisher, startdate):
    """
    Takes publisher and startdate (a single data) as input, fetches all article urls
    of that date using handler(), then passes (url, publisher, startdate) to
    get_and_save_htmls() in threads.

    30 urls per day are processed in any thread.
    """
    logging.info("per_day_thread() START ===> %s, %s, %s" %
                 (threading.current_thread().ident, publisher, startdate))
    article_urls = handler(publisher, startdate, startdate)
    logging.info("Date = {}    Total articles = {}".format(
        startdate, len(article_urls)))
    global TOTAL_NUM_ARTICLES, SUBDATA_LENGTH  # pylint: disable=global-statement
    TOTAL_NUM_ARTICLES += len(article_urls)

    article_per_process = math.ceil(len(article_urls) / PER_DAY)
    article_index = 0

    threads_list = []
    for _ in range(PER_DAY):
        subdata = []
        end_index = min(article_index + article_per_process, len(article_urls))
        for url in article_urls[article_index:end_index]:
            subdata.append([url, publisher, startdate])
            SUBDATA_LENGTH += 1
        article_index += article_per_process
        threads_list.append(Thread(target=get_and_save_htmls,
                                   args=(subdata, )))

    for thread_object in threads_list:
        thread_object.start()
    for thread_object in threads_list:
        thread_object.join()
    logging.info("per_day_thread() END ===> %s, %s, %s" %
                 (threading.current_thread().ident, publisher, startdate))


if __name__ == '__main__':
    initial_doc_count = raw_articles_mongodb.estimated_document_count()
    parser = argparse.ArgumentParser()
    parser.add_argument("-P",
                        "--publisher",
                        help="Publisher Name",
                        default="SCROLL_NEWS")
    parser.add_argument("-S",
                        "--startdate",
                        help="Start Date - format YYYY-MM-DD",
                        default=date.today())
    parser.add_argument("-E", "--enddate", help="End Date - format YYYY-MM-DD")
    args = parser.parse_args()
    publisher_input, archive_start_date, archive_end_date = args.publisher, args.startdate, args.enddate
    if archive_end_date is None:
        archive_end_date = archive_start_date + timedelta(days=1)

    all_dates = []
    for archive_date in pd.period_range(archive_start_date,
                                        archive_end_date,
                                        freq="D"):
        all_dates.append(archive_date.strftime("%Y-%m-%d"))

    # Checks if MongoDB server is ON, and proceeds only if it is
    if client.server_info()['ok'] == 1.0:
        threads = [
            Thread(target=per_day_thread, args=(publisher_input, d))
            for d in all_dates
        ]
        for batch_index in range(0, len(threads), DAYS_AT_A_TIME):
            logging_string = "Starting %d days batch from %s" % (
                DAYS_AT_A_TIME, all_dates[batch_index])
            logging.info(logging_string)
            for thread_element in threads[batch_index:batch_index +
                                          DAYS_AT_A_TIME]:
                thread_element.start()
            for thread_element in threads[batch_index:batch_index +
                                          DAYS_AT_A_TIME]:
                thread_element.join()

        with open("{}_crawl_status.txt".format(publisher_input),
                  'a') as publisher_crawl_file:
            logging.info("Startdate = {}  Enddate = {}".format(
                archive_start_date, archive_end_date))
            logging.info("Length of subdata = {}".format(SUBDATA_LENGTH))
            logging.info(
                "Total #CRAWL_SUCCESS = {}".format(COUNT_CRAWL_SUCCESS))
            logging.info("Total #CRAWL_FAIL = {}".format(COUNT_CRAWL_FAIL))
            logging.info(
                '\n\nTotal num articles = {}'.format(TOTAL_NUM_ARTICLES))
            publisher_crawl_file.write("Startdate = {}  Enddate = {}\n".format(
                archive_start_date, archive_end_date))
            publisher_crawl_file.write(
                "Length of subdata = {}\n".format(SUBDATA_LENGTH))
            publisher_crawl_file.write(
                "Total #CRAWL_SUCCESS = {}\n".format(COUNT_CRAWL_SUCCESS))
            publisher_crawl_file.write(
                "Total #CRAWL_FAIL = {}\n".format(COUNT_CRAWL_FAIL))
            publisher_crawl_file.write(
                'Total num articles = {}\n'.format(TOTAL_NUM_ARTICLES))
    else:
        logging.exception(
            "[Error]  Connection to MongoDB server can't be made. Exiting program"
        )

    docs_added_count = raw_articles_mongodb.estimated_document_count(
    ) - initial_doc_count
    logging.info("{} documents added to database".format(docs_added_count))

    STATS_SQL_QUERY = "SELECT date_crawled, state, count(*) FROM `raw-articles` WHERE publisher='{}' AND date_crawled BETWEEN '{}%' AND '{}%' AND t_create LIKE '{}%' GROUP BY date_crawled, state".format(  # nosec
        publisher_input, archive_start_date, archive_end_date,
        datetime.today().strftime("%Y-%m-%d"))
    stats = pd.read_sql(STATS_SQL_QUERY, my_connect)
    logging.info(stats)

    sys.exit()
