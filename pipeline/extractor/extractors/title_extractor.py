from .abstract_extractor import AbstractExtractor
from bs4 import BeautifulSoup
import json
import re
from retrying import retry
import logging


class TitleExtractor(AbstractExtractor):
    def __init__(self):
        self.name = "title_extractor"

    def _title(self, item):
        self.html_item = item['spider_response']
        self.publisher = item['publisher']
        html = BeautifulSoup(self.html_item.body, 'html5lib')
        title = ""

        try:
            if self.publisher == 'EconomicTimes':
                title = self.title_ET(html)
            if self.publisher == 'TimesofIndia':
                title = self.title_TOI(html)
            if self.publisher == 'DeccanHerald':
                title = self.title_DH(html)
            if self.publisher == 'NDTV':
                title = self.title_NDTV(html)
            if self.publisher == 'Independent':
                title = self.title_Independent(html)
            if self.publisher == 'EveningStandard':
                title = self.title_EveningStandard(html)
            if self.publisher == 'NewYorkPost':
                title = self.title_NewYorkPost(html)
            if self.publisher == 'Express':
                title = self.title_Express(html)
            if self.publisher == 'USAToday':
                title = self.title_USAToday(html)
            if self.publisher == 'DailyMail':
                title = self.title_DailyMail(html)
            if self.publisher == 'IndiaToday':
                title = self.title_IndiaToday(html)
            if self.publisher == 'OneIndia':
                title = self.title_OneIndia(html)
            if self.publisher == 'HinduBusinessLine':
                title = self.title_HinduBusinessLine(html)
            if self.publisher == 'ScrollNews':
                title = self.title_ScrollNews(html)
            if self.publisher == 'CNBCWorld':
                title = self.title_CNBC(html)
            if self.publisher == 'TheIndianExpress':
                title = self.title_TheIndianExpress(html)
            if self.publisher == 'ThePioneer':
                title = self.title_ThePioneer(html)
            if self.publisher == 'TheFinancialExpress':
                title = self.title_FinancialExpress(html)
            if self.publisher == 'EuroNews':
                title = self.title_EuroNews(html)
            if self.publisher == 'ESPNCricInfo':
                title = self.title_ESPNCricInfo(html)
            if self.publisher == 'NYTimes':
                title = self.title_NYTimes(html)
            if self.publisher == 'BusinessStandard':
                title = self.title_BusinessStandard(html)
        except Exception as e:
            logging.exception(e)
        return title


    def text_cleaning(self, text):
        text = text.encode("ascii", "ignore").decode("ascii", "ignore")
        text = re.sub(r'[^\x00-\x7F]', '', text)
        text = text.replace("\n", "")
        text = text.replace("\'", "'")
        text = text.replace("\\\"", '\"')
        text = text.replace("&amp;", "&")
        text = text.replace("&quot;", '\"')
        text = text.strip().lstrip().rstrip()
        return text

    def clean_title(self, title):
        title = title.split("|")[0].strip()
        return self.text_cleaning(title)

    def clean_title_DailyMail(self, title):
        title = title.split("|")[0].strip()
        title = title.replace("\\\"", "")
        title = title.replace("\\'", "'")
        return self.text_cleaning(title)

    def clean_title_IndiaToday(self, title):
        title = title.replace("| India Today Insight", "")
        return self.text_cleaning(title)

    def clean_title_OneIndia(self, title):
        title = title.replace("- Oneindia News", "")
        title = title.split("|")[0].strip()
        return self.text_cleaning(title)

    def clean_title_HinduBusinessLine(self, title):
        title = re.sub("- The Hindu BusinessLine|- VARIETY|- AGRI-BIZ & COMMODITY|- Today's Paper|- OPINION|- NEWS|- PULSE|- STATES|- MARKETS|- BL INK|- OTHERS|- PORTFOLIO|- AUTOMOBILE|- CLEAN TECH", "", title)
        return self.text_cleaning(title)

    def clean_title_ScrollNews(self, title):
        return self.text_cleaning(title)

    def clean_title_TheIndianExpress(self, title):
        title = title.replace("- Indian Express", "")
        return self.text_cleaning(title)

    def clean_title_EuroNews(self, title):
        title = title.replace("| Euronews", "")
        return self.text_cleaning(title)

    def clean_title_ESPNCricInfo(self, title):
        title = title.replace("| ESPNcricinfo.com", "")
        return self.text_cleaning(title)

    def clean_title_NYTimes(self, title):
        title = title.replace("- The New York Times", "")
        return self.text_cleaning(title)

    def clean_title_BusinessStandard(self, title):
        title = title.replace("| Business Standard News", "")
        return self.text_cleaning(title)



    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_ET(self, html):
        titles_list = []
        try:
            title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title(title['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "WebPage":
                        titles_list.append(self.clean_title(data["name"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle":
                        titles_list.append(self.clean_title(data["headline"]))
                except:
                    pass
        except:
            pass
        try:
            title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title(title['content']))
        except:
            pass
        try:
            div = html.find('div', {'class': 'article_block clearfix'})
            if div.get('data-arttitle'):
                titles_list.append(self.clean_title(div.get('data-arttitle')))
        except:
            pass
        try:
            title = html.find('h1')
            titles_list.append(self.clean_title(title.text))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_TOI(self, html):
        titles_list = []
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                data = json.loads(script.string, strict=False)
                try:
                    if data["@type"] == "WebPage":
                        titles_list.append(self.clean_title(data["name"]))
                except:
                    try:
                        if data["@type"] == "NewsArticle":
                            titles_list.append(self.clean_title(data["headline"]))
                    except:
                        pass
        except:
            pass
        try:
            title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title(title['content']))
        except:
            pass
        try:
            title = html.find('meta', {'property': 'twitter:title'})
            titles_list.append(self.clean_title(title['content']))
        except:
            pass
        try:
            title = html.find('h1')
            titles_list.append(self.clean_title(title.text))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_DH(self, html):
        try:
            title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title(title['content']))
        except:
            pass
        try:
            title = html.find('title')
            titles_list.append(self.clean_title(title.text))
        except:
            pass
        try:
            title = html.find('h1', {'id': 'page-title'})
            titles_list.append(self.clean_title(title.text))
        except:
            pass
        try:
            title = html.find('meta', {'itemprop': 'name'})
            titles_list.append(self.clean_title(title['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["headline"]:
                        titles_list.append(self.clean_title(data["headline"]))
                except:
                    pass
        except:
            pass
        try:
            title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title(title['content']))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_NDTV(self, html):
        titles_list = []
        try:
            title = html.find('title')
            titles_list.append(self.clean_title(title.text))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title(twitter_title['content']))
        except:
            pass
        try:
            scripts = html.find('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle":
                        titles_list.append(self.clean_title(data["headline"]))
                except:
                    try:
                        data = json.loads(script.string, strict=False)
                        if data["@type"] == "WebPage":
                            titles_list.append(self.clean_title(data["name"]))
                    except:
                        pass
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_Independent(self, html):
        titles_list = []
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title(twitter_title['content']))
        except:
            pass
        try:
            title = html.find('title')
            titles_list.append(self.clean_title(title.text))
        except:
            pass
        try:
            scripts_one = html.find_all('script', {'type': 'application/ld+json'})
            scripts_one = [script for script in scripts_one if script is not None]
            for script in scripts_one:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["headline"]:
                        titles_list.append(self.clean_title(data["headline"]))
                except:
                    pass
        except:
            pass
        try:
            scripts_two = html.find_all('script', {'type': 'application/json'})
            scripts_two = [script for script in scripts_two if script is not None]
            for script in scripts_two:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["article_title"]:
                        titles_list.append(self.clean_title(data["article_title"]))
                except:
                    pass
        except:
            pass
        try:
            input_streamTitle = html.find('input', {'name': 'streamTitle'})
            titles_list.append(self.clean_title(input_streamTitle["value"]))
        except:
            pass
        try:
            share_twitter = html.find('amp-social-share', {'type': 'twitter'})
            titles_list.append(self.clean_title(share_twitter["data-param-text"]))
        except:
            pass
        try:
            share_email = html.find('amp-social-share', {'type': 'email'})
            titles_list.append(self.clean_title(share_email["data-param-subject"]))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_EveningStandard(self, html):
        titles_list = []
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title(twitter_title['content']))
        except:
            pass
        try:
            title = html.find('title')
            titles_list.append(self.clean_title(title.text))
        except:
            pass
        try:
            scripts_one = html.find_all('script', {'type': 'application/ld+json'})
            scripts_one = [script for script in scripts_one if script is not None]
            for script in scripts_one:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["headline"]:
                        titles_list.append(self.clean_title(data["headline"]))
                except:
                    pass
        except:
            pass
        try:
            scripts_two = html.find_all('script', {'type': 'application/json'})
            scripts_two = [script for script in scripts_two if script is not None]
            for script in scripts_two:
                try:
                    data = json.loads(script.string, strict=False)
                    titles_list.append(self.clean_title(data["article_title"]))
                except:
                    pass
        except:
            pass
        try:
            twitter_share_title = html.find('amp-social-share', {'type': 'twitter'})
            titles_list.append(self.clean_title(twitter_share_title["data-param-text"]))
        except:
            pass
        try:
            email_share_title = html.find('amp-social-share', {'type': 'email'})
            titles_list.append(self.clean_title(email_share_title["data-param-subject"]))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_NewYorkPost(self, html):
        titles_list = []
        try:
            title = html.find('title')
            titles_list.append(self.clean_title(title.text))
        except:
            pass
        try:
            title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title(title['content']))
        except:
            pass
        try:
            title = html.find('meta', {'name': 'twitter:text:title'})
            titles_list.append(self.clean_title(title['content']))
        except:
            pass
        try:
            title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title(title['content']))
        except:
            pass
        try:
            title = html.find('h1')
            titles_list.append(self.clean_title(title.text))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["headline"]:
                        titles_list.append(self.clean_title(data["headline"]))
                except:
                    pass
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_Express(self, html):
        titles_list = []
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'property': 'twitter:title'})
            titles_list.append(self.clean_title(twitter_title['content']))
        except:
            pass
        try:
            h1_headline = html.find('h1', {'itemprop': 'headline'})
            titles_list.append(self.clean_title(h1_headline.text))
        except:
            pass
        try:
            title = html.find('title')
            titles_list.append(self.clean_title(title.text))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["name"]:
                        titles_list.append(self.clean_title(data["name"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["headline"]:
                        titles_list.append(self.clean_title(data["headline"]))
                except:
                    pass
        except:
            pass
        try:
            headline_short = html.find('meta', {'property': 'headline_short'})
            titles_list.append(self.clean_title(headline_short['content']))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_USAToday(self, html):
        titles_list = []
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title(twitter_title['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["headline"]:
                        titles_list.append(self.clean_title(data["headline"]))
                except:
                    pass
        except:
            pass
        try:
            div_share = html.find('div', {'data-ss-t': True})
            titles_list.append(self.clean_title(div_share['data-ss-t']))
        except:
            pass
        try:
            h1_headline = html.find('h1', {'elementtiming': 'ar-headline'})
            titles_list.append(self.clean_title(h1_headline.text))
        except:
            pass
        try:
            title = html.find('title')
            titles_list.append(self.clean_title(title.text))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_DailyMail(self, html):
        titles_list = []
        try:
            mol_headline = html.find('meta', {'property': 'mol:headline'})
            titles_list.append(self.clean_title_DailyMail(mol_headline['content']))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title_DailyMail(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'property': 'twitter:title'})
            titles_list.append(self.clean_title_DailyMail(twitter_title['content']))
        except:
            pass
        try:
            h2 = html.find('h2')
            titles_list.append(self.clean_title_DailyMail(h2.text))
        except:
            pass
        try:
            title = html.find('title')
            titles_list.append(self.clean_title_DailyMail(title.text))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle":
                        if data["headline"]:
                            titles_list.append(self.clean_title_DailyMail(data["headline"]))
                        if type(data["mainEntityOfPage"]) is list:
                            if data["mainEntityOfPage"][0]["name"]:
                                titles_list.append(self.clean_title_DailyMail(data["mainEntityOfPage"][0]["name"]))
                        elif type(data["mainEntityOfPage"]) is not list:
                            if data["mainEntityOfPage"]["name"]:
                                titles_list.append(self.clean_title_DailyMail(data["mainEntityOfPage"]["name"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "WebPage":
                        if data["headline"]:
                            titles_list.append(self.clean_title_DailyMail(data["headline"]))
                        if type(data["mainEntity"]) is list:
                            if data["mainEntity"][0]["name"]:
                                titles_list.append(self.clean_title_DailyMail(data["mainEntity"][0]["name"]))
                        elif type(data["mainEntity"]) is not list:
                            if data["mainEntity"]["name"]:
                                titles_list.append(self.clean_title_DailyMail(data["mainEntity"]["name"]))
                except:
                    pass
        except:
            pass
        try:
            sharelink_top = html.find('li', {'id': 'shareLinkTop'})
            titles_list.append(self.clean_title_DailyMail(sharelink_top['data-formatted-headline']))
        except:
            pass
        try:
            sharelink_bottom = html.find('li', {'id': 'shareLinkBottom'})
            titles_list.append(self.clean_title_DailyMail(sharelink_bottom['data-formatted-headline']))
        except:
            pass
        try:
            div_sharearticles = html.find('div', {'class': 'shareArticles'})
            titles_list.append(self.clean_title_DailyMail(div_sharearticles.h1.text))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_IndiaToday(self, html):
        titles_list = []
        try:
            title = html.find('title')
            titles_list.append(self.clean_title_IndiaToday(title.text.split(" - ")[0]))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title_IndiaToday(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title_IndiaToday(twitter_title['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "WebPage" and data["name"]:
                        titles_list.append(self.clean_title_IndiaToday(data["name"]))
                except:
                    pass
        except:
            pass
        try:
            h1 = html.find('h1', {'itemprop': 'headline'})
            titles_list.append(self.clean_title_IndiaToday(h1.text))
        except:
            pass
        try:
            share_whatsapp = html.find('a', {'title': 'share on whatsapp'})
            titles_list.append(self.clean_title_IndiaToday(share_whatsapp['data-text']))
        except:
            pass
        try:
            span_content_name = html.find('span', {'class': 'content_name'})
            titles_list.append(self.clean_title_IndiaToday(span_content_name.text))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_OneIndia(self, html):
        titles_list = []
        try:
            title = html.find('title')
            titles_list.append(self.clean_title_OneIndia(title.text))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title_OneIndia(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title_OneIndia(twitter_title['content']))
        except:
            pass
        try:
            meta_headline = html.find('meta', {'name': 'headline', 'itemprop': 'headline'})
            titles_list.append(self.clean_title_OneIndia(meta_headline['content']))
        except:
            pass
        try:
            head_data_altimg = html.find('head', {'data-altimg': True})
            titles_list.append(self.clean_title_OneIndia(head_data_altimg['data-altimg']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "WebPage" and data["name"]:
                        titles_list.append(self.clean_title_OneIndia(data["name"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data["headline"]:
                        titles_list.append(self.clean_title_OneIndia(data["headline"]))
                except:
                    pass
        except:
            pass
        try:
            h1_heading = html.find('h1', {'class': 'heading'})
            titles_list.append(self.clean_title_OneIndia(h1_heading.text))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_HinduBusinessLine(self, html):
        titles_list = []
        try:
            title = html.find('title')
            titles_list.append(self.clean_title_HinduBusinessLine(title.text))
        except:
            pass
        try:
            meta_title = html.find('meta', {'name': 'title'})
            titles_list.append(self.clean_title_HinduBusinessLine(meta_title['content']))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title_HinduBusinessLine(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title_HinduBusinessLine(twitter_title['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data["headline"]:
                        titles_list.append(self.clean_title_HinduBusinessLine(data["headline"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "WebPage" and data["name"]:
                        titles_list.append(self.clean_title_HinduBusinessLine(data["name"]))
                except:
                    pass
        except:
            pass
        try:
            h1_title = html.find('h1', {'class': 'tp-title-inf'})
            titles_list.append(self.clean_title_HinduBusinessLine(h1_title.text))
        except:
            pass
        try:
            ul_data_categories = html.find_all('ul', {'data-category': 'social-shares'})
            for ul in ul_data_categories:
                titles_list.append(self.clean_title_HinduBusinessLine(ul['data-share-text']))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_ScrollNews(self, html):
        titles_list = []
        try:
            title = html.find('title')
            titles_list.append(self.clean_title_ScrollNews(title.text))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title_ScrollNews(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title_ScrollNews(twitter_title['content']))
        except:
            pass
        try:
            dcterms_title = html.find('meta', {'name': 'dcterms.title'})
            titles_list.append(self.clean_title_ScrollNews(dcterms_title['content']))
        except:
            pass
        try:
            article_title = html.find('article', {'data-title': True})
            titles_list.append(self.clean_title_ScrollNews(article_title['data-title']))
        except:
            pass
        try:
            li_title = html.find('li', {'data-article-title': True})
            titles_list.append(self.clean_title_ScrollNews(li_title['data-article-title']))
        except:
            pass
        try:
            button_title = html.find('button', {'data-article-title': True})
            titles_list.append(self.clean_title_ScrollNews(button_title['data-article-title']))
        except:
            pass
        try:
            header = html.find('header')
            titles_list.append(self.clean_title_ScrollNews(header.find_next('h1').text))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data['headline']:
                        titles_list.append(self.clean_title_ScrollNews(data['headline']))
                except:
                    pass
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_CNBC(self, html):
        titles_list = []
        try:
            title = html.find('title', {'itemprop': 'name'})
            titles_list.append(self.clean_title_ScrollNews(title.text))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title_ScrollNews(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title_ScrollNews(twitter_title['content']))
        except:
            pass
        try:
            h1_title = html.find('h1', {'class': 'ArticleHeader-headline'})
            titles_list.append(self.clean_title_ScrollNews(h1_title.text))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data['headline']:
                        titles_list.append(self.clean_title_ScrollNews(data["headline"]))
                except:
                    pass
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_TheIndianExpress(self, html):
        titles_list = []
        try:
            title = html.find('title')
            title = title.split("|")[0].strip()
            titles_list.append(self.clean_title_TheIndianExpress(title.text))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title_TheIndianExpress(twitter_title['content']))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title_TheIndianExpress(og_title['content']))
        except:
            pass
        try:
            h1_title = html.find('h1')
            titles_list.append(self.clean_title_TheIndianExpress(h1_title.text))
        except:
            pass
        try:
            h1_headline = html.find('h1', {'itemprop': 'headline'})
            titles_list.append(self.clean_title_TheIndianExpress(h1_headline.text))
        except:
            pass
        try:
            meta_title = html.find('meta', {'itemprop': 'name'})
            titles_list.append(self.clean_title_TheIndianExpress(meta_title['content']))
        except:
            pass
        try:
            meta_headline = html.find('meta', {'itemprop': 'headline'})
            titles_list.append(self.clean_title_TheIndianExpress(meta_headline['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["headline"]:
                        titles_list.append(self.clean_title_TheIndianExpress(data["headline"]))
                except:
                    pass
        except:
            pass

        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_ThePioneer(self, html):
        titles_list = []
        try:
            title = html.find('title')
            titles_list.append(self.text_cleaning(title.text))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.text_cleaning(og_title['content']))
        except:
            pass
        try:
            meta_keywords = html.find('meta', {'name': 'keywords'})
            titles_list.append(self.text_cleaning(meta_keywords['content']))
        except:
            pass
        try:
            h2_headline = html.find('h2', {'itemprop': 'headline'})
            titles_list.append(self.text_cleaning(h2_headline.text))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_FinancialExpress(self, html):
        titles_list = []
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.text_cleaning(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.text_cleaning(twitter_title['content']))
        except:
            pass
        try:
            title = html.find('title')
            titles_list.append(self.text_cleaning(title.text))
        except:
            pass
        try:
            headline_itemprop = html.find('meta', {'itemprop': 'headline'})
            titles_list.append(self.text_cleaning(headline_itemprop['content']))
        except:
            pass
        try:
            h1_headline = html.find('h1', {'itemprop': 'headline'})
            titles_list.append(self.text_cleaning(h1_headline.text))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_EuroNews(self, html):
        titles_list = []
        try:
            title = html.find('title')
            titles_list.append(self.clean_title_EuroNews(title.text))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title_EuroNews(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title_EuroNews(twitter_title['content']))
        except:
            pass
        try:
            script = html.find('script', {'type': 'application/ld+json'})
            try:
                data = json.loads(script.string, strict=False)
                titles_list.append(self.clean_title_EuroNews(data['@graph'][0]['headline']))
            except:
                pass
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_ESPNCricInfo(self, html):
        titles_list = []
        try:
            title = html.find('title')
            titles_list.append(self.clean_title_ESPNCricInfo(title.text))
        except:
            pass
        try:
            meta_title = html.find('meta', {'name': 'title'})
            titles_list.append(self.clean_title_ESPNCricInfo(meta_title['content']))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title_ESPNCricInfo(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.clean_title_ESPNCricInfo(twitter_title['content']))
        except:
            pass
        try:
            h1 = html.find('h1')
            titles_list.append(self.clean_title_ESPNCricInfo(h1.text))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'NewsArticle' and data['headline']:
                        titles_list.append(self.clean_title_ESPNCricInfo(data['headline']))
                except:
                    pass
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_NYTimes(self, html):
        titles_list = []
        try:
            title = html.find('title')
            titles_list.append(self.clean_title_NYTimes(title.text))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title_NYTimes(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'property': 'twitter:title'})
            titles_list.append(self.clean_title_NYTimes(twitter_title['content']))
        except:
            pass
        try:
            link_title = html.find('link', {'data-rh': 'true', 'title': True})
            titles_list.append(self.clean_title_NYTimes(link_title['title']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'NewsArticle' and data['headline']:
                        titles_list.append(self.clean_title_NYTimes(data['headline']))
                except:
                    pass
        except:
            pass
        try:
            h1_title = html.find('h1', {'data-test-id': 'headline'})
            titles_list.append(self.clean_title_NYTimes(h1_title.text))
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_BusinessStandard(self, html):
        titles_list = []
        try:
            title = html.find('title')
            titles_list.append(self.clean_title_BusinessStandard(title.text))
        except:
            pass
        try:
            og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.clean_title_BusinessStandard(og_title['content']))
        except:
            pass
        try:
            twitter_title = html.find('meta', {'property':'twitter:title'})
            titles_list.append(self.clean_title_BusinessStandard(twitter_title['content']))
        except:
            pass
        try:
            meta_title = html.find('meta', {'itemprop': 'name'})
            titles_list.append(self.clean_title_BusinessStandard(meta_title['content']))
        except:
            pass
        try:
            h1_headline = html.find('h1', {'class': 'headline'})
            titles_list.append(self.clean_title_BusinessStandard(h1_headline.text))
        except:
            pass
        try:
            data_title = html.find('div', {'class': "addthis_sharing_toolbox"})
            titles_list.append(self.clean_title_BusinessStandard(data_title['data-title']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data[0]['@type'] == 'NewsArticle':
                        titles_list.append(clean_title(data[0]['headline']))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'WebPage':
                        titles_list.append(clean_title(data['name']))
                except:
                    pass
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title
