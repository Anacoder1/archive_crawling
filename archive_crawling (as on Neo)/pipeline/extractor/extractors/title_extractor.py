"""Script to extract the title from a news article."""

import json
import logging
import re
from contextlib import suppress

from bs4 import BeautifulSoup
from retrying import retry

from .abstract_extractor import AbstractExtractor


class TitleExtractor(AbstractExtractor):
    """
    Custom Title Extractor
    * Used as a fallback for newspaper_extractor
    * Returns the longest string out of all extracted title values
    """
    def __init__(self):  # pylint: disable=super-init-not-called
        """Init function."""
        self.name = "title_extractor"

    def _title(self, item):
        """Returns the extracted title from a news article."""
        html_item = item['spider_response']
        html = BeautifulSoup(html_item.body, 'html5lib')
        title = " "
        try:
            title = self.title_mega(html)
        except Exception as exception:  # pylint: disable=broad-except
            logging.exception(exception)
        return title

    def title_cleaning(self, title):  # pylint: disable=no-self-use
        """Function to clean the title."""
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
        title = re.sub(
            "- The Hindu BusinessLine|- VARIETY|- AGRI-BIZ & COMMODITY|- Today's Paper|- OPINION|"
            "- NEWS|- PULSE|- STATES|- MARKETS|- BL INK|- OTHERS|- PORTFOLIO|"
            "- AUTOMOBILE|- CLEAN TECH", "", title)
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

    @retry(stop_max_attempt_number=3,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def title_mega(self, html):  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        """Returns the longest title from a list of all extracted title values."""
        titles_list = []
        '''
        Tested on
        * https://www.independent.co.uk/news/world/americas/elijah-mcclain-death-colorado-police-black-lives-matter-george-floyd-police-a9584366.html
          <meta property="og:title" content="Petition demanding justice for death of Elijah McClain reaches 2 million signatures">
        * https://nypost.com/2010/09/27/brooklyn-tea-party-rallies-against-ground-zero-mosque-multiculturalism/
          <meta property="og:title" content="Brooklyn Tea Party rallies against Ground Zero mosque, multiculturalism">
        '''
        with suppress(Exception):
            meta_property_og_title = html.find('meta',
                                               {'property': 'og:title'})
            titles_list.append(
                self.title_cleaning(meta_property_og_title['content']))

        '''
        Tested on
        * https://www.usatoday.com/story/entertainment/books/2020/12/08/bob-woodward-robert-costa-pen-book-trumps-final-days-president/6487779002/
          <meta name="twitter:title" content="Bob Woodward to take on final days of Trump’s presidency in next book">
        * https://www.usatoday.com/story/news/politics/2020/12/07/trump-white-house-covid-summit-fda-vaccine-approval/3861768001/
          <meta name="twitter:title" content="President Trump to hold White House COVID-19 summit as pressure mounts for FDA vaccine approval">
        '''
        with suppress(Exception):
            meta_name_twitter_title = html.find('meta',
                                                {'name': 'twitter:title'})
            titles_list.append(
                self.title_cleaning(meta_name_twitter_title['content']))

        '''
        Tested on
        * https://nypost.com/2015/05/21/syndergaards-goal-for-what-may-be-his-last-mlb-start-for-a-while/
          <meta name="twitter:text:title" content="Syndergaard’s goal for what may be his last MLB start for a while">
        * https://nypost.com/2017/06/08/scaramucci-may-have-finally-landed-a-gig-in-the-trump-administration/
          <meta name="twitter:text:title" content="Scaramucci expected to finally join Trump administration">
        '''
        with suppress(Exception):
            meta_name_twitter_text_title = html.find(
                'meta', {'name': 'twitter:text:title'})
            titles_list.append(
                self.title_cleaning(meta_name_twitter_text_title['content']))

        '''
        Tested on
        * https://www.thehindubusinessline.com/todays-paper/tp-news/article33274819.ece
          <meta name="title" content="Kraft paper paucity: Mills blame waste paper costs; box makers accuse them of ‘creating shortage’">
        * https://www.espncricinfo.com/series/vitality-blast-2020-1207645/nottinghamshire-vs-leicestershire-1st-quarter-final-1207789/match-report
          <meta name="title" content="Recent Match Report - Leics vs Notts 1st Quarter Final 2020 | ESPNcricinfo.com">
        '''
        with suppress(Exception):
            meta_name_title = html.find('meta', {'name': 'title'})
            titles_list.append(self.title_cleaning(meta_name_title['content']))

        '''
        Tested on
        * https://scroll.in/field/979390/they-can-beat-australia-in-their-own-den-shastri-backs-india-s-fabulous-five-quicks-to-shine
          <meta name="dcterms.title" content="They can beat Australia in their own den: Shastri backs India's 'fabulous five' quicks to shine">
        * https://scroll.in/field/979393/champions-league-last-gasp-wins-take-juventus-chelsea-and-sevilla-into-last-16-barcelona-cruise
          <meta name="dcterms.title" content="Champions League: Last-gasp wins take Juventus, Chelsea and Sevilla into last 16, Barcelona cruise">
        '''
        with suppress(Exception):
            meta_name_dcterms_title = html.find('meta',
                                                {'name': 'dcterms.title'})
            titles_list.append(
                self.title_cleaning(meta_name_dcterms_title['content']))

        '''
        Tested on
        * https://www.dailypioneer.com/2020/state-editions/punjab-cm-launches----diginest----mobile-app-to-ensure-digital-access-to-state-govt-directory.html
          <meta name="keywords" content="Punjab CM launches ‘Diginest’ mobile app to ensure digital access to State Govt directory">
        * https://www.dailypioneer.com/2020/state-editions/hc-seeks-reply-from-state-in-2-weeks-on-adi-shankaracharya---s-samadhi.html
          <meta name="keywords" content="HC seeks reply from State in 2 weeks on Adi Shankaracharya’s Samadhi">
        '''
        with suppress(Exception):
            meta_name_keywords = html.find('meta', {'name': 'keywords'})
            titles_list.append(
                self.title_cleaning(meta_name_keywords['content']))

        '''
        Tested on
        * https://www.oneindia.com/india/congress-leader-dk-shivakumar-to-appear-before-cbi-in-disproportionate-assets-case-today-3180984.html
          <meta name="headline" itemprop="headline" content="Congress leader DK Shivakumar to appear before CBI in disproportionate assets case today ">
        * https://www.oneindia.com/india/will-make-bengal-police-lick-boots-if-bjp-comes-to-power-in-next-assembly-elections-raju-banerjee-3181010.html
          <meta name="headline" itemprop="headline" content="Will make Bengal police lick boots if BJP comes to power in next Assembly elections: Raju Banerjee">
        '''
        with suppress(Exception):
            meta_name_headline = html.find('meta', {'name': 'headline'})
            titles_list.append(
                self.title_cleaning(meta_name_headline['content']))

        '''
        Tested on
        * https://www.nytimes.com/2020/01/14/books/review-serious-noticing-james-wood.html
          <meta data-rh="true" property="twitter:title" content="In ‘Serious Noticing,’ James Wood Closely Reads Chekhov and Others — Including Himself (Published 2020)">
        * https://www.nytimes.com/2020/01/27/us/politics/impeachment-live.html
          <meta data-rh="true" property="twitter:title" content="Impeachment Trial Highlights: Trump’s Lawyers Avoid Bolton, Giuliani Surfaces and a History Lesson (Published 2020)">
        '''
        with suppress(Exception):
            meta_property_twitter_title = html.find(
                'meta', {'property': 'twitter:title'})
            titles_list.append(
                self.title_cleaning(meta_property_twitter_title['content']))

        '''
        Tested on
        * https://www.business-standard.com/article/international/walmart-disney-suspend-contributions-to-us-lawmakers-who-opposed-biden-win-121011300172_1.html
          <meta itemprop="name" content="Walmart, Disney suspend contributions to US lawmakers who opposed Biden win | Business Standard News">
        * https://www.deccanherald.com/content/1368/agriculture-department-urged-regulate-fertilisers.html
          <meta itemprop="name" content="Agriculture department urged to regulate fertilisers supply">
        '''
        with suppress(Exception):
            meta_itemprop_name = html.find('meta', {'itemprop': 'name'})
            titles_list.append(
                self.title_cleaning(meta_itemprop_name['content']))

        '''
        Tested on
        * https://indianexpress.com/article/world/print/nepals-ruling-communist-partys-powerful-body-to-meet-on-saturday-to-decide-pm-olis-fate-6488994/
          <meta itemprop="headline" content="Nepal’s ruling communist party’s powerful body to meet on Saturday to decide PM Oli’s fate">
        * https://www.financialexpress.com/archive/delhi-power-crisis-gets-worse-arvind-kejriwal-warns-discom-licences-could-be-cancelled/1222283/
          <meta itemprop="headline" content="Delhi power crisis gets worse, Arvind Kejriwal warns discom licences could be cancelled">
        '''
        with suppress(Exception):
            meta_itemprop_headline = html.find('meta',
                                               {'itemprop': 'headline'})
            titles_list.append(
                self.title_cleaning(meta_itemprop_headline['content']))

        '''
        Tested on
        * https://www.express.co.uk/news/weather/1370081/BBC-Weather-Europe-snow-forecast-cold-December-update-video-vn
          <meta property="headline_short" content="BBC Weather: Fog and snow to sweep Europe as continent rocked by 'blocking' high pressure">
        * https://www.express.co.uk/news/politics/1383306/Brexit-live-latest-brexit-deal-Northern-Ireland-customs-boris-johnson-john-redwood
          <meta property="headline_short" content="Brexit LIVE: Laura Kuenssberg exposes almighty fishing row about to erupt 'Could be messy'">
        '''
        with suppress(Exception):
            meta_property_headline_short = html.find(
                'meta', {'property': 'headline_short'})
            titles_list.append(
                self.title_cleaning(meta_property_headline_short['content']))

        '''
        Tested on
        * https://www.dailymail.co.uk/tvshowbiz/article-8988259/TOM-LEONARD-Stars-haunt-mischief-menu.html
          <meta property="mol:headline" content="Stars' haunt that had mischief on the menu: Chorus girls dancing down the bar top. Princess Margaret making mincemeat of other diners. Sozzled A-listers galore. As celeb eaterie Joe Allen fights for cash, tuck into its banquet of gossip">
        * https://www.dailymail.co.uk/sciencetech/article-8988053/NASA-astronaut-Victor-Glover-shares-video-SPACE.html
          <meta property="mol:headline" content="NASA astronaut Victor Glover shares his first video from SPACE of him looking through the SpaceX Crew capsule down at Earth">
        '''
        with suppress(Exception):
            meta_property_mol_headline = html.find(
                'meta', {'property': 'mol:headline'})
            titles_list.append(
                self.title_cleaning(meta_property_mol_headline['content']))

        '''
        Tested on
        * https://www.oneindia.com/india/cyclone-nivar-to-hit-tn-with-winds-at-145-kmph-puducherry-lg-kiran-bedi-appeals-people-to-stay-safe-3181023.html
          <meta name="headline" itemprop="headline" content="Cyclone Nivar to hit TN with winds at 145 Kmph; Puducherry LG Kiran Bedi appeals people to stay safe">
        * https://www.oneindia.com/india/delhi-riots-umar-khalid-didn-t-take-security-to-conspiratorial-meetings-says-charge-sheet-3181302.html
          <meta name="headline" itemprop="headline" content="Delhi riots: Umar Khalid didn't take security to 'conspiratorial meetings', says charge sheet">
        '''
        with suppress(Exception):
            meta_itemprop_name_headline = html.find('meta', {
                'name': 'headline',
                'itemprop': 'headline'
            })
            titles_list.append(
                self.title_cleaning(meta_itemprop_name_headline['content']))

        '''
        Tested on
        * https://economictimes.indiatimes.com/news/economy/policy/government-mops-up-rs-8660-cr-from-disinvestment-in-02/articleshow/33105933.cms
          <div class="article_block clearfix gaDone"... data-arttitle="Government mops up Rs 8,660 cr from disinvestment in '02"...>
        * https://economictimes.indiatimes.com/news/politics-and-nation/delhi-policeman-nabbed-for-taking-bribe-from-kidney-racketeer/articleshow/2785146.cms
          <div class="article_block clearfix gaDone"... data-arttitle="Delhi policeman nabbed for taking bribe from kidney racketeer"...>
        '''
        with suppress(Exception):
            div_data_arttitle = html.find('div',
                                          {'class': 'article_block clearfix'})
            if div_data_arttitle.get('data-arttitle'):
                titles_list.append(
                    self.title_cleaning(
                        div_data_arttitle.get('data-arttitle')))

        '''
        Tested on
        * https://www.usatoday.com/story/news/nation/2020/12/07/north-atlantic-right-whale-endangered-species-newborns/6484190002/
          <div...data-ss-t="Critically endangered North Atlantic right whale population gets a boost: 2 newborns spotted off US coast"...>
        * https://www.usatoday.com/story/sports/mls/2020/12/07/mls-cup-2020-seattle-sounders-advance-play-columbus-crew-title/6487291002/
          <div...data-ss-t="Seattle Sounders pull off dramatic rally to reach 2020 MLS Cup, will play Columbus Crew on Saturday"...>
        '''
        with suppress(Exception):
            div_data_sst = html.find('div', {'data-ss-t': True})
            titles_list.append(self.title_cleaning(div_data_sst['data-ss-t']))

        '''
        Tested on
        * https://www.business-standard.com/article/current-affairs/death-of-galaxy-galactic-collision-spews-gases-equal-to-10-000-suns-a-year-121011300543_1.html
          <div class="addthis_sharing_toolbox"...data-title="Death of galaxy: Galactic collision spews gases equal to 10,000 suns a year"...>
        * https://www.business-standard.com/article/markets/auto-psu-stocks-to-outperform-in-the-short-term-vinay-rajani-of-hdfc-sec-121011300139_1.html
          <div class="addthis_sharing_toolbox"...data-title="Auto, PSU stocks to outperform in the short-term: Vinay Rajani of HDFC Sec"...>
        '''
        with suppress(Exception):
            div_class_sharingtoolbox = html.find(
                'div', {'class': "addthis_sharing_toolbox"})
            titles_list.append(
                self.title_cleaning(div_class_sharingtoolbox['data-title']))

        '''
        Tested on
        * https://economictimes.indiatimes.com/industry/services/education/indian-universities-look-abroad-for-success-at-home/articleshow/5957175.cms
          <h1 class="artTitle font_faus">Indian universities look abroad for success at home</h1>
        * https://nypost.com/2017/06/08/scaramucci-may-have-finally-landed-a-gig-in-the-trump-administration/
          <h1 class="postid-11008199">Scaramucci expected to finally join Trump administration</h1>
        '''
        with suppress(Exception):
            h1_title = html.find('h1')
            titles_list.append(self.title_cleaning(h1_title.text))

        '''
        Tested on
        * https://www.deccanherald.com/content/273743/pak-needs-explain-osamas-presence.html
          <h1 class="f-left sanspro-b" id="page-title">Pak needs to explain Osama's presence in Abbottabad: Haqqani</h1>
        * https://www.deccanherald.com/content/507817/children-adopted-through-state-governmentsmother.html
          <h1 class="f-left sanspro-b" id="page-title">Children to be adopted through State governments:Mother Teresa orphanages</h1>
        '''
        with suppress(Exception):
            h1_id_page_title = html.find('h1', {'id': 'page-title'})
            titles_list.append(self.title_cleaning(h1_id_page_title.text))

        '''
        Tested on
        * https://www.indiatoday.in/india/story/pm-modi-launch-covid-vaccination-drive-jan-16-cowin-app-coronavirus-covaxin-covishield-1758628-2021-01-13
          <h1 itemprop="headline">India's Covid vaccination drive to kick off with virtual launch by PM Modi, roll out of CoWin app on Jan 16</h1>
        * https://www.indiatoday.in/technology/news/story/amazon-great-republic-day-sale-announced-from-january-20-deals-bank-offers-and-more-1758622-2021-01-13
          <h1 itemprop="headline">Amazon Great Republic Day Sale announced from January 20: Deals, bank offers, and more</h1>
        '''
        with suppress(Exception):
            h1_itemprop_headline = html.find('h1', {'itemprop': 'headline'})
            titles_list.append(self.title_cleaning(h1_itemprop_headline.text))

        '''
        Tested on
        * https://www.usatoday.com/story/sports/mls/2020/12/07/mls-cup-2020-seattle-sounders-advance-play-columbus-crew-title/6487291002/
          <h1 class="gnt_ar_hl" elementtiming="ar-headline">Seattle Sounders pull off dramatic rally to reach 2020 MLS Cup, will play Columbus Crew on Saturday</h1>
        * https://www.usatoday.com/story/entertainment/books/2020/12/08/bob-woodward-robert-costa-pen-book-trumps-final-days-president/6487779002/
          <h1 class="gnt_ar_hl" elementtiming="ar-headline">Bob Woodward to take on final days of Trump’s presidency in next book</h1>
        '''
        with suppress(Exception):
            h1_ar_headline = html.find('h1', {'elementtiming': 'ar-headline'})
            titles_list.append(self.title_cleaning(h1_ar_headline.text))

        '''
        Tested on
        * https://www.oneindia.com/india/delhi-riots-umar-khalid-didn-t-take-security-to-conspiratorial-meetings-says-charge-sheet-3181302.html
          <h1 class="heading">Delhi riots: Umar Khalid didn't take security to 'conspiratorial meetings', says charge sheet</h1>
        * https://www.oneindia.com/international/xi-jinping-finally-congratulates-biden-hopes-us-china-will-uphold-spirit-of-non-confrontation-3181336.html
          <h1 class="heading">Xi Jinping finally congratulates Biden; hopes US, China will uphold spirit of non-confrontation</h1>
        '''
        with suppress(Exception):
            h1_class_heading = html.find('h1', {'class': 'heading'})
            titles_list.append(self.title_cleaning(h1_class_heading.text))

        '''
        Tested on
        * https://www.business-standard.com/article/international/wb-economist-china-will-need-to-learn-to-restructure-emerging-market-debt-121011300034_1.html
          <h1 class="headline">WB economist: China will need to learn to restructure emerging market debt</h1>
        * https://www.business-standard.com/article/international/us-house-committee-releases-report-supporting-donald-trump-s-impeachment-121011300125_1.html
          <h1 class="headline">US House committee releases report supporting Donald Trump's impeachment</h1>
        '''
        with suppress(Exception):
            h1_class_headline = html.find('h1', {'class': 'headline'})
            titles_list.append(self.title_cleaning(h1_class_headline.text))

        '''
        Tested on
        * https://www.thehindubusinessline.com/money-and-banking/rbi-to-kotak-mahindra-bank-no-dividend-payment-on-perpetual-non-cumulative-preference-shares/article33299037.ece
          <h1 class="tp-title-inf">RBI to Kotak Mahindra Bank: No dividend payment on perpetual non-cumulative preference shares</h1>
        * https://www.thehindubusinessline.com/money-and-banking/pull-payments-made-on-behalf-of-merchants-acquirer-banks-should-not-push-consumers-to-pay-for-services/article33299994.ece
          <h1 class="tp-title-inf">Pull payments made on behalf of merchants: Acquirer banks should not push consumers to pay for services</h1>
        '''
        with suppress(Exception):
            h1_class_tp_title_inf = html.find('h1', {'class': 'tp-title-inf'})
            titles_list.append(self.title_cleaning(h1_class_tp_title_inf.text))

        '''
        Tested on
        * https://www.cnbc.com/2020/12/25/the-plant-based-meat-industry-is-on-the-rise-but-challenges-remain.html
          <h1 class="ArticleHeader-headline">The plant-based meat industry has grown into a $20 billion business — but challenges remain</h1>
        * https://www.cnbc.com/2020/12/25/covid-stimulus-why-lawmakers-hope-trump-signs-the-bill-very-quietly.html
          <h1 class="ArticleHeader-headline">Why lawmakers from both parties hope Trump ‘calms down and simply signs the bill very quietly’</h1>
        '''
        with suppress(Exception):
            h1_class_articleheader = html.find(
                'h1', {'class': 'ArticleHeader-headline'})
            titles_list.append(self.title_cleaning(
                h1_class_articleheader.text))

        '''
        Tested on
        * https://www.nytimes.com/2020/01/31/learning/is-it-offensive-for-sports-teams-and-their-fans-to-use-native-american-names-imagery-and-gestures.html
          <h1 id="link-7631a3d4" class="css-rsa88z e1h9rw200" data-test-id="headline">Is It Offensive for Sports Teams and Their Fans to Use Native American Names, Imagery and Gestures?</h1>
        * https://www.nytimes.com/2020/01/14/books/review-serious-noticing-james-wood.html
          <h1 id="link-42cf8827" class="css-139djpt e1h9rw200" data-test-id="headline">In ‘Serious Noticing,’ James Wood Closely Reads Chekhov and Others — Including Himself</h1>
        '''
        with suppress(Exception):
            h1_data_test_id_headline = html.find('h1',
                                                 {'data-test-id': 'headline'})
            titles_list.append(
                self.title_cleaning(h1_data_test_id_headline.text))

        '''
        Tested on
        * https://www.dailymail.co.uk/sport/football/article-8987295/Pierre-Emile-Hojbjerg-Jose-Mourinhos-midfield-general-high-flying-Spurs.html
          <h2>Pierre-Emile Hojbjerg has passed more than any other Premier League midfielder and sits fourth in tackles going into this weekend's games... his arrival went under the radar but the £20m man is Jose Mourinho's midfield general at high-flying Tottenham</h2>
        * https://www.dailymail.co.uk/sport/football/article-8986989/The-key-battles-Tottenhams-table-clash-Chelsea-Stamford-Bridge.html
          <h2>Can Jose Mourinho pull off another masterclass as he did against City? Or will Frank Lampard reign supreme once more over his old boss as he did TWICE last season? Sportsmail assesses key battles as Spurs travel to Chelsea in a top of the table clash</h2>
        '''
        with suppress(Exception):
            h2_title = html.find('h2')
            titles_list.append(self.title_cleaning(h2_title.text))

        '''
        Tested on
        * https://www.dailypioneer.com/2020/india/govt-ok---s-bank-loans-at-lower-rates-to-distilleries-for-raising-ethanol-production.html
          <h2 itemprop="headline">Govt OK’s bank loans at lower rates to distilleries for raising ethanol production</h2>
        * https://www.dailypioneer.com/2020/state-editions/aap-mla-visits-singhu-border-to-ensure-wifi-facilities-for-farmers.html
          <h2 itemprop="headline">AAP MLA visits Singhu Border to ensure WiFi facilities for farmers</h2>
        '''
        with suppress(Exception):
            h2_itemprop_headline = html.find('h2', {'itemprop': 'headline'})
            titles_list.append(self.title_cleaning(h2_itemprop_headline.text))

        '''
        Tested on
        * https://www.euronews.com/2020/12/08/charlie-hebdo-trial-prosecutors-request-30-year-sentence-for-fugitive-widow-of-attacker
          <title>Charlie Hebdo trial: Prosecutors request 30-year sentence for fugitive widow of attacker | Euronews</title>
        * https://www.euronews.com/2020/12/08/france-s-next-aircraft-carrier-to-be-nuclear-powered-macron-confirms
          <title>France's next aircraft carrier to be nuclear-powered, Macron confirms | Euronews</title>
        '''
        with suppress(Exception):
            title_main = html.find('title')
            titles_list.append(self.title_cleaning(title_main.text))
            titles_list.append(
                self.title_cleaning(title_main.text.split(" - ")[0]))
            titles_list.append(
                self.title_cleaning(title_main.text.split("|")[0]))

        '''
        Tested on
        * https://www.cnbc.com/2020/12/24/dominion-voting-warns-fox-news-lawsuits-are-imminent.html
          <title itemprop="name">Dominion Voting warns Fox News lawsuits are imminent</title>
        * https://www.cnbc.com/2020/12/25/biden-and-trump-christmas-messages.html
          <title itemprop="name">Biden and Trump Christmas messages</title>
        '''
        with suppress(Exception):
            title_itemprop_name = html.find('title', {'itemprop': 'name'})
            titles_list.append(self.title_cleaning(title_itemprop_name.text))

        '''
        Tested on (RECHECK)
        * https://www.independent.co.uk/life-style/royal-family/the-crown-queen-cousins-nerissa-katherine-bowes-lyon-b1721187.html
        '''
        with suppress(Exception):
            input_name_streamtitle = html.find('input',
                                               {'name': 'streamTitle'})
            titles_list.append(
                self.title_cleaning(input_name_streamtitle["value"]))

        '''
        Tested on
        * https://www.standard.co.uk/news/uk/boris-johnson-u-turn-free-school-meals-marcus-rashford-a4470506.html
          <amp-social-share type="twitter" data-param-text="PM U-turns on school meals as Rashford says: Look what we do together">
        * https://www.independent.co.uk/arts-entertainment/tv/news/ratched-netflix-trigger-warning-child-abuse-suicide-violence-sarah-paulson-b571405.html
          <amp-social-share type="twitter" data-param-text="Ratched fans urge Netflix to introduce ‘trigger warning’ over scenes of child abuse and suicide">
        '''
        with suppress(Exception):
            amp_social_share_twitter = html.find('amp-social-share',
                                                 {'type': 'twitter'})
            titles_list.append(
                self.title_cleaning(
                    amp_social_share_twitter["data-param-text"]))

        '''
        Tested on
        * https://www.independent.co.uk/news/uk/home-news/coronavirus-childcare-parents-lockdown-schools-a9688116.html
          <amp-social-share type="email" data-param-subject="The struggle to access childcare is wreaking havoc on parent's mental health in lockdown">
        * https://www.standard.co.uk/news/politics/david-cameron-warns-uk-will-lose-respect-overseas-with-foreign-aid-department-merger-a4470651.html
          <amp-social-share type="email" data-param-subject="UK will 'lose respect overseas' with foreign aid merger, Cameron warns">
        '''
        with suppress(Exception):
            amp_social_share_email = html.find('amp-social-share',
                                               {'type': 'email'})
            titles_list.append(
                self.title_cleaning(
                    amp_social_share_email["data-param-subject"]))

        '''
        Tested on
        * https://www.dailymail.co.uk/sport/football/article-8986989/The-key-battles-Tottenhams-table-clash-Chelsea-Stamford-Bridge.html
          <li id="shareLinkTop" data-formatted-headline="The key battles in Tottenham\'s top of the table clash with Chelsea">
        * https://www.dailymail.co.uk/sport/football/article-8987295/Pierre-Emile-Hojbjerg-Jose-Mourinhos-midfield-general-high-flying-Spurs.html
          <li id="shareLinkTop" data-formatted-headline="Hojbjerg is Mourinho\'s midfield general at high-flying Spurs">
        '''
        with suppress(Exception):
            li_id_sharelinktop = html.find('li', {'id': 'shareLinkTop'})
            titles_list.append(
                self.title_cleaning(
                    li_id_sharelinktop['data-formatted-headline']))

        '''
        Tested on
        * https://www.dailymail.co.uk/sport/football/article-8986989/The-key-battles-Tottenhams-table-clash-Chelsea-Stamford-Bridge.html
          <li id="shareLinkBottom" data-formatted-headline="The key battles in Tottenham\'s top of the table clash with Chelsea">
        * https://www.dailymail.co.uk/sport/football/article-8987295/Pierre-Emile-Hojbjerg-Jose-Mourinhos-midfield-general-high-flying-Spurs.html
          <li id="shareLinkBottom" data-formatted-headline="Hojbjerg is Mourinho\'s midfield general at high-flying Spurs">
        '''
        with suppress(Exception):
            li_id_sharelinkbottom = html.find('li', {'id': 'shareLinkBottom'})
            titles_list.append(
                self.title_cleaning(
                    li_id_sharelinkbottom['data-formatted-headline']))

        '''
        Tested on
        * https://www.dailymail.co.uk/sciencetech/article-8988053/NASA-astronaut-Victor-Glover-shares-video-SPACE.html
          <h1>NASA astronaut shares his first video from SPACE on way to ISS</h1>
        * https://www.dailymail.co.uk/tvshowbiz/article-8988259/TOM-LEONARD-Stars-haunt-mischief-menu.html
          <h1>TOM LEONARD: Stars' haunt that had mischief on the menu</h1>
        '''
        with suppress(Exception):
            div_class_sharearticles = html.find('div',
                                                {'class': 'shareArticles'})
            titles_list.append(
                self.title_cleaning(div_class_sharearticles.h1.text))

        '''
        Tested on
        * https://www.indiatoday.in/sports/cricket/story/australia-vs-india-tim-paine-apology-not-forced-remorseful-stump-mic-rashwin-sydney-1758534-2021-01-13
          <a title="share on whatsapp" data-text="Tim Paine wasn't forced to apologise: Justin Langer says Australia captain was remorseful over conduct">
        * https://www.indiatoday.in/coronavirus-outbreak/story/covid-vaccines-shipped-safety-concern-indians-1758506-2021-01-13
          <a title="share on whatsapp" data-text="As vaccines get shipped, safety concern looms over Indians, 41% will choose to wait: Survey">
        '''
        with suppress(Exception):
            link_share_whatsapp = html.find('a',
                                            {'title': 'share on whatsapp'})
            titles_list.append(
                self.title_cleaning(link_share_whatsapp['data-text']))

        '''
        Tested on
        * https://www.nytimes.com/2020/01/31/learning/is-it-offensive-for-sports-teams-and-their-fans-to-use-native-american-names-imagery-and-gestures.html
          <link data-rh:'true' title="Is It Offensive for Sports Teams and Their Fans to Use Native American Names, Imagery and Gestures?">
        * https://www.nytimes.com/2020/01/14/books/review-serious-noticing-james-wood.html
          <link data-rh:'true' title="In ‘Serious Noticing,’ James Wood Closely Reads Chekhov and Others — Including Himself">
        '''
        with suppress(Exception):
            link_data_rh_title = html.find('link', {
                'data-rh': 'true',
                'title': True
            })
            titles_list.append(self.title_cleaning(
                link_data_rh_title['title']))

        '''
        Tested on
        * https://www.indiatoday.in/sports/cricket/story/a-win-at-gabba-will-give-india-their-greatest-test-series-victory-ever-says-akhtar-1758619-2021-01-13
          <span class="content_name">India vs Australia: If India win at Gabba, this will be their greatest Test series victory ever-Shoa</span>
        * https://www.indiatoday.in/technology/news/story/amazon-great-republic-day-sale-announced-from-january-20-deals-bank-offers-and-more-1758622-2021-01-13
          <span class="content_name">Amazon Great Republic Day Sale announced from January 20: Deals, bank offers, and more</span>
        '''
        with suppress(Exception):
            span_class_content_name = html.find('span',
                                                {'class': 'content_name'})
            titles_list.append(
                self.title_cleaning(span_class_content_name.text))

        '''
        Tested on
        * https://www.oneindia.com/india/will-make-bengal-police-lick-boots-if-bjp-comes-to-power-in-next-assembly-elections-raju-banerjee-3181010.html
          <head data-altimg="Will make Bengal police lick boots, if BJP comes to power in next Assembly elections: Raju Banerjee"...>
        * https://www.oneindia.com/india/disengagement-process-in-eastern-ladakh-in-final-phase-top-defence-officials-to-parliamentary-panel-3218983.html
          <head data-altimg="Disengagement process in eastern Ladakh in final phase: Top defence officials to Parliamentary panel"...>
        '''
        with suppress(Exception):
            head_data_altimg = html.find('head', {'data-altimg': True})
            titles_list.append(
                self.title_cleaning(head_data_altimg['data-altimg']))

        '''
        Tested on
        * https://www.thehindubusinessline.com/todays-paper/article33294244.ece
          <ul data-share-text="Centre passes on 6th instalment of borrowing to States to meet GST compensation shortfall" data-category="social-shares">
        * https://www.thehindubusinessline.com/money-and-banking/pull-payments-made-on-behalf-of-merchants-acquirer-banks-should-not-push-consumers-to-pay-for-services/article33299994.ece
          <ul data-share-text="Pull payments made on behalf of merchants: Acquirer banks should not push consumers to pay for services" data-category="social-shares">
        '''
        with suppress(Exception):
            ul_category_social_shares = html.find_all(
                'ul', {'data-category': 'social-shares'})
            for element in ul_category_social_shares:
                titles_list.append(
                    self.title_cleaning(element['data-share-text']))

        '''
        Tested on
        * https://scroll.in/latest/979410/khichdification-ima-demands-withdrawal-of-move-allowing-ayurveda-doctors-to-perform-surgery
          <article...data-title="‘Khichdification’: IMA demands withdrawal of move allowing Ayurveda doctors to perform surgery"...>
        * https://scroll.in/article/979318/what-is-the-extent-of-caste-segregation-in-indian-villages-today-new-data-gives-us-an-idea
          <article...data-title="What is the extent of caste segregation in Indian villages today? New data gives us an idea"...>
        '''
        with suppress(Exception):
            article_data_title = html.find('article', {'data-title': True})
            titles_list.append(
                self.title_cleaning(article_data_title['data-title']))

        '''
        Tested on
        * https://scroll.in/field/987252/watch-serena-williams-walks-out-of-press-conference-in-tears-after-loss-to-naomi-osaka
          <li data-article-title="Watch: Serena Williams walks out of press conference in tears after loss to Naomi Osaka ">
        * https://scroll.in/video/986995/watch-pakistani-influencers-pawri-ho-rai-hai-video-sparks-social-media-trend
          <li data-article-title="Watch: Pakistani influencer’s ‘pawri ho rai hai’ video sparks social media trend">
        '''
        with suppress(Exception):
            li_data_article_title = html.find('li',
                                              {'data-article-title': True})
            titles_list.append(
                self.title_cleaning(
                    li_data_article_title['data-article-title']))

        '''
        Tested on
        * https://scroll.in/field/987183/india-vs-england-umesh-yadav-to-replace-shardul-thakur-as-bcci-names-squad-for-final-two-tests
          <button data-article-title="India vs England: Umesh Yadav to replace Shardul Thakur as BCCI names squad for final two Tests">
        * https://scroll.in/field/987156/joe-root-apologies-to-moeen-ali-for-saying-all-rounder-chose-to-go-home-after-second-test-reports
          <button data-article-title="Joe Root apologises to Moeen Ali for saying all-rounder chose to go home after second Test: Reports">
        '''
        with suppress(Exception):
            button_data_article_title = html.find('button',
                                                  {'data-article-title': True})
            titles_list.append(
                self.title_cleaning(
                    button_data_article_title['data-article-title']))

        '''
        Tested on
        * https://scroll.in/reel/985764/why-beginning-on-mubi-is-a-film-you-cannot-miss
          <h1>Why ‘Beginning’ on Mubi is a film you cannot miss</h1>
        * https://scroll.in/article/985739/ground-report-in-haryana-farmer-protests-run-into-a-caste-divide
          <h1>Ground report: In Haryana, farmer protests run into a caste divide</h1>
        '''
        with suppress(Exception):
            header_h1_title = html.find('header')
            titles_list.append(
                self.title_cleaning(header_h1_title.find_next('h1').text))

        '''
        Tested on
        * https://www.euronews.com/2020/12/09/budapest-and-warsaw-protest-their-governments-budget-veto-by-lighting-monuments-eu-blue
          <script type='application/ld+json'...{'@graph':..."headline": "Budapest and Warsaw protest their governments' budget veto by lighting monuments EU-blue"...}...>
        * https://www.euronews.com/2020/12/09/the-eu-must-leverage-closer-trade-ties-with-uzbekistan-to-ensure-progress-on-human-rights-
          <script type='application/ld+json'...{'@graph':..."headline": "The EU must leverage closer trade ties with Uzbekistan to ensure progress on human rights \u01c0 View"}
        '''
        with suppress(Exception):
            script = html.find('script', {'type': 'application/ld+json'})
            with suppress(Exception):
                data = json.loads(script.string, strict=False)
                titles_list.append(
                    self.title_cleaning(data['@graph'][0]['headline']))

        with suppress(Exception):
            scripts_one = html.find_all('script',
                                        {'type': 'application/ld+json'})
            scripts_one = [
                script for script in scripts_one if script is not None
            ]
            for script in scripts_one:
                '''
                Tested on
                * https://economictimes.indiatimes.com/industry/services/education/indian-universities-look-abroad-for-success-at-home/articleshow/5957175.cms
                  <script type='application/ld+json'..."name" : "Indian universities look abroad for success at home"...>
                * https://economictimes.indiatimes.com/industry/transportation/railways/conviction-rate-in-theft-cases-in-central-railways-mumbai-division-falls-steeply/articleshow/48554953.cms
                  <script type='application/ld+json'..."name" : "Conviction rate in theft cases in central railway's Mumbai division falls steeply"...>
                '''
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if (data["@type"] == "WebPage"
                            and data["name"]) or data["name"]:
                        titles_list.append(self.title_cleaning(data["name"]))

                '''
                Tested on
                * https://timesofindia.indiatimes.com/entertainment/events/lucknow/Freshers-join-in-to-participate-in-Clean-Clear-Lucknow-Times-Fresh-Face-2012-at-Shri-Ramswaroop-Memorial-College/articleshow/16463875.cms?
                  <script type='application/ld+json'..."headline": "Freshers join in to participate in Clean & Clear Lucknow Times Fresh Face 2012 at Shri Ramswaroop Memori"...>
                * https://timesofindia.indiatimes.com/city/delhi/CBSE-makes-more-room-for-kids-with-special-needs/articleshow/4202742.cms
                  <script type='application/ld+json'..."headline":"CBSE makes more room for kids with special needs"...>
                '''
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if (data["@type"] == "NewsArticle"
                            and data["headline"]) or data["headline"]:
                        titles_list.append(
                            self.title_cleaning(data["headline"]))

                '''
                Tested on (RECHECK)
                * https://www.dailymail.co.uk/tvshowbiz/article-2937220/Lucy-Mecklenburgh-Thom-Evans-Robbie-Savage-help-PG-Tips-Monkey-prepare-Red-Nose-Day-Challenge.html
                * https://www.dailymail.co.uk/news/article-2937206/Halal-abattoir-staff-hacked-taunted-sheep-One-worker-sacked-three-suspended-caught-camera-carrying-horrifying-routine-abuse.html
                '''
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["@type"] == "NewsArticle":
                        if isinstance(data["mainEntityOfPage"], list):
                            if data["mainEntityOfPage"][0]["name"]:
                                titles_list.append(
                                    self.title_cleaning(
                                        data["mainEntityOfPage"][0]["name"]))
                        elif not isinstance(data["mainEntityOfPage"], list):
                            if data["mainEntityOfPage"]["name"]:
                                titles_list.append(
                                    self.title_cleaning(
                                        data["mainEntityOfPage"]["name"]))

                '''
                Tested on (RECHECK)
                * https://www.dailymail.co.uk/tvshowbiz/article-2937220/Lucy-Mecklenburgh-Thom-Evans-Robbie-Savage-help-PG-Tips-Monkey-prepare-Red-Nose-Day-Challenge.html
                * https://www.dailymail.co.uk/news/article-2937206/Halal-abattoir-staff-hacked-taunted-sheep-One-worker-sacked-three-suspended-caught-camera-carrying-horrifying-routine-abuse.html
                '''
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["@type"] == "WebPage":
                        if data["headline"]:
                            titles_list.append(
                                self.title_cleaning(data["headline"]))
                        if isinstance(data["mainEntity"], list):
                            if data["mainEntity"][0]["name"]:
                                titles_list.append(
                                    self.title_cleaning(
                                        data["mainEntity"][0]["name"]))
                        elif not isinstance(data["mainEntity"], list):
                            if data["mainEntity"]["name"]:
                                titles_list.append(
                                    self.title_cleaning(
                                        data["mainEntity"]["name"]))

        '''
        Tested on
        * https://www.independent.co.uk/arts-entertainment/tv/news/ratched-netflix-trigger-warning-child-abuse-suicide-violence-sarah-paulson-b571405.html
          <script type='application/ld+json'..."article_title":"Ratched fans urge Netflix to introduce ‘trigger warning’ over scenes of child abuse, lobotomies and suicide"...>
        * https://www.independent.co.uk/news/uk/home-news/coronavirus-childcare-parents-lockdown-schools-a9688116.html
          <script type='application/ld+json'..."article_title":"'The guilt, the pressure and the relentlessness': Struggles to access childcare wreaking havoc on parent's mental health and work life"...>
        '''
        with suppress(Exception):
            scripts_two = html.find_all('script', {'type': 'application/json'})
            scripts_two = [
                script for script in scripts_two if script is not None
            ]
            for script in scripts_two:
                with suppress(Exception):
                    data = json.loads(script.string, strict=False)
                    if data["article_title"]:
                        titles_list.append(
                            self.title_cleaning(data["article_title"]))
        titles_list = [title for title in titles_list if title != '']
        if not titles_list:
            return " "
        best_title = max(sorted(set(titles_list)), key=titles_list.count)
        return best_title
