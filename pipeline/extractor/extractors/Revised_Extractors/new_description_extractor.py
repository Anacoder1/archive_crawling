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
        html = BeautifulSoup(self.html_item.body, 'html5lib')
        description = " "
        try:
            description = self.description_mega(html)
        except Exception as e:
            logging.exception(e)
        return description

    def text_cleaning(self, text):
        text = text.encode("ascii", "ignore").decode("ascii", "ignore")
        text = re.sub(r'[^\x00-\x7F]', '', text)
        text = text.replace("\n", "")
        text = text.replace("\'", "'")
        text = text.replace("\\\"", '\"')
        text = text.replace("&amp;", "&")
        text = text.replace("&quot;", '\"')
        text = text.replace("&nbsp;", ' ')
        text = text.strip().lstrip().rstrip()
        desc_text = ' '.join(text.split())
        return desc_text

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def description_mega(self, html):
        description_list = []
        try:
            meta_name_description = html.find('meta', {'name': 'description'})
            description_list.append(self.text_cleaning(meta_name_description['content']))
        except:
            pass
        try:
            meta_property_og_description = html.find('meta', {'property': 'og:description'})
            description_list.append(self.text_cleaning(meta_property_og_description['content']))
        except:
            pass
        try:
            meta_name_twitter_description = html.find('meta', {'name': 'twitter:description'})
            description_list.append(self.text_cleaning(meta_name_twitter_description['content']))
        except:
            pass
        try:
            meta_property_twitter_description = html.find('meta', {'property': 'twitter:description'})
            description_list.append(self.text_cleaning(meta_property_twitter_description['content']))
        except:
            pass
        try:
            meta_itemprop_description = html.find('meta', {'itemprop': 'description'})
            description_list.append(self.text_cleaning(meta_itemprop_description['content']))
        except:
            pass
        try:
            meta_name_itemprop_description = html.find('meta', {'name': 'description', 'itemprop': 'description'})
            description_list.append(self.text_cleaning(meta_name_itemprop_description['content']))
        except:
            pass
        try:
            meta_name_dcterms_description = html.find('meta', {'name': 'dcterms.description'})
            description_list.append(self.text_cleaning(meta_name_dcterms_description['content']))
        except:
            pass
        try:
            div_class_text_description = html.find('div', {'class': 'text-description'})
            description_list.append(self.text_cleaning(div_class_text_description.text))
        except:
            pass
        try:
            div_data_ssd = html.find('div', {'data-ss-d': True})
            description_list.append(self.text_cleaning(div_data_ssd['data-ss-d']))
        except:
            pass
        try:
            div_class_story_kicker = html.find('div', {'class': 'story-kicker'})
            description_list.append(self.text_cleaning(div_class_story_kicker.text))
        except:
            pass
        try:
            p_class_article_summary = html.find('p', {'class': 'article-summary'})
            description_list.append(self.text_cleaning(p_class_article_summary.text))
        except:
            pass
        try:
            p_id_article_summary = html.find('p', {'id': 'article-summary'})
            description_list.append(self.text_cleaning(p_id_article_summary.text))
        except:
            pass
        try:
            h2_class_summary_description = html.find('h2', {'class': 'summary'})
            description_list.append(self.text_cleaning(h2_class_summary_description.text))
        except:
            pass
        try:
            h2_class_sp_descp_description = html.find('h2', {'class': 'sp-descp'})
            description_list.append(self.text_cleaning(h2_class_sp_descp_description.text))
        except:
            pass
        try:
            h2_itemprop_description = html.find('h2', {'itemprop': 'description'})
            description_list.append(self.text_cleaning(h2_itemprop_description.text))
        except:
            pass
        try:
            h2_class_alternative_headline = html.find('h2', {'class': 'alternativeHeadline'})
            description_list.append(self.text_cleaning(h2_class_alternative_headline.text))
        except:
            pass
        try:
            h3_description = html.find('h3')
            description_list.append(self.text_cleaning(h3_description.text))
        except:
            pass
        try:
            header_id_articleheader = html.find('header', {'id': 'articleHeader'})
            h2 = header_id_articleheader.find('h2')
            description_list.append(self.text_cleaning(h2.text))
        except:
            pass
        try:
            header = html.find('header')
            description_list.append(self.text_cleaning(header.find_next('h2').text))
        except:
            pass
        try:
            first_script = html.find('script', {'type': 'application/ld+json'})
            data = json.loads(first_script.string, strict=False)
            description_list.append(self.text_cleaning(data['@graph'][0]['description']))
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
                        if data["description"]:
                            description_list.append(self.text_cleaning(data["description"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle":
                        if type(data["video"]) is list:
                            description_list.append(self.text_cleaning(data["video"][0]["description"]))
                        elif type(data["video"]) is not list:
                            description_list.append(self.text_cleaning(data["video"]["description"]))
                except:
                    pass
        except:
            pass
        description_list = [description for description in description_list if description != '']
        if len(description_list) == 0:
            return " "
        best_description = max(description_list, key=len)
        return best_description
