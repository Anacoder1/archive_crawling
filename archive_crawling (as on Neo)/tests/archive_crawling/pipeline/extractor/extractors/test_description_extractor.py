"""Unit tests for the custom description extractor in Archive-Crawling project. Started 03-02-21"""

import unittest
import requests
import requests_mock
from bs4 import BeautifulSoup
from dotmap import DotMap
from python.tests.archive_crawling.url_dict import url_dict
from python.services.archive_crawling.pipeline.extractor.extractors.description_extractor import DescriptionExtractor

HTML_DIR = "tests/archive_crawling/test_data/"


class UnitTestsDescriptionExtractor(unittest.TestCase):
    @requests_mock.Mocker(kw='mock')
    def boilerplate_function(self, html_file_name, url_variable, expected_content, **kwargs):
        self.DE = DescriptionExtractor()
        item = {}
        item['spider_response'] = DotMap()
        with open(HTML_DIR + html_file_name, 'r') as html_data:
            kwargs['mock'].get(url_dict[url_variable], text=html_data.read())
            item['spider_response'].body = requests.get(url_dict[url_variable]).text
            self.assertEqual(self.DE._description({'spider_response': item['spider_response']}), expected_content)

    def test_description_mega(self):
        self.boilerplate_function('blank_1.html', 'blank_1', " ")

        self.boilerplate_function('business_standard_1.html', 'business_standard_1', "Walmart Inc, the world's biggest retailer, and Walt Disney Co joined other major companies in indefinitely suspending donations to US lawmakers who voted against Joe Biden's election certification")
        self.boilerplate_function('business_standard_2.html', 'business_standard_2', "US House Judiciary Committee issued a 76-page compiled report supporting the impeachment of President Donald Trump on \"incitement of insurrection\" charges following a riot in the Capitol")
        self.boilerplate_function('business_standard_3.html', 'business_standard_3', "Increasing debt distress in emerging markets means that China will need to start restructuring debts in the same way that Paris Club lenders did in past crises, World Bank Chief Economist said")
        self.boilerplate_function('business_standard_4.html', 'business_standard_4', "The merging galaxy formed 4.5 billion years ago is dubbed ID2299 and is ejecting gases equivalent to 10,000 Suns-worth of gas a year")
        self.boilerplate_function('business_standard_5.html', 'business_standard_5', "Immediate resistance for the Nifty is seen at 14,890")

        self.boilerplate_function('cnbc_1.html', 'cnbc_1', "Demand for meat alternatives has grown and will continue to rise, but the industry still has hurdles to overcome in different parts of the world, analysts said.")
        self.boilerplate_function('cnbc_2.html', 'cnbc_2', "CNBC contributor Ben White explains how Congress could override a veto from President Trump on the Covid stimulus bill.")
        self.boilerplate_function('cnbc_3.html', 'cnbc_3', "Nearly 330,000 Americans have died from the virus, and there are over 18.7 million confirmed cases in the U.S.")
        self.boilerplate_function('cnbc_4.html', 'cnbc_4', "Media allies of President Trump, such as Fox News, have been sent letters by Dominion Voting Systems about election conspiracy claims.")
        self.boilerplate_function('cnbc_5.html', 'cnbc_5', "\"Wonder Woman 1984\" arrives in theaters and on HBO Max Christmas Day. It could have the highest pandemic box office open, if streaming doesn't hurt ticket sales.")

        self.boilerplate_function('daily_mail_1.html', 'daily_mail_1', "A casting agent has blamed Brexit rules for why she cannot pick a British child to play a young Prince William in a biopic about Lady Diana insisting the role must go to an EU youngster.")
        self.boilerplate_function('daily_mail_2.html', 'daily_mail_2', "TOM LEONARD: Princess Margaret chain-smoked at a back table, Ava Gardner joined the pianist for an impromptu duet and Elizabeth Taylor packed her guest Rock Hudson off to the nearest gay haunt.")
        self.boilerplate_function('daily_mail_3.html', 'daily_mail_3', "NASA astronaut Victor Glover shared his first video from space as he and three other astronauts soared above the Earth while traveling to the International Space Station.")
        self.boilerplate_function('daily_mail_4.html', 'daily_mail_4', "Pierre-Emile Hojbjerg may have been a signing that didn't create much fanfare among Tottenham supporters, but they already know his worth under their manager Jose Mourinho.")
        self.boilerplate_function('daily_mail_5.html', 'daily_mail_5', "After such a solid start to the season, there is reason to believe Tottenham could well challenge for the title. Chelsea, too, will always fancy their chances at this early stage of the season.")
        self.boilerplate_function('daily_mail_6.html', 'daily_mail_6', "Lucy Mecklenburgh, Thom Evans and Robbie Savage have been helping the PG Tips Monkey prepare to take on the monumental challenge of climbing The Shard in a bid to raise money for Red Nose Day.")
        self.boilerplate_function('daily_mail_7.html', 'daily_mail_7', "GRAPHIC CONTENT: A worker at a halal abattoir in Thirsk, North Yorkshire has been sacked and three others suspended after being filmed carrying out horrifying abuse on sheep.")

        self.boilerplate_function('deccan_herald_1.html', 'deccan_herald_1', "Farmers will be happy only if they get good rains and sufficient fertilisers. They were is deep trouble due to the improper supply of fertilisers.")
        self.boilerplate_function('deccan_herald_2.html', 'deccan_herald_2', "Osama bin Laden's presence in Abbottabad was definitely known to ''somebody'' in Pakistan, Islamabad's former top diplomat in the US, Husain Haqqani, has said, arguing that his country owes an explanation to the world about the slain al Qaeda leader's local benefactor.")
        self.boilerplate_function('deccan_herald_3.html', 'deccan_herald_3', "The decision of Mother Teresa's orphanages not to offer children for adoption over ideological differences with the new adoption guidelines has kicked off ...")
        self.boilerplate_function('deccan_herald_4.html', 'deccan_herald_4', "Five athletes from Dakshina Kannada will take part in the Special Olympics World Games in Abu Dhabi in 2019.")
        self.boilerplate_function('deccan_herald_5.html', 'deccan_herald_5', "When a group of farmers in Anjaw the country's easternmost district in Arunachal Pradesh, agreed to shift from the \"lucrative\"poppycultivation to grow the aromatic large cardamom a decade ago, they were not expecting a huge turnaround in their fortunes. But their decision to move away from the harmfulpoppycultivation has paid off. Come February, the farmers willget to see their organically grown large cardamom exported under a brand name of their own, a reward for the gamble they took years ago.")

        self.boilerplate_function('economic_times_1.html', 'economic_times_1', "The total disinvestment realisation of the government during 2002 topped Rs 8,660 crore. The cabinet committee on disinvestment (CCD) had cleared transactions worth Rs 6,168 crore during the year.")
        self.boilerplate_function('economic_times_2.html', 'economic_times_2', "Delhi Police has arrested an Assistant Sub Inspector for allegedly accepting a bribe of Rs 19 lakh from the driver of an accused in the infamous kidney racket to let them go scot-free.")
        self.boilerplate_function('economic_times_3.html', 'economic_times_3', "Foreign universities may soon be able to set up in India but some of their Indian counterparts are looking in the other direction to better equip students for the demands of the global economy.")
        self.boilerplate_function('economic_times_4.html', 'economic_times_4', "According to official data, the conviction rate in theft cases of railway properties has witnessed a steep fall in Mumbai Division of Central Railway.")
        self.boilerplate_function('economic_times_5.html', 'economic_times_5', "Farmers have been protesting against the Centre's farm laws, fearing that the new laws would lead to the dismantling of the minimum support price system, leaving them at the \"mercy\" of big corporates.")

        self.boilerplate_function('espn_cricinfo_1.html', 'espn_cricinfo_1', "Nottinghamshire progress on higher Powerplay score after securing dramatic tie off last ball")
        self.boilerplate_function('espn_cricinfo_2.html', 'espn_cricinfo_2', "Seamer will miss first two games of 2021 as well after nine-match ban imposed by CDC")
        self.boilerplate_function('espn_cricinfo_3.html', 'espn_cricinfo_3', "Ex-player fears that current cricketers will be reluctant to speak out about colleagues")
        self.boilerplate_function('espn_cricinfo_4.html', 'espn_cricinfo_4', "Fifty-over cricket must take a back seat in build-up to T20 World Cup, says senior batsman")
        self.boilerplate_function('espn_cricinfo_5.html', 'espn_cricinfo_5', "Glenn breaks into top ten on bowlers' list; Georgia Wareham reaches career-best-equalling No. 10 position")

        self.boilerplate_function('euro_news_1.html', 'euro_news_1', "France's current flagship warship is to be retired in 2038. It will be replaced by a bigger, nuclear-powered model, Macron said on Tuesday.")
        self.boilerplate_function('euro_news_2.html', 'euro_news_2', "Prosecutors have asked for sentences ranging from 5 years to life imprisonment for the defendants in the Charlie Hebdo trial, including the fugitive widow of one of the attackers.")
        self.boilerplate_function('euro_news_3.html', 'euro_news_3', "The recent US presidential elections have been marred by accusations of voter fraud, with misinformation spreading online. It's not just an American-centric issue. The problem is spreading across Europe ahead of crucial elections in France and Germany in 2021.")
        self.boilerplate_function('euro_news_4.html', 'euro_news_4', "As Uzbekistans applies to the EU's GSP+ scheme, Brussels should use its leverage in the application process to ensure progress is being made on human and labour rights in the central Asian country.")
        self.boilerplate_function('euro_news_5.html', 'euro_news_5', "Budapest's Statue of Liberty and Warsaw's Palace of Culture and Science are to be lighted EU-blue for three days starting on Wednesday.")

        self.boilerplate_function('evening_standard_1.html', 'evening_standard_1', "'THIS is England in 2020'")
        self.boilerplate_function('evening_standard_2.html', 'evening_standard_2', "The former Prime Minister tweeted his commentson Tuesday afternoon followingthe Government's announcement")
        self.boilerplate_function('evening_standard_3.html', 'evening_standard_3', "Experts warned easing measures was throwing fuel on the Covid fire")
        self.boilerplate_function('evening_standard_4.html', 'evening_standard_4', "The BBC has defended an episode of Have I Got News For You after it featured a joke about bombing Glastonbury to get rid of Jeremy Corbyn supporters.")
        self.boilerplate_function('evening_standard_5.html', 'evening_standard_5', "Downing Street has confirmed that while under Tier 2 restrictions, restaurants will be free to serve tables of any size provided diners are all from one household or social bubble.")

        self.boilerplate_function('express_1.html', 'express_1', "FRENCH fishermen have lashed out at Emmanuel Macron, warning he is playing a \"dangerous game\" and has \"overstepped the mark\" by threatening to veto a post-Brexit trade deal with the UK.")
        self.boilerplate_function('express_2.html', 'express_2', "BBC Weather has forecast stagnant and cold air across Europe that will bring mist, fog and frost to the continent over the coming days.")
        self.boilerplate_function('express_3.html', 'express_3', "A HUGE new fishing row has erupted between Scottish fishermen anf the UK Government, with BBC Political Editor Laura Kuenssberg warning: \"This could get messy.\"")
        self.boilerplate_function('express_4.html', 'express_4', "OFFICIALS in India are reportedly seeking to manage panic in the Indian state of Andhra Pradesh due to a mysterious illness spreading in the district.")
        self.boilerplate_function('express_5.html', 'express_5', "SIR ISAAC NEWTON'S fascination with biblical apocalypse, pyramids and the occult have been revealed in burnt fragmentary manuscript notes.")

        self.boilerplate_function('financial_express_1.html', 'financial_express_1', "Barring a last minute order by the central government to NTPC, or a temporary cash support by the Delhi government, large areas in eastern and central parts of the capital can expect 10-12 hours of daily power cuts within a week")
        self.boilerplate_function('financial_express_2.html', 'financial_express_2', "In a shocking incidence of violence in South Delhi's Lajpat Nagar area, a student from northeast Nido Tania, was beaten to death mercilessly by as many as 8 men")
        self.boilerplate_function('financial_express_3.html', 'financial_express_3', "Diesel price was hiked by 50 paise per litre today, but there will be no change in petrol rates")
        self.boilerplate_function('financial_express_4.html', 'financial_express_4', "The Cabinet Committee on Political Affairs Thursday granted Congress vice-president Rahul Gandhis wish and raised the annual cap for subsidised cylinders to 12 from nine, undoing the reformist move to restrict LPG subsidy to deserving families with an eye on elections")
        self.boilerplate_function('financial_express_5.html', 'financial_express_5', "Without explicitly saying so, the Reserve Bank of India (RBI), with Governor Raghuram Rajan in hot seat, has effectively begun to target inflation based on consumer prices, a dramatic shift in approach for a central bank that has struggled to manage the balance between growth and inflation")

        self.boilerplate_function('hindu_business_line_1.html', 'hindu_business_line_1', "Paper mills have blamed rising waste paper cost for the recent increase in prices of kraft paper supplied to corrugated box makers.This is in contrast to the user industry blaming the paper mills for")
        self.boilerplate_function('hindu_business_line_2.html', 'hindu_business_line_2', "A delegation of 70 Ambassadors and High Commissioners visited the Bharat Biotech facility today at Genome Valley, Hyderabad, to study the progress being made in the development of Covid vaccine.They w")
        self.boilerplate_function('hindu_business_line_3.html', 'hindu_business_line_3', "GST compensation shortfallGovt releases 6th instalment to StatesThe Finance Ministry on Wednesday released the sixth weekly instalment of Rs. 6,000 crore to the States to meet the GST compensation sho")
        self.boilerplate_function('hindu_business_line_4.html', 'hindu_business_line_4', "The Reserve Bank of India (RBI) needs to move towards creating an environment whereby for pull payments effected on behalf of merchants, the acquirer banks/Payment Aggregators (PAs) are not allowed to")
        self.boilerplate_function('hindu_business_line_5.html', 'hindu_business_line_5', "The Reserve Bank of India has restricted Kotak Mahindra Bank from paying dividend on perpetual non-cumulative preference shares (PNCPS).The private sector lender, in a regulatory filing, said it has r")

        self.boilerplate_function('independent_1.html', 'independent_1', "'Demand these officers are taken off duty, and that a more in-depth investigation is held', page reads")
        self.boilerplate_function('independent_2.html', 'independent_2', "'I had to ask my work to leave me on furlough as I wasnt able to work my required hours with our pre-school only opening part-time. I have since been made redundant,' says mother-of-two")
        self.boilerplate_function('independent_3.html', 'independent_3', "Despite presence of warning over graphic content, fans have called for more")
        self.boilerplate_function('independent_4.html', 'independent_4', "New season of The Crown revisits the story of the sisters tragic lives")
        self.boilerplate_function('independent_5.html', 'independent_5', "Gemmell starred in the 2004 CBBC film Tracy Beaker: The Movie of Me")

        self.boilerplate_function('india_today_1.html', 'india_today_1', "Prime Minister Narendra Modi will kickstart the Covid-19 vaccination programme in India with a virtual launch on January 16, sources have told India Today.")
        self.boilerplate_function('india_today_2.html', 'india_today_2', "Amazon's Great Republic Day Sale begins January 20 but Prime members will get 24 hours early access on deals.")
        self.boilerplate_function('india_today_3.html', 'india_today_3', "Former Pakistan fast bowler Shoaib Akhtar lauded India for the fight they have shown in the series so far and said that they should go on to win the final Test in Brisbane.")
        self.boilerplate_function('india_today_4.html', 'india_today_4', "India tour of Australia: Australia head coach Justin Langer backed Tim Paine, saying he was not forced to apologised for his conduct in the Sydney Test. Paine was slammed by former cricketers for his nasty behaviour on Day 5 when India sealed a fighting draw.")
        self.boilerplate_function('india_today_5.html', 'india_today_5', "The Covid-19 vaccination drive is just hours away now. However, reports indicate that though a majority are keen to get vaccinated, concern about the safety and efficacy of the vaccine is common among citizens.")

        self.boilerplate_function('ndtv_1.html', 'ndtv_1', "Pakistan Cricket Board made it clear that it had done everything under its power to get the visas for its cricketers to play in the IPL next year.")
        self.boilerplate_function('ndtv_2.html', 'ndtv_2', "Newspaper advertisements are the latest bone of contention between the Congress and the BJP in poll bound Himachal Pradesh. Congress is crying foul over the advertisement the Dhumal government has put out to list its achievements during its tenure.")
        self.boilerplate_function('ndtv_3.html', 'ndtv_3', "These perils sicken, disable and kill millions in India annually, making for one of the worst public health disasters in the world, writes The New York Times' Gardiner Harris.")
        self.boilerplate_function('ndtv_4.html', 'ndtv_4', "Uttar Pradesh Chief Minister Yogi Adityanath on Sunday attributed the spread of Japanese Encephalitis (JE) in the state's eastern region to the lack of sanitation and cleanliness of water bodies.")
        self.boilerplate_function('ndtv_5.html', 'ndtv_5', "Hugh Jackman wrote: \"I grew up idolizing Sean Connery. A legend on screen and off. Rest in peace\"")

        self.boilerplate_function('new_york_post_1.html', 'new_york_post_1', "About 125 people gathered at a recent Bay Ridge rally of the Brooklyn Tea Party to protest a variety of hot subjects especially the planned Ground Zero mosque, according to a Brooklyn Ink")
        self.boilerplate_function('new_york_post_2.html', 'new_york_post_2', "Noah Syndergaard is ready to take the baton. If the rookie right-hander needed any additional inspiration for his scheduled start Friday night in Pittsburgh, it came from watching Jacob deGrom manh")
        self.boilerplate_function('new_york_post_3.html', 'new_york_post_3', "Anthony Scaramuccis White House ambitions may end up taking the former hedgie to Paris. Scaramucci, founder of SkyBridge Capital, is expected to be named by President Trump to serve as ambassador")
        self.boilerplate_function('new_york_post_4.html', 'new_york_post_4', "'Opportunist' Corey Johnson turns on cops after long history as ally")
        self.boilerplate_function('new_york_post_5.html', 'new_york_post_5', "Buck McCoy had to scramble to safety when the explosion rocked his apartment near the blast site nearly a week ago.")

        self.boilerplate_function('new_york_times_1.html', 'new_york_times_1', "Senators hear the second installment of President Trumps legal defense and arguments for why he should not be removed from office.")
        self.boilerplate_function('new_york_times_2.html', 'new_york_times_2', "This new book includes the commanding literary critics pieces on Virginia Woolf, Saul Bellow and others, as well as more personal work about his childhood and his family.")
        self.boilerplate_function('new_york_times_3.html', 'new_york_times_3', "The Kansas City Chiefs will face the San Francisco 49ers for Super Bowl LIV. Chiefs fans regularly use a tomahawk chop to urge on their beloved team: Is it offensive?")
        self.boilerplate_function('new_york_times_4.html', 'new_york_times_4', "Western intelligence showed that Iran was responsible for the plane crash, suggesting that the deaths of those aboard were a consequence of the heightened tensions between Washington and Iran.")
        self.boilerplate_function('new_york_times_5.html', 'new_york_times_5', "Because the president refuses to level with the American people about the dangers United States troops and civilians now face in the Middle East, Mr. Biden said, I will attempt to do that.")

        self.boilerplate_function('one_india_1.html', 'one_india_1', "On October 5, the CBI conducted raids at 14 locations, including in Karnataka, Delhi and Mumbai at the premises belonging to Shivakumar and others, and recovered Rs 57 lakh cash and several documents, including property documents, bank related information, computer hard disk.")
        self.boilerplate_function('one_india_2.html', 'one_india_2', "Slamming Mamata Banerjee government, the BJP leader said the police force in the state do not extend any help to check the 'Gunda Raj'. His comment is facing backlash and has also angered locals in the state.")
        self.boilerplate_function('one_india_3.html', 'one_india_3', "Cyclone Nivar, which is expected to intensify into a 'very severe cyclonic storm' and cross Tamil Nadu and Puducherry coasts between Karaikal and Mamallapuram late in the evening of November 25 with a wind speed of 120-130 km per hour gusting to 145 kmph, India Meteorological Department (IMD) Director General Mrutunjay")
        self.boilerplate_function('one_india_4.html', 'one_india_4', "The ease and poise with which Khalid was navigating both the ideologies of left and ultra left strains of political thoughts indicated that his position in the overall power matrix was very, very close to the very top, it alleged. According to the charge sheet, Khalid allegedly held meetings with his associates a")
        self.boilerplate_function('one_india_5.html', 'one_india_5', "President Xi sent a message to Biden to congratulate him on his election as US president, becoming one of the last major leaders to congratulate the Democratic presidential candidate. Promoting healthy and stable development of China-US relations not only serves the fundamental interests of the people in both countries")

        self.boilerplate_function('scroll_news_1.html', 'scroll_news_1', "The India coach said his teams pace unit was the best in the world, despite being likely to be without the injured Ishant Sharma.")
        self.boilerplate_function('scroll_news_2.html', 'scroll_news_2', "They are the first teams to make it out of the group stage, doing so with two games to spare.")
        self.boilerplate_function('scroll_news_3.html', 'scroll_news_3', "Punjab announced night curfews in cities and towns from December 1 to 15.")
        self.boilerplate_function('scroll_news_4.html', 'scroll_news_4', "The extent of intra-village segregation in Karnataka is greater than the local black-white segregation in the American South.")
        self.boilerplate_function('scroll_news_5.html', 'scroll_news_5', "The medical body said that the move should not be seen in isolation, referring to other government decisions legitimising Mixopathy.")
        self.boilerplate_function('scroll_news_6.html', 'scroll_news_6', "Dea Kulumbegashvilis directorial debut is Georgias submission for the Best International Feature Film category at the Oscars.")
        self.boilerplate_function('scroll_news_7.html', 'scroll_news_7', "Jats form the backbone of the protests. This has turned other communities away from them.")

        self.boilerplate_function('the_indian_express_1.html', 'the_indian_express_1', "A shootout between the militants and the security forces broke out at the hotel as the anti-terrorism force, the Army and the Frontier Corps were called in, Gwadar Station House Officer (SHO) Aslam Bangulzai said.")
        self.boilerplate_function('the_indian_express_2.html', 'the_indian_express_2', "In case the Aadhaar number isnotavailable, beneficiaries have to at least provide documents to prove that they have enrolled for the 12-digit unique identity number, said Indu Bhushan, CEO of the National Health Agency, responsible for implementing the PMJAY.")
        self.boilerplate_function('the_indian_express_3.html', 'the_indian_express_3', "An FIR was filed against BJP MP Shobha Karandlaje on charges of provoking people to cause riots, disturbing communal harmony and spreading rumours.")
        self.boilerplate_function('the_indian_express_4.html', 'the_indian_express_4', "\"Those days are not far when the displaced people will return to their Kashmir with dignity and honour. The BJP will leave no stone unturned in solving the problems of the hapless people who were forced to leave the Valley,\" Jammu and Kashmir BJP unit chief Sat Sharma said.")
        self.boilerplate_function('the_indian_express_5.html', 'the_indian_express_5', "Congress leader Manish Tewari tagged Chandigarh Police DGP Tajender Singh Luthra on his Twitter account, carrying the video clip demanding strict action against the policeman.")

        self.boilerplate_function('the_pioneer_1.html', 'the_pioneer_1', "To bring in more automation and efficacy in the functioning of the state Public Relations department, Punjab Chief Minister Capt Amarinder Singh on Wednesday virtually launched a mobile application DigiNest, to give people digital access to the state governments directory, which can be")
        self.boilerplate_function('the_pioneer_2.html', 'the_pioneer_2', "The Uttarakhand High Court has sought a reply from the State Government regarding non-compliance to its earlier order on restoring Adi Shankaracharyas Samadhi at Kedarnath following the 2013 disaster.In the past, the High Court had directed that the Samadhi be restored within a year but the")
        self.boilerplate_function('the_pioneer_3.html', 'the_pioneer_3', "The Aam Aadmi Party (AAP) leader and MLA, Raghav Chadha on Wednesday visited the Singhu border to ensure proper installation and functioning of five free WiFi hotspots on the border for protesting farmers.Chadha had yesterday announced that Chief Minister Arvind Kejriwal will begin another 'sewa'")
        self.boilerplate_function('the_pioneer_4.html', 'the_pioneer_4', "The Union Cabinet on Wednesday approved a scheme to provide bank loans at lower rates to distilleries producing ethanol for doping in petrol, with a view to raising Indias ethanol production capacity to suck out surplus sugar as well as cut oil imports. Oil Minister Dharmendra Pradhan")
        self.boilerplate_function('the_pioneer_5.html', 'the_pioneer_5', "Hearing on a public interest litigation filed against acquisition of 1,072 acres land of GB Pant University of Agriculture and Technology for construction of an airport in Pantnagar, the Uttarakhand High Court has directed the State and Central Governments, the university and Civil Aviation")

        self.boilerplate_function('times_of_india_1.html', 'times_of_india_1', "BANGALORE: The second launch pad for the Indian Space Research Organisation will be dispatched to Sriharikota by the end of March. The Mobile Launch P")
        self.boilerplate_function('times_of_india_2.html', 'times_of_india_2', "CBSE has introduced changes in examination bylaws to include all kinds of disabilities mentioned in the Disability Act 1995 for Board exams 2009.")
        self.boilerplate_function('times_of_india_3.html', 'times_of_india_3', "The first season of the Clean & Clear Lucknow Times Fresh Face contest kick-started amidst great engery and enthusiasm, when the fuchchas at the Shri")
        self.boilerplate_function('times_of_india_4.html', 'times_of_india_4', "Education News: While the ministry will grant Rs 1,000 crore funds to the three public institutions in the next five years, the private institutes will not be eligibl")
        self.boilerplate_function('times_of_india_5.html', 'times_of_india_5', "JAIPUR: Samples of nine out of the 11 UK-returnees from Rajasthan tested negative for the mutated strain.")

        self.boilerplate_function('usa_today_1.html', 'usa_today_1', "The White House will host drug manufacturers, distributors and governors to discuss its $12-billion plan to vaccinate Americans against COVID-19.")
        self.boilerplate_function('usa_today_2.html', 'usa_today_2', "President Trump presented the nation's highest civilian honor to Dan Gable, the two-time NCAA wrestling champion and 1972 Olympic gold medalist.")
        self.boilerplate_function('usa_today_3.html', 'usa_today_3', "Two North Atlantic right whale newborns have been spotted in the last week at the start of calving season, providing hope for an endangered species.")
        self.boilerplate_function('usa_today_4.html', 'usa_today_4', "The Seattle Sounders scored two late goals to complete a dramatic rally over Minnesota United and advance to MLS Cup to play the Columbus Crew.")
        self.boilerplate_function('usa_today_5.html', 'usa_today_5', "Bob Woodwards next book finds him in the familiar world of documenting a presidencys ending. He is teaming with colleague Robert Costa.")


if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
