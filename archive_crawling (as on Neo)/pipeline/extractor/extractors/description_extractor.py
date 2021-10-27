"""Script to extract the description from a news article."""

import json
import logging
import re
from contextlib import suppress

from bs4 import BeautifulSoup
from retrying import retry

from .abstract_extractor import AbstractExtractor


class DescriptionExtractor(AbstractExtractor):
    """
    Custom Description Extractor
    * Used as a fallback for newspaper_extractor
    * Returns the longest string out of all extracted description values
    """
    def __init__(self):  # pylint: disable=super-init-not-called
        """Init function."""
        self.name = "description_extractor"

    def _description(self, item):
        """Returns the extracted description from a news article."""
        html_item = item['spider_response']
        html = BeautifulSoup(html_item.body, 'html5lib')
        description = " "
        try:
            description = self.description_mega(html)
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(exception)
        return description

    def text_cleaning(self, text):  # pylint: disable=no-self-use
        """Function to clean the description string."""
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

    @retry(stop_max_attempt_number=3,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def description_mega(self, html):  # pylint: disable=too-many-statements,too-many-branches
        """
        Returns the longest description from a list of all extracted description
        values.
        """
        description_list = []
        with suppress(Exception):
            '''
            Tested on
            * https://economictimes.indiatimes.com/news/economy/policy/government-mops-up-rs-8660-cr-from-disinvestment-in-02/articleshow/33105933.cms
              <meta content="The total disinvestment realisation of the government during 2002 topped Rs 8,660 crore. The cabinet committee on disinvestment (CCD) had cleared transactions worth Rs 6,168 crore during the year." name="description">
            * https://timesofindia.indiatimes.com/city/bengaluru/ISROs-second-launch-pad-to-be-sent-by-March-end/articleshow/3801270.cms
              <meta name="description" content="BANGALORE: The second launch pad for the Indian Space Research Organisation will be dispatched to Sriharikota by the end of March. The Mobile Launch P">
            '''
            meta_name_description = html.find('meta', {'name': 'description'})
            description_list.append(
                self.text_cleaning(meta_name_description['content']))

        with suppress(Exception):
            '''
            Tested on
            * https://www.deccanherald.com/content/1368/agriculture-department-urged-regulate-fertilisers.html
              <meta property="og:description" content="Farmers will be happy only if they get good rains and sufficient fertilisers. They were is deep trouble due to the improper supply of fertilisers.">
            * https://sports.ndtv.com/cricket/we-cant-influence-indian-high-commission-for-visas-pcb-1594242
              <meta property="og:description" content="Pakistan Cricket Board made it clear that it had done everything under its power to get the visas for its cricketers to play in the IPL next year.">
            '''
            meta_property_og_description = html.find(
                'meta', {'property': 'og:description'})
            description_list.append(
                self.text_cleaning(meta_property_og_description['content']))

        with suppress(Exception):
            '''
            Tested on
            * https://www.independent.co.uk/news/world/americas/elijah-mcclain-death-colorado-police-black-lives-matter-george-floyd-police-a9584366.html
              <meta name="twitter:description" content="'Demand these officers are taken off duty, and that a more in-depth investigation is held', page reads">
            * https://nypost.com/2010/09/27/brooklyn-tea-party-rallies-against-ground-zero-mosque-multiculturalism/
              <meta name="twitter:description" content="About 125 people gathered at a recent Bay Ridge rally of the Brooklyn Tea Party to protest a variety of hot subjects — especially the planned Ground Zero mosque, according to a Brooklyn Ink">
            '''
            meta_name_twitter_description = html.find(
                'meta', {'name': 'twitter:description'})
            description_list.append(
                self.text_cleaning(meta_name_twitter_description['content']))

        with suppress(Exception):
            '''
            Tested on
            * https://www.standard.co.uk/news/uk/boris-johnson-u-turn-free-school-meals-marcus-rashford-a4470506.html
              <meta property="twitter:description" content="'THIS is England in 2020'">
            * https://www.express.co.uk/news/politics/1369685/brexit-news-uk-eu-trade-deal-france-fishing-emmanuel-macron-no-deal-latest
              <meta property="twitter:description" content="FRENCH fishermen have lashed out at Emmanuel Macron, warning he is playing a &quot;dangerous game&quot; and has &quot;overstepped the mark&quot; by threatening to veto a post-Brexit trade deal with the UK.">
            '''
            meta_property_twitter_desc = html.find(
                'meta', {'property': 'twitter:description'})
            description_list.append(
                self.text_cleaning(meta_property_twitter_desc['content']))

        with suppress(Exception):
            '''
            Tested on
            * https://www.indiatoday.in/india/story/pm-modi-launch-covid-vaccination-drive-jan-16-cowin-app-coronavirus-covaxin-covishield-1758628-2021-01-13
              <meta itemprop="description" content="Prime Minister Narendra Modi will kickstart the Covid-19 vaccination programme in India with a virtual launch on January 16, sources have told India Today.">
            * https://indianexpress.com/article/world/print/four-killed-as-armed-militants-storm-5-star-hotel-in-pakistans-gwadar-port-city-police-5723193/
              <meta itemprop="description" content="A shootout between the militants and the security forces broke out at the hotel as the anti-terrorism force, the Army and the Frontier Corps were called in, Gwadar Station House Officer (SHO) Aslam Bangulzai said.">
            '''
            meta_itemprop_description = html.find('meta',
                                                  {'itemprop': 'description'})
            description_list.append(
                self.text_cleaning(meta_itemprop_description['content']))

        with suppress(Exception):
            '''
            Tested on
            * https://www.cnbc.com/2020/12/25/the-plant-based-meat-industry-is-on-the-rise-but-challenges-remain.html
              <meta itemprop="description" name="description" content="Demand for meat alternatives has grown and will continue to rise, but the industry still has hurdles to overcome in different parts of the world, analysts said.">
            * https://www.oneindia.com/india/congress-leader-dk-shivakumar-to-appear-before-cbi-in-disproportionate-assets-case-today-3180984.html
              <meta name="description" itemprop="description" content="On October 5, the CBI conducted raids at 14 locations, including in Karnataka, Delhi and Mumbai at the premises belonging to Shivakumar and others, and recovered Rs 57 lakh cash and several documents, including property documents, bank related information, computer hard disk. ">
            '''
            meta_name_itemprop_description = html.find(
                'meta', {
                    'name': 'description',
                    'itemprop': 'description'
                })
            description_list.append(
                self.text_cleaning(meta_name_itemprop_description['content']))

        with suppress(Exception):
            '''
            Tested on
            * https://scroll.in/field/979390/they-can-beat-australia-in-their-own-den-shastri-backs-india-s-fabulous-five-quicks-to-shine
              <meta name="dcterms.description" content="The India coach said his team’s pace unit was the best in the world, despite being likely to be without the injured Ishant Sharma.">
            * https://scroll.in/field/979393/champions-league-last-gasp-wins-take-juventus-chelsea-and-sevilla-into-last-16-barcelona-cruise
              <meta name="dcterms.description" content="They are the first teams to make it out of the group stage, doing so with two games to spare.">
            '''
            meta_name_dcterms_description = html.find(
                'meta', {'name': 'dcterms.description'})
            description_list.append(
                self.text_cleaning(meta_name_dcterms_description['content']))

        with suppress(Exception):
            '''
            Tested on
            * https://www.express.co.uk/news/weather/1370081/BBC-Weather-Europe-snow-forecast-cold-December-update-video-vn
              <div class="text-description"><p><span>BBC Weather meteorologist Stav Danaos forecast unsettled weather across the&nbsp;</span><span>Mediterranean for the rest of the week. He added a blocking area of high pressure across Russia was contributing to the unsettling weather.</span></p></div>
            * https://www.express.co.uk/news/politics/1383306/Brexit-live-latest-brexit-deal-Northern-Ireland-customs-boris-johnson-john-redwood
              <div class='text-description'><p>Earlier today, Boris Johnson suggested some fishing businesses in Scotland would receive compensation as he defended...</p></div>
            '''
            div_class_text_description = html.find(
                'div', {'class': 'text-description'})
            description_list.append(
                self.text_cleaning(div_class_text_description.text))

        with suppress(Exception):
            '''
            Tested on
            * https://www.usatoday.com/story/news/nation/2020/12/07/north-atlantic-right-whale-endangered-species-newborns/6484190002/
              <div...data-ss-d="Two North Atlantic right whale newborns have been spotted in the last week at the start of calving season, providing hope for an endangered species."...>
            * https://www.usatoday.com/story/sports/mls/2020/12/07/mls-cup-2020-seattle-sounders-advance-play-columbus-crew-title/6487291002/
              <div...data-ss-d="The Seattle Sounders scored two late goals to complete a dramatic rally over Minnesota United and advance to MLS Cup to play the Columbus Crew."...>
            '''
            div_data_ssd = html.find('div', {'data-ss-d': True})
            description_list.append(
                self.text_cleaning(div_data_ssd['data-ss-d']))

        with suppress(Exception):
            '''
            Tested on
            * https://www.indiatoday.in/technology/news/story/amazon-great-republic-day-sale-announced-from-january-20-deals-bank-offers-and-more-1758622-2021-01-13
              <div class="story-kicker"><h2>Amazon's Great Republic Day Sale begins January 20 but Prime members will get 24 hours early access on deals.</h2></div>
            * https://www.indiatoday.in/sports/cricket/story/a-win-at-gabba-will-give-india-their-greatest-test-series-victory-ever-says-akhtar-1758619-2021-01-13
              <div class="story-kicker"><h2>Former Pakistan fast bowler Shoaib Akhtar lauded India for the fight they have shown in the series so far and said that they should go on to win the final Test in Brisbane.</h2></div>
            '''
            div_class_story_kicker = html.find('div',
                                               {'class': 'story-kicker'})
            description_list.append(
                self.text_cleaning(div_class_story_kicker.text))

        with suppress(Exception):
            '''
            Tested on
            * https://www.espncricinfo.com/story/vitality-t20-blast-mitchell-claydon-misses-sussex-s-t20-blast-defeat-after-hand-sanitiser-ball-tampering-ban-1234150
              <p class="article-summary">Seamer will miss first two games of 2021 as well after nine-match ban imposed by CDC</p>
            * https://www.espncricinfo.com/series/vitality-blast-2020-1207645/nottinghamshire-vs-leicestershire-1st-quarter-final-1207789/match-report
              <p class="article-summary">Nottinghamshire progress on higher Powerplay score after securing dramatic tie off last ball</p>
            '''
            p_class_article_summary = html.find('p',
                                                {'class': 'article-summary'})
            description_list.append(
                self.text_cleaning(p_class_article_summary.text))

        with suppress(Exception):
            '''
            Tested on
            * https://www.nytimes.com/2020/01/31/learning/is-it-offensive-for-sports-teams-and-their-fans-to-use-native-american-names-imagery-and-gestures.html
              <p id="article-summary" class="css-w6ymp8 e1wiw3jv0">The Kansas City Chiefs will face the San Francisco 49ers for Super Bowl LIV. Chiefs fans regularly use a “tomahawk chop” to urge on their beloved team: Is it offensive?</p>
            * https://www.nytimes.com/2020/01/09/world/middleeast/iran-plane-crash-ukraine.html
              <p id="article-summary" class="css-w6ymp8 e1wiw3jv0">Western intelligence showed that Iran was responsible for the plane crash, suggesting that the deaths of those aboard were a consequence of the heightened tensions between Washington and Iran. </p>
            '''
            p_id_article_summary = html.find('p', {'id': 'article-summary'})
            description_list.append(
                self.text_cleaning(p_id_article_summary.text))

        with suppress(Exception):
            '''
            Tested on
            * https://economictimes.indiatimes.com/industry/services/education/indian-universities-look-abroad-for-success-at-home/articleshow/5957175.cms
              <h2 class="summary">Foreign universities may soon be able to set up in India but some of their Indian counterparts are looking in the other direction — to better equip students for the demands of the global economy.</h2>
            * https://economictimes.indiatimes.com/industry/transportation/railways/conviction-rate-in-theft-cases-in-central-railways-mumbai-division-falls-steeply/articleshow/48554953.cms
              <h2 class="summary">According to official data, the conviction rate in theft cases of railway properties has witnessed a steep fall in Mumbai Division of Central Railway.</h2>
            '''
            h2_class_summary_description = html.find('h2',
                                                     {'class': 'summary'})
            description_list.append(
                self.text_cleaning(h2_class_summary_description.text))

        with suppress(Exception):
            '''
            Tested on
            * https://sports.ndtv.com/india-vs-england-2020-21/ind-vs-eng-virat-kohli-reflects-on-battling-depression-during-2014-england-tour-2373999
              <h2 class="sp-descp">India vs England: Virat Kohli opened up about dealing with depression on India's 2014 tour of England where Kohli endured a horror run with the bat.</h2>
            * https://sports.ndtv.com/cricket/we-cant-influence-indian-high-commission-for-visas-pcb-1594242
              <h2 class="sp-descp">Pakistan Cricket Board made it clear that it had done everything under its power to get the visas for its cricketers to play in the IPL next year.</h2>
            '''
            h2_class_sp_descp_description = html.find('h2',
                                                      {'class': 'sp-descp'})
            description_list.append(
                self.text_cleaning(h2_class_sp_descp_description.text))

        with suppress(Exception):
            '''
            Tested on
            * https://indianexpress.com/article/news-archive/days-are-not-far-when-kashmiri-pandits-would-return-to-their-homes-with-dignity-jk-bjp-4842449/
              <h2 itemprop="description" class="synopsis">"Those days are not far when the displaced people will return to their Kashmir with dignity and honour. The BJP will leave no stone unturned in solving the problems of the hapless people who were forced to leave the Valley," Jammu and Kashmir BJP unit chief Sat Sharma said. </h2>
            * https://indianexpress.com/article/india/web/bjp-mp-karandlaje-challenges-karnataka-cm-siddaramaiah-govt-to-arrest-her-4996043/
              <h2 itemprop="description" class="synopsis">An FIR was filed against BJP MP Shobha Karandlaje on charges of provoking people to cause riots, disturbing communal harmony and spreading rumours.</h2>
            '''
            h2_itemprop_description = html.find('h2',
                                                {'itemprop': 'description'})
            description_list.append(
                self.text_cleaning(h2_itemprop_description.text))

        with suppress(Exception):
            '''
            Tested on
            * https://www.business-standard.com/article/current-affairs/death-of-galaxy-galactic-collision-spews-gases-equal-to-10-000-suns-a-year-121011300543_1.html
              <h2 class="alternativeHeadline">The merging galaxy formed 4.5 billion years ago is dubbed ID2299 and is ejecting gases equivalent to 10,000 Suns-worth of gas a year</h2>
            * https://www.business-standard.com/article/international/wb-economist-china-will-need-to-learn-to-restructure-emerging-market-debt-121011300034_1.html
              <h2 class="alternativeHeadline">Increasing debt distress in emerging markets means that China will need to start  restructuring debts in the same way that Paris Club lenders did in past crises, World Bank Chief Economist said</h2>
            '''
            h2_class_alternative_headline = html.find(
                'h2', {'class': 'alternativeHeadline'})
            description_list.append(
                self.text_cleaning(h2_class_alternative_headline.text))

        with suppress(Exception):
            '''
            Tested on
            * https://www.express.co.uk/news/world/1369648/India-news-mystery-illness-coronavirus-covid-Andhra-Pradesh-eluru-disease-cause-ont
              <h3>OFFICIALS in India are reportedly seeking to manage panic in the Indian state of Andhra Pradesh due to a mysterious illness spreading in the district.</h3>
            * https://www.express.co.uk/news/politics/1383306/Brexit-live-latest-brexit-deal-Northern-Ireland-customs-boris-johnson-john-redwood
              <h3>A HUGE new fishing row has erupted between Scottish fishermen anf the UK Government, with BBC News Political Editor Laura Kuenssberg warning: "This could get messy."</h3>
            '''
            h3_description = html.find('h3')
            description_list.append(self.text_cleaning(h3_description.text))

        with suppress(Exception):
            '''
            Tested on
            * https://www.independent.co.uk/arts-entertainment/tv/news/ratched-netflix-trigger-warning-child-abuse-suicide-violence-sarah-paulson-b571405.html
              <h2 class="sc-qYhdC bflsCm"><p>Despite presence of warning over graphic content, fans have called for more</p></h2>
            * https://www.independent.co.uk/arts-entertainment/tv/news/bridgerton-violet-actor-ruth-gemmell-tracy-beaker-b1780757.html
              <h2 class="sc-oTcDH eZHAcN"><p>Gemmell starred in the 2004 CBBC film Tracy Beaker: The Movie of Me</p></h2>
            '''
            header_id_articleheader = html.find('header',
                                                {'id': 'articleHeader'})
            header_two = header_id_articleheader.find('h2')
            description_list.append(self.text_cleaning(header_two.text))

        with suppress(Exception):
            '''
            Tested on
            * https://scroll.in/article/979318/what-is-the-extent-of-caste-segregation-in-indian-villages-today-new-data-gives-us-an-idea
              <h2>‘The extent of intra-village segregation in Karnataka is greater than the local black-white segregation in the American South.’</h2>
            * https://scroll.in/latest/979410/khichdification-ima-demands-withdrawal-of-move-allowing-ayurveda-doctors-to-perform-surgery
              <h2>The medical body said that the move should not be seen in isolation, referring to other government decisions ‘legitimising Mixopathy’.</h2>
            '''
            header = html.find('header')
            description_list.append(
                self.text_cleaning(header.find_next('h2').text))

        with suppress(Exception):
            '''
            Tested on
            * https://www.euronews.com/2020/12/08/charlie-hebdo-trial-prosecutors-request-30-year-sentence-for-fugitive-widow-of-attacker
              <script type="application/ld+json"... '@graph': ["description": "Prosecutors have asked for sentences ranging from 5 years to life imprisonment for the defendants in the Charlie Hebdo trial, including the fugitive widow of one of the attackers."...]...>
            * https://www.euronews.com/2020/12/08/france-s-next-aircraft-carrier-to-be-nuclear-powered-macron-confirms
              <script type="application/ld+json"... '@graph': ["description": "France's current flagship warship is to be retired in 2038. It will be replaced by a bigger, nuclear-powered model, Macron said on Tuesday."...]...>
            '''
            first_script = html.find('script', {'type': 'application/ld+json'})
            data = json.loads(first_script.string, strict=False)
            description_list.append(
                self.text_cleaning(data['@graph'][0]['description']))

        with suppress(Exception):
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                with suppress(Exception):
                    '''
                    Tested on
                    * https://www.espncricinfo.com/story/ipl-2020-jofra-archer-thriving-in-different-type-of-pressure-at-ipl-says-rajasthan-royals-team-mate-jos-buttler-1234126
                      <script type='application/ld+json'..."description":"Fifty-over cricket must take a back seat in build-up to T20 World Cup, says senior batsman"...>
                    '''
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["@type"] == "NewsArticle" or data[
                            "@type"] == "WebPage":
                        if data["description"]:
                            description_list.append(
                                self.text_cleaning(data["description"]))
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle":
                        if isinstance(data["video"], list):
                            description_list.append(
                                self.text_cleaning(
                                    data["video"][0]["description"]))
                        elif not isinstance(data["video"], list):
                            description_list.append(
                                self.text_cleaning(
                                    data["video"]["description"]))
        description_list = [
            description for description in description_list
            if description != ''
        ]
        if not description_list:
            return " "
        best_description = max(sorted(set(description_list)),
                               key=description_list.count)
        return best_description
