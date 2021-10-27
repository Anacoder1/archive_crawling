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
        html = BeautifulSoup(self.html_item.body, 'html5lib')
        title = ""
        try:
            title = self.title_mega(html)
        except Exception as e:
            logging.exception(e)
        return title

    def title_cleaning(self, title):
        title = title.encode("ascii", "ignore").decode("ascii", "ignore")
        title = re.sub(r'[^\x00-\x7F]', '', title)
        title = title.replace("| Deccan Herald", "")
        title = title.replace("- Times of India", "")
        title = title.replace("| The Independent", "")
        title = title.replace("| London Evening Standard", "")
        title = title.replace("| Evening Standard", "")
        title = title.replace("| Express.co.uk", "")
        title = title.replace("| India Today Insight", "")
        title = title.replace("- Oneindia News", "")
        title = re.sub("- The Hindu BusinessLine|- VARIETY|- AGRI-BIZ & COMMODITY|- Today's Paper|- OPINION|- NEWS|- PULSE|- STATES|- MARKETS|- BL INK|- OTHERS|- PORTFOLIO|- AUTOMOBILE|- CLEAN TECH", "", title)
        title = title.replace("- Indian Express", "")
        title = title.replace("| Euronews", "")
        title = title.replace("| ESPNcricinfo.com", "")
        title = title.replace("- The New York Times", "")
        title = title.replace("| Business Standard News", "")
        title = title.replace("\n", "")
        title = title.replace("\'", "'")
        title = title.replace("\\\"", '\"')
        title = title.replace("&amp;", "&")
        title = title.replace("&quot;", '\"')
        title = title.replace("&nbsp;", ' ')
        title = title.replace("\\'", "'")
        title = title.strip().lstrip().rstrip()
        return title

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def title_mega(self, html):
        titles_list = []
        try:
            meta_property_og_title = html.find('meta', {'property': 'og:title'})
            titles_list.append(self.title_cleaning(meta_property_og_title['content']))
        except:
            pass
        try:
            meta_name_twitter_title = html.find('meta', {'name': 'twitter:title'})
            titles_list.append(self.title_cleaning(meta_name_twitter_title['content']))
        except:
            pass
        try:
            meta_name_twitter_text_title = html.find('meta', {'name': 'twitter:text:title'})
            titles_list.append(self.title_cleaning(meta_name_twitter_text_title['content']))
        except:
            pass
        try:
            meta_name_title = html.find('meta', {'name': 'title'})
            titles_list.append(self.title_cleaning(meta_name_title['content']))
        except:
            pass
        try:
            meta_name_dcterms_title = html.find('meta', {'name': 'dcterms.title'})
            titles_list.append(self.title_cleaning(meta_name_dcterms_title['content']))
        except:
            pass
        try:
            meta_name_keywords = html.find('meta', {'name': 'keywords'})
            titles_list.append(self.title_cleaning(meta_name_keywords['content']))
        except:
            pass
        try:
            meta_name_headline = html.find('meta', {'name': 'headline'})
            titles_list.append(self.title_cleaning(meta_name_headline['content']))
        except:
            pass
        try:
            meta_property_twitter_title = html.find('meta', {'property': 'twitter:title'})
            titles_list.append(self.title_cleaning(meta_property_twitter_title['content']))
        except:
            pass
        try:
            meta_itemprop_name = html.find('meta', {'itemprop': 'name'})
            titles_list.append(self.title_cleaning(meta_itemprop_name['content']))
        except:
            pass
        try:
            meta_itemprop_headline = html.find('meta', {'itemprop': 'headline'})
            titles_list.append(self.title_cleaning(meta_itemprop_headline['content']))
        except:
            pass
        try:
            meta_property_headline_short = html.find('meta', {'property': 'headline_short'})
            titles_list.append(self.title_cleaning(meta_property_headline_short['content']))
        except:
            pass
        try:
            meta_property_mol_headline = html.find('meta', {'property': 'mol:headline'})
            titles_list.append(self.title_cleaning(meta_property_mol_headline['content']))
        except:
            pass
        try:
            meta_itemprop_name_headline = html.find('meta', {'name': 'headline', 'itemprop': 'headline'})
            titles_list.append(self.title_cleaning(meta_itemprop_name_headline['content']))
        except:
            pass
        try:
            div_data_arttitle = html.find('div', {'class': 'article_block clearfix'})
            if div_data_arttitle.get('data-arttitle'):
                titles_list.append(self.title_cleaning(div_data_arttitle.get('data-arttitle')))
        except:
            pass
        try:
            div_data_sst = html.find('div', {'data-ss-t': True})
            titles_list.append(self.title_cleaning(div_data_sst['data-ss-t']))
        except:
            pass
        try:
            div_class_sharingtoolbox = html.find('div', {'class': "addthis_sharing_toolbox"})
            titles_list.append(self.title_cleaning(div_class_sharingtoolbox['data-title']))
        except:
            pass
        try:
            h1_title = html.find('h1')
            titles_list.append(self.title_cleaning(h1_title.text))
        except:
            pass
        try:
            h1_id_page_title = html.find('h1', {'id': 'page-title'})
            titles_list.append(self.title_cleaning(h1_id_page_title.text))
        except:
            pass
        try:
            h1_itemprop_headline = html.find('h1', {'itemprop': 'headline'})
            titles_list.append(self.title_cleaning(h1_itemprop_headline.text))
        except:
            pass
        try:
            h1_ar_headline = html.find('h1', {'elementtiming': 'ar-headline'})
            titles_list.append(self.title_cleaning(h1_ar_headline.text))
        except:
            pass
        try:
            h1_class_heading = html.find('h1', {'class': 'heading'})
            titles_list.append(self.title_cleaning(h1_class_heading.text))
        except:
            pass
        try:
            h1_class_headline = html.find('h1', {'class': 'headline'})
            titles_list.append(self.title_cleaning(h1_class_headline.text))
        except:
            pass
        try:
            h1_class_tp_title_inf = html.find('h1', {'class': 'tp-title-inf'})
            titles_list.append(self.title_cleaning(h1_class_tp_title_inf.text))
        except:
            pass
        try:
            h1_class_articleheader = html.find('h1', {'class': 'ArticleHeader-headline'})
            titles_list.append(self.title_cleaning(h1_class_articleheader.text))
        except:
            pass
        try:
            h1_data_test_id_headline = html.find('h1', {'data-test-id': 'headline'})
            titles_list.append(self.title_cleaning(h1_data_test_id_headline.text))
        except:
            pass
        try:
            h2_title = html.find('h2')
            titles_list.append(self.title_cleaning(h2_title.text))
        except:
            pass
        try:
            h2_itemprop_headline = html.find('h2', {'itemprop': 'headline'})
            titles_list.append(self.title_cleaning(h2_itemprop_headline.text))
        except:
            pass
        try:
            title_main = html.find('title')
            titles_list.append(self.title_cleaning(title_main.text))
            titles_list.append(self.title_cleaning(title_main.text.split(" - ")[0]))
            titles_list.append(self.title_cleaning(title_main.text.split("|")[0]))
        except:
            pass
        try:
            title_itemprop_name = html.find('title', {'itemprop': 'name'})
            titles_list.append(self.title_cleaning(title_itemprop_name.text))
        except:
            pass
        try:
            input_name_streamtitle = html.find('input', {'name': 'streamTitle'})
            titles_list.append(self.title_cleaning(input_name_streamtitle["value"]))
        except:
            pass
        try:
            amp_social_share_twitter = html.find('amp-social-share', {'type': 'twitter'})
            titles_list.append(self.title_cleaning(amp_social_share_twitter["data-param-text"]))
        except:
            pass
        try:
            amp_social_share_email = html.find('amp-social-share', {'type': 'email'})
            titles_list.append(self.title_cleaning(amp_social_share_email["data-param-subject"]))
        except:
            pass
        try:
            li_id_sharelinktop = html.find('li', {'id': 'shareLinkTop'})
            titles_list.append(self.title_cleaning(li_id_sharelinktop['data-formatted-headline']))
        except:
            pass
        try:
            li_id_sharelinkbottom = html.find('li', {'id': 'shareLinkBottom'})
            titles_list.append(self.title_cleaning(li_id_sharelinkbottom['data-formatted-headline']))
        except:
            pass
        try:
            div_class_sharearticles = html.find('div', {'class': 'shareArticles'})
            titles_list.append(self.title_cleaning(div_class_sharearticles.h1.text))
        except:
            pass
        try:
            link_share_whatsapp = html.find('a', {'title': 'share on whatsapp'})
            titles_list.append(self.title_cleaning(link_share_whatsapp['data-text']))
        except:
            pass
        try:
            link_data_rh_title = html.find('link', {'data-rh': 'true', 'title': True})
            titles_list.append(self.title_cleaning(link_data_rh_title['title']))
        except:
            pass
        try:
            span_class_content_name = html.find('span', {'class': 'content_name'})
            titles_list.append(self.title_cleaning(span_class_content_name.text))
        except:
            pass
        try:
            head_data_altimg = html.find('head', {'data-altimg': True})
            titles_list.append(self.title_cleaning(head_data_altimg['data-altimg']))
        except:
            pass
        try:
            ul_category_social_shares = html.find_all('ul', {'data-category': 'social-shares'})
            for element in ul_category_social_shares:
                titles_list.append(self.title_cleaning(element['data-share-text']))
        except:
            pass
        try:
            article_data_title = html.find('article', {'data-title': True})
            titles_list.append(self.title_cleaning(article_data_title['data-title']))
        except:
            pass
        try:
            li_data_article_title = html.find('li', {'data-article-title': True})
            titles_list.append(self.title_cleaning(li_data_article_title['data-article-title']))
        except:
            pass
        try:
            button_data_article_title = html.find('button', {'data-article-title': True})
            titles_list.append(self.title_cleaning(button_data_article_title['data-article-title']))
        except:
            pass
        try:
            header_h1_title = html.find('header')
            titles_list.append(self.title_cleaning(header_h1_title.find_next('h1').text))
        except:
            pass
        try:
            script = html.find('script', {'type': 'application/ld+json'})
            try:
                data = json.loads(script.string, strict=False)
                titles_list.append(self.title_cleaning(data['@graph'][0]['headline']))
            except:
                pass
        except:
            pass
        try:
            scripts_one = html.find_all('script', {'type': 'application/ld+json'})
            scripts_one = [script for script in scripts_one if script is not None]
            for script in scripts_one:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if (data["@type"] == "WebPage" and data["name"]) or data["name"]:
                        titles_list.append(self.title_cleaning(data["name"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if (data["@type"] == "NewsArticle" and data["headline"]) or data["headline"]:
                        titles_list.append(self.title_cleaning(data["headline"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle":
                        if type(data["mainEntityOfPage"]) is list:
                            if data["mainEntityOfPage"][0]["name"]:
                                titles_list.append(self.title_cleaning(data["mainEntityOfPage"][0]["name"]))
                        elif type(data["mainEntityOfPage"]) is not list:
                            if data["mainEntityOfPage"]["name"]:
                                titles_list.append(self.title_cleaning(data["mainEntityOfPage"]["name"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "WebPage":
                        if data["headline"]:
                            titles_list.append(self.title_cleaning(data["headline"]))
                        if type(data["mainEntity"]) is list:
                            if data["mainEntity"][0]["name"]:
                                titles_list.append(self.title_cleaning(data["mainEntity"][0]["name"]))
                        elif type(data["mainEntity"]) is not list:
                            if data["mainEntity"]["name"]:
                                titles_list.append(self.title_cleaning(data["mainEntity"]["name"]))
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
                        titles_list.append(self.title_cleaning(data["article_title"]))
                except:
                    pass
        except:
            pass
        titles_list = [title for title in titles_list if title != '']
        if len(titles_list) == 0:
            return " "
        best_title = max(titles_list, key=len)
        return best_title
