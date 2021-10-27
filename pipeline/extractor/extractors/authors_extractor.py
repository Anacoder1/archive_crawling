from .abstract_extractor import AbstractExtractor
from bs4 import BeautifulSoup
import json
import re
from retrying import retry


class AuthorsExtractor(AbstractExtractor):
    def __init__(self):
        self.name = "authors_extractor"

    def _author(self, item):
        self.html_item = item['spider_response']
        self.publisher = item['publisher']
        html = BeautifulSoup(self.html_item.body, 'html5lib')
        authors = None

        try:
            if self.publisher == 'EconomicTimes':
                authors = self.authors_ET(html)
            if self.publisher == 'TimesofIndia':
                authors = self.authors_TOI(html)
            if self.publisher == 'DeccanHerald':
                authors = self.authors_DH(html)
            if self.publisher == 'NDTV':
                authors = self.authors_NDTV(html)
            if self.publisher == 'Independent':
                authors = self.authors_Independent(html)
            if self.publisher == 'EveningStandard':
                authors = self.authors_EveningStandard(html)
            if self.publisher == 'NewYorkPost':
                authors = self.authors_NewYorkPost(html)
            if self.publisher == 'Express':
                authors = self.authors_Express(html)
            if self.publisher == 'USAToday':
                authors = self.authors_USAToday(html)
            if self.publisher == 'DailyMail':
                authors = self.authors_DailyMail(html)
            if self.publisher == 'IndiaToday':
                authors = self.authors_IndiaToday(html)
            if self.publisher == 'OneIndia':
                authors = self.authors_OneIndia(html)
            if self.publisher == 'HinduBusinessLine':
                authors = self.authors_HinduBusinessLine(html)
            if self.publisher == 'ScrollNews':
                authors = self.authors_ScrollNews(html)
            if self.publisher == 'CNBCWorld':
                authors = self.authors_CNBC(html)
            if self.publisher == 'TheIndianExpress':
                authors = self.authors_TheIndianExpress(html)
            if self.publisher == 'ThePioneer':
                authors = self.authors_ThePioneer(html)
            if self.publisher == 'TheFinancialExpress':
                authors = self.authors_FinancialExpress(html)
            if self.publisher == 'EuroNews':
                authors = self.authors_EuroNews(html)
            if self.publisher == 'ESPNCricInfo':
                authors = self.authors_ESPNCricInfo(html)
            if self.publisher == 'NYTimes':
                authors = self.authors_NYTimes(html)
            if self.publisher == 'BusinessStandard':
                authors = self.authors_BusinessStandard(html)
        except:
            pass
        return authors


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

    def clean_authors(self, text):
        text = text.replace(",", "")
        return self.text_cleaning(text)

    def clean_authors_normal(self, text):
        return self.text_cleaning(text)

    def clean_authors_DailyMail(self, text):
        text = text.replace("By ", "")
        return self.text_cleaning(text)

    def clean_authors_OneIndia(self, text):
        text = text.replace("By ", "")
        text = text.replace(",", "")
        return self.text_cleaning(text)


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_ET(self, html):
        authors_ET = []
        try:
            for script in html.find_all('script', {'type': 'application/ld+json'}):
                try:
                    data = json.loads(script.string, strict=False)
                    if data["author"] and type(data["author"]) is not list:
                        authors_ET.append(data['author']['name'])
                    elif data["author"] and type(data["author"]) is list:
                        authors_ET.append(data['author'][0]['name'])
                        break
                except:
                    try:
                        if "author" in script.string:
                            authors_ET.append(script.string.split("author\": {")[1].split("name\": \"")[1].split("\"")[0])
                    except:
                        pass
            try:
                ag = html.find('span', {'class': 'ag'})
                if ag.img:
                    if ag.img.get('title') not in authors_ET:
                        authors_ET.append(ag.img.get('title'))
                else:
                    if ag.text not in authors_ET:
                        authors_ET.append(ag.text)
            except:
                pass
            if len(authors_ET) == 1 and authors_ET[0] == '':
                authors_ET.append("Economic Times")
            authors_ET = [author for author in authors_ET if author != '']
        except:
            authors_ET.append(" ")
        authors_ET = ", ".join(authors_ET)
        return authors_ET


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_TOI(self, html):
        authors_TOI = []
        try:
            for script in html.find_all('script', {'type': 'application/ld+json'}):
                try:
                    data = json.loads(script.string, strict=False)
                    if data["author"] and type(data["author"]) is not list:
                        authors_TOI.append(data['author']['name'])
                    elif data["author"] and type(data["author"]) is list:
                        authors_TOI.append(data['author'][0]['name'])
                        break
                except:
                    pass
            try:
                author_span = html.find('span', {'itemprop': 'author'})
                for author in author_span.children:
                    authors_TOI.append(author.text)
            except:
                pass
            if len(authors_TOI) == 0 and authors_TOI[0] == '':
                authors_TOI.append("The Times of India")
            authors_TOI = [author for author in authors_TOI if author != '']
        except:
            authors_TOI.append(" ")
        authors_TOI = ", ".join(authors_TOI)
        return authors_TOI


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_DH(self, html):
        authors_DH = []
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["author"]:
                        authors_DH.append(data["author"])
                except:
                    pass
        except:
            pass
        try:
            author_names = html.find_all('a', {'class': 'sanspro-reg article-author__name'})
            for author in author_names:
                author_text = self.clean_authors(author.text)
                if author_text not in authors_DH:
                    authors_DH.append(author_text)
        except:
            pass
        if len(authors_DH) == 1 and authors_DH[0] == '':
            authors_DH.append(" ")
        authors_DH = [author for author in authors_DH if author != '']
        authors_DH = ", ".join(authors_DH)
        return authors_DH


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_NDTV(self, html):
        authors_NDTV = []
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["author"]:
                        if data["author"]["name"] != '':
                            authors_NDTV.append(data["author"]["name"].strip())
                            break
                        elif data["author"]["name"] == '' and data["publisher"]["@type"] == "Organization":
                            authors_NDTV.append(data["publisher"]["name"].strip())
                            break
                except:
                    pass
        except:
            pass
        try:
            author_spans = html.find_all('span', {'itemprop': 'author'})
            for author in author_spans:
                authors_NDTV.append(author.text.strip())
            try:
                for author in author_spans:
                    for author_meta in author.find_all('meta', {'itemprop': 'name'}):
                        if author_meta['content'].strip() not in authors_NDTV:
                            authors_NDTV.append(author_meta['content'].strip())
            except:
                pass
        except:
            pass
        try:
            span_authorname = html.find_all('span', {'class': 'pst-by_lnk'})
            for span in span_authorname:
                if span.find('span', {'itemprop': 'name'}):
                    authors_NDTV.append(span.text.strip())
        except:
            pass
        try:
            div_author = html.find('div', {'class': 'td-post-author-name'})
            authors_NDTV.append(div_author.text.strip())
        except:
            pass
        if len(authors_NDTV) == 1 and authors_NDTV[0] == '':
            authors_NDTV.append(" ")
        authors_NDTV = [author for author in authors_NDTV if author != '']
        authors_NDTV = list(set(authors_NDTV))
        authors_NDTV = ", ".join(authors_NDTV)
        return authors_NDTV


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_Independent(self, html):
        authors_Independent = []
        try:
            meta_author = html.find('meta', {'property': 'article:author_name'})
            authors_Independent.append(self.clean_authors_normal(meta_author['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle":
                        if type(data["author"]) is not list:
                            authors_Independent.append(self.clean_authors_normal(data["author"]["name"]))
                        if type(data["author"]) is list:
                            authors_Independent.append(self.clean_authors_normal(data["author"][0]["name"]))
                except:
                    pass
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    authors_Independent.append(self.clean_authors_normal(data["article_author"]))
                except:
                    pass
        except:
            pass
        if len(authors_Independent) == 1 and authors_Independent[0] == '':
            authors_Independent.append(" ")
        authors_Independent = [author for author in authors_Independent if author != '']
        authors_Independent = list(set(authors_Independent))
        authors_Independent = ", ".join(authors_Independent)
        return authors_Independent


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_EveningStandard(self, html):
        authors_EveningStandard = []
        try:
            article_author = html.find('meta', {'property': 'article:author_name'})
            authors_EveningStandard.append(self.clean_authors_normal(article_author['content']))
        except:
            pass
        try:
            article_author_name = html.find('meta', {'name': 'article:author_name'})
            authors_EveningStandard.append(self.clean_authors_normal(article_author_name['content']))
        except:
            pass
        try:
            meta_author = html.find('meta', {'name': 'author'})
            authors_EveningStandard.append(self.clean_authors_normal(meta_author['content']))
        except:
            pass
        try:
            scripts_one = html.find_all('script', {'type': 'application/ld+json'})
            scripts_one = [script for script in scripts_one if script is not None]
            for script in scripts_one:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["author"]:
                        authors_EveningStandard.append(self.clean_authors_normal(data["author"]["name"]))
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
                    authors_EveningStandard.append(self.clean_authors_normal(data["article_author"]))
                except:
                    pass
        except:
            pass
        if len(authors_EveningStandard) == 1 and authors_EveningStandard[0] == '':
            authors_EveningStandard.append(" ")
        authors_EveningStandard = [author for author in authors_EveningStandard if author != '']
        authors_EveningStandard = list(set(authors_EveningStandard))
        authors_EveningStandard = ", ".join(authors_EveningStandard)
        return authors_EveningStandard


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_NewYorkPost(self, html):
        authors_NewYorkPost = []
        try:
            div_author = html.find('div', {'id': 'author-byline'})
            for link in div_author.p.find_all('a'):
                authors_NewYorkPost.append(link.text.strip())
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and type(data["author"]) is list:
                        authors_NewYorkPost.append(data["author"][0]["name"])
                    elif data["@type"] == "NewsArticle" and type(data["author"]) is not list:
                        authors_NewYorkPost.append(data["author"]["name"])
                except:
                    pass
        except:
            pass
        if len(authors_NewYorkPost) == 1 and authors_NewYorkPost[0] == '':
            authors_NewYorkPost.append(" ")
        authors_NewYorkPost = [author for author in authors_NewYorkPost if author != '']
        authors_NewYorkPost = list(set(authors_NewYorkPost))
        authors_NewYorkPost = ", ".join(authors_NewYorkPost)
        return authors_NewYorkPost


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_Express(self, html):
        authors_Express = []
        try:
            meta_author = html.find('meta', {'name': 'author'})
            authors_Express.append(self.clean_authors_normal(meta_author['content']))
        except:
            pass
        try:
            meta_itemprop_author = html.find('meta', {'itemprop': 'author'})
            authors_Express.append(self.clean_authors_normal(meta_itemprop_author['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle":
                        if type(data["author"]) is list:
                            authors_Express.append(self.clean_authors_normal(data["author"][0]))
                        elif type(data["author"]) is not list:
                            authors_Express.append(self.clean_authors_normal(data["author"]))
                except:
                    pass
        except:
            pass
        try:
            span_authors = html.find_all('span', {'itemprop': 'author'})
            for span_author in span_authors:
                authors_Express.append(self.clean_authors_normal(span_author.text))
        except:
            pass
        if len(authors_Express) == 1 and authors_Express[0] == '':
            authors_Express.append(" ")
        authors_Express = [author for author in authors_Express if author != '']
        authors_Express = list(set(authors_Express))
        authors_Express = ", ".join(authors_Express)
        return authors_Express


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_USAToday(self, html):
        authors_USAToday = []
        try:
            meta_author = html.find('meta', {'property': 'article:author'})
            authors_USAToday.append(meta_author['content'].strip())
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
                        if type(data["author"]) is list:
                            try:
                                authors_USAToday.append(data["author"][0].strip())
                            except:
                                pass
                            try:
                                authors_USAToday.append(data["author"][0]["name"].strip())
                            except:
                                pass
                        if type(data["author"]) is not list:
                            try:
                                authors_USAToday.append(data["author"].strip())
                            except:
                                pass
                            try:
                                authors_USAToday.append(data["author"]["name"].strip())
                            except:
                                pass
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "Article":
                        if type(data["author"]) is list:
                            authors_USAToday.append(data["author"][0]["name"].strip())
                        elif type(data["author"]) is not list:
                            authors_USAToday.append(data["author"]["name"].strip())
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "VideoObject":
                        if type(data["publisher"]) is list:
                            authors_USAToday.append(data["publisher"][0]["name"].strip())
                        elif type(data["publisher"]) is not list:
                            authors_USAToday.append(data["publisher"]["name"].strip())
                except:
                    pass
        except:
            pass
        try:
            div_authors = html.find('div', {'class': 'gnt_ar_by'})
            for link in div_authors.find_all('a'):
                authors_USAToday.append(link.text.strip())
        except:
            pass
        if len(authors_USAToday) == 1 and authors_USAToday[0] == '':
            authors_USAToday.append(" ")
        authors_USAToday = [author for author in authors_USAToday if author != '']
        authors_USAToday = list(set(authors_USAToday))
        authors_USAToday = ", ".join(authors_USAToday)
        return authors_USAToday


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_DailyMail(self, html):
        authors_DailyMail = []
        try:
            meta_author = html.find('meta', {'name': 'author'})
            authors_DailyMail.append(self.clean_authors_DailyMail(meta_author['content']))
        except:
            pass
        try:
            article_author = html.find('meta', {'property': 'article:author'})
            authors_DailyMail.append(self.clean_authors_DailyMail(article_author['content']))
        except:
            pass
        try:
            author_links = html.find_all('a', {'class': 'author'})
            for author_link in author_links:
                authors_DailyMail.append(self.clean_authors_DailyMail(author_link.text))
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
                    if data["@type"] == "NewsArticle" or data["@type"] == "WebPage":
                        if data["author"] and type(data["author"]) is list:
                            authors_DailyMail.append(self.clean_authors_DailyMail(data["author"][0]["name"]))
                        if data["author"] and type(data["author"]) is not list:
                            authors_DailyMail.append(self.clean_authors_DailyMail(data["author"]["name"]))
                except:
                    pass
        except:
            pass
        if len(authors_DailyMail) == 1 and authors_DailyMail[0] == '':
            authors_DailyMail.append(" ")
        authors_DailyMail = [author for author in authors_DailyMail if author != '']
        authors_DailyMail = [author for author in authors_DailyMail if "https://" not in author]
        authors_DailyMail = list(set(authors_DailyMail))
        authors_DailyMail = ", ".join(authors_DailyMail)
        return authors_DailyMail


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_IndiaToday(self, html):
        authors_IndiaToday = []
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "Person" and data["name"]:
                        authors_IndiaToday.append(self.clean_authors_normal(data["name"]))
                except:
                    pass
        except:
            pass
        try:
            span_authors = html.find_all('span', {'itemprop': 'author'})
            for author in span_authors:
                for entity in author:
                    authors_IndiaToday.append(self.clean_authors_normal(entity.text))
        except:
            pass
        if len(authors_IndiaToday) == 1 and authors_IndiaToday[0] == '':
            authors_IndiaToday.append(" ")
        authors_IndiaToday = [author for author in authors_IndiaToday if author != '']
        authors_IndiaToday = list(set(authors_IndiaToday))
        authors_IndiaToday = ", ".join(authors_IndiaToday)
        return authors_IndiaToday


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_OneIndia(self, html):
        authors_OneIndia = []
        try:
            meta_author = html.find('meta', {'property': 'article:author'})
            authors_OneIndia.append(self.clean_authors_OneIndia(meta_author['content']))
            authors_OneIndia.append(self.clean_authors_OneIndia(meta_author['data-author'].split("-")[1]))
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
                    if data["@type"] == "NewsArticle" and data["author"]:
                        if type(data["author"]) is list:
                            authors_OneIndia.append(self.clean_authors_OneIndia(data["author"][0]["name"]))
                        elif type(data["author"]) is not list:
                            authors_OneIndia.append(self.clean_authors_OneIndia(data["author"]["name"]))
                except:
                    pass
        except:
            pass
        try:
            io_author = html.find('div', {'class': 'io-author'})
            authors_OneIndia.append(self.clean_authors_OneIndia(io_author.text.split("-")[1]))
        except:
            pass
        try:
            author_clearfix = html.find('div', {'class': 'author-detail clearfix'})
            authors_OneIndia.append(self.clean_authors_OneIndia(author_clearfix['data-author']))
        except:
            pass
        try:
            author_posted = html.find('div', {'class': 'posted-by'})
            authors_OneIndia.append(self.clean_authors_OneIndia(author_posted.text))
        except:
            pass
        if len(authors_OneIndia) == 1 and authors_OneIndia[0] == '':
            authors_OneIndia.append(" ")
        authors_OneIndia = [author for author in authors_OneIndia if author != '']
        authors_OneIndia = list(set(authors_OneIndia))
        authors_OneIndia = ", ".join(authors_OneIndia)
        return authors_OneIndia


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_HinduBusinessLine(self, html):
        authors_HinduBusinessLine = []
        try:
            meta_author = html.find('meta', {'property': 'article:author'})
            authors_HinduBusinessLine.append(self.clean_authors(meta_author['content']))
        except:
            pass
        try:
            twitter_creator = html.find('meta', {'name': 'twitter:creator'})
            authors_HinduBusinessLine.append(self.clean_authors(twitter_creator['content']))
        except:
            pass
        try:
            link_authors = html.find_all('a', {'class': 'auth-nm lnk'})
            for author in link_authors:
                authors_HinduBusinessLine.append(self.clean_authors(author.text))
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
                    if data["@type"] == "NewsArticle" and data["author"]:
                        if type(data["author"]) is list:
                            authors_HinduBusinessLine.append(data["author"][0]["name"])
                        if type(data["author"]) is not list:
                            authors_HinduBusinessLine.append(data["author"]["name"])
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "VideoObject" and data["publisher"]:
                        if type(data["publisher"]) is list:
                            authors_HinduBusinessLine.append(data["publisher"][0]["name"])
                        if type(data["publisher"]) is not list:
                            authors_HinduBusinessLine.append(data["publisher"]["name"])
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "Organization" and data["name"]:
                        if type(data["name"]) is list:
                            authors_HinduBusinessLine.append(data["name"][0])
                        if type(data["name"]) is not list:
                            authors_HinduBusinessLine.append(data["name"])
                except:
                    pass

        except:
            pass
        if len(authors_HinduBusinessLine) == 1 and authors_HinduBusinessLine[0] == '':
            authors_HinduBusinessLine.append(" ")
        authors_HinduBusinessLine = [author for author in authors_HinduBusinessLine if author != '']
        authors_HinduBusinessLine = list(set(authors_HinduBusinessLine))
        authors_HinduBusinessLine = ", ".join(authors_HinduBusinessLine)
        return authors_HinduBusinessLine


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_ScrollNews(self, html):
        authors_ScrollNews = []
        try:
            meta_author = html.find('meta', {'name': 'author'})
            authors_ScrollNews.append(self.clean_authors_normal(meta_author['content']))
        except:
            pass
        try:
            dcterms_creator = html.find('meta', {'name': 'dcterms.creator'})
            authors_ScrollNews.append(self.clean_authors_normal(dcterms_creator['content']))
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
                    if data["@type"] == "NewsArticle" and data["author"]:
                        if type(data["author"]) is list:
                            authors_ScrollNews.append(self.clean_authors_normal(data["author"][0]["name"]))
                        if type(dtaa["author"]) is not list:
                            authors_ScrollNews.append(self.clean_authors_normal(data["author"]["name"]))
                except:
                    pass
        except:
            pass
        try:
            article_authors = html.find('article', {'data-cb-authors': True})
            authors_ScrollNews.append(self.clean_authors_normal(article_authors['data-cb-authors']))
        except:
            pass
        try:
            address = html.find('address')
            for author in address.find_all('a', {'rel': 'author'}):
                authors_ScrollNews.append(self.clean_authors_normal(author.text))
        except:
            pass
        try:
            span_authors = html.find('span', {'itemprop': 'author'})
            for author in span_authors.find_all('a', {'rel': 'author'}):
                authors_ScrollNews.append(self.clean_authors_normal(author.text))
        except:
            pass
        if len(authors_ScrollNews) == 1 and authors_ScrollNews[0] == '':
            authors_ScrollNews.append("XPTN = ScrollNews")
        authors_ScrollNews = [author for author in authors_ScrollNews if author != '']
        authors_ScrollNews = list(set(authors_ScrollNews))
        authors_ScrollNews = ", ".join(authors_ScrollNews)
        return authors_ScrollNews


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_CNBC(self, html):
        authors_CNBC = []
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data["author"]:
                        if type(data["author"]) is list:
                            authors_CNBC.append(self.clean_authors_normal(data["author"][0]["name"]))
                        if type(data["author"]) is not list:
                            authors_CNBC.append(self.clean_authors_normal(data["author"]["name"]))
                    if data["@type"] == "NewsArticle" and data["creator"]:
                        if type(data["creator"]) is list:
                            authors_CNBC.append(self.clean_authors_normal(data["creator"][0]))
                        if type(data["creator"]) is not list:
                            authors_CNBC.append(self.clean_authors_normal(data["creator"]))
                except:
                    pass
        except:
            pass
        try:
            meta_author = html.find('meta', {'name': 'author'})
            authors_CNBC.append(self.clean_authors_normal(meta_author['content']))
        except:
            pass
        try:
            author_links = html.find_all('a', {'class': "Author-authorName"})
            for author in author_links:
                authors_CNBC.append(self.clean_authors_normal(author.text))
        except:
            pass
        if len(authors_CNBC) == 1 and authors_CNBC[0] == '':
            authors_CNBC.append(" ")
        if len(authors_CNBC) == 0:
            authors_CNBC.append(" ")
        authors_CNBC = [author for author in authors_CNBC if author != '']
        authors_CNBC = list(set(authors_CNBC))
        authors_CNBC = ", ".join(authors_CNBC)
        return authors_CNBC


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_TheIndianExpress(self, html):
        authors_TheIndianExpress = []
        try:
            story_date = html.find('div', {'class': 'story-date'})
            for link in story_date.find_all('a'):
                if 'columnist' in link.get('href'):
                    authors_TheIndianExpress.append(self.clean_authors_normal(link.text))
        except:
            pass
        try:
            editor_link = html.find('div', {'class': 'editor'})
            for link in editor_link.find_all('a'):
                authors_TheIndianExpress.append(self.clean_authors_normal(link.text))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'Person' and data['name']:
                        authors_TheIndianExpress.append(self.clean_authors_normal(data['name']))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'NewsArticle' and data['author']:
                        authors_TheIndianExpress.append(self.clean_authors_normal(data['author']['name']))
                except:
                    pass
        except:
            pass
        if len(authors_TheIndianExpress) == 1 and authors_TheIndianExpress[0] == '' or len(authors_TheIndianExpress) == 0:
            authors_TheIndianExpress.append("TheIndianExpress")
        authors_TheIndianExpress = [author for author in authors_TheIndianExpress if author != '']
        authors_TheIndianExpress = list(set(authors_TheIndianExpress))
        authors_TheIndianExpress = ", ".join(authors_TheIndianExpress)
        return authors_TheIndianExpress


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_ThePioneer(self, html):
        authors_ThePioneer = []
        try:
            article_author = html.find('meta', {'property': 'article:author'})
            authors_ThePioneer.append(self.clean_authors_normal(article_author['content']))
        except:
            pass
        try:
            span_author = html.find('span', {'itemprop': 'author'})
            authors_ThePioneer.append(self.clean_authors_normal(span_author.text))
        except:
            pass
        if len(authors_ThePioneer) == 1 and authors_ThePioneer[0] == '' or len(authors_ThePioneer) == 0:
            authors_ThePioneer.append("ThePioneer")
        authors_ThePioneer = [author for author in authors_ThePioneer if author != '']
        authors_ThePioneer = list(set(authors_ThePioneer))
        authors_ThePioneer = ", ".join(authors_ThePioneer)
        return authors_ThePioneer


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_FinancialExpress(self, html):
        authors_FinancialExpress = []
        try:
            meta_author = html.find('meta', {'itemprop': 'author'})
            authors_FinancialExpress.append(self.clean_authors_normal(meta_author['content']))
        except:
            pass
        try:
            written_by = html.find('a', {'id': 'written_by1'})
            authors_FinancialExpress.append(self.clean_authors_normal(written_by.text))
        except:
            pass
        if len(authors_FinancialExpress) == 1 and authors_FinancialExpress[0] == '' or len(authors_FinancialExpress) == 0:
            authors_FinancialExpress.append("FinancialExpress")
        authors_FinancialExpress = [author for author in authors_FinancialExpress if author != '']
        authors_FinancialExpress = list(set(authors_FinancialExpress))
        authors_FinancialExpress = ", ".join(authors_FinancialExpress)
        return authors_FinancialExpress


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_EuroNews(self, html):
        authors_EuroNews = []
        try:
            meta_author = html.find('meta', {'property': 'article:author'})
            authors_EuroNews.append(self.clean_authors_normal(meta_author['content']))
        except:
            pass
        try:
            script = html.find('script', {'type': 'application/ld+json'})
            try:
                data = json.loads(script.string, strict=False)
                authors_EuroNews.append(self.clean_authors_normal(data['@graph'][0]['author']['name']))
            except:
                pass
        except:
            pass
        try:
            span_author = html.find('span', {'class': 'c-article-meta__author'})
            authors_EuroNews.append(self.clean_authors_normal(span_author.text))
        except:
            pass
        if len(authors_EuroNews) == 1 and authors_EuroNews[0] == '' or len(authors_EuroNews) == 0:
            authors_EuroNews.append("EuroNews")
        authors_EuroNews = [author for author in authors_EuroNews if author != '']
        authors_EuroNews = list(set(authors_EuroNews))
        authors_EuroNews = ", ".join(authors_EuroNews)
        return authors_EuroNews


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_ESPNCricInfo(self, html):
        authors_ESPNCricInfo = []
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'NewsArticle' and data['author']:
                        if type(data['author']) is not list:
                            authors_ESPNCricInfo.append(self.clean_authors_normal(data['author']['name']))
                        else:
                            authors_ESPNCricInfo.append(self.clean_authors_normal(data['author'][0]['name']))
                except:
                    pass
        except:
            pass
        try:
            span_author = html.find('span', {'class': 'author'})
            authors_ESPNCricInfo.append(self.clean_authors_normal(span_author.text))
        except:
            pass
        try:
            div_author = html.find('div', {'class': 'author'})
            authors_ESPNCricInfo.append(self.clean_authors_normal(div_author.a.text))
        except:
            pass
        if len(authors_ESPNCricInfo) == 1 and authors_ESPNCricInfo[0] == '' or len(authors_ESPNCricInfo) == 0:
            authors_ESPNCricInfo.append("ESPNCricInfo")
        authors_ESPNCricInfo = [author for author in authors_ESPNCricInfo if author != '']
        authors_ESPNCricInfo = list(set(authors_ESPNCricInfo))
        authors_ESPNCricInfo = ", ".join(authors_ESPNCricInfo)
        return authors_ESPNCricInfo


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_NYTimes(self, html):
        authors_NYTimes = []
        try:
            meta_byline = html.find('meta', {'name': 'byl'})
            authors_NYTimes.append(self.clean_authors_normal(meta_byline['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'NewsArticle' and data['author']:
                        if type(data['author']) is list:
                            authors_NYTimes.append(self.clean_authors_normal(data['author'][0]['name']))
                        else:
                            authors_NYTimes.append(self.clean_authors_normal(data['author']['name']))
                except:
                    pass
        except:
            pass
        try:
            span_author = html.find('span', {'class': 'last-byline'})
            authors_NYTimes.append(self.clean_authors_normal(span_author.text))
        except:
            pass
        if len(authors_NYTimes) == 1 and authors_NYTimes[0] == '' or len(authors_NYTimes) == 0:
            authors_NYTimes.append("NYTimes")
        authors_NYTimes = [author for author in authors_NYTimes if author != '']
        authors_NYTimes = list(set(authors_NYTimes))
        authors_NYTimes = ", ".join(authors_NYTimes)
        return authors_NYTimes


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_BusinessStandard(self, html):
        authors_BusinessStandard = []
        try:
            meta_author = html.find('meta', {'name': 'author'})
            authors_BusinessStandard.append(self.clean_authors_normal(meta_author['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data[0]['@type'] == 'NewsArticle' and data[0]['author']:
                        authors_BusinessStandard.append(self.clean_authors_normal(data[0]['author']))
                except:
                    pass
        except:
            pass
        if len(authors_BusinessStandard) == 1 and authors_BusinessStandard[0] == '' or len(authors_BusinessStandard) == 0:
            authors_BusinessStandard.append("Business Standard")
        authors_BusinessStandard = [author for author in authors_BusinessStandard if author != '']
        authors_BusinessStandard = list(set(authors_BusinessStandard))
        authors_BusinessStandard = ", ".join(authors_BusinessStandard)
        return authors_BusinessStandard
