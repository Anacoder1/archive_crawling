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
logging.basicConfig(filename='date_extractor.log',
                    encoding='utf-8',
                    level=logging.INFO)

# to improve performance, regex statements are compiled only once per module
re_pub_date = re.compile(
    r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9][\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?'
)
re_class = re.compile(
    "pubdate|timestamp|article_date|articledate|date|posted-on", re.IGNORECASE)


class DateExtractor(AbstractExtractor):
    """Extracts the publish_date from a HTML page using 3 functions."""
    
    def __init__(self):
        self.name = "date_extractor"

    def detect_lang(self, html):
        """Detects the language of a HTML page. Returns an exception if language isn't English.
        
        Args:
            html: A HTML page.
        
        Returns:
            detect(html.text): Language of the HTML page.
        """
        try:
            tags = ['noscript', 'style']
            for tag in tags:
                for element in html.find_all(tag):
                    element.decompose()
            return detect(html.text)
        except Exception as e:
            logging.exception(
                "(Inside detect_lang) ==> Language of Article URL is not English. Aborting."
            )
            return str(e)

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

        self.html_item = item['spider_response']
        publish_date = None
        html = BeautifulSoup(self.html_item.body, 'html5lib')

        try:
            publish_date = self._extract_from_json(html)
            if publish_date is None:
                publish_date = self._extract_from_meta(html)
            if publish_date is None:
                publish_date = self._extract_from_html_tag(html)
        except Exception as e:
            logging.exception(
                "Exception thrown while trying executing _publish_date function: {}"
                .format(e))
            pass

        return publish_date

    def parse_date_str(self, date_string):
        """Parses a date string and returns it in the format of "YYYY-MM-DD HH:MM:SS"
        
        Args:
            date_string: A string containing a datetime instance, e.g. "Thursday, 04 May, 2020"
            
        Returns:
            date_string in the format of "YYYY-MM-DD HH:MM:SS", e.g. "2020-05-04 00:00:00"
        """
        try:
            date = parse(date_string)
            return date.strftime("%Y-%m-%d %H:%M:%S")
        except:
            try:
                matches = datefinder.find_dates(date_string)
                for m in matches:
                    if m.strftime("%Y") in date_string:
                        return m.strftime("%Y-%m-%d %H:%M:%S")
            except:
                return None

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _extract_from_json(self, html):
        """
        Fetches publish_date instance from HTML page, if present in <script> tags.
        
        Args:
            html: A HTML page, passed with the item argument in _publish_date().
         
        Returns:
            The publish_date extracted from the HTML page, if present. Otherwise, None is returned.
            If the language detected on the HTML page isn't English, None is returned.
        """
        date_from_script = None
        if self.detect_lang(html) != 'en':
            logging.exception(
                "(Inside _extract_from_json) ==> Language of Article URL is not English. Aborting."
            )
            return None
        else:
            try:
                scripts_one = html.find_all('script',
                                            type='application/ld+json')
                scripts_one = [
                    script for script in scripts_one if script is not None
                ]
                for script in scripts_one:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    try:
                        date_from_script = self.parse_date_str(
                            data['datePublished'])
                        logging.info(
                            "{} ==> (Inside _extract_from_json) ==> Date extracted from 'datePublished' attribute"
                            .format(self.html_item))
                        return date_from_script
                    except:
                        try:
                            date_from_script = self.parse_date_str(
                                data['dateCreated'])
                            logging.info(
                                "{} ==> (Inside _extract_from_json) ==> Date extracted from 'dateCreated' attribute"
                                .format(self.html_item))
                            return date_from_script
                        except:
                            try:
                                date_from_script = self.parse_date_str(
                                    data['uploadDate'])
                                logging.info(
                                    "{} ==> (Inside _extract_from_json) ==> Date extracted from 'uploadDate' attribute"
                                    .format(self.html_item))
                                return date_from_script
                            except:
                                pass
            except:
                try:
                    scripts_two = html.find_all('script',
                                                type='text/javascript')
                    scripts_two = [
                        script for script in scripts_two if script is not None
                    ]
                    for script in scripts_two:
                        data = json.loads(script.string, strict=False)
                        if type(data) is list:
                            data = data[0]
                            try:
                                date_from_script = self.parse_date_str(
                                    data['contentPublishedDate'])
                                logging.info(
                                    "{} ==> (Inside _extract_from_json) ==> Date extracted from 'contentPublishedDate' attribute"
                                    .format(self.html_item))
                                return date_from_script
                            except:
                                pass
                except:
                    return None

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _extract_from_meta(self, html):
        """
        Fetches publish_date instance from HTML page, if present in <meta> tags.
        
        Args:
            html: A HTML page, passed with the item argument in _publish_date().
         
        Returns:
            The publish_date extracted from the HTML page, if present. Otherwise, None is returned.
            If the language detected on the HTML page isn't English, None is returned.
        """
        date_from_meta = None
        if self.detect_lang(html) != 'en':
            logging.exception(
                "(Inside _extract_from_meta) ==> Language of Article URL is not English. Aborting."
            )
            return None
        else:
            try:
                for meta in html.find_all('meta'):
                    meta_name = meta.get('name', '').lower()
                    item_prop = meta.get('itemprop', '').lower()
                    http_equiv = meta.get('http-equiv', '').lower()
                    meta_property = meta.get('property', '').lower()

                    # <meta name="pubdate" content="2015-11-26T07:11:02Z" >
                    if 'pubdate' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta name='publishdate' content='201511261006'/>
                    if 'publishdate' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break
                    '''
                    <meta name="publish-date" content="Wed, 12 Feb 2020 17:00:00 +0530">, Tested on...
                    https://health.economictimes.indiatimes.com/news/diagnostics/novel-coronavirus-to-be-called-covid-19-who/74100705
                    https://health.economictimes.indiatimes.com/news/pharma/bharat-biotech-starts-human-trial-of-its-anti-covid-vaccine-at-pgi-rohtak-minister-anil-vij/77018713
                    https://cfo.economictimes.indiatimes.com/news/ashok-chawla-resigns-as-yes-bank-chairman/66625206
                    https://cfo.economictimes.indiatimes.com/news/dhfl-didnt-create-shell-companies-deviate-from-lending-norms-audit-report/68296051
                    https://auto.economictimes.indiatimes.com/news/industry/turkey-charges-seven-people-over-carlos-ghosn-escape/75640259
                    https://tech.economictimes.indiatimes.com/news/internet/after-facebook-staff-walkout-zuckerberg-defends-no-action-on-trump-posts/76166846
                    https://telecom.economictimes.indiatimes.com/news/upa-adopted-arbitrary-first-come-first-pay-policy-manoj-sinha/62192784
                    https://bfsi.economictimes.indiatimes.com/news/policy/10-decisions-taken-by-rbi-to-counter-coronavirus-impact-on-economy/74844644
                    https://energy.economictimes.indiatimes.com/news/power/only-lights-to-go-off-not-all-other-appliances-power-min-on-pms-9-minute-call/74981960
                    https://government.economictimes.indiatimes.com/news/secure-india/iaf-plans-to-buy-33-mig-29-sukhoi-30-fighter-jets/70894545
                    '''
                    if 'publish-date' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta name="timestamp"  data-type="date" content="2015-11-25 22:40:25" />
                    if 'timestamp' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta name="DC.date.issued" content="2015-11-26">
                    if 'dc.date.issued' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta name="Date" content="2015-11-26" />
                    if 'date' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta name="sailthru.date" content="2015-11-25T19:56:04+0000" />
                    if 'sailthru.date' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta name="article.published" content="2015-11-26T11:53:00.000Z" />
                    if 'article.published' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta name="published-date" content="2015-11-26T11:53:00.000Z" />
                    if 'published-date' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta name="article.created" content="2015-11-26T11:53:00.000Z" />
                    if 'article.created' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta name="article_date_original" content="Thursday, November 26, 2015,  6:42 AM" />
                    if 'article_date_original' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta name="cXenseParse:recs:publishtime" content="2015-11-26T14:42Z"/>
                    if 'cxenseparse:recs:publishtime' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta name="DATE_PUBLISHED" content="11/24/2015 01:05AM" />
                    if 'date_published' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break
                    '''
                    <meta name="OriginalPublicationDate" content="2009/04/09 08:12:43">, Tested on
                    http://news.bbc.co.uk/2/hi/south_asia/7991385.stm
                    http://news.bbc.co.uk/onthisday/hi/dates/stories/february/27/newsid_4168000/4168073.stm
                    http://news.bbc.co.uk/2/hi/asia-pacific/5402292.stm
                    http://news.bbc.co.uk/2/hi/south_asia/7756068.stm
                    http://news.bbc.co.uk/2/hi/middle_east/7159077.stm
                    http://news.bbc.co.uk/sport2/hi/cricket/7009035.stm#:~:text=India%20beat%20Pakistan%20in%20the,5%2C%20despite%20Gautam%20Gambhir's%2075
                    http://news.bbc.co.uk/sport2/hi/cricket/9444277.stm
                    http://news.bbc.co.uk/2/hi/entertainment/8498039.stm
                    '''
                    if 'originalpublicationdate' == meta_name:
                        date_from_meta = meta['content'].strip()
                        break
                    '''
                    <meta property="article:published_time"  content="2015-11-25" />, Tested on
                    https://www.sportskeeda.com/cricket/sri-lanka-plans-tougher-laws-against-match-fixing
                    https://www.sportskeeda.com/football/breaking-mls-and-eredivisie-set-to-be-suspended-due-to-coronavirus-outbreak
                    https://www.sportskeeda.com/sports/india-lifts-the-cricket-world-cup-2011-india-bleed-blue
                    https://www.sportskeeda.com/football/breaking-news-serie-a-set-to-return-from-june-20
                    '''
                    if 'article:published_time' == meta_property:
                        date_from_meta = meta['content'].strip()
                        break

                    if 'article:published' == meta_property:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta property="bt:pubDate" content="2015-11-26T00:10:33+00:00">
                    if 'bt:pubdate' == meta_property:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
                    if 'datepublished' == item_prop:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
                    if 'datecreated' == item_prop:
                        date_from_meta = meta['content'].strip()
                        break

                    # <meta http-equiv="data" content="10:27:15 AM Thursday, November 26, 2015">
                    if 'date' == http_equiv:
                        date_from_meta = meta['content'].strip()
                        break
                if date_from_meta is not None:
                    logging.info(
                        "{} ==> (Inside _extract_from_meta) ==> Date extracted using <meta> tags"
                        .format(self.html_item))
                    return self.parse_date_str(date_from_meta)
                else:
                    return None
            except:
                return None

    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def _extract_from_html_tag(self, html):
        """
        Fetches publish_date instance from HTML page, if present in other HTML tags
        such as <span>, <p>, <div>, <font>, etc.
        
        Args:
            html: A HTML page, passed with the item argument in _publish_date().
         
        Returns:
            The publish_date extracted from the HTML page, if present. Otherwise, None is returned.
            If the language detected on the HTML page isn't English, None is returned.
        """
        if self.detect_lang(html) != 'en':
            logging.exception(
                "(Inside _extract_from_html_tag) ==> Language of Article URL is not English. Aborting."
            )
            return None
        else:
            try:
                '''
                <i class="time> 2020-04-06 19:25:11</i>, Tested on...
                http://www.xinhuanet.com/english/2020-04/06/c_138951576.htm
                http://www.xinhuanet.com/english/2020-07/22/c_139232557.htm
                http://www.xinhuanet.com/english/africa/2020-07/07/c_139193352.htm
                '''
                i_tag = html.find('i', attrs={'class': 'time'})
                if i_tag is not None:
                    logging.info(
                        "{} ==> (Inside _extract_from_html_tag) ==> Date extracted from i_tag"
                        .format(self.html_item))
                    return self.parse_date_str(str(i_tag.text))
                '''
                <font size="1" face="Verdana, Arial, Helvetica, sans-serif" color="#FFFFFF">Friday, March 01, 2002</font>
                Tested on http://archive.indianexpress.com/old/ie20020301/top1.html
                <font size="1" face="Verdana, Arial, Helvetica, sans-serif">Thursday, February 28, 2002</font>
                Tested on http://archive.indianexpress.com/old/ie20020228/index.html
                '''
                font_face_tags = html.find_all(
                    'font',
                    attrs={'face': 'Verdana, Arial, Helvetica, sans-serif'})
                for font_face_tag in font_face_tags:
                    if self.parse_date_str(font_face_tag.text) is not None:
                        # if font_face_tag is not None:
                        font_face_tag_text = str(font_face_tag.text)
                        logging.info(
                            "{} ==> (Inside _extract_from_html_tag) ==> Date extracted from font_face_tag"
                            .format(self.html_item))
                        return self.parse_date_str(font_face_tag_text)
                '''
                <p class="cbz-news-datetime" style="margin-top:0px;">May 28 2018 by Rex Clementine</p>, Tested on
                https://m.cricbuzz.com/cricket-news/102280/kulatunga-lokuhettige-deny-wrongdoing-al-jazeera-sting-operation-sri-lanka-cricket
                https://m.cricbuzz.com/cricket-news/64546/gavaskar-relieved-from-bcci-duties
                '''
                p_tag_cbz = html.find('p',
                                      attrs={'class': 'cbz-news-datetime'})
                if p_tag_cbz is not None:
                    cbz_publish_datetime = str(p_tag_cbz.text)
                    matches = datefinder.find_dates(cbz_publish_datetime)
                    for m in matches:
                        if m > datetime.today():
                            continue
                        required_datetime = m.strftime("%Y-%m-%d %H:%M:%S")
                        logging.info(
                            "{} ==> (Inside _extract_from_html_tag) ==> Date extracted from p_tag_cbz"
                            .format(self.html_item))
                        return required_datetime

                for time in html.find_all('time'):
                    date_time = time.get('datetime', '')
                    if len(date_time) > 0:
                        logging.info(
                            "{} ==> (Inside _extract_from_html_tag) ==> Date extracted from time > datetime"
                            .format(self.html_item))
                        return self.parse_date_str(date_time)
                    date_time = time.get('class', '')
                    if len(date_time) > 0 and date_time[0].lower(
                    ) == 'timestamp':
                        logging.info(
                            "{} ==> (Inside _extract_from_html_tag) ==> Date extracted from time > class"
                            .format(self.html_item))
                        return self.parse_date_str(time.string)

                # Tested on.. https://www.cricbuzz.com/cricket-news/102609/ball-change-controversy-sri-lanka-windies-cricbuzzcom
                # https://www.cricbuzz.com/cricket-news/74216/bans-on-salman-butt-and-mohammad-asif-will-expire-on-september-1
                html_time = html.find('time',
                                      attrs={'itemprop': 'datePublished'})
                if html_time is not None:
                    time_from_html = html_time.get('datetime', '')
                    matches = datefinder.find_dates(str(time_from_html))
                    for m in matches:
                        if m > datetime.today():
                            continue
                        logging.info(
                            "{} ==> (Inside _extract_from_html_tag) ==> Date extracted from html_time"
                            .format(self.html_item))
                        return m.strftime("%Y-%m-%d %H:%M:%S")
                '''
                <div class = "story-date">, Tested on
                http://archive.indianexpress.com/news/godhra-carnage-case-trial-to-be-held-in-sabarmati-jail/455589/
                http://archive.indianexpress.com/news/delhi-gangrape-condition-of-victim-remains-/1047016/
                http://archive.indianexpress.com/news/suresh-kalmadi-sacked-as-ioa-president-after-15-years/781800/3
                http://archive.indianexpress.com/news/khaps-gathered-to-protest--onesided-action--by-cops/1166568/
                '''
                div_story_date = html.find('div',
                                           attrs={'class': 'story-date'})
                if div_story_date is not None:
                    div_story_date_text = str(div_story_date.text)
                    matches = datefinder.find_dates(div_story_date_text)
                    for m in matches:
                        if m > datetime.today():
                            continue
                        logging.info(
                            "{} ==> (Inside _extract_from_html_tag) ==> Date extracted from div_story_date"
                            .format(self.html_item))
                        return m.strftime("%Y-%m-%d %H:%M:%S")

                # Tested on http://archive.indianexpress.com/oldStory/15325/
                div_posted = html.find('div', attrs={'class': 'posted'})
                if div_posted is not None:
                    div_posted_text = str(div_posted.text)
                    matches = datefinder.find_dates(div_posted_text)
                    for m in matches:
                        if m > datetime.today():
                            continue
                        logging.info(
                            "{} ==> (Inside _extract_from_html_tag) ==> Date extracted from div_posted"
                            .format(self.html_item))
                        return m.strftime("%Y-%m-%d %H:%M:%S")


                tag = html.find('span', attrs={"itemprop": "datePublished"})
                if tag is not None:
                    date_string = tag.get('content')
                    if date_string is None:
                        date_string = tag.text
                    if date_string is not None:
                        logging.info(
                            "{} ==> (Inside _extract_from_html_tag) ==> Date extracted from span tag (itemprop)"
                            .format(self.html_item))
                        return self.parse_date_str(date_string)

                li_itemprop = html.find('li',
                                        attrs={'itemprop': 'datePublished'})
                if li_itemprop is not None:
                    date_string = li_itemprop.text
                    if date_string is not None:
                        logging.info(
                            "{} ==> (Inside _extract_from_html_tag) ==> Date extracted from li tag (itemprop"
                            .format(self.html_item))
                        return self.parse_date_str(date_string)

                for tag in html.find_all(['span', 'p', 'div'],
                                         class_=re_class):
                    date_string = tag.string
                    if date_string is None:
                        date_string = tag.text
                    date = self.parse_date_str(date_string)
                    if date is not None:
                        logging.info(
                            "{} ==> (Inside _extract_from_html_tag) ==> Date extracted from regex matching on span, p, div tags"
                            .format(self.html_item))
                        return date
                return None
            except:
                return None