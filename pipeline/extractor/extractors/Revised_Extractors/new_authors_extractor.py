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
        html = BeautifulSoup(self.html_item.body, 'html5lib')
        authors = " "
        try:
            authors = self.authors_mega(html)
        except Exception as e:
            logging.exception(e)
        return authors

    def text_cleaning(self, text):
        text = text.encode("ascii", "ignore").decode("ascii", "ignore")
        text = re.sub(r'[^\x00-\x7F]', '', text)
        text = text.replace("\n", "")
        text = text.replace("\'", "'")
        text = text.replace("\\\"", '\"')
        text = text.replace("&amp;", "&")
        text = text.replace("&quot;", '\"')
        text = text.replace("&nbsp;", ' ')
        text = text.replace("By ", "")
        text = text.strip().lstrip().rstrip()
        return text

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def authors_mega(self, html):
        authors_list = []
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["author"] and type(data["author"]) is not list:
                        authors_list.append(self.text_cleaning(data['author']['name']))
                    elif data["author"] and type(data["author"]) is list:
                        try:
                            authors_list.append(self.text_cleaning(data['author'][0]['name']))
                        except:
                            pass
                        try:
                            authors_list.append(self.text_cleaning(data["author"][0]))
                        except:
                            pass
                        break
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "Article" or data["@type"] == "WebPage":
                        if type(data["author"]) is list:
                            authors_list.append(self.text_cleaning(data["author"][0]["name"]))
                        elif type(data["author"]) is not list:
                            authors_list.append(self.text_cleaning(data["author"]["name"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "VideoObject":
                        if type(data["publisher"]) is list:
                            authors_list.append(self.text_cleaning(data["publisher"][0]["name"]))
                        elif type(data["publisher"]) is not list:
                            authors_list.append(self.text_cleaning(data["publisher"]["name"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle":
                        if type(data["author"]) is list:
                            authors_list.append(self.text_cleaning(data["author"][0]))
                        elif type(data["author"]) is not list:
                            authors_list.append(self.text_cleaning(data["author"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["creator"]:
                        if type(data["creator"]) is list:
                            authors_list.append(self.text_cleaning(data["creator"][0]))
                        if type(data["creator"]) is not list:
                            authors_list.append(self.text_cleaning(data["creator"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["publisher"]["@type"] == "Organization":
                        authors_list.append(self.text_cleaning(data["publisher"]["name"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["author"]:
                        authors_list.append(self.text_cleaning(data["author"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data[0]['@type'] == 'NewsArticle' and data[0]['author']:
                        authors_list.append(self.text_cleaning(data[0]['author']))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if (data["@type"] == "Person" or data["@type"] == "Organization") and data["name"]:
                        authors_list.append(self.text_cleaning(data["name"]))
                        if type(data["name"]) is list:
                            authors_list.append(self.text_cleaning(data["name"][0]))
                except:
                    pass
                try:
                    if "author" in script.string:
                        authors_list.append(self.text_cleaning(script.string.split("author\": {")[1].split("name\": \"")[1].split("\"")[0]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    authors_list.append(self.text_cleaning(data['@graph'][0]['author']['name']))
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
                    authors_list.append(self.text_cleaning(data["article_author"]))
                except:
                    pass
        except:
            pass
        try:
            span_class_ag = html.find('span', {'class': 'ag'})
            if span_class_ag.img:
                if span_class_ag.img.get('title') not in authors_list:
                    authors_list.append(span_class_ag.img.get('title'))
            else:
                if span_class_ag.text not in authors_list:
                    authors_list.append(span_class_ag.text)
        except:
            pass
        try:
            span_itemprop_author = html.find('span', {'itemprop': 'author'})
            authors_list.append(self.text_cleaning(span_itemprop_author.text))
            for author in span_itemprop_author.children:
                authors_list.append(self.text_cleaning(author.text))
            try:
                for author in span_itemprop_author:
                    for author_meta in author.find_all('meta', {'itemprop': 'name'}):
                        authors_list.append(self.text_cleaning(author_meta['content']))
            except:
                pass
            try:
                for author in span_itemprop_author.find_all('a', {'rel': 'author'}):
                    authors_list.append(self.text_cleaning(author.text))
            except:
                pass
        except:
            pass
        try:
            span_itemprop_authors = html.find_all('span', {'itemprop': 'author'})
            for span_author in span_itemprop_authors:
                authors_list.append(self.text_cleaning(span_author.text))
                try:
                    for element in span_author:
                        authors_list.append(self.text_cleaning(element.text))
                except:
                    pass
        except:
            pass
        try:
            span_class_author = html.find('span', {'class': 'author'})
            authors_list.append(self.text_cleaning(span_class_author.text))
        except:
            pass
        try:
            link_class_sanspro = html.find_all('a', {'class': 'sanspro-reg article-author__name'})
            for author in link_class_sanspro:
                authors_list.append(self.text_cleaning(author.text))
        except:
            pass
        try:
            span_class_sanspro = html.find_all('span', {'class': 'sanspro-reg article-author__name'})
            for author in span_class_sanspro:
                authors_list.append(self.text_cleaning(author.text))
        except:
            pass
        try:
            span_class_pst_bylnk = html.find_all('span', {'class': 'pst-by_lnk'})
            for span in span_class_pst_bylnk:
                if span.find('span', {'itemprop': 'name'}):
                    authors_list.append(self.text_cleaning(span.text))
        except:
            pass
        try:
            div_class_td_post_author_name = html.find('div', {'class': 'td-post-author-name'})
            authors_list.append(self.text_cleaning(div_class_td_post_author_name.text))
        except:
            pass
        try:
            meta_property_article_author_name = html.find('meta', {'property': 'article:author_name'})
            authors_list.append(self.text_cleaning(meta_property_article_author_name['content']))
        except:
            pass
        try:
            meta_property_article_author = html.find('meta', {'property': 'article:author'})
            authors_list.append(self.text_cleaning(meta_property_article_author['content']))
            try:
                authors_list.append(self.text_cleaning(meta_property_article_author['data-author'].split("-")[1]))
            except:
                pass
        except:
            pass
        try:
            meta_name_twitter_creator = html.find('meta', {'name': 'twitter:creator'})
            authors_list.append(self.text_cleaning(meta_name_twitter_creator['content']))
        except:
            pass
        try:
            meta_name_dcterms_creator = html.find('meta', {'name': 'dcterms.creator'})
            authors_list.append(self.text_cleaning(meta_name_dcterms_creator['content']))
        except:
            pass
        try:
            meta_name_article_author_name = html.find('meta', {'name': 'article:author_name'})
            authors_list.append(self.text_cleaning(meta_name_article_author_name['content']))
        except:
            pass
        try:
            meta_name_author = html.find('meta', {'name': 'author'})
            authors_list.append(self.text_cleaning(meta_name_author['content']))
        except:
            pass
        try:
            meta_name_byline = html.find('meta', {'name': 'byl'})
            authors_list.append(self.text_cleaning(meta_name_byline['content']))
        except:
            pass
        try:
            meta_itemprop_author = html.find('meta', {'itemprop': 'author'})
            authors_list.append(self.text_cleaning(meta_itemprop_author['content']))
        except:
            pass
        try:
            div_id_author_byline = html.find('div', {'id': 'author-byline'})
            for link in div_id_author_byline.p.find_all('a'):
                authors_list.append(self.text_cleaning(link.text))
        except:
            pass
        try:
            div_class_gnt_arby = html.find('div', {'class': 'gnt_ar_by'})
            for link in div_class_gnt_arby.find_all('a'):
                authors_list.append(self.text_cleaning(link.text))
        except:
            pass
        try:
            link_class_author = html.find_all('a', {'class': 'author'})
            for author_link in link_class_author:
                authors_list.append(self.text_cleaning(author_link.text))
        except:
            pass
        try:
            div_class_io_author = html.find('div', {'class': 'io-author'})
            authors_list.append(self.text_cleaning(div_class_io_author.text.split("-")[1]))
        except:
            pass
        try:
            div_class_storydate = html.find('div', {'class': 'story-date'})
            for link in div_class_storydate.find_all('a'):
                if 'columnist' in link.get('href'):
                    authors_list.append(self.text_cleaning(link.text))
        except:
            pass
        try:
            div_class_author_clearfix = html.find('div', {'class': 'author-detail clearfix'})
            authors_list.append(self.text_cleaning(div_class_author_clearfix['data-author']))
        except:
            pass
        try:
            div_class_posted_by = html.find('div', {'class': 'posted-by'})
            authors_list.append(self.text_cleaning(div_class_posted_by.text))
        except:
            pass
        try:
            div_class_editor = html.find('div', {'class': 'editor'})
            for link in div_class_editor.find_all('a'):
                authors_list.append(self.text_cleaning(link.text))
        except:
            pass
        try:
            div_class_author = html.find('div', {'class': 'author'})
            authors_list.append(self.text_cleaning(div_class_author.a.text))
        except:
            pass
        try:
            link_class_auth_nmlink = html.find_all('a', {'class': 'auth-nm lnk'})
            for author in link_class_auth_nmlink:
                authors_list.append(self.text_cleaning(author.text))
        except:
            pass
        try:
            article_datacb_authors = html.find('article', {'data-cb-authors': True})
            authors_list.append(self.text_cleaning(article_datacb_authors['data-cb-authors']))
        except:
            pass
        try:
            address = html.find('address')
            for author in address.find_all('a', {'rel': 'author'}):
                authors_list.append(self.text_cleaning(author.text))
        except:
            pass
        try:
            link_class_authorname = html.find_all('a', {'class': "Author-authorName"})
            for author in link_class_authorname:
                authors_list.append(self.text_cleaning(author.text))
        except:
            pass
        try:
            link_id_written_by = html.find('a', {'id': 'written_by1'})
            authors_list.append(self.text_cleaning(link_id_written_by.text))
        except:
            pass
        try:
            span_class_meta_author = html.find('span', {'class': 'c-article-meta__author'})
            authors_list.append(self.text_cleaning(span_class_meta_author.text))
        except:
            pass
        try:
            span_class_last_byline = html.find('span', {'class': 'last-byline'})
            authors_list.append(self.text_cleaning(span_class_last_byline.text))
        except:
            pass
        if len(authors_list) == 1 and authors_list[0] == '' or len(authors_list) == 0:
            authors_list.append(" ")
        authors_list = [author for author in authors_list if author != '']
        authors_list = list(set(authors_list))
        authors_list = ", ".join(authors_list)
        return authors_list
