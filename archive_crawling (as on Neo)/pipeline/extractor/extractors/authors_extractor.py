"""Script to extract the authors from a news article."""

import json
import logging
import re
from contextlib import suppress

from bs4 import BeautifulSoup
from retrying import retry

from .abstract_extractor import AbstractExtractor


class AuthorsExtractor(AbstractExtractor):
    """
    Custom Authors Extractor
    * Used over newspaper_extractor due to better performance
    * Returns a list of unique author values extracted from an article.
    """
    def __init__(self):  # pylint: disable=super-init-not-called
        """Init function."""
        self.name = "authors_extractor"

    def _author(self, item):
        """Returns the extracted authors from a news article."""
        html_item = item['spider_response']
        html = BeautifulSoup(html_item.body, 'html5lib')
        authors = " "
        try:
            authors = self.authors_mega(html)
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(exception)
        return authors

    def text_cleaning(self, text):  # pylint: disable=no-self-use
        """Function to clean the authors string."""
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

    @retry(stop_max_attempt_number=3,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def authors_mega(self, html):  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        """
        Finds all unique author strings in a news article and returns a
        concatenated string with their values.
        """
        authors_list = []
        with suppress(Exception):
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    '''
                    Tested on:
                    * https://economictimes.indiatimes.com/news/economy/policy/government-mops-up-rs-8660-cr-from-disinvestment-in-02/articleshow/33105933.cms
                      "author": {"@type": "Thing", "name": "TNN"}
                    * https://timesofindia.indiatimes.com/city/bengaluru/ISROs-second-launch-pad-to-be-sent-by-March-end/articleshow/3801270.cms
                      "author":{"@type":"Thing","name":"TNN"}
                    '''
                    if data["author"] and not isinstance(data["author"], list):
                        authors_list.append(
                            self.text_cleaning(data['author']['name']))
                    elif data["author"] and isinstance(data["author"], list):
                        '''
                        Tested on:
                        * https://www.nytimes.com/2020/01/31/learning/is-it-offensive-for-sports-teams-and-their-fans-to-use-native-american-names-imagery-and-gestures.html
                          "author":[{"@context":"http://schema.org","@type":"Person","url":"https://www.nytimes.com/by/jeremy-engle","name":"Jeremy Engle"}]
                        * https://www.nytimes.com/2020/01/09/world/middleeast/iran-plane-crash-ukraine.html
                          "author":[{"@context":"http://schema.org","@type":"Person","url":"https://www.nytimes.com/by/julian-e-barnes","name":"Julian E. Barnes"}
                        '''
                        with suppress(Exception):
                            authors_list.append(
                                self.text_cleaning(data['author'][0]['name']))
                        with suppress(Exception):
                            authors_list.append(
                                self.text_cleaning(data["author"][0]))
                        break
                '''
                Tested on:
                * https://www.dailymail.co.uk/news/article-2937206/Halal-abattoir-staff-hacked-taunted-sheep-One-worker-sacked-three-suspended-caught-camera-carrying-horrifying-routine-abuse.html
                  <script type="application/ld+json">{"@type":"WebPage", "author":{"@type":"Person","name":"By Chris Brooke for the Daily Mail Dan Bloom for MailOnline"}...}</script>
                * https://www.dailymail.co.uk/tvshowbiz/article-2937220/Lucy-Mecklenburgh-Thom-Evans-Robbie-Savage-help-PG-Tips-Monkey-prepare-Red-Nose-Day-Challenge.html
                  <script type="application/ld+json">{"@type":"WebPage", "author":{"@type":"Person","name":"By MailOnline Reporter"}...}</script>
                '''
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["@type"] == "Article" or data["@type"] == "WebPage":
                        if isinstance(data["author"], list):
                            authors_list.append(
                                self.text_cleaning(data["author"][0]["name"]))
                        elif not isinstance(data["author"], list):
                            authors_list.append(
                                self.text_cleaning(data["author"]["name"]))
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["@type"] == "VideoObject":
                        if isinstance(data["publisher"], list):
                            authors_list.append(
                                self.text_cleaning(
                                    data["publisher"][0]["name"]))
                            '''
                            Tested on:
                            * https://www.usatoday.com/videos/news/2020/11/17/north-carolina-elections-director-blocked-her-dead-mothers-vote/6320770002/
                              "publisher":{"@type":"Organization","name":"USA TODAY"...}
                            * https://www.usatoday.com/videos/entertainment/celebrities/2020/11/15/duchess-kate-concludes-her-successful-hold-still-pandemic-photo-project/6294741002/
                              "publisher":{"@type":"Organization","name":"USA TODAY"...}
                            '''
                        elif not isinstance(data["publisher"], list):
                            authors_list.append(
                                self.text_cleaning(data["publisher"]["name"]))
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle":
                        if isinstance(data["author"], list):
                            authors_list.append(
                                self.text_cleaning(data["author"][0]))
                            '''
                            Tested on:
                            * https://www.express.co.uk/news/politics/1369685/brexit-news-uk-eu-trade-deal-france-fishing-emmanuel-macron-no-deal-latest
                              "author":"Paul Withers"
                            * https://www.express.co.uk/news/world/1369648/India-news-mystery-illness-coronavirus-covid-Andhra-Pradesh-eluru-disease-cause-ont
                              "author":"Edward Browne"
                            '''
                        elif not isinstance(data["author"], list):
                            authors_list.append(
                                self.text_cleaning(data["author"]))
                '''
                Tested on:
                * https://www.cnbc.com/2020/11/01/election-2020-live-updates-biden-in-pennsylvania-as-trump-barnstorms-the-country.html
                  <script type="application/ld+json">{"@type":"NewsArticle", "creator":["CNBC.com staff"]}</script>
                * https://www.cnbc.com/2020/12/24/wonder-woman-1984-box-office-preview-what-the-superhero-film-can-make.html
                  <script type="application/ld+json">{"@type":"NewsArticle", "creator":["Sarah Whitten"]}</script>
                '''
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["creator"]:
                        if isinstance(data["creator"], list):
                            authors_list.append(
                                self.text_cleaning(data["creator"][0]))
                        if not isinstance(data["creator"], list):
                            authors_list.append(
                                self.text_cleaning(data["creator"]))
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if data["publisher"]["@type"] == "Organization":
                        authors_list.append(
                            self.text_cleaning(data["publisher"]["name"]))
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if data["author"]:
                        authors_list.append(self.text_cleaning(data["author"]))
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if data[0]['@type'] == 'NewsArticle' and data[0]['author']:
                        authors_list.append(
                            self.text_cleaning(data[0]['author']))
                '''
                Tested on:
                * https://www.thehindubusinessline.com/money-and-banking/rbi-to-kotak-mahindra-bank-no-dividend-payment-on-perpetual-non-cumulative-preference-shares/article33299037.ece
                  <script type="application/ld+json">{"@type": "Organization","name": "The Hindu BusinessLine",...}</script>
                * https://indianexpress.com/article/news-archive/days-are-not-far-when-kashmiri-pandits-would-return-to-their-homes-with-dignity-jk-bjp-4842449/
                  <script type="application/ld+json">{"@type":"Person","name":"PTI"...}</script>
                '''
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if (data["@type"] == "Person" or data["@type"]
                            == "Organization") and data["name"]:
                        authors_list.append(self.text_cleaning(data["name"]))
                        if isinstance(data["name"], list):
                            authors_list.append(
                                self.text_cleaning(data["name"][0]))
                with suppress(Exception):
                    if "author" in script.string:
                        authors_list.append(
                            self.text_cleaning(
                                script.string.split("author\": {")[1].split(
                                    "name\": \"")[1].split("\"")[0]))
                '''
                Tested on:
                * https://www.euronews.com/2020/12/09/budapest-and-warsaw-protest-their-governments-budget-veto-by-lighting-monuments-eu-blue
                  <script type="application/ld+json">{"@graph": ["author": {"@type": "Person","name": "Euronews","url": "https://www.euronews.com/","sameAs": "https://twitter.com/euronews"}]}</script>
                * https://www.euronews.com/2020/12/09/the-eu-must-leverage-closer-trade-ties-with-uzbekistan-to-ensure-progress-on-human-rights-
                  <script type="application/ld+json">{"@graph": ["author": {"@type": "Person","name": "Euronews","url": "https://www.euronews.com/","sameAs": "https://twitter.com/euronews"}]}</script>
                '''
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    authors_list.append(
                        self.text_cleaning(
                            data['@graph'][0]['author']['name']))
        '''
        Tested on:
        * https://www.independent.co.uk/arts-entertainment/tv/news/bridgerton-violet-actor-ruth-gemmell-tracy-beaker-b1780757.html
          <script type="application/json">{"article_author":"Isobel Lewis"}</script>
        * https://www.independent.co.uk/life-style/royal-family/the-crown-queen-cousins-nerissa-katherine-bowes-lyon-b1721187.html
          <script type="application/json">{"article_author":"Sarah Young"}</script>
        '''
        with suppress(Exception):
            scripts = html.find_all('script', {'type': 'application/json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    authors_list.append(
                        self.text_cleaning(data["article_author"]))
        with suppress(Exception):
            span_class_ag = html.find('span', {'class': 'ag'})
            '''
            Tested on:
            * https://economictimes.indiatimes.com/news/politics-and-nation/modi-toiling-with-rs-10000-per-annum-payment-to-farmers/articleshow/67385159.cms
              <span class="ag"><img style="vertical-align: middle;" title="ET Now" alt="ET Now" src="https://img.etimg.com/photo/64781824.cms"></span>
            '''
            if span_class_ag.img:
                if span_class_ag.img.get('title') not in authors_list:
                    authors_list.append(span_class_ag.img.get('title'))
                    '''
                    Tested on:
                    * https://economictimes.indiatimes.com/news/politics-and-nation/centre-always-ready-for-talks-dialogue-would-fetch-solution-manohar-lal-khattar-to-farmers/articleshow/79444811.cms
                      <span class="ag">PTI</span>
                    '''
            else:
                if span_class_ag.text not in authors_list:
                    authors_list.append(span_class_ag.text)
        with suppress(Exception):
            span_itemprop_author = html.find('span', {'itemprop': 'author'})
            authors_list.append(self.text_cleaning(span_itemprop_author.text))
            for author in span_itemprop_author.children:
                authors_list.append(self.text_cleaning(author.text))
            with suppress(Exception):
                for author in span_itemprop_author:
                    for author_meta in author.find_all('meta',
                                                       {'itemprop': 'name'}):
                        authors_list.append(
                            self.text_cleaning(author_meta['content']))
            with suppress(Exception):
                for author in span_itemprop_author.find_all(
                        'a', {'rel': 'author'}):
                    authors_list.append(self.text_cleaning(author.text))
        '''
        Tested on:
        * https://www.indiatoday.in/sports/cricket/story/a-win-at-gabba-will-give-india-their-greatest-test-series-victory-ever-says-akhtar-1758619-2021-01-13
          <span itemprop="author" itemscope="" itemtype="https://schema.org/Person"><dt class="title" itemprop="name"> Rahul Bhatnagar</dt> </span>
        * https://www.indiatoday.in/technology/news/story/amazon-great-republic-day-sale-announced-from-january-20-deals-bank-offers-and-more-1758622-2021-01-13
          <span itemprop="author" itemscope="" itemtype="https://schema.org/Person"><dt class="title" itemprop="name"> <a title="Ketan Pratap" href="/author/ketan-pratap" target="_blank">Ketan Pratap</a>...</span>
        '''
        with suppress(Exception):
            span_itemprop_authors = html.find_all('span',
                                                  {'itemprop': 'author'})
            for span_author in span_itemprop_authors:
                authors_list.append(self.text_cleaning(span_author.text))
                with suppress(Exception):
                    for element in span_author:
                        authors_list.append(self.text_cleaning(element.text))
        '''
        Tested on:
        * https://www.espncricinfo.com/story/icc-women-s-rankings-england-s-sarah-glenn-reaches-career-best-t20i-rankings-meg-lanning-moves-up-1234107
          <span class="author">ESPNcricinfo staff</span>
        * https://www.espncricinfo.com/story/ipl-2020-jofra-archer-thriving-in-different-type-of-pressure-at-ipl-says-rajasthan-royals-team-mate-jos-buttler-1234126
          <span class="author">Nagraj Gollapudi</span>
        '''
        with suppress(Exception):
            span_class_author = html.find('span', {'class': 'author'})
            authors_list.append(self.text_cleaning(span_class_author.text))
        '''
        Tested on:
        * https://www.deccanherald.com/national/east-and-northeast/switching-from-poppy-to-cardamom-arunachal-district-farmers-set-to-taste-success-in-2021-933703.html
          <a class="sanspro-reg article-author__name" href="/author/sumir-karmakar">Sumir Karmakar, </a>; <a class="sanspro-reg article-author__name" href="/author/dhns">DHNS, </a>
        * https://www.deccanherald.com/5-dk-take-part-special-705298.html
          <a class="sanspro-reg article-author__name" href="/author/naina-j-a">Naina J A, </a>
        '''
        with suppress(Exception):
            link_class_sanspro = html.find_all(
                'a', {'class': 'sanspro-reg article-author__name'})
            for author in link_class_sanspro:
                authors_list.append(self.text_cleaning(author.text))
        '''
        Tested on:
        * https://www.deccanherald.com/content/507817/children-adopted-through-state-governmentsmother.html
          <span class="sanspro-reg article-author__name">New Delhi, Oct 21, 2015, (PTI), </span>
        * https://www.deccanherald.com/content/273743/pak-needs-explain-osamas-presence.html
          <span class="sanspro-reg article-author__name">Washington, Aug 23, 2012, PTI:, </span>
        '''
        with suppress(Exception):
            span_class_sanspro = html.find_all(
                'span', {'class': 'sanspro-reg article-author__name'})
            for author in span_class_sanspro:
                authors_list.append(self.text_cleaning(author.text))
        '''
        Tested on:
        * https://sports.ndtv.com/cricket/we-cant-influence-indian-high-commission-for-visas-pcb-1594242
          <span class="pst-by_lnk">Written by <span itemprop="name">Press Trust of India</span></span>
        * https://sports.ndtv.com/cricket/india-new-zealand-world-test-championship-final-in-southampton-from-june-18-22-bcci-president-sourav-ganguly-2386373
          <span class="pst-by_lnk"><span itemprop="name">Press Trust of India</span></span>
        '''
        with suppress(Exception):
            span_class_pst_bylnk = html.find_all('span',
                                                 {'class': 'pst-by_lnk'})
            for span in span_class_pst_bylnk:
                if span.find('span', {'itemprop': 'name'}):
                    authors_list.append(self.text_cleaning(span.text))
        with suppress(Exception):
            div_class_td_post_author_name = html.find(
                'div', {'class': 'td-post-author-name'})
            authors_list.append(
                self.text_cleaning(div_class_td_post_author_name.text))
        '''
        Tested on:
        * https://www.independent.co.uk/arts-entertainment/tv/news/bridgerton-violet-actor-ruth-gemmell-tracy-beaker-b1780757.html
          <meta property="article:author_name" content="Isobel Lewis">
        * https://www.standard.co.uk/news/uk/christmas-bubbles-science-sage-advice-b79264.html
          <meta property="article:author_name" content="April Roach">
        '''
        with suppress(Exception):
            meta_property_author_name = html.find(
                'meta', {'property': 'article:author_name'})
            authors_list.append(
                self.text_cleaning(meta_property_author_name['content']))
        '''
        Tested on:
        * https://www.dailymail.co.uk/sport/football/article-8986989/The-key-battles-Tottenhams-table-clash-Chelsea-Stamford-Bridge.html
          <meta property="article:author" content="https://www.dailymail.co.uk/home/search.html?s=&amp;authornamef=Tom+Farmery+For+Mailonline">
        * https://www.dailymail.co.uk/sciencetech/article-8988053/NASA-astronaut-Victor-Glover-shares-video-SPACE.html
          <meta property="article:author" content="https://www.facebook.com/DailyMail">
        '''
        with suppress(Exception):
            meta_property_article_author = html.find(
                'meta', {'property': 'article:author'})
            authors_list.append(
                self.text_cleaning(meta_property_article_author['content']))
            '''
            Tested on:
            * https://www.oneindia.com/international/xi-jinping-finally-congratulates-biden-hopes-us-china-will-uphold-spirit-of-non-confrontation-3181336.html
              <meta property="article:author" content="Madhuri Adnal" data-author="pti-Madhuri Adnal" data-match-video="true">
            * https://www.oneindia.com/india/delhi-riots-umar-khalid-didn-t-take-security-to-conspiratorial-meetings-says-charge-sheet-3181302.html
              <meta property="article:author" content="Simran Kashyap" data-author="pti-Madhuri Adnal" data-match-video="true">
            '''
            with suppress(Exception):
                authors_list.append(
                    self.text_cleaning(
                        meta_property_article_author['data-author'].split(
                            "-")[1]))
        '''
        Tested on:
        * https://www.thehindubusinessline.com/todays-paper/tp-news/article33274819.ece
          <meta name="twitter:creator" content="Suresh P Iyengar">
        * https://www.thehindubusinessline.com/money-and-banking/delegation-of-ambassadors-high-commissionersvisits-bharat-biotech-to-discuss-progress-of-covaxin/article33289689.ece
          <meta name="twitter:creator" content="Our Bureau.">
        '''
        with suppress(Exception):
            meta_name_twitter_creator = html.find('meta',
                                                  {'name': 'twitter:creator'})
            authors_list.append(
                self.text_cleaning(meta_name_twitter_creator['content']))
        '''
        Tested on:
        * https://scroll.in/article/985739/ground-report-in-haryana-farmer-protests-run-into-a-caste-divide
          <meta name="dcterms.creator" content="Shoaib Daniyal &amp; Vijayta Lalwani">
        * https://scroll.in/reel/985764/why-beginning-on-mubi-is-a-film-you-cannot-miss
          <meta name="dcterms.creator" content="Rashid Irani">
        '''
        with suppress(Exception):
            meta_name_dcterms_creator = html.find('meta',
                                                  {'name': 'dcterms.creator'})
            authors_list.append(
                self.text_cleaning(meta_name_dcterms_creator['content']))
        '''
        Tested on:
        * https://www.standard.co.uk/reveller/restaurants/tier-2-single-household-any-table-size-restaurants-b79359.html
          <meta property="article:author_name" content="David Ellis">
        * https://www.standard.co.uk/news/uk/jeremy-corbyn-joke-hignfy-bbc-b79298.html
          <meta property="article:author_name" content="Lizzie Edmonds">
        '''
        with suppress(Exception):
            meta_name_article_author_name = html.find(
                'meta', {'name': 'article:author_name'})
            authors_list.append(
                self.text_cleaning(meta_name_article_author_name['content']))
        '''
        Tested on:
        * https://www.business-standard.com/article/international/walmart-disney-suspend-contributions-to-us-lawmakers-who-opposed-biden-win-121011300172_1.html
          <meta name="author" content="Reuters">
        * https://www.business-standard.com/article/international/us-house-committee-releases-report-supporting-donald-trump-s-impeachment-121011300125_1.html
          <meta name="author" content="ANI">
        '''
        with suppress(Exception):
            meta_name_author = html.find('meta', {'name': 'author'})
            authors_list.append(self.text_cleaning(
                meta_name_author['content']))
        '''
        Tested on:
        * https://www.nytimes.com/2020/01/07/us/politics/joe-biden-elizabeth-warren-foreign-policy.html
          <meta data-rh="true" name="byl" content="By Katie Glueck and Shane Goldmacher">
        * https://www.nytimes.com/2020/01/09/world/middleeast/iran-plane-crash-ukraine.html
          <meta data-rh="true" name="byl" content="By Julian E. Barnes, Eric Schmitt, Anton Troianovski and Natalie Kitroeff">
        '''
        with suppress(Exception):
            meta_name_byline = html.find('meta', {'name': 'byl'})
            authors_list.append(self.text_cleaning(
                meta_name_byline['content']))
        '''
        Tested on:
        * https://www.financialexpress.com/archive/rbi-governor-raghuram-rajan-effects-dramatic-shift-as-india-quietly-begins-tryst-with-inflation-targeting/1221591/
          <meta itemprop="author" content="Reuters">
        * https://www.financialexpress.com/archive/govt-kills-two-reforms-raises-lpg-cap-snaps-its-aadhaar-link-rahul-gandhis-wish-will-cost-rs-5000-cr/1222008/
          <meta itemprop="author" content="Express news service">
        '''
        with suppress(Exception):
            meta_itemprop_author = html.find('meta', {'itemprop': 'author'})
            authors_list.append(
                self.text_cleaning(meta_itemprop_author['content']))
        '''
        Tested on:
        * https://nypost.com/2020/12/31/country-singer-reunited-with-cat-after-nashville-bombing/
          <div id="author-byline"><p class="byline">By <a class="jorge-fittz-gibbon" href="https://nypost.com/author/jorge-fittz-gibbon/"><span>Jorge Fitz-Gibbon</span></a></p>...</div>
        * https://nypost.com/2019/10/30/campaign-for-disgraced-ex-cop-daniel-pantaleo-raises-more-than-170k/
          <div id="author-byline"><p class="byline">By <a class="craig-mccarthy" href="https://nypost.com/author/craig-mccarthy/"><span>Craig McCarthy</span></a></p>...</div>
        '''
        with suppress(Exception):
            div_id_author_byline = html.find('div', {'id': 'author-byline'})
            for link in div_id_author_byline.p.find_all('a'):
                authors_list.append(self.text_cleaning(link.text))
        '''
        Tested on:
        * https://www.usatoday.com/story/sports/mls/2020/12/07/mls-cup-2020-seattle-sounders-advance-play-columbus-crew-title/6487291002/
          <div class="gnt_ar_by"><a href="https://www.dispatch.com/staff/3334168001/jacob-myers/" class="gnt_ar_by_a gnt_ar_by_a__fi">Jacob Myers</a><div class="gnt_ar_pb">The Columbus Dispatch</div></div>
        * https://www.usatoday.com/story/news/nation/2020/12/07/north-atlantic-right-whale-endangered-species-newborns/6484190002/
          <div class="gnt_ar_by"><a href="/staff/2647867001/elinor-aspegren/" class="gnt_ar_by_a gnt_ar_by_a__fi">Elinor Aspegren</a><div class="gnt_ar_pb">USA TODAY</div></div>
        '''
        with suppress(Exception):
            div_class_gnt_arby = html.find('div', {'class': 'gnt_ar_by'})
            for link in div_class_gnt_arby.find_all('a'):
                authors_list.append(self.text_cleaning(link.text))
        '''
        Tested on:
        * https://www.dailymail.co.uk/news/article-2937206/Halal-abattoir-staff-hacked-taunted-sheep-One-worker-sacked-three-suspended-caught-camera-carrying-horrifying-routine-abuse.html
          <a href="/home/search.html?s=&amp;authornamef=Dan+Bloom+for+MailOnline" class="author" rel="nofollow">Dan Bloom for MailOnline</a
        * https://www.dailymail.co.uk/tvshowbiz/article-2937220/Lucy-Mecklenburgh-Thom-Evans-Robbie-Savage-help-PG-Tips-Monkey-prepare-Red-Nose-Day-Challenge.html
          <a href="/home/search.html?s=&amp;authornamef=MailOnline+Reporter" class="author" rel="nofollow">MailOnline Reporter</a>
        '''
        with suppress(Exception):
            link_class_author = html.find_all('a', {'class': 'author'})
            for author_link in link_class_author:
                authors_list.append(self.text_cleaning(author_link.text))
        '''
        Tested on:
        * https://www.oneindia.com/india/cyclone-nivar-to-hit-tn-with-winds-at-145-kmph-puducherry-lg-kiran-bedi-appeals-people-to-stay-safe-3181023.html
          <div class="io-author" style="display: none">oi-Briti Roy Barman</div>
        * https://www.oneindia.com/india/will-make-bengal-police-lick-boots-if-bjp-comes-to-power-in-next-assembly-elections-raju-banerjee-3181010.html
          <div class="io-author" style="display: none">oi-Ajay Joseph Raj P</div>
        '''
        with suppress(Exception):
            div_class_io_author = html.find('div', {'class': 'io-author'})
            authors_list.append(
                self.text_cleaning(div_class_io_author.text.split("-")[1]))
        '''
        Tested on:
        * http://archive.indianexpress.com/news/indias-average-economic-growth-during-upa-i/1214985/0
          <div class="story-date"> <a href="/columnist/ptindia/">PTI</a>...</div>
        '''
        with suppress(Exception):
            div_class_storydate = html.find('div', {'class': 'story-date'})
            for link in div_class_storydate.find_all('a'):
                if 'columnist' in link.get('href'):
                    authors_list.append(self.text_cleaning(link.text))
        '''
        Tested on:
        * https://www.oneindia.com/international/xi-jinping-finally-congratulates-biden-hopes-us-china-will-uphold-spirit-of-non-confrontation-3181336.html
          <div class="author-detail clearfix" data-author="Madhuri Adnal" data-twit-handle="">
        * https://www.oneindia.com/india/delhi-riots-umar-khalid-didn-t-take-security-to-conspiratorial-meetings-says-charge-sheet-3181302.html
          <div class="author-detail clearfix" data-author="Simran Kashyap" data-twit-handle="">
        '''
        with suppress(Exception):
            div_class_author_clearfix = html.find(
                'div', {'class': 'author-detail clearfix'})
            authors_list.append(
                self.text_cleaning(div_class_author_clearfix['data-author']))
        '''
        Tested on:
        * https://www.oneindia.com/international/xi-jinping-finally-congratulates-biden-hopes-us-china-will-uphold-spirit-of-non-confrontation-3181336.html
          <div class="posted-by">...Madhuri Adnal...</div>
        * https://www.oneindia.com/india/delhi-riots-umar-khalid-didn-t-take-security-to-conspiratorial-meetings-says-charge-sheet-3181302.html
          <div class="posted-by">...Simran Kashyap...</div>
        '''
        with suppress(Exception):
            div_class_posted_by = html.find('div', {'class': 'posted-by'})
            authors_list.append(self.text_cleaning(div_class_posted_by.text))
        '''
        Tested on:
        * https://indianexpress.com/article/world/print/four-killed-as-armed-militants-storm-5-star-hotel-in-pakistans-gwadar-port-city-police-5723193/
          <div class="editor" id="storycenterbyline">By: <a href="/agency/pti/">PTI</a>...</div>
        * https://indianexpress.com/article/news-archive/ayushman-bharat-aadhaar-mandatory-for-those-seeking-treatment-for-second-time-5390924/
          <div class="editor" id="storycenterbyline">By: <a href="/agency/pti/">PTI</a>...</div>
        '''
        with suppress(Exception):
            div_class_editor = html.find('div', {'class': 'editor'})
            for link in div_class_editor.find_all('a'):
                authors_list.append(self.text_cleaning(link.text))
        '''
        Tested on:
        * https://www.espncricinfo.com/series/vitality-blast-2020-1207645/nottinghamshire-vs-leicestershire-1st-quarter-final-1207789/match-report
          <div class="author">...George Dobell...</div>
        * https://www.espncricinfo.com/story/ipl-2020-jofra-archer-thriving-in-different-type-of-pressure-at-ipl-says-rajasthan-royals-team-mate-jos-buttler-1234126
          <div class="author">...Andrew Miller...</div>
        '''
        with suppress(Exception):
            div_class_author = html.find('div', {'class': 'author'})
            authors_list.append(self.text_cleaning(div_class_author.a.text))
        '''
        Tested on:
        * https://www.thehindubusinessline.com/money-and-banking/rbi-to-kotak-mahindra-bank-no-dividend-payment-on-perpetual-non-cumulative-preference-shares/article33299037.ece
          <a href="https://www.thehindubusinessline.com/profile/author/Our-Bureau-137009/" class="auth-nm lnk">Our Bureau.</a>
        * https://www.thehindubusinessline.com/money-and-banking/pull-payments-made-on-behalf-of-merchants-acquirer-banks-should-not-push-consumers-to-pay-for-services/article33299994.ece
          <a href="https://www.thehindubusinessline.com/profile/author/Our-Bureau-137009/" class="auth-nm lnk">Our Bureau.</a>
        '''
        with suppress(Exception):
            link_class_auth_nmlink = html.find_all('a',
                                                   {'class': 'auth-nm lnk'})
            for author in link_class_auth_nmlink:
                authors_list.append(self.text_cleaning(author.text))
        '''
        Tested on:
        * https://scroll.in/reel/985764/why-beginning-on-mubi-is-a-film-you-cannot-miss
          <article id="article-unique-985764" ... data-cb-authors="Rashid Irani">
        * https://scroll.in/article/979318/what-is-the-extent-of-caste-segregation-in-indian-villages-today-new-data-gives-us-an-idea
          <article id="article-unique-979318" ... data-cb-authors="Naveen Bharathi, Deepak Malghan, Andaleeb Rahman">
        '''
        with suppress(Exception):
            article_datacb_authors = html.find('article',
                                               {'data-cb-authors': True})
            authors_list.append(
                self.text_cleaning(article_datacb_authors['data-cb-authors']))
        '''
        Tested on:
        * https://scroll.in/article/985739/ground-report-in-haryana-farmer-protests-run-into-a-caste-divide
          <address><a href="//scroll.in/author/362" rel="author">Shoaib Daniyal</a>...</address>
        * https://scroll.in/reel/985764/why-beginning-on-mubi-is-a-film-you-cannot-miss
          <address><a href="//scroll.in/author/17926" rel="author">Rashid Irani</a></address>
        '''
        with suppress(Exception):
            address = html.find('address')
            for author in address.find_all('a', {'rel': 'author'}):
                authors_list.append(self.text_cleaning(author.text))
        '''
        Tested on:
        * https://www.cnbc.com/2020/12/25/the-plant-based-meat-industry-is-on-the-rise-but-challenges-remain.html
          <a href="https://www.cnbc.com/abigail-ng/" class="Author-authorName">Abigail Ng<span class="Author-authorUnderline"></span></a>
        * https://www.cnbc.com/2020/12/25/covid-stimulus-why-lawmakers-hope-trump-signs-the-bill-very-quietly.html
          <a href="https://www.cnbc.com/emily-deciccio/" class="Author-authorName">Emily DeCiccio<span class="Author-authorUnderline"></span></a>
        '''
        with suppress(Exception):
            link_class_authorname = html.find_all(
                'a', {'class': "Author-authorName"})
            for author in link_class_authorname:
                authors_list.append(self.text_cleaning(author.text))
        '''
        Tested on:
        * https://www.financialexpress.com/archive/rbi-governor-raghuram-rajan-effects-dramatic-shift-as-india-quietly-begins-tryst-with-inflation-targeting/1221591/
          <a id="written_by1" class="bulletProj" href="https://www.financialexpress.com/archive/columnist/reuters/">Reuters</a>
        * https://www.financialexpress.com/archive/delhi-power-crisis-gets-worse-arvind-kejriwal-warns-discom-licences-could-be-cancelled/1222283/
          <a id="written_by1" class="bulletProj" href="https://www.financialexpress.com/archive/columnist/fe-bureau/">fe Bureau</a>
        '''
        with suppress(Exception):
            link_id_written_by = html.find('a', {'id': 'written_by1'})
            authors_list.append(self.text_cleaning(link_id_written_by.text))
        with suppress(Exception):
            span_class_meta_author = html.find(
                'span', {'class': 'c-article-meta__author'})
            authors_list.append(self.text_cleaning(
                span_class_meta_author.text))
        '''
        Tested on:
        * https://www.nytimes.com/2020/01/31/learning/is-it-offensive-for-sports-teams-and-their-fans-to-use-native-american-names-imagery-and-gestures.html
          <span class="css-1baulvz last-byline">Jeremy Engle</span>
        * https://www.nytimes.com/2020/01/07/us/politics/joe-biden-elizabeth-warren-foreign-policy.html
          <span class="css-1baulvz last-byline">Shane Goldmacher</span>
        '''
        with suppress(Exception):
            span_class_last_byline = html.find('span',
                                               {'class': 'last-byline'})
            authors_list.append(self.text_cleaning(
                span_class_last_byline.text))
        if len(authors_list
               ) == 1 and authors_list[0] == '' or not authors_list:
            authors_list.append(" ")
        authors_list = [author for author in authors_list if author != '']
        authors_list = list(set(authors_list))
        authors_list = ", ".join(authors_list)
        return authors_list
