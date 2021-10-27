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
        self.publisher = item['publisher']
        html = BeautifulSoup(self.html_item.body, 'html5lib')
        article_body = ""

        try:
            if self.publisher == 'EconomicTimes':
                article_body = self.articlebody_ET(html)
            if self.publisher == 'TimesofIndia':
                article_body = self.articlebody_TOI(html)
            if self.publisher == 'DeccanHerald':
                article_body = self.articlebody_DH(html)
            if self.publisher == 'NDTV':
                article_body = self.articlebody_NDTV(html)
            if self.publisher == 'Independent':
                article_body = self.articlebody_Independent(html)
            if self.publisher == 'EveningStandard':
                article_body = self.articlebody_EveningStandard(html)
            if self.publisher == 'NewYorkPost':
                article_body = self.articlebody_NewYorkPost(html)
            if self.publisher == 'Express':
                article_body = self.articlebody_Express(html)
            if self.publisher == 'USAToday':
                article_body = self.articlebody_USAToday(html)
            if self.publisher == 'DailyMail':
                article_body = self.articlebody_DailyMail(html)
            if self.publisher == 'IndiaToday':
                article_body = self.articlebody_IndiaToday(html)
            if self.publisher == 'OneIndia':
                article_body = self.articlebody_OneIndia(html)
            if self.publisher == 'HinduBusinessLine':
                article_body = self.articlebody_HinduBusinessLine(html)
            if self.publisher == 'ScrollNews':
                article_body = self.articlebody_ScrollNews(html)
            if self.publisher == 'CNBCWorld':
                article_body = self.articlebody_CNBC(html)
            if self.publisher == 'TheIndianExpress':
                article_body = self.articlebody_TheIndianExpress(html)
            if self.publisher == 'ThePioneer':
                article_body = self.articlebody_ThePioneer(html)
            if self.publisher == 'TheFinancialExpress':
                article_body = self.articlebody_FinancialExpress(html)
            if self.publisher == 'EuroNews':
                article_body = self.articlebody_EuroNews(html)
            if self.publisher == 'ESPNCricInfo':
                article_body = self.articlebody_ESPNCricInfo(html)
            if self.publisher == 'NYTimes':
                article_body = self.articlebody_NYTimes(html)
            if self.publisher == 'BusinessStandard':
                article_body = self.articlebody_BusinessStandard(html)
        except:
            pass
        return article_body


    def clean_text(self, body):
        article_text = body.encode("ascii", "ignore").decode("ascii", "ignore")
        article_text = re.sub(r'[^\x00-\x7F]', '', article_text)
        article_text = article_text.replace("\n", "")
        article_text = article_text.replace("\'", "'")
        article_text = article_text.replace("\\\"", '\"')
        article_text = article_text.replace("&amp;", "&")
        article_text = article_text.replace("&quot;", '\"')
        article_text = article_text.strip().lstrip().rstrip()
        article_text = ' '.join(article_text.split())
        return article_text


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


    def decompose_tags_TOI(self, tag):
        junk_tags = ['script', 'noscript', 'style']
        junk_texts = ['Facebook', 'Twitter', 'Linkedin', 'EMail', 'Pinterest']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        check_tags = ['span', 'i']
        for junk_text in junk_texts:
            for check_tag in check_tags:
                for element in tag.find_all(check_tag):
                    if element.text == junk_text:
                        element.decompose()
        return tag


    def decompose_tags_NDTV(self, tag):
        class_tags = ["cmt_btn", "tgs", "sp_txt-sm", "firework-cont", "social_link", "lstng_tagsContainer", "sp-scr_wrp", "reltd-main", "story_footer", "nsl pt-0", "social-media", "generic-demo-box text-center", "article__comment js-trigger-comments", "story_share", "comments_slide dismiss", "_dct", "_fln"]
        id_tags = ["jiosaavn-widget", "checked"]
        for script in tag.find_all('script'):
            script.decompose()
        for class_tag in class_tags:
            for x in tag.find_all('div', {'class': class_tag}):
                x.decompose()
        for id_tag in id_tags:
            for x in tag.find_all('div', {'id': id_tag}):
                x.decompose()
        return tag


    def decompose_tags_Independent(self, tag):
        junk_tags = ['script', 'noscript', 'style']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['div', 'section']
            junk_texts = ['video', 'above-article', 'shortcut']
            for try_tag in try_tags:
                for junk_text in junk_texts:
                    remove_me = tag.find_all(try_tag, {'class': junk_text})
                    for remove in remove_me:
                        remove.decompose()
        except:
            pass
        return tag


    def decompose_tags_EveningStandard(self, tag):
        junk_tags = ['script', 'noscript', 'style', 'aside', 'form']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['div']
            junk_texts = ['gallery-btn']
            for try_tag in try_tags:
                for junk_text in junk_texts:
                    remove_me = tag.find_all(try_tag, {'class': junk_text})
                    for remove in remove_me:
                        remove.decompose()
        except:
            pass
        return tag


    def decompose_tags_NewYorkPost(self, tag):
        junk_tags = ['script', 'noscript', 'style', 'iframe']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['div']
            junk_texts = ['flag-region', 'up-next-slide', 'box no-mobile module images-show widget_nypost_top_five_widget', 'author-flyout', 'box show-mobile module widget_text', 'slide-image', 'slide-heading']
            for try_tag in try_tags:
                for junk_text in junk_texts:
                    remove_me = tag.find_all(try_tag, {'class': junk_text})
                    for remove in remove_me:
                        remove.decompose()
        except:
            pass
        return tag


    def decompose_tags_Express(self, tag):
        junk_tags = ['script', 'noscript', 'style', 'iframe', 'video', 'button']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['div']
            junk_texts = ['video-player-container', 'newsletter-pure', 'panel new', 'box two-related-articles clear', 'clear rma', 'box right']
            for try_tag in try_tags:
                for junk_text in junk_texts:
                    remove_me = tag.find_all(try_tag, {'class': junk_text})
                    for remove in remove_me:
                        remove.decompose()
            p_texts = ["DON'T MISS", "JUST IN"]
            for p in tag.find_all('p'):
                for junk_p_text in p_texts:
                    if junk_p_text in p.text:
                        p.decompose()
            h1_headline = tag.find('h1', {'itemprop': 'headline'})
            h1_headline.decompose()
        except:
            pass
        return tag


    def decompose_tags_USAToday(self, tag):
        junk_tags = ['script', 'noscript', 'style', 'iframe', 'video', 'button', 'aside', 'footer']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['div']
            junk_texts = ['gnt_ar_by', 'gnt_ar_dt', 'gnt_ss', 'article-print-url', 'utility-bar-wrap', 'story-share-buttons sms']
            for try_tag in try_tags:
                for junk_text in junk_texts:
                    remove_me = tag.find_all(try_tag, {'class': junk_text})
                    for remove in remove_me:
                        remove.decompose()
            for p in tag.find_all('p'):
                if "Follow USA TODAY's" in p.text:
                    p.decompose()
        except:
            pass
        return tag


    def decompose_tags_DailyMail(self, tag):
        junk_tags = ['script', 'noscript', 'style', 'iframe', 'video', 'button']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['div']
            junk_texts = ['fb', 'rotator bdrcc', 'share']
            for try_tag in try_tags:
                for junk_text in junk_texts:
                    remove_me = tag.find_all(try_tag, {'class': junk_text})
                    for remove in remove_me:
                        remove.decompose()
        except:
            pass
        return tag


    def decompose_tags_IndiaToday(self, tag):
        junk_tags = ['script', 'noscript', 'style', 'iframe', 'video', 'button']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['div']
            id_texts = ['tab-link-wrapper-plugin']
            class_texts = ['inline-story-add', 'youtube-embed-wrapper', 'tab-link']
            for try_tag in try_tags:
                for class_text in class_texts:
                    remove_me = tag.find_all(try_tag, {'class': class_text})
                    for remove in remove_me:
                        remove.decompose()
            for try_tag in try_tags:
                for id_text in id_texts:
                    remove_me = tag.find_all(try_tag, {'id': id_text})
                    for remove in remove_me:
                        remove.decompose()
            p_texts = ["Also Read", "Also read", "ALSO READ", "READ", "Also Watch", "Also watch", "ALSO WATCH", "the daily newsletter"]
            for p in tag.find_all('p'):
                for junk_p_text in p_texts:
                    if junk_p_text in p.text:
                        p.decompose()
        except:
            pass
        return tag


    def decompose_tags_ScrollNews(self, tag):
        junk_tags = ['script', 'noscript', 'style', 'iframe', 'video', 'button']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['div']
            class_texts = ['engagement-block', 'in-article-adx']
            for try_tag in try_tags:
                for class_text in class_texts:
                    remove_me = tag.find_all(try_tag, {'class': class_text})
                    for remove in remove_me:
                        remove.decompose()
        except:
            pass
        return tag


    def decompose_tags_IndianExpress(self, tag):
        junk_tags = ['script', 'noscript', 'style', 'iframe', 'video', 'button']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['div']
            class_texts = ['ie2013-contentLeft', 'ie2013-pagination', 'tags2013', 'termstoolbox']
            id_texts = ['moreindia']
            for try_tag in try_tags:
                for class_text in class_texts:
                    remove_me = tag.find_all(try_tag, {'class': class_text})
                    for remove in remove_me:
                        remove.decompose()
            for try_tag in try_tags:
                for id_text in id_texts:
                    remove_me = tag.find_all(try_tag, {'id': id_text})
                    for remove in remove_me:
                        remove.decompose()
            tnc = tag.find('span', {'class': 'tnc'})
            tnc.decompose()
        except:
            pass
        return tag


    def decompose_tags_ESPNCricInfo(tag):
        junk_tags = ['script', 'noscript', 'style', 'iframe', 'video', 'button']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['div']
            class_texts = ['article-endcredit']
            for try_tag in try_tags:
                for class_text in class_texts:
                    remove_me = tag.find_all(try_tag, {'class': class_text})
                    for remove in remove_me:
                        remove.decompose()
        except:
            pass
        return tag


    def decompose_tags_BusinessStandard(tag):
        junk_tags = ['script', 'noscript', 'style', 'iframe', 'video', 'button']
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        try:
            try_tags = ['p']
            id_texts = ['auto_disclaimer']
            for try_tag in try_tags:
                for id_text in id_texts:
                    remove_me = tag.find_all(try_tag, {'id': id_text})
                    for remove in remove_me:
                        remove.decompose()
        except:
            pass
        return tag


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_ET(self, html):
        try:
            article_body = self.return_articlebody(html)
            if article_body != '' and article_body is not None:
                return article_body
        except:
            return " "


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_TOI(self, html):
        articlebody_list = []
        try:
            article_body = html.find('div', {'class': 'ga-headlines'})
            article_body = self.decompose_tags_TOI(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'Normal'})
            article_body = self.decompose_tags_TOI(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('span', {'class': 'readmore_span'})
            article_body = self.decompose_tags_TOI(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'main-content'})
            article_body = self.decompose_tags_TOI(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'data-articlebody': True})
            article_body = self.decompose_tags_TOI(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_DH(self, html):
        articlebody_list = []
        try:
            article_body = self.return_articlebody(html)
            if article_body != '' and article_body is not None:
                articlebody_list.append(article_body)
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'content'})
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_NDTV(self, html):
        articlebody_list = []
        try:
            article_body = html.find('div', {'class': 'story__content '})
            article_body = self.decompose_tags_NDTV(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'itemprop': 'articleBody'})
            article_body = self.decompose_tags_NDTV(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'artiLis-MainBlock'})
            article_body = self.decompose_tags_NDTV(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'content_text row description'})
            article_body = self.decompose_tags_NDTV(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('span', {'itemprop': 'articleBody'})
            article_body = self.decompose_tags_NDTV(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'post-content-bd'})
            article_body = self.decompose_tags_NDTV(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'article__content h__mb40'})
            article_body = self.decompose_tags_NDTV(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'story_content'})
            article_body = self.decompose_tags_NDTV(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'article_storybody'})
            article_body = self.decompose_tags_NDTV(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'sp-cn ins_storybody'})
            article_body = self.decompose_tags_NDTV(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        try:
            article_body = html.find('div', {'class': '_dc'})
            article_body = self.decompose_tags_NDTV(article_body)
            articlebody_list.append(self.clean_text(article_body.get_text(separator=" ")))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_Independent(self, html):
        articlebody_list = []
        try:
            article_body = html.find('div', {'id': 'main'})
            article_body = self.decompose_tags_Independent(article_body)
            article_body_text = self.clean_text(self.remove_html_tags(article_body.get_text(separator=" ")))
            articlebody_list.append(article_body_text)
        except:
            pass
        try:
            description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'name': 'twitter:description'})
            articlebody_list.append(self.clean_text(description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_EveningStandard(self, html):
        articlebody_list = []
        try:
            article_body = html.find('div', {'id': 'main'})
            article_body = self.decompose_tags_EveningStandard(article_body)
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        try:
            article_body = html.find('div', {'itemprop': 'articleBody'})
            article_body = self.decompose_tags_EveningStandard(article_body)
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'property': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_NewYorkPost(self, html):
        articlebody_list = []
        try:
            article_body = html.find('div', {'class': 'entry-content entry-content-read-more'})
            article_body = self.decompose_tags_NewYorkPost(article_body)
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        try:
            article_body = html.find('div', {'id': 'article-wrapper'})
            article_body = self.decompose_tags_NewYorkPost(article_body)
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        try:
            description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'name': 'twitter:description'})
            articlebody_list.append(self.clean_text(description['content']))
        except:
            pass
        try:
            description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_Express(self, html):
        articlebody_list = []
        try:
            article_body = html.find('article', {'itemprop': 'mainEntity'})
            article_body = self.decompose_tags_Express(article_body)
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'property': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            h3 = html.find('h3')
            articlebody_list.append(self.clean_text(h3.text))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_USAToday(self, html):
        articlebody_list = []
        try:
            article = html.find('article')
            article = self.decompose_tags_USAToday(article)
            articlebody_list.append(self.clean_text(self.remove_html_tags(article.get_text(separator=" "))))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["description"]:
                        articlebody_list.append(self.clean_text(data["description"]))
                except:
                    pass
        except:
            pass
        try:
            div_share = html.find('div', {'data-ss-d': True})
            articlebody_list.append(self.clean_text(div_share['data-ss-d']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_DailyMail(self, html):
        articlebody_list = []
        try:
            article_body = html.find('div', {'itemprop': 'articleBody'})
            article_body = self.decompose_tags_DailyMail(article_body)
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'property': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
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
                        articlebody_list.append(self.clean_text(data["description"]))
                except:
                    pass
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_IndiaToday(self, html):
        articlebody_list = []
        try:
            article_body = html.find('div', {'itemprop': 'articleBody'})
            article_body = self.decompose_tags_IndiaToday(article_body)
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_OneIndia(self, html):
        articlebody_list = []
        try:
            all_paras_text = []
            all_paras = html.find_all('p')
            for para in all_paras:
                all_paras_text.append(self.clean_text(para.get_text()))
            all_paras_text = " ".join(all_paras_text)
            articlebody_list.append(all_paras_text)
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
                    if data["@type"] == "NewsArticle" and data["articleBody"]:
                        articlebody_list.append(self.clean_text(data["articleBody"]))
                except:
                    pass
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description', 'itemprop': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_HinduBusinessLine(self, html):
        articlebody_list = []
        try:
            article_body = html.find('div', {'class': 'contentbody inf-body'})
            articlebody_list.append(self.remove_html_tags(article_body.div.get_text(separator=" ")))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_ScrollNews(self, html):
        articlebody_list = []
        try:
            article_body = html.find('div', {'class': 'article-body'})
            article_body = self.decompose_tags_ScrollNews(article_body)
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_CNBC(self, html):
        articlebody_list = []
        try:
            article_body = html.find('div', {'data-module': 'ArticleBody'})
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        try:
            article_body = html.find('div', {'data-module': 'featuredContent'})
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        try:
            article_body = html.find('div', {'data-module': 'LiveBlogBody'})
            articlebody_list.append(self.clean_text(self.remove_html_tags(article_body.get_text(separator=" "))))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                data = json.loads(script.string, strict=False)
                body_list = []
                try:
                    if data["@type"] == "LiveBlogPosting":
                        if type(data["liveBlogUpdate"]) is list:
                            for x in data["liveBlogUpdate"]:
                                body_list.append(self.clean_text(self.remove_html_tags(x['articleBody'])))
                    body_list = ", ".join(body_list)
                    articlebody_list.append(body_list)
                except:
                    pass
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_TheIndianExpress(self, html):
        articlebody_list = []
        try:
            body = html.find('div', {'class': 'ie2013-contentstory'})
            body = self.decompose_tags_IndianExpress(body)
            articlebody_list.append(self.clean_text(body.get_text(separator=' ')))
        except:
            pass
        try:
            body = html.find('div', {'id': 'pcl-full-content'})
            body = self.decompose_tags_IndianExpress(body)
            articlebody_list.append(self.clean_text(body.get_text(separator=' ')))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'NewsArticle' and data['articleBody']:
                        articlebody_list.append(self.clean_text(data['articleBody']))
                except:
                    pass
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_ThePioneer(self, html):
        articlebody_list = []
        try:
            body = html.find('div', {'class': 'newsDetailedContent', 'itemprop': 'articleBody'})
            articlebody_list.append(self.clean_text(body.get_text(separator=' ')))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_FinancialExpress(self, html):
        articlebody_list = []
        try:
            body = html.find('div', {'class': 'runningtext'})
            articlebody_list.append(self.clean_text(body.get_text(separator=' ')))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_EuroNews(self, html):
        articlebody_list = []
        try:
            body = html.find('div', {'class': 'c-article-content js-article-content article__content'})
            articlebody_list.append(self.clean_text(body.get_text(separator=' ')))
        except:
            pass
        try:
            script = html.find('script', {'type': 'application/ld+json'})
            try:
                data = json.loads(script.string, strict=False)
                articlebody_list.append(self.clean_text(data['@graph'][0]['articleBody']))
            except:
                pass
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_ESPNCricInfo(self, html):
        articlebody_list = []
        try:
            tex = []
            div_body = html.find('div', {'class': 'article-body'})
            div_body = self.decompose_tags_ESPNCricInfo(div_body)
            for p in div_body.find_all('p'):
                tex.append(p.text)
            tex = " ".join(tex)
            articlebody_list.append(self.clean_text(tex))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data['@type'] == 'NewsArticle' and data['articleBody']:
                        articlebody_list.append(self.clean_text(data['articleBody']))
                except:
                    pass
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'name': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_NYTimes(self, html):
        articlebody_list = []
        try:
            article_body = html.find('section', {'name': "articleBody"})
            articlebody_list.append(self.clean_text(article_body.get_text(separator=' ')))
        except:
            pass
        try:
            article = html.find('article')
            articlebody_list.append(self.clean_text(article.get_text(separator=' ')))
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'property': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def articlebody_BusinessStandard(self, html):
        articlebody_list = []
        try:
            span_body = html.find('span', {'class': 'p-content'})
            span_body = self.decompose_tags_BusinessStandard(span_body)
            articlebody_list.append(self.clean_text(span_body.get_text(separator=' ')))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data[0]['@type'] == 'NewsArticle' and data[0]['articleBody']:
                        articlebody_list.append(self.clean_text(data[0]['articleBody']))
                except:
                    pass
        except:
            pass
        try:
            meta_description = html.find('meta', {'name': 'description'})
            articlebody_list.append(self.clean_text(meta_description['content']))
        except:
            pass
        try:
            og_description = html.find('meta', {'property': 'og:description'})
            articlebody_list.append(self.clean_text(og_description['content']))
        except:
            pass
        try:
            twitter_description = html.find('meta', {'property': 'twitter:description'})
            articlebody_list.append(self.clean_text(twitter_description['content']))
        except:
            pass
        articlebody_list = [body for body in articlebody_list if body != '']
        if len(articlebody_list) == 0:
            return " "
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody
