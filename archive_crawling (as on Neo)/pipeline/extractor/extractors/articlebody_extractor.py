"""Script to extract the body text from a news article."""

import json
import logging
import re
from contextlib import suppress

from bs4 import BeautifulSoup
from retrying import retry

from .abstract_extractor import AbstractExtractor


class ArticlebodyExtractor(AbstractExtractor):
    """
    Custom Article-body Extractor
    * Used as a fallback for newspaper_extractor
    * Returns the longest string out of all extracted article-body values
    """
    def __init__(self):  # pylint: disable=super-init-not-called
        """Init function."""
        self.name = 'articlebody_extractor'

    def _text(self, item):
        """Returns the extracted body text from a news article."""
        html_item = item['spider_response']
        html = BeautifulSoup(html_item.body, 'html5lib')
        article_body = ""
        try:
            article_body = self.articlebody_mega(html)
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(exception)
        return article_body

    def text_cleaning(self, body):  # pylint: disable=no-self-use
        """Function to clean the body text."""
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

    def remove_html_tags(self, text):  # pylint: disable=no-self-use
        """Removes html tags and whitespaces from body text."""
        clean = re.compile('<.*?>')
        whitespace = re.compile('&nbsp;')
        text = re.sub(whitespace, ' ', text)
        return re.sub(clean, '', text)

    def decompose_junk_tags(self, tag):  # pylint: disable=too-many-branches,no-self-use
        """Removes junk tags and their content."""
        junk_tags = [
            'script', 'noscript', 'style', 'iframe', 'video', 'button',
            'aside', 'form', 'footer'
        ]
        for junk_tag in junk_tags:
            for element in tag.find_all(junk_tag):
                element.decompose()
        with suppress(Exception):
            try_tags = ['div', 'section']
            junk_texts = [
                'video', 'above-article', 'shortcut', "cmt_btn", "tgs",
                "sp_txt-sm", "firework-cont", "social_link",
                "lstng_tagsContainer", "sp-scr_wrp", "reltd-main",
                "story_footer", "nsl pt-0", "social-media",
                "generic-demo-box text-center",
                "article__comment js-trigger-comments", "story_share",
                "comments_slide dismiss", "_dct", "_fln", "gallery-btn",
                'flag-region', 'up-next-slide',
                'box no-mobile module images-show widget_nypost_top_five_widget',
                'author-flyout', 'box show-mobile module widget_text',
                'slide-image', 'slide-heading', 'video-player-container',
                'newsletter-pure', 'panel new',
                'box two-related-articles clear', 'clear rma', 'box right',
                'gnt_ar_by', 'gnt_ar_dt', 'gnt_ss', 'article-print-url',
                'utility-bar-wrap', 'story-share-buttons sms', 'fb',
                'rotator bdrcc', 'share', 'inline-story-add',
                'youtube-embed-wrapper', 'tab-link', 'engagement-block',
                'in-article-adx', 'ie2013-contentLeft', 'ie2013-pagination',
                'tags2013', 'termstoolbox', 'article-endcredit'
            ]
            id_tags = [
                "jiosaavn-widget", "checked", 'tab-link-wrapper-plugin',
                'moreindia', 'auto_disclaimer'
            ]
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
            p_texts = [
                "DON'T MISS", "JUST IN", "Follow USA TODAY's", "Also Read",
                "Also read", "ALSO READ", "READ", "Also Watch", "Also watch",
                "ALSO WATCH", "the daily newsletter"
            ]
            for para in tag.find_all('p'):
                for junk_p_text in p_texts:
                    if junk_p_text in para.text:
                        para.decompose()
            tnc = tag.find('span', {'class': 'tnc'})
            tnc.decompose()
        return tag

    @retry(stop_max_attempt_number=3,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def articlebody_mega(self, html):  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        """
        Returns the longest body text from a list of all extracted body
        text values.
        """
        articlebody_list = []
        with suppress(Exception):
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                '''
                Tested on
                * https://www.euronews.com/2020/12/08/france-s-next-aircraft-carrier-to-be-nuclear-powered-macron-confirms
                  "France's next-generation aircraft...7 billion."
                * https://www.euronews.com/2020/12/08/charlie-hebdo-trial-prosecutors-request-30-year-sentence-for-fugitive-widow-of-attacker
                  "Prosecutors in the Charlie Hebdo trial...basilica in Nice."
                '''
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    articlebody_list.append(
                        self.text_cleaning(data['@graph'][0]['articleBody']))
                '''
                Tested on
                * https://www.business-standard.com/article/international/wb-economist-china-will-need-to-learn-to-restructure-emerging-market-debt-121011300034_1.html
                  "WASHINGTON (Reuters) - Increasing...a syndicated feed.)"
                * https://www.business-standard.com/article/international/us-house-committee-releases-report-supporting-donald-trump-s-impeachment-121011300125_1.html
                  "US House Judiciary Committee...from a syndicated feed.)"
                '''
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if data[0]['@type'] == 'NewsArticle' and data[0][
                            'articleBody']:
                        articlebody_list.append(
                            self.text_cleaning(data[0]['articleBody']))
                '''
                Tested on
                * https://indianexpress.com/article/world/print/four-killed-as-armed-militants-storm-5-star-hotel-in-pakistans-gwadar-port-city-police-5723193/
                  "Three heavily-armed militants...in Karachi last year."
                * https://indianexpress.com/article/news-archive/ayushman-bharat-aadhaar-mandatory-for-those-seeking-treatment-for-second-time-5390924/
                  "Aadhaar is not mandatory...implementing the PMJAY."
                '''
                with suppress(Exception):
                    if isinstance(data, list):
                        data = data[0]
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["articleBody"]:
                        articlebody_list.append(
                            self.text_cleaning(
                                self.remove_html_tags(data["articleBody"])))
                '''
                Tested on
                * https://www.cnbc.com/2020/11/01/election-2020-live-updates-biden-in-pennsylvania-as-trump-barnstorms-the-country.html
                  "With just two days left...Fayetteville, North Carolina"
                '''
                with suppress(Exception):
                    body_list = []
                    if data["@type"] == "LiveBlogPosting":
                        if isinstance(data["liveBlogUpdate"], list):
                            for element in data["liveBlogUpdate"]:
                                body_list.append(
                                    self.text_cleaning(
                                        self.remove_html_tags(
                                            element['articleBody'])))
                    body_list = ", ".join(body_list)
                    articlebody_list.append(body_list)
        '''
        Tested on
        * https://timesofindia.indiatimes.com/city/bengaluru/ISROs-second-launch-pad-to-be-sent-by-March-end/articleshow/3801270.cms
          "bangalore: the second launch pad...and manufactured it."
        * https://timesofindia.indiatimes.com/city/delhi/CBSE-makes-more-room-for-kids-with-special-needs/articleshow/4202742.cms
          "new delhi: CBSE has introduced...scribe to write the paper"
        '''
        with suppress(Exception):
            div_class_ga_headlines = html.find('div',
                                               {'class': 'ga-headlines'})
            div_class_ga_headlines = self.decompose_junk_tags(
                div_class_ga_headlines)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_ga_headlines.get_text(separator=" ")))
        '''
        Tested on
        * https://timesofindia.indiatimes.com/entertainment/events/lucknow/Freshers-join-in-to-participate-in-Clean-Clear-Lucknow-Times-Fresh-Face-2012-at-Shri-Ramswaroop-Memorial-College/articleshow/16463875.cms?
          "The first season of the...runners up title."
        * https://timesofindia.indiatimes.com/home/education/news/iit-madras-disappointed-over-not-granted-institutes-of-eminence-status-writes-to-hrd-ministry/articleshow/66356947.cms?
          "NEW DELHI: The Indian Institute...was conditional."
        '''
        with suppress(Exception):
            div_class_normal = html.find('div', {'class': 'Normal'})
            div_class_normal = self.decompose_junk_tags(div_class_normal)
            articlebody_list.append(
                self.text_cleaning(div_class_normal.get_text(separator=" ")))
        '''
        Tested on
        * https://timesofindia.indiatimes.com/life-style/relationships/love-sex/how-to-make-time-for-intimacy-in-your-love-life-according-to-zodiac-signs/photostory/80667320.cms
          "We live in a fast-paced world...zodiac sign."
        '''
        with suppress(Exception):
            span_class_readmore_span = html.find('span',
                                                 {'class': 'readmore_span'})
            span_class_readmore_span = self.decompose_junk_tags(
                span_class_readmore_span)
            articlebody_list.append(
                self.text_cleaning(
                    span_class_readmore_span.get_text(separator=" ")))
        with suppress(Exception):
            span_itemprop_articlebody = html.find('span',
                                                  {'itemprop': 'articleBody'})
            span_itemprop_articlebody = self.decompose_junk_tags(
                span_itemprop_articlebody)
            articlebody_list.append(
                self.text_cleaning(
                    span_itemprop_articlebody.get_text(separator=" ")))
        '''
        Tested on
        * https://timesofindia.indiatimes.com/blogs/toi-edit-page/turn-the-tide-against-cancer-india-needs-affordable-and-accessible-cancer-treatment-else-cancer-screenings-arent-much-use/
          "The fight against cancer...destroy me?"
        '''
        with suppress(Exception):
            div_class_main_content = html.find('div',
                                               {'class': 'main-content'})
            div_class_main_content = self.decompose_junk_tags(
                div_class_main_content)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_main_content.get_text(separator=" ")))
        with suppress(Exception):
            div_data_articlebody = html.find('div', {'data-articlebody': True})
            div_data_articlebody = self.decompose_junk_tags(
                div_data_articlebody)
            articlebody_list.append(
                self.text_cleaning(
                    div_data_articlebody.get_text(separator=" ")))
        with suppress(Exception):
            div_class_content = html.find('div', {'class': 'content'})
            div_class_content = self.decompose_junk_tags(div_class_content)
            articlebody_list.append(
                self.text_cleaning(
                    self.remove_html_tags(
                        div_class_content.get_text(separator=" "))))
        with suppress(Exception):
            div_class_story_content_one = html.find(
                'div', {'class': 'story__content '})
            div_class_story_content_one = self.decompose_junk_tags(
                div_class_story_content_one)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_story_content_one.get_text(separator=" ")))
        with suppress(Exception):
            div_class_story_content_two = html.find('div',
                                                    {'class': 'story_content'})
            div_class_story_content_two = self.decompose_junk_tags(
                div_class_story_content_two)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_story_content_two.get_text(separator=" ")))
        '''
        Tested on
        * https://www.ndtv.com/india-news/bjp-and-congress-lock-horns-over-newspaper-advertisements-in-poll-bound-himachal-pradesh-503275
          "Shimla: Newspaper...those they were meant for."
        * https://www.ndtv.com/india-news/spread-of-japanese-encephalitis-in-poorvanchal-due-to-lack-of-sanitation-up-chief-minister-yogi-adit-1687935
          "UP Chief Minister Yogi Adityanath...Uttar Pradesh, it said."
        '''
        with suppress(Exception):
            div_itemprop_articlebody = html.find('div',
                                                 {'itemprop': 'articleBody'})
            div_itemprop_articlebody = self.decompose_junk_tags(
                div_itemprop_articlebody)
            articlebody_list.append(
                self.text_cleaning(
                    div_itemprop_articlebody.get_text(separator=" ")))
            tex = []
            for para in div_itemprop_articlebody.find_all('p'):
                tex.append(para.text)
            tex = " ".join(tex)
            articlebody_list.append(self.text_cleaning(tex))
        with suppress(Exception):
            div_class_articlebody = html.find('div', {'class': 'article-body'})
            div_class_articlebody = self.decompose_junk_tags(
                div_class_articlebody)
            articlebody_list.append(
                self.text_cleaning(
                    self.remove_html_tags(
                        div_class_articlebody.get_text(separator=" "))))
        '''
        Tested on
        * https://www.ndtv.com/education/jee-main-2021-know-preparation-tips-salient-topics-and-weightage
          "JEE Main 2021: Know Preparation Tips,...IIT JEE Main"
        '''
        with suppress(Exception):
            div_class_artilis_mainblock = html.find(
                'div', {'class': 'artiLis-MainBlock'})
            div_class_artilis_mainblock = self.decompose_junk_tags(
                div_class_artilis_mainblock)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_artilis_mainblock.get_text(separator=" ")))
        '''
        Tested on
        * https://gadgets.ndtv.com/entertainment/news/little-things-season-2-release-date-trailer-netflix-1911696
          "Netflix has announced that...Little Things season 2 will release October 5 on Netflix."
        '''
        with suppress(Exception):
            div_class_content_text = html.find(
                'div', {'class': 'content_text row description'})
            div_class_content_text = self.decompose_junk_tags(
                div_class_content_text)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_content_text.get_text(separator=" ")))
        '''
        Tested on
        * https://swachhindia.ndtv.com/air-pollution-crisis-delhi-air-quality-in-severe-category-for-third-consecutive-day-29289/
          "The pollution level went up to...two of India's major river bodies."
        '''
        with suppress(Exception):
            div_class_post_contentbd = html.find('div',
                                                 {'class': 'post-content-bd'})
            div_class_post_contentbd = self.decompose_junk_tags(
                div_class_post_contentbd)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_post_contentbd.get_text(separator=" ")))
        '''
        Tested on
        * https://www.carandbike.com/news/maruti-suzuki-has-sold-4-million-pre-owned-vehicles-in-india-in-19-years-2362794
          "Maruti Suzuki announced that...our YouTube channel."
        '''
        with suppress(Exception):
            div_class_article_content = html.find(
                'div', {'class': 'article__content h__mb40'})
            div_class_article_content = self.decompose_junk_tags(
                div_class_article_content)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_article_content.get_text(separator=" ")))
        with suppress(Exception):
            div_class_article_storybody = html.find(
                'div', {'class': 'article_storybody'})
            div_class_article_storybody = self.decompose_junk_tags(
                div_class_article_storybody)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_article_storybody.get_text(separator=" ")))
        '''
        Tested on
        * https://www.ndtv.com/india-news/spread-of-japanese-encephalitis-in-poorvanchal-due-to-lack-of-sanitation-up-chief-minister-yogi-adit-1687935
          "UP Chief Minister Yogi Adityanath...were contributed by Uttar Pradesh, it said."
        * https://www.ndtv.com/entertainment/sean-connery-a-legend-on-screen-and-off-tributes-from-hugh-jackman-abhishek-bachchan-and-others-2318676
          "Sean Connery died on Saturday....Farwell Sir Sean Connery - there will never be another."
        '''
        with suppress(Exception):
            div_class_spcn_ins_storybody = html.find(
                'div', {'class': 'sp-cn ins_storybody'})
            div_class_spcn_ins_storybody = self.decompose_junk_tags(
                div_class_spcn_ins_storybody)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_spcn_ins_storybody.get_text(separator=" ")))
        with suppress(Exception):
            div_class_dc = html.find('div', {'class': '_dc'})
            div_class_dc = self.decompose_junk_tags(div_class_dc)
            articlebody_list.append(
                self.text_cleaning(div_class_dc.get_text(separator=" ")))
        '''
        Tested on
        * https://www.independent.co.uk/news/uk/home-news/coronavirus-childcare-parents-lockdown-schools-a9688116.html
          "Parents say not being able...double for childcare"
        * https://www.independent.co.uk/arts-entertainment/tv/news/ratched-netflix-trigger-warning-child-abuse-suicide-violence-sarah-paulson-b571405.html
          "Ratched fans have urged...plot twist in the series"
        '''
        with suppress(Exception):
            div_id_main = html.find('div', {'id': 'main'})
            div_id_main = self.decompose_junk_tags(div_id_main)
            articlebody_list.append(
                self.text_cleaning(
                    self.remove_html_tags(
                        div_id_main.get_text(separator=" "))))
        '''
        Tested on
        * https://nypost.com/2010/09/27/brooklyn-tea-party-rallies-against-ground-zero-mosque-multiculturalism/
          "Facebook...Marist poll puts Cuomo way ahead"
        * https://nypost.com/2015/05/21/syndergaards-goal-for-what-may-be-his-last-mlb-start-for-a-while/
          "Facebook...Hell Freezes Over as Meghan McCain Praises AOC for “Hammering..."
        '''
        with suppress(Exception):
            div_id_article_wrapper = html.find('div',
                                               {'id': 'article-wrapper'})
            div_id_article_wrapper = self.decompose_junk_tags(
                div_id_article_wrapper)
            articlebody_list.append(
                self.text_cleaning(
                    self.remove_html_tags(
                        div_id_article_wrapper.get_text(separator=" "))))
        '''
        Tested on
        * https://nypost.com/2010/09/27/brooklyn-tea-party-rallies-against-ground-zero-mosque-multiculturalism/
          "About 125 people gathered...Brooklyn Tea Party Protest (The Brooklyn Ink)"
        * https://nypost.com/2015/05/21/syndergaards-goal-for-what-may-be-his-last-mlb-start-for-a-while/
          "Noah Syndergaard is ready to take the baton....Mets also started 17-6 at home."
        '''
        with suppress(Exception):
            div_class_entry_content = html.find(
                'div', {'class': 'entry-content entry-content-read-more'})
            div_class_entry_content = self.decompose_junk_tags(
                div_class_entry_content)
            articlebody_list.append(
                self.text_cleaning(
                    self.remove_html_tags(
                        div_class_entry_content.get_text(separator=" "))))
        '''
        Tested on
        * https://www.express.co.uk/news/weather/1370081/BBC-Weather-Europe-snow-forecast-cold-December-update-video-vn
          "BBC Weather: Fog and snow...early in December at the moment.”"
        * https://www.express.co.uk/news/politics/1383306/Brexit-live-latest-brexit-deal-Northern-Ireland-customs-boris-johnson-john-redwood
          "Brexit LIVE: Laura Kuenssberg...shape the UK's relationship with the EU."
        '''
        with suppress(Exception):
            article_itemprop_mainentity = html.find('article',
                                                    {'itemprop': 'mainEntity'})
            article_itemprop_mainentity = self.decompose_junk_tags(
                article_itemprop_mainentity)
            articlebody_list.append(
                self.text_cleaning(
                    self.remove_html_tags(
                        article_itemprop_mainentity.get_text(separator=" "))))
        '''
        Tested on
        * https://www.nytimes.com/2020/01/31/learning/is-it-offensive-for-sports-teams-and-their-fans-to-use-native-american-names-imagery-and-gestures.html
          "student opinion...teachers across the country."
        * https://www.nytimes.com/2020/01/09/world/middleeast/iran-plane-crash-ukraine.html
          "Iranian Missile Accidentally Brought...Continue reading the main story"
        '''
        with suppress(Exception):
            article = html.find('article')
            article = self.decompose_junk_tags(article)
            articlebody_list.append(
                self.text_cleaning(
                    self.remove_html_tags(article.get_text(separator=" "))))
        '''
        Tested on
        * https://www.oneindia.com/india/will-make-bengal-police-lick-boots-if-bjp-comes-to-power-in-next-assembly-elections-raju-banerjee-3181010.html
          "Kolkata, Nov 25:...where only TMC's rules prevail"."
        * https://www.oneindia.com/india/cyclone-nivar-to-hit-tn-with-winds-at-145-kmph-puducherry-lg-kiran-bedi-appeals-people-to-stay-safe-3181023.html
          "Chennai, Puducherry, Nov 25:...centres that are ready to occupy."
        '''
        with suppress(Exception):
            all_paras_text = []
            all_paras = html.find_all('p')
            for para in all_paras:
                para = self.decompose_junk_tags(para)
                all_paras_text.append(self.text_cleaning(para.get_text()))
            all_paras_text = " ".join(all_paras_text)
            articlebody_list.append(all_paras_text)
        '''
        Tested on
        * https://www.thehindubusinessline.com/todays-paper/tp-news/article33274819.ece
          "Paper mills have blamed rising waste...COMMENTS"
        * https://www.thehindubusinessline.com/money-and-banking/delegation-of-ambassadors-high-commissionersvisits-bharat-biotech-to-discuss-progress-of-covaxin/article33289689.ece
          "A delegation of 70 Ambassadors...COMMENTS"
        '''
        with suppress(Exception):
            div_class_contentbody = html.find(
                'div', {'class': 'contentbody inf-body'})
            div_class_contentbody = self.decompose_junk_tags(
                div_class_contentbody)
            articlebody_list.append(
                self.text_cleaning(
                    self.remove_html_tags(
                        div_class_contentbody.div.get_text(separator=" "))))
        '''
        Tested on
        * https://www.cnbc.com/2020/12/25/covid-stimulus-why-lawmakers-hope-trump-signs-the-bill-very-quietly.html
          "VIDEO...he wants bigger stimulus checks.”"
        * https://www.cnbc.com/2020/12/25/biden-and-trump-christmas-messages.html
          "Combination picture of Democratic U.S....Adam Edelman is a political reporter for NBC News."
        '''
        with suppress(Exception):
            div_data_module_article_body = html.find(
                'div', {'data-module': 'ArticleBody'})
            div_data_module_article_body = self.decompose_junk_tags(
                div_data_module_article_body)
            articlebody_list.append(
                self.text_cleaning(
                    self.remove_html_tags(
                        div_data_module_article_body.get_text(separator=" "))))
        with suppress(Exception):
            div_featured_content = html.find(
                'div', {'data-module': 'featuredContent'})
            div_featured_content = self.decompose_junk_tags(
                div_featured_content)
            articlebody_list.append(
                self.text_cleaning(
                    self.remove_html_tags(
                        div_featured_content.get_text(separator=" "))))
        with suppress(Exception):
            div_data_module_liveblog = html.find(
                'div', {'data-module': 'LiveBlogBody'})
            div_data_module_liveblog = self.decompose_junk_tags(
                div_data_module_liveblog)
            articlebody_list.append(
                self.text_cleaning(
                    self.remove_html_tags(
                        div_data_module_liveblog.get_text(separator=" "))))
        '''
        Tested on
        * http://archive.indianexpress.com/news/vikram-to-play-villain-in-heropanti/1214798/
          "Related...abusive, obscene, inflammatory, derogatory or defamatory."
        * http://archive.indianexpress.com/news/the-role-i-d-die-for-with-arif-zakaria/1214797/
          "Related...abusive, obscene, inflammatory, derogatory or defamatory."
        '''
        with suppress(Exception):
            div_class_ie_content_story = html.find(
                'div', {'class': 'ie2013-contentstory'})
            div_class_ie_content_story = self.decompose_junk_tags(
                div_class_ie_content_story)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_ie_content_story.get_text(separator=' ')))
        '''
        Tested on
        * https://indianexpress.com/article/news-archive/days-are-not-far-when-kashmiri-pandits-would-return-to-their-homes-with-dignity-jk-bjp-4842449/
          "MLCs Surinder Ambardar...Taploo and other martyrs."
        * https://indianexpress.com/article/news-archive/head-constable-suspended-and-challaned-for-talking-on-cell-phone-while-driving-in-chandigarh-4836554/
          "Also, a departmental probe has been ordered...took away his driving licence."
        '''
        with suppress(Exception):
            div_id_pcl_full_content = html.find('div',
                                                {'id': 'pcl-full-content'})
            div_id_pcl_full_content = self.decompose_junk_tags(
                div_id_pcl_full_content)
            articlebody_list.append(
                self.text_cleaning(
                    div_id_pcl_full_content.get_text(separator=' ')))
        '''
        Tested on
        * https://www.dailypioneer.com/2020/state-editions/punjab-cm-launches----diginest----mobile-app-to-ensure-digital-access-to-state-govt-directory.html
          "To bring in more automation and efficacy...the end-to-end process."
        * https://www.dailypioneer.com/2020/state-editions/hc-seeks-reply-from-state-in-2-weeks-on-adi-shankaracharya---s-samadhi.html
          "The Uttarakhand High Court has sought a reply...the petitioner added."
        '''
        with suppress(Exception):
            div_class_itemprop_articlebody = html.find(
                'div', {
                    'class': 'newsDetailedContent',
                    'itemprop': 'articleBody'
                })
            div_class_itemprop_articlebody = self.decompose_junk_tags(
                div_class_itemprop_articlebody)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_itemprop_articlebody.get_text(separator=' ')))
        '''
        Tested on
        * https://www.financialexpress.com/archive/delhi-power-crisis-gets-worse-arvind-kejriwal-warns-discom-licences-could-be-cancelled/1222283/
          "Barring a last minute order...500 MW of power supply from early February 2014."
        * https://www.financialexpress.com/archive/northeast-student-nido-tania-beaten-to-death-in-delhi-shocked-community-demands-action/1222157/
          "In a shocking incidence of violence...arrest the culprits immediately and to punish them severely."
        '''
        with suppress(Exception):
            div_class_running_text = html.find('div', {'class': 'runningtext'})
            div_class_running_text = self.decompose_junk_tags(
                div_class_running_text)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_running_text.get_text(separator=' ')))
        '''
        Tested on
        * https://www.euronews.com/2020/12/09/the-eu-must-leverage-closer-trade-ties-with-uzbekistan-to-ensure-progress-on-human-rights-
          "Since coming to power four years ago,...to send pitches or submissions and be part of the conversation."
        * https://www.euronews.com/2020/12/08/election-misinformation-isn-t-an-american-phenomenon-it-s-spreading-across-europe-too-view
          "The certification of election results...to send pitches or submissions and be part of the conversation."
        '''
        with suppress(Exception):
            div_class_js_article = html.find('div', {
                'class':
                'c-article-content js-article-content article__content'
            })
            div_class_js_article = self.decompose_junk_tags(
                div_class_js_article)
            articlebody_list.append(
                self.text_cleaning(
                    div_class_js_article.get_text(separator=' ')))
        '''
        Tested on
        * https://www.nytimes.com/2020/01/14/books/review-serious-noticing-james-wood.html
          "Early in his career, James Wood,...“To save life from itself.”"
        * https://www.nytimes.com/2020/01/31/learning/is-it-offensive-for-sports-teams-and-their-fans-to-use-native-american-names-imagery-and-gestures.html
          "Find all our Student Opinion questions here. Native American names and symbols...once your comment is accepted, it will be made public."
        '''
        with suppress(Exception):
            section_name_articlebody = html.find('section',
                                                 {'name': "articleBody"})
            section_name_articlebody = self.decompose_junk_tags(
                section_name_articlebody)
            articlebody_list.append(
                self.text_cleaning(
                    section_name_articlebody.get_text(separator=' ')))
        '''
        Tested on
        * https://www.business-standard.com/article/markets/auto-psu-stocks-to-outperform-in-the-short-term-vinay-rajani-of-hdfc-sec-121011300139_1.html
          "Nifty is in continuation of an uptrend...The analyst doesn't have any holding in the stock. Views are personal."
        * https://www.business-standard.com/article/international/wb-economist-china-will-need-to-learn-to-restructure-emerging-market-debt-121011300034_1.html
          "WASHINGTON (Reuters) - Increasing debt distress in...the content is auto-generated from a syndicated feed.)"
        '''
        with suppress(Exception):
            span_class_p_content = html.find('span', {'class': 'p-content'})
            span_class_p_content = self.decompose_junk_tags(
                span_class_p_content)
            articlebody_list.append(
                self.text_cleaning(
                    span_class_p_content.get_text(separator=' ')))

        articlebody_list = [body for body in articlebody_list if body != '']
        if not articlebody_list:
            return ""
        best_articlebody = max(articlebody_list, key=len)
        return best_articlebody
