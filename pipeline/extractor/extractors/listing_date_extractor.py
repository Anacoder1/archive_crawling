from .abstract_extractor import AbstractExtractor
from bs4 import BeautifulSoup
from copy import deepcopy
from datetime import datetime
from dateutil.parser import parse
import datefinder
from langdetect import detect, DetectorFactory
import logging
import json
import requests
import re
from retrying import retry
import sys
import codecs

DetectorFactory.seed = 0
# logging.basicConfig(filename='date_extractor.log',
#                     encoding='utf-8',
#                     level=logging.INFO)

# to improve performance, regex statements are compiled only once per module
re_pub_date = re.compile(
    r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9][\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?'
)
re_class = re.compile(
    "pubdate|timestamp|article_date|articledate|date|posted-on", re.IGNORECASE)


class DateExtractor(AbstractExtractor):
    """Extracts the publish_date from a HTML page using 3 functions."""

    def __init__(self):
        self.name = "listing_date_extractor"

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _publish_date(self, item):
        """Returns the publish_date of the extracted article, using 3 functions.

        Args:
            item: A dictionary containing a HTML page as element.

        Returns:
            publish_date: The publish_date of the HTML page, if present.
                          Otherwise, None is returned.
                          If language detected by detect_lang() is not English,
                          publish_date is returned as None instantly.
        """

        return item['article_publish_date']