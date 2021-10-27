"""Unit tests for the custom authors extractor in Archive-Crawling project. Started 04-02-21"""

import unittest
import requests
import requests_mock
from bs4 import BeautifulSoup
from dotmap import DotMap
from python.tests.archive_crawling.url_dict import url_dict
from python.services.archive_crawling.pipeline.extractor.extractors.authors_extractor import AuthorsExtractor

HTML_DIR = "tests/archive_crawling/test_data/"


class UnitTestsAuthorsExtractor(unittest.TestCase):
    @requests_mock.Mocker(kw='mock')
    def boilerplate_function(self, html_file_name, url_variable, expected_content, **kwargs):
        self.AE = AuthorsExtractor()
        item = {}
        item['spider_response'] = DotMap()
        with open(HTML_DIR + html_file_name, 'r') as html_data:
            kwargs['mock'].get(url_dict[url_variable], text=html_data.read())
            item['spider_response'].body = requests.get(url_dict[url_variable]).text
            for author in expected_content:
                self.assertIn(author, self.AE._author({'spider_response': item['spider_response']}))

    def test_authors_mega(self):
        self.boilerplate_function('blank_1.html', 'blank_1', [" "])

        self.boilerplate_function('business_standard_1.html', 'business_standard_1', ['Reuters', 'Busienss Standard'])
        self.boilerplate_function('business_standard_2.html', 'business_standard_2', ['Busienss Standard', 'ANI'])
        self.boilerplate_function('business_standard_3.html', 'business_standard_3', ['Reuters', 'Busienss Standard'])
        self.boilerplate_function('business_standard_4.html', 'business_standard_4', ['Busienss Standard', 'Shibu Tripathi'])
        self.boilerplate_function('business_standard_5.html', 'business_standard_5', ['Vinay Rajani', 'Busienss Standard'])

        self.boilerplate_function('cnbc_1.html', 'cnbc_1', ['CNBC', '@abigailngwy', 'https://www.facebook.com/CNBC', 'Abigail Ng'])
        self.boilerplate_function('cnbc_2.html', 'cnbc_2', ['Emily DeCiccio', 'CNBC', 'https://www.facebook.com/CNBC'])
        self.boilerplate_function('cnbc_3.html', 'cnbc_3', ['Adam Edelman', '@CNBC', 'CNBC'])
        self.boilerplate_function('cnbc_4.html', 'cnbc_4', ['CNBC', '_DanMangan', 'Dan Mangan', 'https://www.facebook.com/CNBC'])
        self.boilerplate_function('cnbc_5.html', 'cnbc_5', ['Sarah Whitten', 'CNBC', '@sarahwhit10', 'https://www.facebook.com/CNBC'])
        self.boilerplate_function('cnbc_6.html', 'cnbc_6', ['@CNBC', 'CNBC', 'CNBC.com staff', 'https://www.facebook.com/CNBC'])

        self.boilerplate_function('daily_mail_1.html', 'daily_mail_1', ['Daily Mail', 'Darren Boyle for MailOnline', 'https://www.facebook.com/DailyMail', 'Darren Boyle'])
        self.boilerplate_function('daily_mail_2.html', 'daily_mail_2', ['Daily Mail', 'Tom Leonard for the Daily Mail', 'Tom Leonard','https://www.facebook.com/DailyMailCeleb'])
        self.boilerplate_function('daily_mail_3.html', 'daily_mail_3', ['https://www.facebook.com/DailyMail', 'Stacy Liberatore For Dailymail.com', 'Stacy Liberatore'])
        self.boilerplate_function('daily_mail_4.html', 'daily_mail_4', ['Luke Augustus', 'Luke Augustus for MailOnline'])
        self.boilerplate_function('daily_mail_5.html', 'daily_mail_5', ['Tom Farmery For Mailonline', 'Tom Farmery'])
        self.boilerplate_function('daily_mail_6.html', 'daily_mail_6', ['MailOnline Reporter', 'MailOnline', 'https://www.facebook.com/DailyMailCeleb'])
        self.boilerplate_function('daily_mail_7.html', 'daily_mail_7', ['Dan Bloom for MailOnline', 'Chris Brooke for the Daily Mail', 'https://www.facebook.com/DailyMail', 'Chris Brooke'])

        self.boilerplate_function('deccan_herald_1.html', 'deccan_herald_1', ['Narasimharajapur, DH News Service:,', 'DH News Service'])
        self.boilerplate_function('deccan_herald_2.html', 'deccan_herald_2', ['DH News Service'])
        self.boilerplate_function('deccan_herald_3.html', 'deccan_herald_3', ['DH News Service'])
        self.boilerplate_function('deccan_herald_4.html', 'deccan_herald_4', ['Naina J A', 'DH News Service'])
        self.boilerplate_function('deccan_herald_5.html', 'deccan_herald_5', ['DH News Service', 'Sumir Karmakar,', 'DHNS,'])

        self.boilerplate_function('economic_times_1.html', 'economic_times_1', ['Economic Times', 'TNN'])
        self.boilerplate_function('economic_times_2.html', 'economic_times_2', ['PTI', 'Economic Times'])
        self.boilerplate_function('economic_times_3.html', 'economic_times_3', ['Economic Times', 'Agencies'])
        self.boilerplate_function('economic_times_4.html', 'economic_times_4', ['PTI', 'Economic Times'])
        self.boilerplate_function('economic_times_5.html', 'economic_times_5', ['PTI', 'Economic Times'])
        self.boilerplate_function('economic_times_6.html', 'economic_times_6', ['Economic Times', 'Parisha Tyagi', 'ET Now'])

        self.boilerplate_function('espn_cricinfo_1.html', 'espn_cricinfo_1', ['ESPN Digital Media Pvt Ltd', 'George Dobell', 'ESPNcricinfo'])
        self.boilerplate_function('espn_cricinfo_2.html', 'espn_cricinfo_2', ['ESPN Digital Media Pvt Ltd', 'ESPNcricinfo staff', 'ESPNcricinfo'])
        self.boilerplate_function('espn_cricinfo_3.html', 'espn_cricinfo_3', ['ESPN Digital Media Pvt Ltd', 'George Dobell', 'ESPNcricinfo'])
        self.boilerplate_function('espn_cricinfo_4.html', 'espn_cricinfo_4', ['ESPN Digital Media Pvt Ltd', 'Andrew Miller', 'ESPNcricinfo'])
        self.boilerplate_function('espn_cricinfo_5.html', 'espn_cricinfo_5', ['ESPN Digital Media Pvt Ltd', 'ESPNcricinfo staff', 'ESPNcricinfo'])

        self.boilerplate_function('euro_news_1.html', 'euro_news_1', ['Euronews'])
        self.boilerplate_function('euro_news_2.html', 'euro_news_2', ['David Walsh'])
        self.boilerplate_function('euro_news_3.html', 'euro_news_3', ['Euronews'])
        self.boilerplate_function('euro_news_4.html', 'euro_news_4', ['Euronews'])
        self.boilerplate_function('euro_news_5.html', 'euro_news_5', ['Euronews'])

        self.boilerplate_function('evening_standard_1.html', 'evening_standard_1', ['Sophia Sleigh', 'Joe Murphy', 'Evening Standard'])
        self.boilerplate_function('evening_standard_2.html', 'evening_standard_2', ['Evening Standard', 'Naomi Ackerman'])
        self.boilerplate_function('evening_standard_3.html', 'evening_standard_3', ['Evening Standard', 'April Roach'])
        self.boilerplate_function('evening_standard_4.html', 'evening_standard_4', ['Evening Standard', 'Lizzie Edmonds'])
        self.boilerplate_function('evening_standard_5.html', 'evening_standard_5', ['Evening Standard', 'David Ellis'])

        self.boilerplate_function('express_1.html', 'express_1', ['Express.co.uk', 'Paul Withers'])
        self.boilerplate_function('express_2.html', 'express_2', ['Express.co.uk', 'Svar Nanan-Sen'])
        self.boilerplate_function('express_3.html', 'express_3', ['Express.co.uk', 'Paul Withers'])
        self.boilerplate_function('express_4.html', 'express_4', ['Express.co.uk', 'Edward Browne'])
        self.boilerplate_function('express_5.html', 'express_5', ['Express.co.uk', 'Tom Fish'])

        self.boilerplate_function('financial_express_1.html', 'financial_express_1', ['@FinancialXpress', 'fe Bureau'])
        self.boilerplate_function('financial_express_2.html', 'financial_express_2', ['@FinancialXpress', 'PTI'])
        self.boilerplate_function('financial_express_3.html', 'financial_express_3', ['@FinancialXpress', 'PTI'])
        self.boilerplate_function('financial_express_4.html', 'financial_express_4', ['@FinancialXpress', 'Express news service'])
        self.boilerplate_function('financial_express_5.html', 'financial_express_5', ['@FinancialXpress', 'Reuters'])

        self.boilerplate_function('hindu_business_line_1.html', 'hindu_business_line_1', ['The Hindu BusinessLine', 'Suresh P Iyengar'])
        self.boilerplate_function('hindu_business_line_2.html', 'hindu_business_line_2', ['The Hindu BusinessLine', 'Our Bureau.'])
        self.boilerplate_function('hindu_business_line_3.html', 'hindu_business_line_3', ['The Hindu BusinessLine'])
        self.boilerplate_function('hindu_business_line_4.html', 'hindu_business_line_4', ['The Hindu BusinessLine', 'Our Bureau.'])
        self.boilerplate_function('hindu_business_line_5.html', 'hindu_business_line_5', ['The Hindu BusinessLine', 'Our Bureau.'])

        self.boilerplate_function('independent_1.html', 'independent_1', ['The Independent', 'Louise Hall'])
        self.boilerplate_function('independent_2.html', 'independent_2', ['The Independent', 'Maya Oppenheim'])
        self.boilerplate_function('independent_3.html', 'independent_3', ['The Independent', 'Adam White'])
        self.boilerplate_function('independent_4.html', 'independent_4', ['The Independent', 'Sarah Young'])
        self.boilerplate_function('independent_5.html', 'independent_5', ['The Independent', 'Isobel Lewis'])

        self.boilerplate_function('india_today_1.html', 'india_today_1', ['@indiatoday', 'India Today', 'Milan Sharma'])
        self.boilerplate_function('india_today_2.html', 'india_today_2', ['@indiatoday', 'India Today', 'Ketan Pratap'])
        self.boilerplate_function('india_today_3.html', 'india_today_3', ['@indiatoday', 'India Today', 'Rahul Bhatnagar'])
        self.boilerplate_function('india_today_4.html', 'india_today_4', ['@indiatoday', 'India Today', 'India Today Web Desk'])
        self.boilerplate_function('india_today_5.html', 'india_today_5', ['@indiatoday', 'India Today', 'Aishwarya Paliwal'])

        self.boilerplate_function('ndtv_1.html', 'ndtv_1', ['NDTV Sports', 'Press Trust of India', 'Written by Press Trust of India'])
        self.boilerplate_function('ndtv_2.html', 'ndtv_2', ['NDTV', 'Ketki Angre', 'Sabyasachi Dasgupta'])
        self.boilerplate_function('ndtv_3.html', 'ndtv_3', ['NDTV'])
        self.boilerplate_function('ndtv_4.html', 'ndtv_4', ['NDTV', 'Press Trust of India'])
        self.boilerplate_function('ndtv_5.html', 'ndtv_5', ['NDTV', 'Gitanjali Roy'])
        self.boilerplate_function('ndtv_6.html', 'ndtv_6', ['Akhil Arora', 'https://www.facebook.com/arora.akhil', 'https://twitter.com/akhil_arora', 'Gadgets 360'])
        self.boilerplate_function('ndtv_7.html', 'ndtv_7', ['NDTV', 'Gargi Tomar'])
        self.boilerplate_function('ndtv_8.html', 'ndtv_8', ['.post-views-bd{display:none !important;}PTI'])
        self.boilerplate_function('ndtv_9.html', 'ndtv_9', ['CarandBike', 'carandbike', 'Ameya Naik'])

        self.boilerplate_function('new_york_post_1.html', 'new_york_post_1', ['@Rich_Calder', 'Rich Calder'])
        self.boilerplate_function('new_york_post_2.html', 'new_york_post_2', ['Mike Puma', '@NYPost_Mets'])
        self.boilerplate_function('new_york_post_3.html', 'new_york_post_3', ['@nypost', 'Carleton English'])
        self.boilerplate_function('new_york_post_4.html', 'new_york_post_4', ['@createcraig', 'Craig McCarthy'])
        self.boilerplate_function('new_york_post_5.html', 'new_york_post_5', ['@nypost', 'Jorge Fitz-Gibbon'])

        self.boilerplate_function('new_york_times_1.html', 'new_york_times_1', ['Eileen Sullivan'])
        self.boilerplate_function('new_york_times_2.html', 'new_york_times_2', ['Parul Sehgal'])
        self.boilerplate_function('new_york_times_3.html', 'new_york_times_3', ['Jeremy Engle'])
        self.boilerplate_function('new_york_times_4.html', 'new_york_times_4', ['Julian E. Barnes', 'Eric Schmitt', 'Anton Troianovski and Natalie Kitroeff', 'Natalie Kitroeff'])
        self.boilerplate_function('new_york_times_5.html', 'new_york_times_5', ['Katie Glueck', 'Shane Goldmacher', 'Katie Glueck and Shane Goldmacher'])

        self.boilerplate_function('one_india_1.html', 'one_india_1', ['Oneindia', 'Ajay Joseph Raj P', 'Alphonse Joseph'])
        self.boilerplate_function('one_india_2.html', 'one_india_2', ['Oneindia', 'Ajay Joseph Raj P', 'Alphonse Joseph'])
        self.boilerplate_function('one_india_3.html', 'one_india_3', ['Oneindia', 'Briti Roy Barman'])
        self.boilerplate_function('one_india_4.html', 'one_india_4', ['Oneindia', 'Madhuri Adnal', 'Simran Kashyap'])
        self.boilerplate_function('one_india_5.html', 'one_india_5', ['Oneindia', 'Madhuri Adnal'])

        self.boilerplate_function('scroll_news_1.html', 'scroll_news_1', ['Scroll.in', '@thefield_in', 'Scroll Staff'])
        self.boilerplate_function('scroll_news_2.html', 'scroll_news_2', ['Scroll.in', '@thefield_in', 'AFP'])
        self.boilerplate_function('scroll_news_3.html', 'scroll_news_3', ['Scroll.in', 'Scroll Staff', '@scroll_in'])
        self.boilerplate_function('scroll_news_4.html', 'scroll_news_4', ['Scroll.in', '@scroll_in', 'Deepak Malghan & Andaleeb Rahman', 'Naveen Bharathi'])
        self.boilerplate_function('scroll_news_5.html', 'scroll_news_5', ['Scroll.in', '@scroll_in', 'Scroll Staff'])
        self.boilerplate_function('scroll_news_6.html', 'scroll_news_6', ['Scroll.in', 'Rashid Irani', '@TheReel_in'])
        self.boilerplate_function('scroll_news_7.html', 'scroll_news_7', ['Vijayta Lalwani', '@scroll_in', 'Shoaib Daniyal & Vijayta Lalwani', 'Shoaib Daniyal'])

        self.boilerplate_function('the_indian_express_1.html', 'the_indian_express_1', ['The Indian Express', '@indianexpress', 'PTI'])
        self.boilerplate_function('the_indian_express_2.html', 'the_indian_express_2', ['The Indian Express', '@indianexpress', 'PTI'])
        self.boilerplate_function('the_indian_express_3.html', 'the_indian_express_3', ['The Indian Express', '@indianexpress', 'PTI'])
        self.boilerplate_function('the_indian_express_4.html', 'the_indian_express_4', ['The Indian Express', '@indianexpress', 'PTI'])
        self.boilerplate_function('the_indian_express_5.html', 'the_indian_express_5', ['The Indian Express', 'Express News Service', '@indianexpress'])
        self.boilerplate_function('the_indian_express_6.html', 'the_indian_express_6', [" "])
        self.boilerplate_function('the_indian_express_7.html', 'the_indian_express_7', [" "])
        self.boilerplate_function('the_indian_express_8.html', 'the_indian_express_8', ["PTI"])

        self.boilerplate_function('the_pioneer_1.html', 'the_pioneer_1', ['PNS', 'The Pioneer'])
        self.boilerplate_function('the_pioneer_2.html', 'the_pioneer_2', ['PNS', 'The Pioneer'])
        self.boilerplate_function('the_pioneer_3.html', 'the_pioneer_3', ['The Pioneer', 'Staff Reporter'])
        self.boilerplate_function('the_pioneer_4.html', 'the_pioneer_4', ['PNS', 'The Pioneer'])
        self.boilerplate_function('the_pioneer_5.html', 'the_pioneer_5', ['PNS', 'The Pioneer'])

        self.boilerplate_function('times_of_india_1.html', 'times_of_india_1', ['Times Of India', 'TNN'])
        self.boilerplate_function('times_of_india_2.html', 'times_of_india_2', ['Times Of India', 'TNN'])
        self.boilerplate_function('times_of_india_3.html', 'times_of_india_3', ['Times Of India', 'Devanshi Seth'])
        self.boilerplate_function('times_of_india_4.html', 'times_of_india_4', ['PTI'])
        self.boilerplate_function('times_of_india_5.html', 'times_of_india_5', ['Times Of India'])
        self.boilerplate_function('times_of_india_6.html', 'times_of_india_6', ['Times of India', 'TIMESOFINDIA.COM'])
        self.boilerplate_function('times_of_india_7.html', 'times_of_india_7', ['Times of India', 'Harmala Gupta'])

        self.boilerplate_function('usa_today_1.html', 'usa_today_1', ['@usatoday', 'David Jackson and Courtney Subramanian'])
        self.boilerplate_function('usa_today_2.html', 'usa_today_2', ['@usatoday', 'USA TODAY'])
        self.boilerplate_function('usa_today_3.html', 'usa_today_3', ['@usatoday', 'Elinor Aspegren'])
        self.boilerplate_function('usa_today_4.html', 'usa_today_4', ['@usatoday', 'Jacob Myers'])
        self.boilerplate_function('usa_today_5.html', 'usa_today_5', ['@usatoday', 'The Associated Press'])


if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
