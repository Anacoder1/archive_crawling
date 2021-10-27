"""Unit tests for the custom title extractor in Archive-Crawling project. Started 03-02-21"""

import logging
import unittest
import requests
import requests_mock
from bs4 import BeautifulSoup
from dotmap import DotMap
from python.tests.archive_crawling.url_dict import url_dict
from python.services.archive_crawling.pipeline.extractor.extractors.title_extractor import TitleExtractor

HTML_DIR = "tests/archive_crawling/test_data/"


class UnitTestsTitleExtractor(unittest.TestCase):
    @requests_mock.Mocker(kw='mock')
    def boilerplate_function(self, html_file_name, url_variable, expected_content, **kwargs):
        self.TE = TitleExtractor()
        item = {}
        item['spider_response'] = DotMap()
        with open(HTML_DIR + html_file_name, 'r') as html_data:
            kwargs['mock'].get(url_dict[url_variable], text=html_data.read())
            item['spider_response'].body = requests.get(url_dict[url_variable]).text
            self.assertEqual(self.TE._title({'spider_response': item['spider_response']}), expected_content)

    def test_title_mega(self):
        self.boilerplate_function('blank_1.html', 'blank_1', " ")

        self.boilerplate_function('business_standard_1.html', 'business_standard_1', "Walmart, Disney suspend contributions to US lawmakers who opposed Biden win")
        self.boilerplate_function('business_standard_2.html', 'business_standard_2', "US House committee releases report supporting Donald Trump's impeachment")
        self.boilerplate_function('business_standard_3.html', 'business_standard_3', "WB economist: China will need to learn to restructure emerging market debt")
        self.boilerplate_function('business_standard_4.html', 'business_standard_4', "Death of galaxy: Galactic collision spews gases equal to 10,000 suns a year")
        self.boilerplate_function('business_standard_5.html', 'business_standard_5', "Auto, PSU stocks to outperform in the short-term: Vinay Rajani of HDFC Sec")

        self.boilerplate_function('cnbc_1.html', 'cnbc_1', "The plant-based meat industry has grown into a $20 billion business  but challenges remain")
        self.boilerplate_function('cnbc_2.html', 'cnbc_2', "Why lawmakers from both parties hope Trump 'calms down and simply signs the bill very quietly'")
        self.boilerplate_function('cnbc_3.html', 'cnbc_3', "In very different Christmas messages, Biden discusses Covid and Trump barely makes reference")
        self.boilerplate_function('cnbc_4.html', 'cnbc_4', "Dominion Voting warns Fox News, Sean Hannity, other conservative outlets that defamation lawsuits are imminent")
        self.boilerplate_function('cnbc_5.html', 'cnbc_5', "'Wonder Woman 1984' could have the best pandemic opening if HBO Max doesn't cannibalize ticket sales")

        self.boilerplate_function('daily_mail_1.html', 'daily_mail_1', "Brexit: UK actors to miss out on Prince William role and future jobs")
        self.boilerplate_function('daily_mail_2.html', 'daily_mail_2', "TOM LEONARD: Stars' haunt that had mischief on the menu")
        self.boilerplate_function('daily_mail_3.html', 'daily_mail_3', "NASA astronaut Victor Glover shares his first video from SPACE")
        self.boilerplate_function('daily_mail_4.html', 'daily_mail_4', "Hojbjerg is Mourinho's midfield general at high-flying Spurs")
        self.boilerplate_function('daily_mail_5.html', 'daily_mail_5', "The key battles in Tottenham's top of the table clash with Chelsea")
        self.boilerplate_function('daily_mail_6.html', 'daily_mail_6', "Lucy Mecklenburgh and the PG Tips Monkey lend support for Comic Relief")
        self.boilerplate_function('daily_mail_7.html', 'daily_mail_7', "Halal abattoir staff 'hacked and taunted sheep'")

        self.boilerplate_function('deccan_herald_1.html', 'deccan_herald_1', "Agriculture department urged to regulate fertilisers supply")
        self.boilerplate_function('deccan_herald_2.html', 'deccan_herald_2', "Pak needs to explain Osama's presence in Abbottabad: Haqqani")
        self.boilerplate_function('deccan_herald_3.html', 'deccan_herald_3', "Children to be adopted through State governments:Mother Teresa orphanages")
        self.boilerplate_function('deccan_herald_4.html', 'deccan_herald_4', "5 from DK to take part in Special Olympics World Games")
        self.boilerplate_function('deccan_herald_5.html', 'deccan_herald_5', "Switching from poppy to cardamom, Arunachal district farmers set to taste success in 2021")

        self.boilerplate_function('economic_times_1.html', 'economic_times_1', "Government mops up Rs 8,660 cr from disinvestment in '02")
        self.boilerplate_function('economic_times_2.html', 'economic_times_2', "Delhi policeman nabbed for taking bribe from kidney racketeer")
        self.boilerplate_function('economic_times_3.html', 'economic_times_3', "Indian universities look abroad for success at home")
        self.boilerplate_function('economic_times_4.html', 'economic_times_4', "Conviction rate in theft cases in central railway's Mumbai division falls steeply")
        self.boilerplate_function('economic_times_5.html', 'economic_times_5', "Centre always ready for talks, dialogue would fetch solution: Manohar Lal Khattar to farmers")

        self.boilerplate_function('espn_cricinfo_1.html', 'espn_cricinfo_1', "Leicestershire let Finals Day appearance slip as Samit Patel hauls Notts through")
        self.boilerplate_function('espn_cricinfo_2.html', 'espn_cricinfo_2', "Mitchell Claydon misses Sussex's Blast defeat after hand-sanitiser ball-tampering ban")
        self.boilerplate_function('espn_cricinfo_3.html', 'espn_cricinfo_3', "Azeem Rafiq calls for witness anonymity in Yorkshire racism investigation")
        self.boilerplate_function('espn_cricinfo_4.html', 'espn_cricinfo_4', "IPL 2020 - Jofra Archer thriving in different type of pressure at IPL, says Rajasthan Royals team-mate Jos Buttler")
        self.boilerplate_function('espn_cricinfo_5.html', 'espn_cricinfo_5', "England's Sarah Glenn reaches career-best T20I rankings, Meg Lanning moves up")

        self.boilerplate_function('euro_news_1.html', 'euro_news_1', "France's next aircraft carrier to be nuclear-powered, Macron confirms")
        self.boilerplate_function('euro_news_2.html', 'euro_news_2', "Charlie Hebdo trial: Prosecutors request 30-year sentence for fugitive widow of attacker")
        self.boilerplate_function('euro_news_3.html', 'euro_news_3', "Election misinformation isn't an American phenomenon - it's spreading across Europe, too  View")
        self.boilerplate_function('euro_news_4.html', 'euro_news_4', "The EU must leverage closer trade ties with Uzbekistan to ensure progress on human rights  View")
        self.boilerplate_function('euro_news_5.html', 'euro_news_5', "Budapest and Warsaw protest their governments' budget veto by lighting monuments EU-blue")

        self.boilerplate_function('evening_standard_1.html', 'evening_standard_1', "Boris Johnson forced into free school meals U-turn after Marcus Rashford campaign as footballer says: Look what we can do together")
        self.boilerplate_function('evening_standard_2.html', 'evening_standard_2', "David Cameron warns UK will 'lose respect overseas' with merger of Foreign Office and Department of International Development")
        self.boilerplate_function('evening_standard_3.html', 'evening_standard_3', "Calls for advice behind Christmas bubbles to be published as scientists warn easing restrictions could prompt third wave")
        self.boilerplate_function('evening_standard_4.html', 'evening_standard_4', "BBC defends Have I Got News For You over joke about bombing Glastonbury to get rid of Jeremy Corbyn supporters")
        self.boilerplate_function('evening_standard_5.html', 'evening_standard_5', "Londons restaurants in Tier 2 will face no specific limit on table sizes for single households dining indoors, No 10 confirms")

        self.boilerplate_function('express_1.html', 'express_1', "French fishermen TURN on Emmanuel Macron after Brexit ultimatum - 'We've overstepped mark'")
        self.boilerplate_function('express_2.html', 'express_2', "BBC Weather: Fog and snow to sweep Europe as continent rocked by 'blocking' high pressure")
        self.boilerplate_function('express_3.html', 'express_3', "Brexit LIVE: Laura Kuenssberg exposes almighty fishing row about to erupt 'Could be messy'")
        self.boilerplate_function('express_4.html', 'express_4', "Mysterious illness causes public panic in Indian district as hundreds hospitalised")
        self.boilerplate_function('express_5.html', 'express_5', "Bible apocalypse: Burnt Pyramid notes reveal Newton's astonishingly complex occult study")

        self.boilerplate_function('financial_express_1.html', 'financial_express_1', "Delhi power crisis gets worse, Arvind Kejriwal warns discom licences could be cancelled")
        self.boilerplate_function('financial_express_2.html', 'financial_express_2', "Northeast student Nido Tania beaten to death in Delhi, shocked community demands action")
        self.boilerplate_function('financial_express_3.html', 'financial_express_3', "Diesel price hiked by 50p, non-subsidised LPG cylinder rate cut by Rs 107 day after quota hiked from 9 to 12")
        self.boilerplate_function('financial_express_4.html', 'financial_express_4', "Govt kills two reforms: raises LPG cap, snaps its Aadhaar link; Rahul Gandhi's wish will cost Rs 5,000 cr")
        self.boilerplate_function('financial_express_5.html', 'financial_express_5', "RBI Governor Raghuram Rajan effects dramatic shift as India quietly begins tryst with inflation targeting")

        self.boilerplate_function('hindu_business_line_1.html', 'hindu_business_line_1', "Kraft paper paucity: Mills blame waste paper costs; box makers accuse them of creating shortage")
        self.boilerplate_function('hindu_business_line_2.html', 'hindu_business_line_2', "Delegation of Ambassadors, High Commissioners visits Bharat Biotech to discuss progress of Covaxin")
        self.boilerplate_function('hindu_business_line_3.html', 'hindu_business_line_3', "Centre passes on 6th instalment of borrowing to States to meet GST compensation shortfall")
        self.boilerplate_function('hindu_business_line_4.html', 'hindu_business_line_4', "Pull payments made on behalf of merchants: Acquirer banks should not push consumers to pay for services")
        self.boilerplate_function('hindu_business_line_5.html', 'hindu_business_line_5', "RBI to Kotak Mahindra Bank: No dividend payment on perpetual non-cumulative preference shares")

        self.boilerplate_function('independent_1.html', 'independent_1', "Elijah McClain: Petition demanding justice for death of young black man detained by police reaches 2 million signatures")
        self.boilerplate_function('independent_2.html', 'independent_2', "'The guilt, the pressure and the relentlessness': Struggles to access childcare wreaking havoc on parent's mental health and work life")
        self.boilerplate_function('independent_3.html', 'independent_3', "Ratched fans urge Netflix to introduce trigger warning over scenes of child abuse, lobotomies and suicide")
        self.boilerplate_function('independent_4.html', 'independent_4', "The Queens hidden cousins: Who were Nerissa and Katherine Bowes-Lyon and why were they kept away from the royal family?")
        self.boilerplate_function('independent_5.html', 'independent_5', "Bridgerton viewers learn that Lady Violet actor Ruth Gemmell played Tracy Beakers mum: She really was a famous actress after all")

        self.boilerplate_function('india_today_1.html', 'india_today_1', "India's Covid vaccination drive to kick off with virtual launch by PM Modi, roll out of CoWin app on Jan 16")
        self.boilerplate_function('india_today_2.html', 'india_today_2', "Amazon Great Republic Day Sale announced from January 20: Deals, bank offers, and more")
        self.boilerplate_function('india_today_3.html', 'india_today_3', "India vs Australia: If India win at Gabba, this will be their greatest Test series victory ever-Shoaib Akhtar")
        self.boilerplate_function('india_today_4.html', 'india_today_4', "Tim Paine wasn't forced to apologise: Justin Langer says Australia captain was remorseful over conduct")
        self.boilerplate_function('india_today_5.html', 'india_today_5', "As vaccines get shipped, safety concern looms over Indians, 41% will choose to wait: Survey")

        self.boilerplate_function('ndtv_1.html', 'ndtv_1', "We can't influence Indian High Commission for visas: PCB | Cricket News")
        self.boilerplate_function('ndtv_2.html', 'ndtv_2', "BJP and Congress lock horns over newspaper advertisements in poll-bound Himachal Pradesh")
        self.boilerplate_function('ndtv_3.html', 'ndtv_3', "NYT's Gardiner Harris Writes 'Delhi's True Menace Come From Its Air, Water, Food and Flies'. Do You Agree?")
        self.boilerplate_function('ndtv_4.html', 'ndtv_4', "Spread Of Japanese Encephalitis In Poorvanchal Due To Lack Of Sanitation: UP Chief Minister Yogi Adityanath")
        self.boilerplate_function('ndtv_5.html', 'ndtv_5', "Sean Connery, \"A Legend On Screen And Off\": Tributes From Hugh Jackman, Abhishek Bachchan, Hrithik Roshan And Others")

        self.boilerplate_function('new_york_post_1.html', 'new_york_post_1', "Brooklyn Tea Party rallies against Ground Zero mosque, multiculturalism")
        self.boilerplate_function('new_york_post_2.html', 'new_york_post_2', "Syndergaards goal for what may be his last MLB start for a while")
        self.boilerplate_function('new_york_post_3.html', 'new_york_post_3', "Scaramucci expected to finally join Trump administration")
        self.boilerplate_function('new_york_post_4.html', 'new_york_post_4', "Campaign for disgraced ex-cop Daniel Pantaleo raises more than $170K")
        self.boilerplate_function('new_york_post_5.html', 'new_york_post_5', "Country singer who survived Nashville bombing reunited with cat")

        self.boilerplate_function('new_york_times_1.html', 'new_york_times_1', "Impeachment Trial Highlights: Trumps Lawyers Avoid Bolton, Giuliani Surfaces and a History Lesson")
        self.boilerplate_function('new_york_times_2.html', 'new_york_times_2', "In Serious Noticing, James Wood Closely Reads Chekhov and Others  Including Himself")
        self.boilerplate_function('new_york_times_3.html', 'new_york_times_3', "Is It Offensive for Sports Teams and Their Fans to Use Native American Names, Imagery and Gestures?")
        self.boilerplate_function('new_york_times_4.html', 'new_york_times_4', "Iranian Missile Accidentally Brought Down Ukrainian Jet, Officials Say")
        self.boilerplate_function('new_york_times_5.html', 'new_york_times_5', "Joe Biden, Seeking Commander-in-Chief Moment, Denounces Trumps Iran Escalation")

        self.boilerplate_function('one_india_1.html', 'one_india_1', "Congress leader DK Shivakumar to appear before CBI in disproportionate assets case today")
        self.boilerplate_function('one_india_2.html', 'one_india_2', "Will make Bengal police lick boots if BJP comes to power in next Assembly elections: Raju Banerjee")
        self.boilerplate_function('one_india_3.html', 'one_india_3', "Cyclone Nivar to hit TN with winds at 145 Kmph; Puducherry LG Kiran Bedi appeals people to stay safe")
        self.boilerplate_function('one_india_4.html', 'one_india_4', "Delhi riots: Umar Khalid didn't take security to 'conspiratorial meetings', says charge sheet")
        self.boilerplate_function('one_india_5.html', 'one_india_5', "Xi Jinping finally congratulates Biden; hopes US, China will uphold spirit of non-confrontation")

        self.boilerplate_function('scroll_news_1.html', 'scroll_news_1', "They can beat Australia in their own den: Shastri backs India's 'fabulous five' quicks to shine")
        self.boilerplate_function('scroll_news_2.html', 'scroll_news_2', "Champions League: Last-gasp wins take Juventus, Chelsea and Sevilla into last 16, Barcelona cruise")
        self.boilerplate_function('scroll_news_3.html', 'scroll_news_3', "Coronavirus: In fresh protocols, Centre asks states to consult before imposing local lockdowns")
        self.boilerplate_function('scroll_news_4.html', 'scroll_news_4', "What is the extent of caste segregation in Indian villages today? New data gives us an idea")
        self.boilerplate_function('scroll_news_5.html', 'scroll_news_5', "Khichdification: IMA demands withdrawal of move allowing Ayurveda doctors to perform surgery")
        self.boilerplate_function('scroll_news_6.html', 'scroll_news_6', "Why Beginning on Mubi is a film you cannot miss")
        self.boilerplate_function('scroll_news_7.html', 'scroll_news_7', "Ground report: In Haryana, farmer protests run into a caste divide")

        self.boilerplate_function('the_indian_express_1.html', 'the_indian_express_1', "Pakistan hotel attack: Four killed as armed militants storm 5-star hotel in Gwadar port city, says police")
        self.boilerplate_function('the_indian_express_2.html', 'the_indian_express_2', "Ayushman Bharat: Aadhaar mandatory for those seeking treatment for second time")
        self.boilerplate_function('the_indian_express_3.html', 'the_indian_express_3', "BJP MP Shobha Karandlaje challenges Karnataka CM Siddaramaiah govt to arrest her")
        self.boilerplate_function('the_indian_express_4.html', 'the_indian_express_4', "Days are not far when Kashmiri Pandits would return to their homes with dignity: JK BJP")
        self.boilerplate_function('the_indian_express_5.html', 'the_indian_express_5', "Head constable suspended and challaned for talking on cell phone while driving in Chandigarh")

        self.boilerplate_function('the_pioneer_1.html', 'the_pioneer_1', "Punjab CM launches Diginest mobile app to ensure digital access to State Govt directory")
        self.boilerplate_function('the_pioneer_2.html', 'the_pioneer_2', "HC seeks reply from State in 2 weeks on Adi Shankaracharyas Samadhi")
        self.boilerplate_function('the_pioneer_3.html', 'the_pioneer_3', "AAP MLA visits Singhu Border to ensure WiFi facilities for farmers")
        self.boilerplate_function('the_pioneer_4.html', 'the_pioneer_4', "Govt OKs bank loans at lower rates to distilleries for raising ethanol production")
        self.boilerplate_function('the_pioneer_5.html', 'the_pioneer_5', "PIL questions acquisition of universitys fertile land for constructing Pantnagar airport")

        self.boilerplate_function('times_of_india_1.html', 'times_of_india_1', "ISRO's second launch pad to be sent by March-end")
        self.boilerplate_function('times_of_india_2.html', 'times_of_india_2', "CBSE makes more room for kids with special needs")
        self.boilerplate_function('times_of_india_3.html', 'times_of_india_3', "Freshers join in to participate in Clean & Clear Lucknow Times Fresh Face 2012 at Shri Ramswaroop Memorial College")
        self.boilerplate_function('times_of_india_4.html', 'times_of_india_4', "IIT Madras disappointed over not granted Institutes of Eminence status; writes to HRD ministry")
        self.boilerplate_function('times_of_india_5.html', 'times_of_india_5', "Nine samples of UK-returned and their contacts test negative for UKs mutated Covid-19 strain, report of two awaited")

        self.boilerplate_function('usa_today_1.html', 'usa_today_1', "President Trump to hold White House COVID-19 summit as pressure mounts for FDA vaccine approval")
        self.boilerplate_function('usa_today_2.html', 'usa_today_2', "College and Olympic wrestling legend Dan Gable 'honored' with Presidential Medal of Freedom")
        self.boilerplate_function('usa_today_3.html', 'usa_today_3', "Critically endangered North Atlantic right whale population gets a boost: 2 newborns spotted off US coast")
        self.boilerplate_function('usa_today_4.html', 'usa_today_4', "Seattle Sounders pull off dramatic rally to reach 2020 MLS Cup, will play Columbus Crew on Saturday")
        self.boilerplate_function('usa_today_5.html', 'usa_today_5', "Bob Woodward to take on final days of Trumps presidency in next book")

    def test_title_mega_exception(self):
        TE = TitleExtractor()
        item = {}
        item['spider_response'] = DotMap()
        item['spider_response'].body = ''
        with self.assertLogs('foo', level='ERROR') as cm:
            logging.getLogger('foo').exception('exception')
        self.assertEqual(cm.output, ['ERROR:foo:exception\nNoneType: None'])
        self.assertEqual(TE._title({'spider_response': item['spider_response']}), " ")


if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
