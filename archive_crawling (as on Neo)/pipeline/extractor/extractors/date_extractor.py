"""Script to extract publish datetime from a news article."""

import json
import logging
import re
from contextlib import suppress
from datetime import datetime

import datefinder
import pytz
from bs4 import BeautifulSoup
from dateutil.parser import parse
from retrying import retry

from .abstract_extractor import AbstractExtractor

# To improve performance, regex statements are compiled only once per module
re_pub_date = re.compile(
    r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9][\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?'  # noqa: E501
)
re_class = re.compile(
    "pubdate|timestamp|article_date|articledate|date|posted-on", re.IGNORECASE)


class DateExtractor(AbstractExtractor):
    """Extracts the publish_date from a HTML page using 3 functions."""
    def __init__(self):  # pylint: disable=super-init-not-called
        """Init function."""
        self.name = "date_extractor"

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)
    def _publish_date(self, item):
        """ # noqa: D406, D413
        Returns the publish_date of the extracted article, using 3 functions.

        Args:
            item: A dictionary containing a HTML page as element.

        Returns:
            publish_date: The publish_date of the HTML page, if present.
                          Otherwise, None is returned.
                          If language detected by detect_lang() is not English,
                          publish_date is returned as None instantly.
        """

        html_item = item['spider_response']
        publish_date = None
        html = BeautifulSoup(html_item.body, 'html5lib')

        try:
            publish_date = self._extract_from_json(html)
            if publish_date is None:
                publish_date = self._extract_from_meta(html)
            if publish_date is None:
                publish_date = self._extract_from_html_tag(html)
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(
                "Exception thrown while trying executing _publish_date function: %s",
                exception)
            pass  # pylint: disable=unnecessary-pass

        return publish_date

    def parse_date_str(self, date_string):  # pylint: disable=no-self-use
        """ # noqa: D406, D413
        Parses a date string and returns it in the format of "YYYY-MM-DD HH:MM:SS"

        Args:
            date_string: A string containing a datetime instance, e.g. "Thursday, 04 May, 2020"

        Returns:
            date_string in the format of "YYYY-MM-DD HH:MM:SS", e.g. "2020-05-04 00:00:00"
        """
        date_string = date_string.replace("IST", "+05:30")
        ist_timezone = pytz.timezone('Asia/Kolkata')
        with suppress(Exception):
            date = parse(date_string)
            date = date.astimezone(ist_timezone)
            return date.strftime("%Y-%m-%d %H:%M:%S")
        with suppress(Exception):
            matches = datefinder.find_dates(date_string)
            for match in matches:
                if match.strftime("%Y") in date_string:
                    match = match.astimezone(ist_timezone)
                    return match.strftime("%Y-%m-%d %H:%M:%S")
        return None

    @retry(
        stop_max_attempt_number=2,  # noqa: C901
        wait_exponential_multiplier=1000,
        wait_exponential_max=3000)
    def _extract_from_json(self, html):  # pylint: disable=too-many-branches,too-many-return-statements
        """ # noqa: D406, D413
        Fetches publish_date instance from HTML page, if present in <script> tags.

        Args:
            html: A HTML page, passed with the item argument in _publish_date().

        Returns:
            The publish_date extracted from the HTML page, if present. Otherwise, None is returned.
            If the language detected on the HTML page isn't English, None is returned.
        """
        date_from_script = None
        with suppress(Exception):
            scripts_one = html.find_all('script', type='application/ld+json')
            scripts_one = [
                script for script in scripts_one if script is not None
            ]
            for script in scripts_one:
                data = json.loads(script.string, strict=False)
                if isinstance(data, list):
                    data = data[0]
                '''
                Tested on:
                * https://economictimes.indiatimes.com/internet/after-facebook-staff-walkout-zuckerberg-defends-no-action-on-trump-posts/articleshow/76166846.cms
                  <script type="application/ld+json">{"datePublished": "2020-06-03T07:37:00+05:30"}</script>
                * https://energy.economictimes.indiatimes.com/news/power/only-lights-to-go-off-not-all-other-appliances-power-min-on-pms-9-minute-call/74981960
                  <script type="application/ld+json">{"datePublished":"Sat, 04 Apr 2020 16:08:00 +0530"}</script>
                '''
                with suppress(Exception):
                    date_from_script = self.parse_date_str(
                        data['datePublished'])
                    return date_from_script
                with suppress(Exception):
                    date_from_script = self.parse_date_str(data['dateCreated'])
                    return date_from_script
                with suppress(Exception):
                    date_from_script = self.parse_date_str(data['uploadDate'])
                    return date_from_script
        with suppress(Exception):
            scripts_two = html.find_all('script', type='text/javascript')
            scripts_two = [
                script for script in scripts_two if script is not None
            ]
            for script in scripts_two:
                data = json.loads(script.string, strict=False)
                if isinstance(data, list):
                    data = data[0]
                with suppress(Exception):
                    date_from_script = self.parse_date_str(
                        data['contentPublishedDate'])
                    return date_from_script
        with suppress(Exception):
            scripts_three = html.find_all('script', {'charset': 'UTF-8'})
            scripts_three = [
                script for script in scripts_three if script is not None
            ]
            for script in scripts_three:
                with suppress(Exception):
                    if "post_date_gmt" in script.string:
                        date_from_script = self.parse_date_str(
                            script.string.split("post_date_gmt")[1])
                        return date_from_script
        '''
        Tested on
        * https://www.independent.co.uk/arts-entertainment/tv/news/bridgerton-violet-actor-ruth-gemmell-tracy-beaker-b1780757.html
          <script type="application/json">{"first_published_date":"Thursday, 31 December 2020", "article_publication_time":"09:38:07"}</script>
        * https://www.independent.co.uk/life-style/royal-family/the-crown-queen-cousins-nerissa-katherine-bowes-lyon-b1721187.html
          <script type="application/json">{"first_published_date":"Thursday, 26 November 2020", "article_publication_time":"07:26:01"}</script>
        '''
        with suppress(Exception):
            scripts = html.find_all('script', {'type': 'application/json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    first_published_date = str(data["first_published_date"])
                    article_publication_time = str(
                        data["article_publication_time"])
                    full_datetime = first_published_date + " " + article_publication_time
                    return self.parse_date_str(full_datetime)
        '''
        Tested on:
        * https://www.independent.co.uk/life-style/royal-family/the-crown-queen-cousins-nerissa-katherine-bowes-lyon-b1721187.html
          <script>var JSGlobals = {"publish":"2020-11-26T07:26:01Z"...}</script>
        * https://www.independent.co.uk/arts-entertainment/tv/news/bridgerton-violet-actor-ruth-gemmell-tracy-beaker-b1780757.html
          <script>var JSGlobals = {"publish":"2020-12-31T09:38:07Z"...}</script>
        '''
        with suppress(Exception):
            scripts = html.find_all('script')
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                if "\"publish\":" in str(script.string):
                    return self.parse_date_str(
                        str(script.string).split("var JSGlobals = ")[1].split(
                            "\"publish\":")[1].split(",")[0].replace("\"", ""))
        return date_from_script

    @retry(
        stop_max_attempt_number=2,  # noqa: C901
        wait_exponential_multiplier=1000,
        wait_exponential_max=3000)
    def _extract_from_meta(self, html):  # pylint: disable=too-many-branches
        """ # noqa: D406, D413
        Fetches publish_date instance from HTML page, if present in <meta> tags.

        Args:
            html: A HTML page, passed with the item argument in _publish_date().

        Returns:
            The publish_date extracted from the HTML page, if present. Otherwise, None is returned.
            If the language detected on the HTML page isn't English, None is returned.
        """
        date_from_meta = None
        with suppress(Exception):
            for meta in html.find_all('meta'):
                meta_name = meta.get('name', '').lower()
                item_prop = meta.get('itemprop', '').lower()
                http_equiv = meta.get('http-equiv', '').lower()
                meta_property = meta.get('property', '').lower()

                # <meta name="pubdate" content="2015-11-26T07:11:02Z" >
                if meta_name == 'pubdate':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta name='publishdate' content='201511261006'/>
                if meta_name == 'publishdate':
                    date_from_meta = meta['content'].strip()
                    break
                '''
                Tested on:
                * https://health.economictimes.indiatimes.com/news/diagnostics/novel-coronavirus-to-be-called-covid-19-who/74100705
                  <meta name="publish-date" content="Wed, 12 Feb 2020 17:00:00 +0530">
                * https://health.economictimes.indiatimes.com/news/pharma/bharat-biotech-starts-human-trial-of-its-anti-covid-vaccine-at-pgi-rohtak-minister-anil-vij/77018713
                  <meta name="publish-date" content="Fri, 17 Jul 2020 17:08:00 +0530">
                * https://cfo.economictimes.indiatimes.com/news/ashok-chawla-resigns-as-yes-bank-chairman/66625206
                  <meta name="publish-date" content="Wed, 14 Nov 2018 22:07:00 +0530">
                * https://cfo.economictimes.indiatimes.com/news/dhfl-didnt-create-shell-companies-deviate-from-lending-norms-audit-report/68296051
                  <meta name="publish-date" content="Thu, 07 Mar 2019 07:43:00 +0530">
                * https://auto.economictimes.indiatimes.com/news/industry/turkey-charges-seven-people-over-carlos-ghosn-escape/75640259
                  <meta name="publish-date" content="Sat, 09 May 2020 09:57:00 +0530">
                * https://telecom.economictimes.indiatimes.com/news/upa-adopted-arbitrary-first-come-first-pay-policy-manoj-sinha/62192784
                  <meta name="publish-date" content="Thu, 21 Dec 2017 15:28:00 +0530">
                * https://bfsi.economictimes.indiatimes.com/news/policy/10-decisions-taken-by-rbi-to-counter-coronavirus-impact-on-economy/74844644
                  <meta name="publish-date" content="Fri, 27 Mar 2020 14:16:00 +0530">
                * https://energy.economictimes.indiatimes.com/news/power/only-lights-to-go-off-not-all-other-appliances-power-min-on-pms-9-minute-call/74981960
                  <meta name="publish-date" content="Sat, 04 Apr 2020 16:08:00 +0530">
                * https://government.economictimes.indiatimes.com/news/secure-india/iaf-plans-to-buy-33-mig-29-sukhoi-30-fighter-jets/70894545
                  <meta name="publish-date" content="Thu, 29 Aug 2019 18:37:00 +0530">
                '''    # pylint: disable=pointless-string-statement
                if meta_name == 'publish-date':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta name="timestamp"  data-type="date" content="2015-11-25 22:40:25" />
                if meta_name == 'timestamp':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta name="DC.date.issued" content="2015-11-26">
                if meta_name == 'dc.date.issued':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta name="Date" content="2015-11-26" />
                if meta_name == 'date':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta name="sailthru.date" content="2015-11-25T19:56:04+0000" />
                if meta_name == 'sailthru.date':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta name="article.published" content="2015-11-26T11:53:00.000Z" />
                if meta_name == 'article.published':
                    date_from_meta = meta['content'].strip()
                    break
                '''
                Tested on
                * https://www.euronews.com/2020/12/08/france-s-next-aircraft-carrier-to-be-nuclear-powered-macron-confirms
                  <meta name="date.created" content="2020-12-08 19:16:03">
                * https://www.euronews.com/2020/12/09/the-eu-must-leverage-closer-trade-ties-with-uzbekistan-to-ensure-progress-on-human-rights-
                  <meta name="date.created" content="2020-12-09 07:00:10">
                '''
                if meta_name == 'date.created':
                    date_from_meta = meta['content'].strip()
                    break
                '''
                Tested on
                * https://www.euronews.com/2020/12/08/france-s-next-aircraft-carrier-to-be-nuclear-powered-macron-confirms
                  <meta name="date.available" content="2020-12-08 19:16:03">
                * https://www.euronews.com/2020/12/09/the-eu-must-leverage-closer-trade-ties-with-uzbekistan-to-ensure-progress-on-human-rights-
                  <meta name="date.available" content="2020-12-09 07:00:10">
                '''
                if meta_name == 'date.available':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta name="published-date" content="2015-11-26T11:53:00.000Z" />
                if meta_name == 'published-date':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta name="article.created" content="2015-11-26T11:53:00.000Z" />
                if meta_name == 'article.created':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta name="article_date_original" content="Thursday, November 26, 2015,  6:42 AM" />
                if meta_name == 'article_date_original':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta name="cXenseParse:recs:publishtime" content="2015-11-26T14:42Z"/>
                if meta_name == 'cxenseparse:recs:publishtime':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta name="DATE_PUBLISHED" content="11/24/2015 01:05AM" />
                if meta_name == 'date_published':
                    date_from_meta = meta['content'].strip()
                    break
                '''
                Tested on
                * http://news.bbc.co.uk/2/hi/south_asia/7991385.stm
                  <meta name="OriginalPublicationDate" content="2009/04/09 08:12:43">
                * http://news.bbc.co.uk/onthisday/hi/dates/stories/february/27/newsid_4168000/4168073.stm
                  <meta name="OriginalPublicationDate" content="2002/02/27 00:00:00">
                * http://news.bbc.co.uk/2/hi/asia-pacific/5402292.stm
                  <meta name="OriginalPublicationDate" content="2006/10/03 10:23:56">
                * http://news.bbc.co.uk/2/hi/south_asia/7756068.stm
                  <meta name="OriginalPublicationDate" content="2008/11/29 09:05:28">
                * http://news.bbc.co.uk/2/hi/middle_east/7159077.stm
                  <meta name="OriginalPublicationDate" content="2008/03/11 13:43:08">
                * http://news.bbc.co.uk/sport2/hi/cricket/7009035.stm#:~:text=India%20beat%20Pakistan%20in%20the,5%2C%20despite%20Gautam%20Gambhir's%2075
                  <meta name="OriginalPublicationDate" content="2007/09/24 15:19:20">
                * http://news.bbc.co.uk/sport2/hi/cricket/9444277.stm
                  <meta name="OriginalPublicationDate" content="2011/04/02 17:24:00">
                * http://news.bbc.co.uk/2/hi/entertainment/8498039.stm
                  <meta name="OriginalPublicationDate" content="2010/02/04 12:29:10">
                '''    # pylint: disable=pointless-string-statement
                if meta_name == 'originalpublicationdate':
                    date_from_meta = meta['content'].strip()
                    break
                '''
                Tested on
                * https://www.sportskeeda.com/cricket/sri-lanka-plans-tougher-laws-against-match-fixing
                  <meta property="article:published_time" content="2018-06-07T20:36:02+05:30">
                * https://www.sportskeeda.com/football/breaking-mls-and-eredivisie-set-to-be-suspended-due-to-coronavirus-outbreak
                  <meta property="article:published_time" content="2020-03-12T21:07:02+05:30">
                * https://www.sportskeeda.com/sports/india-lifts-the-cricket-world-cup-2011-india-bleed-blue
                  <meta property="article:published_time" content="2011-04-03T10:46:51+05:30">
                * https://www.sportskeeda.com/football/breaking-news-serie-a-set-to-return-from-june-20
                  <meta property="article:published_time" content="2020-05-28T23:30:07+05:30">
                * https://www.euronews.com/2020/12/08/france-s-next-aircraft-carrier-to-be-nuclear-powered-macron-confirms
                  <meta property="article:published_time" content="2020-12-08 19:16:03">
                '''    # pylint: disable=pointless-string-statement
                if meta_property == 'article:published_time':
                    date_from_meta = meta['content'].strip()
                    break

                if meta_property == 'article:published':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta property="bt:pubDate" content="2015-11-26T00:10:33+00:00">
                if meta_property == 'bt:pubdate':
                    date_from_meta = meta['content'].strip()
                    break
                '''
                Tested on:
                * https://www.independent.co.uk/arts-entertainment/tv/news/bridgerton-violet-actor-ruth-gemmell-tracy-beaker-b1780757.html
                <meta property="date" content="2020-12-31T09:38:07.000Z">
                * https://www.independent.co.uk/life-style/royal-family/the-crown-queen-cousins-nerissa-katherine-bowes-lyon-b1721187.html
                <meta property="date" content="2020-11-26T07:26:01.000Z">
                '''
                if meta_property == 'date':
                    date_from_meta = meta['content'].strip()
                    break
                '''
                Tested on
                * https://indianexpress.com/article/news-archive/cm-modi-does-the-victory-lap/
                  <meta itemprop="datePublished" content="2002-12-23">
                '''
                if item_prop == 'datepublished':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
                if item_prop == 'datecreated':
                    date_from_meta = meta['content'].strip()
                    break
                '''
                Tested on
                * https://m.cricbuzz.com/cricket-commentary/32232/pak-vs-rsa-2nd-test-south-africa-tour-of-pakistan-2021
                  <meta itemprop="startDate" content="Thursday, Feb 04, 2021">
                '''
                if item_prop == 'startdate':
                    date_from_meta = meta['content'].strip()
                    break

                # <meta http-equiv="data" content="10:27:15 AM Thursday, November 26, 2015">
                if http_equiv == 'date':
                    date_from_meta = meta['content'].strip()
                    break
            if date_from_meta is not None:
                return self.parse_date_str(date_from_meta)
            # else:
            # return None
        return date_from_meta

    @retry(
        stop_max_attempt_number=2,  # noqa: C901
        wait_exponential_multiplier=1000,
        wait_exponential_max=3000)
    def _extract_from_html_tag(self, html):  # pylint: disable=too-many-return-statements,too-many-branches
        """ # noqa: D406, D413
        Fetches publish_date instance from HTML page, if present in other HTML tags
        such as <span>, <p>, <div>, <font>, etc.

        Args:
            html: A HTML page, passed with the item argument in _publish_date().

        Returns:
            The publish_date extracted from the HTML page, if present. Otherwise, None is returned.
            If the language detected on the HTML page isn't English, None is returned.
        """
        with suppress(Exception):
            '''
            Tested on:
            * http://www.xinhuanet.com/english/2020-04/06/c_138951576.htm
              <i class="time"> 2020-04-06 19:25:11</i>
            * http://www.xinhuanet.com/english/2020-07/22/c_139232557.htm
              <i class="time"> 2020-07-22 20:49:48</i>
            * http://www.xinhuanet.com/english/africa/2020-07/07/c_139193352.htm
              <i class="time"> 2020-07-07 07:54:53</i>
            '''    # pylint: disable=pointless-string-statement
            i_tag = html.find('i', attrs={'class': 'time'})
            if i_tag is not None:
                return self.parse_date_str(str(i_tag.text))
            '''
            Tested on:
            * http://archive.indianexpress.com/old/ie20020301/top1.html
              <font size="1" face="Verdana, Arial, Helvetica, sans-serif" color="#FFFFFF">Friday, March 01, 2002</font>
            * http://archive.indianexpress.com/old/ie20020228/index.html
              <font size="1" face="Verdana, Arial, Helvetica, sans-serif">Thursday, February 28, 2002</font>
            '''    # pylint: disable=pointless-string-statement
            font_face_tags = html.find_all(
                'font',
                attrs={'face': 'Verdana, Arial, Helvetica, sans-serif'})
            for font_face_tag in font_face_tags:
                if self.parse_date_str(font_face_tag.text) is not None:
                    # if font_face_tag is not None:
                    font_face_tag_text = str(font_face_tag.text)
                    return self.parse_date_str(font_face_tag_text)
            '''
            https://m.cricbuzz.com/cricket-news/102280/kulatunga-lokuhettige-deny-wrongdoing-al-jazeera-sting-operation-sri-lanka-cricket
            https://m.cricbuzz.com/cricket-news/64546/gavaskar-relieved-from-bcci-duties
            '''    # pylint: disable=pointless-string-statement
            p_tag_cbz = html.find('p', attrs={'class': 'cbz-news-datetime'})
            if p_tag_cbz is not None:
                cbz_publish_datetime = str(p_tag_cbz.text)
                return self.parse_date_str(cbz_publish_datetime)
            '''
            Tested on
            * https://www.cricbuzz.com/cricket-news/102609/ball-change-controversy-sri-lanka-windies-cricbuzzcom
              <time itemprop="datePublished" datetime="Jun 16 Sat 2018 UTC 03:06:42 0"></time>
            * https://www.cricbuzz.com/cricket-news/74216/bans-on-salman-butt-and-mohammad-asif-will-expire-on-september-1
              <time itemprop="datePublished" datetime="Aug 19 Wed 2015 UTC 03:08:50 0"></time>
            '''
            for time in html.find_all('time'):
                date_time = time.get('datetime', '')
                if len(date_time) > 0:
                    return self.parse_date_str(date_time)
                date_time = time.get('class', '')
                if len(date_time) > 0 and date_time[0].lower() == 'timestamp':
                    return self.parse_date_str(time.string)

            '''
            Tested on
            * http://archive.indianexpress.com/news/godhra-carnage-case-trial-to-be-held-in-sabarmati-jail/455589/
              <div class="story-date">...Ahmedabad, Thu May 07 2009, 00:08 hrs...</div>
            * http://archive.indianexpress.com/news/delhi-gangrape-condition-of-victim-remains-/1047016/
              <div class="story-date">...New Delhi, Mon Dec 24 2012, 11:04 hrs...</div>
            * http://archive.indianexpress.com/news/suresh-kalmadi-sacked-as-ioa-president-after-15-years/781800/3
              <div class="story-date">...New Delhi, Tue Apr 26 2011, 20:00 hrs...</div>
            * http://archive.indianexpress.com/news/khaps-gathered-to-protest--onesided-action--by-cops/1166568/
              <div class="story-date">...Lucknow, Mon Sep 09 2013, 03:55 hrs...</div>
            * http://archive.indianexpress.com/news/indias-average-economic-growth-during-upa-i/1214985/0
              <div class="story-date">...New Delhi, Fri Jan 03 2014, 12:54 hrs...</div>
            '''    # pylint: disable=pointless-string-statement
            div_story_date = html.find('div', attrs={'class': 'story-date'})
            if div_story_date is not None:
                div_story_date_text = str(div_story_date.text)
                matches = datefinder.find_dates(div_story_date_text)
                for match in matches:
                    if match > datetime.today():
                        continue
                    return match.strftime("%Y-%m-%d %H:%M:%S")

            div_posted = html.find('div', attrs={'class': 'posted'})
            if div_posted is not None:
                div_posted_text = str(div_posted.text)
                return self.parse_date_str(div_posted_text)
            '''
            Tested on
            * https://timesofindia.indiatimes.com/business/india-business/parliamentary-panel-question-paytm-about-chinese-investment-google-over-resisting-data-localisation/articleshowprint/78942848.cms
              <div class="time_cptn">TNN | Oct 30, 2020, 03.46 AM IST</div>
            '''
            div_time_cptn = html.find('div', attrs={'class': 'time_cptn'})
            if div_time_cptn is not None:
                div_time_cptn_text = str(div_time_cptn.text).strip()
                return self.parse_date_str(div_time_cptn_text)
            '''
            Tested on
            * https://www.business-standard.com/article/markets/auto-psu-stocks-to-outperform-in-the-short-term-vinay-rajani-of-hdfc-sec-121011300139_1.html
              <span itemprop="datePublished" content="2021-01-13">Last Updated at January 13, 2021 07:37 IST</span>
            * https://www.business-standard.com/article/current-affairs/death-of-galaxy-galactic-collision-spews-gases-equal-to-10-000-suns-a-year-121011300543_1.html
              <span itemprop="datePublished" content="2021-01-13">Last Updated at January 13, 2021 13:06 IST</span>
            '''
            span_tag = html.find('span', attrs={"itemprop": "datePublished"})
            if span_tag is not None:
                date_string = span_tag.get('content')
                if date_string is None:
                    date_string = span_tag.text
                if date_string is not None:
                    return self.parse_date_str(date_string)

            li_itemprop = html.find('li', attrs={'itemprop': 'datePublished'})
            if li_itemprop is not None:
                date_string = li_itemprop.text
                if date_string is not None:
                    return self.parse_date_str(date_string)

            for tag in html.find_all(['span', 'p', 'div'], class_=re_class):
                date_string = tag.string
                if date_string is None:
                    date_string = tag.text
                date = self.parse_date_str(date_string)
                if date is not None:
                    return date
            '''
            Tested on:
            * https://www.independent.co.uk/arts-entertainment/tv/news/bridgerton-violet-actor-ruth-gemmell-tracy-beaker-b1780757.html
            <amp-timeago datetime="2020-12-31T09:38:07.000Z"></amp-timeago>
            * https://www.independent.co.uk/life-style/royal-family/the-crown-queen-cousins-nerissa-katherine-bowes-lyon-b1721187.html
            <amp-timeago datetime="2020-11-26T07:10:00.000Z"></amp-timeago>
            '''
            with suppress(Exception):
                amp_timeago = html.find('amp-timeago')
                return self.parse_date_str(str(amp_timeago["datetime"]))
            return None
        return None
