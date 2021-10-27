from .abstract_extractor import AbstractExtractor
from bs4 import BeautifulSoup
import json
import re
from retrying import retry
import logging


class ArticlebodyExtractor(AbstractExtractor):
    def __init__(self):
        self.name = 'articlebody_extractor'

    def _text(self, item):
        self.html_item = item['spider_response']
        html = BeautifulSoup(self.html_item.body, 'html5lib')
        article_body = ""
        try:
            article_body = self.articlebody_mega(html)
        except Exception as e:
            logging.exception(e)
        return article_body

    def text_cleaning(self, body):
        article_text = body.encode("ascii", "ignore").decode("ascii", "ignore")
        article_text = re.sub(r'[^\x00-\x7F]', '', article_text)
        article_text = article_text.replace("\n", "")
        article_text = article_text.replace("\'", "'")
        article_text = article_text.replace("\\\"", '\"')
        article_text = article_text.replace("&amp;", "&")
        article_text = article_text.replace("&quot;", '\"')
        article_text = article_text.replace("&nbsp;", ' ')
        article_text = article_text.strip().lstrip().rstrip()
        article_text = ' '.join(article_text.split())
        return article_text

    def remove_html_tags(self, text):
        clean = re.compile('<.*?>')
        whitespace = re.compile('&nbsp;')
        text = re.sub(whitespace, ' ', text)
        return re.sub(clean, '', text)

    def decompose_junk_tags(self, tag):
        junk_tags = ['script', 'noscript', 'style', 'iframe', 'video', 'button', 'aside', 'form', 'footer']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['div', 'section']
            junk_texts = ['video', 'above-article', 'shortcut', "cmt_btn", "tgs", "sp_txt-sm", "firework-cont",
                          "social_link", "lstng_tagsContainer", "sp-scr_wrp", "reltd-main", "story_footer",
                          "nsl pt-0", "social-media", "generic-demo-box text-center",
                          "article__comment js-trigger-comments", "story_share", "comments_slide dismiss", "_dct",
                          "_fln", "gallery-btn", 'flag-region', 'up-next-slide',
                          'box no-mobile module images-show widget_nypost_top_five_widget', 'author-flyout',
                          'box show-mobile module widget_text', 'slide-image', 'slide-heading',
                          'video-player-container', 'newsletter-pure', 'panel new', 'box two-related-articles clear',
                          'clear rma', 'box right', 'gnt_ar_by', 'gnt_ar_dt', 'gnt_ss', 'article-print-url',
                          'utility-bar-wrap', 'story-share-buttons sms', 'fb', 'rotator bdrcc', 'share',
                          'inline-story-add', 'youtube-embed-wrapper', 'tab-link', 'engagement-block',
                          'in-article-adx', 'ie2013-contentLeft', 'ie2013-pagination', 'tags2013', 'termstoolbox',
                          'article-endcredit']
            id_tags = ["jiosaavn-widget", "checked", 'tab-link-wrapper-plugin', 'moreindia', 'auto_disclaimer']
            for try_tag in try_tags:
                for junk_text in junk_texts:
                    remove_me = tag.find_all(try_tag, {'class': junk_text})
                    for remove in remove_me:
                        remove.decompose()
            for id_tag in id_tags:
                for element in tag.find_all('div', {'id': id_tag}):
                    element.decompose()
                for element in tag.find_all('p', {'id': id_tag}):
                    element.decompose()
            p_texts = ["DON'T MISS", "JUST IN", "Follow USA TODAY's", "Also Read", "Also read", "ALSO READ", "READ",
                       "Also Watch", "Also watch", "ALSO WATCH", "the daily newsletter"]
            for p in tag.find_all('p'):
                for junk_p_text in p_texts:
                    if junk_p_text in p.text:
                        p.decompose()
            tnc = tag.find('span', {'class': 'tnc'})
            tnc.decompose()
        except:
            pass
        return tag

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_mega(self, html):
        articlebody_list = []
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    articlebody_list.append(self.text_cleaning(data['@graph'][0]['articleBody']))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data[0]['@type'] == 'NewsArticle' and data[0]['articleBody']:
                        articlebody_list.append(self.text_cleaning(data[0]['articleBody']))
                except:
                    pass
                try:
                    if type(data) is list:
                        data = data[0]
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["articleBody"]:
                        articlebody_list.append(self.text_cleaning(self.remove_html_tags(data["articleBody"])))
                except:
                    pass
                try:
                    body_list = []
                    if data["@type"] == "LiveBlogPosting":
                        if type(data["liveBlogUpdate"]) is list:
                            for element in data["liveBlogUpdate"]:
                                body_list.append(self.text_cleaning(self.remove_html_tags(element['articleBody'])))
                    body_list = ", ".join(body_list)
                    articlebody_list.append(body_list)
                except:
                    pass
        except:
            pass
        try:
            div_class_ga_headlines = html.find('div', {'class': 'ga-headlines'})
            div_class_ga_headlines = self.decompose_junk_tags(div_class_ga_headlines)
            articlebody_list.append(self.text_cleaning(div_class_ga_headlines.get_text(separator=" ")))
        except:
            pass
        try:
            div_class_normal = html.find('div', {'class': 'Normal'})
            div_class_normal = self.decompose_junk_tags(div_class_normal)
            articlebody_list.append(self.text_cleaning(div_class_normal.get_text(separator=" ")))
        except:
            pass
        try:
            span_class_readmore_span = html.find('span', {'class': 'readmore_span'})
            span_class_readmore_span = self.decompose_junk_tags(span_class_readmore_span)
            articlebody_list.append(self.text_cleaning(span_class_readmore_span.get_text(separator=" ")))
        except:
            pass
        try:
            span_itemprop_articlebody = html.find('span', {'itemprop': 'articleBody'})
            span_itemprop_articlebody = self.decompose_junk_tags(span_itemprop_articlebody)
            articlebody_list.append(self.text_cleaning(span_itemprop_articlebody.get_text(separator=" ")))
        except:
            pass
        try:
            div_class_main_content = html.find('div', {'class': 'main-content'})
            div_class_main_content = self.decompose_junk_tags(div_class_main_content)
            articlebody_list.append(self.text_cleaning(div_class_main_content.get_text(separator=" ")))
        except:
            pass
        try:
            div_data_articlebody = html.find('div', {'data-articlebody': True})
            div_data_articlebody = self.decompose_junk_tags(div_data_articlebody)
            articlebody_list.append(self.text_cleaning(div_data_articlebody.get_text(separator=" ")))
        except:
            pass
        try:
            div_class_content = html.find('div', {'class': 'content'})
            articlebody_list.append(self.text_cleaning(self.remove_html_tags(div_class_content.get_text(separator=" "))))
        except:
            pass
        try:
            div_class_story_content_one = html.find('div', {'class': 'story__content '})
            div_class_story_content_one = self.decompose_junk_tags(div_class_story_content_one)
            articlebody_list.append(self.text_cleaning(div_class_story_content_one.get_text(separator=" ")))
        except:
            pass
        try:
            div_class_story_content_two = html.find('div', {'class': 'story_content'})
            div_class_story_content_two = self.decompose_junk_tags(div_class_story_content_two)
            articlebody_list.append(self.text_cleaning(div_class_story_content_two.get_text(separator=" ")))
        except:
            pass
        try:
            div_itemprop_articlebody = html.find('div', {'itemprop': 'articleBody'})
            div_itemprop_articlebody = self.decompose_junk_tags(div_itemprop_articlebody)
            articlebody_list.append(self.text_cleaning(div_itemprop_articlebody.get_text(separator=" ")))
            tex = []
            for p in div_itemprop_articlebody.find_all('p'):
                tex.append(p.text)
            tex = " ".join(tex)
            articlebody_list.append(self.text_cleaning(tex))
        except:
            pass
        try:
            div_class_articlebody = html.find('div', {'class': 'article-body'})
            div_class_articlebody = self.decompose_junk_tags(div_class_articlebody)
            articlebody_list.append(self.text_cleaning(self.remove_html_tags(div_class_articlebody.get_text(separator=" "))))
        except:
            pass
        try:
            div_class_artilis_mainblock = html.find('div', {'class': 'artiLis-MainBlock'})
            div_class_artilis_mainblock = self.decompose_junk_tags(div_class_artilis_mainblock)
            articlebody_list.append(self.text_cleaning(div_class_artilis_mainblock.get_text(separator=" ")))
        except:
            pass
        try:
            div_class_content_text = html.find('div', {'class': 'content_text row description'})
            div_class_content_text = self.decompose_junk_tags(div_class_content_text)
            articlebody_list.append(self.text_cleaning(div_class_content_text.get_text(separator=" ")))
        except:
            pass
        try:
            div_class_post_contentbd = html.find('div', {'class': 'post-content-bd'})
            div_class_post_contentbd = self.decompose_junk_tags(div_class_post_contentbd)
            articlebody_list.append(self.text_cleaning(div_class_post_contentbd.get_text(separator=" ")))
        except:
            pass
        try:
            div_class_article_content = html.find('div', {'class': 'article__content h__mb40'})
            div_class_article_content = self.decompose_junk_tags(div_class_article_content)
            articlebody_list.append(self.text_cleaning(div_class_article_content.get_text(separator=" ")))
        except:
            pass
        try:
            div_class_article_storybody = html.find('div', {'class': 'article_storybody'})
            div_class_article_storybody = self.decompose_junk_tags(div_class_article_storybody)
            articlebody_list.append(self.text_cleaning(div_class_article_storybody.get_text(separator=" ")))
        except:
            pass
        try:
            div_class_spcn_ins_storybody = html.find('div', {'class': 'sp-cn ins_storybody'})
            div_class_spcn_ins_storybody = self.decompose_junk_tags(div_class_spcn_ins_storybody)
            articlebody_list.append(self.text_cleaning(div_class_spcn_ins_storybody.get_text(separator=" ")))
        except:
            pass
        try:
            div_class_dc = html.find('div', {'class': '_dc'})
            div_class_dc = self.decompose_junk_tags(div_class_dc)
            articlebody_list.append(self.text_cleaning(div_class_dc.get_text(separator=" ")))
        except:
            pass
        try:
            div_id_main = html.find('div', {'id': 'main'})
            div_id_main = self.decompose_junk_tags(div_id_main)
            articlebody_list.append(self.text_cleaning(self.remove_html_tags(div_id_main.get_text(separator=" "))))
        except:
            pass
        try:
            div_id_article_wrapper = html.find('div', {'id': 'article-wrapper'})
            div_id_article_wrapper = self.decompose_junk_tags(div_id_article_wrapper)
            articlebody_list.append(self.text_cleaning(self.remove_html_tags(div_id_article_wrapper.get_text(separator=" "))))
        except:
            pass
        try:
            div_class_entry_content = html.find('div', {'class': 'entry-content entry-content-read-more'})
            div_class_entry_content = self.decompose_junk_tags(div_class_entry_content)
            articlebody_list.append(self.text_cleaning(self.remove_html_tags(div_class_entry_content.get_text(separator=" "))))
        except:
            pass
        try:
            article_itemprop_mainentity = html.find('article', {'itemprop': 'mainEntity'})
            article_itemprop_mainentity = self.decompose_junk_tags(article_itemprop_mainentity)
            articlebody_list.append(self.text_cleaning(self.remove_html_tags(article_itemprop_mainentity.get_text(separator=" "))))
        except:
            pass
        try:
            article = html.find('article')
            article = self.decompose_junk_tags(article)
            articlebody_list.append(self.text_cleaning(self.remove_html_tags(article.get_text(separator=" "))))
        except:
            pass
        try:
            all_paras_text = []
            all_paras = html.find_all('p')
            for para in all_paras:
                all_paras_text.append(self.text_cleaning(para.get_text()))
            all_paras_text = " ".join(all_paras_text)
            articlebody_list.append(all_paras_text)
        except:
            pass
        try:
            div_class_contentbody = html.find('div', {'class': 'contentbody inf-body'})
            articlebody_list.append(self.text_cleaning(self.remove_html_tags(div_class_contentbody.div.get_text(separator=" "))))
        except:
            pass
        try:
            div_data_module_article_body = html.find('div', {'data-module': 'ArticleBody'})
            articlebody_list.append(self.text_cleaning(self.remove_html_tags(div_data_module_article_body.get_text(separator=" "))))
        except:
            pass
        try:
            div_data_module_featured_content = html.find('div', {'data-module': 'featuredContent'})
            articlebody_list.append(self.text_cleaning(self.remove_html_tags(div_data_module_featured_content.get_text(separator=" "))))
        except:
            pass
        try:
            div_data_module_liveblog = html.find('div', {'data-module': 'LiveBlogBody'})
            articlebody_list.append(self.text_cleaning(self.remove_html_tags(div_data_module_liveblog.get_text(separator=" "))))
        except:
            pass
        try:
            div_class_ie_content_story = html.find('div', {'class': 'ie2013-contentstory'})
            div_class_ie_content_story = self.decompose_junk_tags(div_class_ie_content_story)
            articlebody_list.append(self.text_cleaning(div_class_ie_content_story.get_text(separator=' ')))
        except:
            pass
        try:
            div_id_pcl_full_content = html.find('div', {'id': 'pcl-full-content'})
            div_id_pcl_full_content = self.decompose_junk_tags(div_id_pcl_full_content)
            articlebody_list.append(self.text_cleaning(div_id_pcl_full_content.get_text(separator=' ')))
        except:
            pass
        try:
            div_class_itemprop_articlebody = html.find('div', {'class': 'newsDetailedContent', 'itemprop': 'articleBody'})
            articlebody_list.append(self.text_cleaning(div_class_itemprop_articlebody.get_text(separator=' ')))
        except:
            pass
        try:
            div_class_running_text = html.find('div', {'class': 'runningtext'})
            articlebody_list.append(self.text_cleaning(div_class_running_text.get_text(separator=' ')))
        except:
            pass
        try:
            div_class_js_article = html.find('div', {'class': 'c-article-content js-article-content article__content'})
            articlebody_list.append(self.text_cleaning(div_class_js_article.get_text(separator=' ')))
        except:
            pass
        try:
            section_name_articlebody = html.find('section', {'name': "articleBody"})
            articlebody_list.append(self.text_cleaning(section_name_articlebody.get_text(separator=' ')))
        except:
            pass
        try:
            span_class_p_content = html.find('span', {'class': 'p-content'})
            span_class_p_content = self.decompose_junk_tags(span_class_p_content)
            articlebody_list.append(self.text_cleaning(span_class_p_content.get_text(separator=' ')))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return ""
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody
