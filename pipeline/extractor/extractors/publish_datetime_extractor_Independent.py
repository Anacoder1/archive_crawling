from .abstract_extractor import AbstractExtractor
from bs4 import BeautifulSoup
from datetime import datetime
import dateparser
import datefinder
from langdetect import detect, DetectorFactory
import logging
import json
import pytz
from retrying import retry

class PublishDatetimeExtractor(AbstractExtractor):
    def __init__(self):
        self.name = "publish_datetime_extractor_Independent"

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _publish_date(self, item):
        self.html_item = item['spider_response']
        publish_date = None
        html = BeautifulSoup(self.html_item.body, 'html5lib')

        try:
            publish_date = self._extract_publish_datetime(html)
        except Exception as e:
            logging.exception(
                "Exception thrown while trying executing _publish_datetime function: {}"
                .format(e))
            pass

        return publish_date


    def parse_date_str(self, date_string):
        date_string = date_string.replace("IST", "+05:30")
        IST = pytz.timezone('Asia/Kolkata')
        try:
            date = dateparser.parse(date_string)
            date = date.astimezone(IST)
            return date.strftime("%Y-%m-%d %H:%M:%S")
        except:
            try:
                matches = datefinder.find_dates(date_string)
                for m in matches:
                    if m.strftime("%Y") in date_string:
                        m = m.astimezone(IST)
                        return m.strftime("%Y-%m-%d %H:%M:%S")
            except:
                return None


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _extract_publish_datetime(self, html):
        publish_datetime_list = []
        try:
            scripts = html.find_all('script', {'type': 'application/json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    first_published_date = str(data["first_published_date"])
                    article_publication_time = str(data["article_publication_time"])
                    full_datetime = first_published_date + " " + article_publication_time
                    publish_datetime_list.append(self.parse_date_str(full_datetime))
                except:
                    pass
        except:
            pass
        try:
            amp_timeago = html.find('amp-timeago')
            publish_datetime_list.append(self.parse_date_str(str(amp_timeago["datetime"])))
        except:
            pass
        try:
            meta_date = html.find('meta', {'name': 'date'})
            publish_datetime_list.append(self.parse_date_str(str(meta_date["content"])))
        except:
            pass
        try:
            scripts = html.find_all('script')
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                if "var JSGLobals" in str(script.string):
                    publish_datetime_list.append(self.parse_date_str(str(scripts[13].string).split("var JSGlobals = ")[1].split("\"publish\":")[1].split(",")[0].replace("\"", "")))
        except:
            pass
        if len(publish_datetime_list) == 0:
            return None
        publish_datetime_list.sort(key = lambda date: datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))
        return publish_datetime_list[-1]
