from .abstract_extractor import AbstractExtractor
from bs4 import BeautifulSoup
import json
import re
from retrying import retry
import logging


class DescriptionExtractor(AbstractExtractor):
    def __init__(self):
        self.name = "description_extractor"

    def _description(self, item):
        self.html_item = item['spider_response']
        self.publisher = item['publisher']
        html = BeautifulSoup(self.html_item.body, 'html5lib')
        description = ""

        try:
            if self.publisher == 'EconomicTimes':
                description = self.description_ET(html)
            if self.publisher == 'TimesofIndia':
                description = self.description_TOI(html)
            if self.publisher == 'DeccanHerald':
                description = self.description_DH(html)
            if self.publisher == 'NDTV':
                description = self.description_NDTV(html)
            if self.publisher == 'Independent':
                description = self.description_Independent(html)
            if self.publisher == 'EveningStandard':
                description = self.description_EveningStandard(html)
            if self.publisher == 'NewYorkPost':
                description = self.description_NewYorkPost(html)
            if self.publisher == 'Express':
                description = self.description_Express(html)
            if self.publisher == 'USAToday':
                description = self.description_USAToday(html)
            if self.publisher == 'DailyMail':
                description = self.description_DailyMail(html)
            if self.publisher == 'IndiaToday':
                description = self.description_IndiaToday(html)
            if self.publisher == 'OneIndia':
                description = self.description_OneIndia(html)
            if self.publisher == 'HinduBusinessLine':
                description = self.description_HinduBusinessLine(html)
            if self.publisher == 'ScrollNews':
                description = self.description_ScrollNews(html)
            if self.publisher == 'CNBCWorld':
                description = self.description_CNBC(html)
            if self.publisher == 'TheIndianExpress':
                description = self.description_TheIndianExpress(html)
            if self.publisher == 'ThePioneer':
                description = self.description_ThePioneer(html)
            if self.publisher == 'TheFinancialExpress':
                description = self.description_FinancialExpress(html)
            if self.publisher == 'EuroNews':
                description = self.description_EuroNews(html)
            if self.publisher == 'ESPNCricInfo':
                description = self.description_ESPNCricInfo(html)
            if self.publisher == 'NYTimes':
                description = self.description_NYTimes(html)
            if self.publisher == 'BusinessStandard':
                description = self.description_BusinessStandard(html)
        except:
            pass
        return description


    def clean_text(self, desc):
        desc = desc.encode("ascii", "ignore").decode("ascii", "ignore")
        desc = re.sub(r'[^\x00-\x7F]', '', desc)
        desc = desc.replace("\n", "")
        desc = desc.replace("\'", "'")
        desc = desc.replace("\\\"", '\"')
        desc = desc.replace("&amp;", "&")
        desc = desc.replace("&quot;", '\"')
        desc = desc.strip().lstrip().rstrip()
        desc_text = ' '.join(desc.split())
        return desc_text


    def remove_html_tags(self, text):
        clean = re.compile('<.*?>')
        whitespace = re.compile('&nbsp;')
        text = re.sub(whitespace, ' ', text)
        return re.sub(clean, '', text)


    def return_articlebody(self, html):
        scripts = html.find_all('script', {'type': 'application/ld+json'})
        scripts = [script for script in scripts if script is not None]
        for script in scripts:
            try:
                data = json.loads(script.string, strict=False)
                if data["@type"] == "NewsArticle" and data["articleBody"]:
                    return self.clean_text(self.remove_html_tags(data["articleBody"]))
            except:
                pass
        return None


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_ET(self, html):
        description_list = []
        try:
            description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'itemprop': 'description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('h2', {'class': 'summary'})
            description_list.append(self.clean_text(description.text))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["description"]:
                        description_list.append(self.clean_text(data['description']))
                except:
                    pass
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_TOI(self, html):
        description_list = []
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["description"]:
                        description_list.append(self.clean_text(data['description']))
                except:
                    pass
        except:
            pass
        try:
            description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_DH(self, html):
        description_list = []
        try:
            description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'itemprop': 'description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            body = self.return_articlebody(html)
            if body != '' and body is not None:
                return body
            else:
                return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_NDTV(self, html):
        description_list = []
        try:
            description = html.find('meta', {'name': 'description', 'itemprop': 'description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["description"]:
                        description_list.append(self.clean_text(data["description"]))
                except:
                    try:
                        data = json.loads(script.string, strict=False)
                        if data["@type"] == "WebPage" and data["description"]:
                            description_list.append(self.clean_text(data["description"]))
                    except:
                        pass
        except:
            pass
        try:
            description = html.find('h2', {'class': 'sp-descp'})
            description_list.append(self.clean_text(description.text))
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_Independent(self, html):
        description_list = []
        try:
            description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["description"]:
                        description_list.append(self.clean_text(data["description"]))
                except:
                    pass
        except:
            pass
        try:
            header = html.find('header', {'id': 'articleHeader'})
            h2 = header.find('h2')
            description_list.append(self.clean_text(h2.text))
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_EveningStandard(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'property': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["description"]:
                        description_list.append(self.clean_text(data["description"]))
                except:
                    pass
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_NewYorkPost(self, html):
        description_list = []
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_Express(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'property': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            h3 = html.find('h3')
            description_list.append(self.clean_text(h3.text))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["description"]:
                        description_list.append(self.clean_text(data["description"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle":
                        if type(data["video"]) is list:
                            description_list.append(self.clean_text(data["video"][0]["description"]))
                        elif type(data["video"]) is not list:
                            description_list.append(self.clean_text(data["video"]["description"]))
                except:
                    pass
        except:
            pass
        try:
            div_text_description = html.find('div', {'class': 'text-description'})
            description_list.append(self.clean_text(div_text_description.text))
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_USAToday(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["description"]:
                        description_list.append(self.clean_text(data["description"]))
                except:
                    pass
        except:
            pass
        try:
            div_share = html.find('div', {'data-ss-d': True})
            description_list.append(self.clean_text(div_share['data-ss-d']))
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_DailyMail(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'property': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
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
                        description_list.append(self.clean_text(data["description"]))
                except:
                    pass
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_IndiaToday(self, html):
        description_list = []
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
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
                    if data["@type"] == "WebPage" and data["description"]:
                        description_list(self.clean_text(data["description"]))
                except:
                    pass
        except:
            pass
        try:
            story_kicker_div = html.find('div', {'class': 'story-kicker'})
            description_list.append(self.clean_text(story_kicker_div.text))
        except:
            pass
        try:
            itemprop_description = html.find('meta', {'itemprop': 'description'})
            description_list.append(self.clean_text(itemprop_description['content']))
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_OneIndia(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description', 'itemprop': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
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
                    if data["@type"] == "WebPage" or data["@type"] == "NewsArticle":
                        if data["description"]:
                            description_list.append(self.clean_text(data["description"]))
                except:
                    pass
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_HinduBusinessLine(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
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
                    if data["@type"] == "NewsArticle" and data["description"]:
                        description_list.append(self.clean_text(data["description"]))
                except:
                    pass
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_ScrollNews(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            dcterms_description = html.find('meta', {'name': 'dcterms.description'})
            description_list.append(self.clean_text(dcterms_description['content']))
        except:
            pass
        try:
            header = html.find('header')
            description_list.append(self.clean_text(header.find_next('h2').text))
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
                    if data["@type"] == "NewsArticle" and data['description']:
                        description_list.append(self.clean_text(data['description']))
                except:
                    pass
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_CNBC(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'itemprop': 'description', 'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
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
                    if data["@type"] == "NewsArticle" and data['description']:
                        description_list.append(self.clean_text(data['description']))
                except:
                    pass
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_TheIndianExpress(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            itemprop_description = html.find('meta', {'itemprop': 'description'})
            description_list.append(self.clean_text(itemprop_description['content']))
        except:
            pass
        try:
            h2_description = html.find('h2', {'itemprop': 'description'})
            description_list.append(self.clean_text(h2_description.text))
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
                    if data["@type"] == "NewsArticle" and data['description']:
                        description_list.append(self.clean_text(data['description']))
                except:
                    pass
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_ThePioneer(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_FinancialExpress(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_EuroNews(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            script = html.find('script', {'type': 'application/ld+json'})
            try:
                data = json.loads(script.string, strict=False)
                description_list.append(self.clean_text(data['@graph'][0]['description']))
            except:
                pass
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_ESPNCricInfo(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            article_summary = html.find('p', {'class': 'article-summary'})
            description_list.append(self.clean_text(article_summary.text))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'NewsArticle' and data['description']:
                        description_list.append(self.clean_text(data['description']))
                except:
                    pass
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_NYTimes(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'property': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'NewsArticle' and data['description']:
                        description_list.append(self.clean_text(data['description']))
                except:
                    pass
        except:
            pass
        try:
            article_summary = html.find('p', {'id': 'article-summary'})
            description_list.append(self.clean_text(article_summary.text))
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_BusinessStandard(self, html):
        description_list = []
        try:
            meta_description = html.find('meta', {'name': 'description'})
            description_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'property': 'twitter:description'})
            description_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            itemprop_description = html.find('meta', {'itemprop': 'description'})
            description_list.append(self.clean_text(itemprop_description['content']))
        except:
            pass
        try:
            h2_description = html.find('h2', {'class': 'alternativeHeadline'})
            description_list.append(self.clean_text(h2_description.text))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'WebPage' and data['description']:
                        description_list.append(self.clean_text(data['description']))
                except:
                    pass
        except:
            pass
        description_list = [desc for desc in description_list if desc != '']
        if len(description_list) == 0:
            return " "
        best_desc = max(description_list, key=len)
        return best_desc
