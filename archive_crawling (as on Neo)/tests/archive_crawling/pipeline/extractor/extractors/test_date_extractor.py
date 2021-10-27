"""Unit tests for the custom date extractor in Archive-Crawling project. Started 04-02-21"""

import unittest
import requests
import requests_mock
from bs4 import BeautifulSoup
from dotmap import DotMap
from python.tests.archive_crawling.url_dict import url_dict
from python.services.archive_crawling.pipeline.extractor.extractors.date_extractor import DateExtractor

HTML_DIR = "tests/archive_crawling/test_data/"


class UnitTestsDateExtractor(unittest.TestCase):
    @requests_mock.Mocker(kw='mock')
    def boilerplate_function(self, html_file_name, url_variable, expected_content, **kwargs):
        self.DE = DateExtractor()
        item = {}
        item['spider_response'] = DotMap()
        with open(HTML_DIR + html_file_name, 'r') as html_data:
            kwargs['mock'].get(url_dict[url_variable], text=html_data.read())
            item['spider_response'].body = requests.get(url_dict[url_variable]).text
            self.assertEqual(self.DE._publish_date({'spider_response': item['spider_response']}), expected_content)

    def test_publish_date(self):
        self.boilerplate_function('blank_1.html', 'blank_1', None)

        self.boilerplate_function('business_standard_1.html', 'business_standard_1', '2021-01-13 08:55:00')
        self.boilerplate_function('business_standard_2.html', 'business_standard_2', '2021-01-13 08:56:00')
        self.boilerplate_function('business_standard_3.html', 'business_standard_3', '2021-01-13 01:33:00')
        self.boilerplate_function('business_standard_4.html', 'business_standard_4', '2021-01-13 12:57:00')
        self.boilerplate_function('business_standard_5.html', 'business_standard_5', '2021-01-13 07:25:00')

        self.boilerplate_function('cnbc_1.html', 'cnbc_1', '2020-12-25 08:29:59')
        self.boilerplate_function('cnbc_2.html', 'cnbc_2', '2020-12-25 06:45:12')
        self.boilerplate_function('cnbc_3.html', 'cnbc_3', '2020-12-26 00:40:03')
        self.boilerplate_function('cnbc_4.html', 'cnbc_4', '2020-12-25 01:08:23')
        self.boilerplate_function('cnbc_5.html', 'cnbc_5', '2020-12-24 22:17:43')
        self.boilerplate_function('cnbc_6.html', 'cnbc_6', '2020-11-01 18:49:41')

        self.boilerplate_function('daily_mail_1.html', 'daily_mail_1', '2020-11-26 06:32:54')
        self.boilerplate_function('daily_mail_2.html', 'daily_mail_2', '2020-11-26 06:58:41')
        self.boilerplate_function('daily_mail_3.html', 'daily_mail_3', '2020-11-26 04:58:03')
        self.boilerplate_function('daily_mail_4.html', 'daily_mail_4', '2020-11-29 02:00:54')
        self.boilerplate_function('daily_mail_5.html', 'daily_mail_5', '2020-11-28 19:18:02')
        self.boilerplate_function('daily_mail_6.html', 'daily_mail_6', '2015-02-03 06:07:26')
        self.boilerplate_function('daily_mail_7.html', 'daily_mail_7', '2015-02-03 05:40:58')

        self.boilerplate_function('deccan_herald_1.html', 'deccan_herald_1', '2009-05-07 22:55:19')
        self.boilerplate_function('deccan_herald_2.html', 'deccan_herald_2', '2012-08-23 20:57:45')
        self.boilerplate_function('deccan_herald_3.html', 'deccan_herald_3', '2015-10-22 14:32:42')
        self.boilerplate_function('deccan_herald_4.html', 'deccan_herald_4', '2018-11-27 23:21:01')
        self.boilerplate_function('deccan_herald_5.html', 'deccan_herald_5', '2020-12-31 19:41:15')

        self.boilerplate_function('economic_times_1.html', 'economic_times_1', '2003-01-02 07:11:00')
        self.boilerplate_function('economic_times_2.html', 'economic_times_2', '2008-02-15 14:02:00')
        self.boilerplate_function('economic_times_3.html', 'economic_times_3', '2010-05-21 11:23:00')
        self.boilerplate_function('economic_times_4.html', 'economic_times_4', '2015-08-20 14:32:00')
        self.boilerplate_function('economic_times_5.html', 'economic_times_5', '2020-11-27 15:19:00')
        self.boilerplate_function('economic_times_6.html', 'economic_times_6', '2019-01-04 19:36:00')

        self.boilerplate_function('espn_cricinfo_1.html', 'espn_cricinfo_1', '2020-10-02 02:52:48')
        self.boilerplate_function('espn_cricinfo_2.html', 'espn_cricinfo_2', '2020-10-01 23:06:43')
        self.boilerplate_function('espn_cricinfo_3.html', 'espn_cricinfo_3', '2020-10-01 22:40:58')
        self.boilerplate_function('espn_cricinfo_4.html', 'espn_cricinfo_4', '2020-10-02 08:00:00')
        self.boilerplate_function('espn_cricinfo_5.html', 'espn_cricinfo_5', '2020-10-01 15:40:21')

        self.boilerplate_function('euro_news_1.html', 'euro_news_1', '2020-12-08 19:16:03')
        self.boilerplate_function('euro_news_2.html', 'euro_news_2', '2020-12-08 14:46:15')
        self.boilerplate_function('euro_news_3.html', 'euro_news_3', '2020-12-08 09:30:32')
        self.boilerplate_function('euro_news_4.html', 'euro_news_4', '2020-12-09 07:00:10')
        self.boilerplate_function('euro_news_5.html', 'euro_news_5', '2020-12-09 19:35:09')

        self.boilerplate_function('evening_standard_1.html', 'evening_standard_1', '2020-06-16 22:22:19')
        self.boilerplate_function('evening_standard_2.html', 'evening_standard_2', '2020-06-16 21:36:49')
        self.boilerplate_function('evening_standard_3.html', 'evening_standard_3', '2020-11-26 14:40:14')
        self.boilerplate_function('evening_standard_4.html', 'evening_standard_4', '2020-11-26 18:27:34')
        self.boilerplate_function('evening_standard_5.html', 'evening_standard_5', '2020-11-26 21:06:18')

        self.boilerplate_function('express_1.html', 'express_1', '2020-12-08 13:38:00')
        self.boilerplate_function('express_2.html', 'express_2', '2020-12-09 04:26:00')
        self.boilerplate_function('express_3.html', 'express_3', '2021-01-13 12:59:00')
        self.boilerplate_function('express_4.html', 'express_4', '2020-12-08 11:17:00')
        self.boilerplate_function('express_5.html', 'express_5', '2020-12-08 12:06:00')

        self.boilerplate_function('financial_express_1.html', 'financial_express_1', '2014-02-01 04:20:00')
        self.boilerplate_function('financial_express_2.html', 'financial_express_2', '2014-01-31 23:57:00')
        self.boilerplate_function('financial_express_3.html', 'financial_express_3', '2014-02-01 01:35:00')
        self.boilerplate_function('financial_express_4.html', 'financial_express_4', '2014-01-31 14:52:00')
        self.boilerplate_function('financial_express_5.html', 'financial_express_5', '2014-01-30 00:18:00')

        self.boilerplate_function('hindu_business_line_1.html', 'hindu_business_line_1', '2020-12-08 00:00:00')
        self.boilerplate_function('hindu_business_line_2.html', 'hindu_business_line_2', '2020-12-09 17:04:00')
        self.boilerplate_function('hindu_business_line_3.html', 'hindu_business_line_3', '2020-12-10 00:00:00')
        self.boilerplate_function('hindu_business_line_4.html', 'hindu_business_line_4', '2020-12-10 18:27:41')
        self.boilerplate_function('hindu_business_line_5.html', 'hindu_business_line_5', '2020-12-10 16:54:17')

        self.boilerplate_function('independent_1.html', 'independent_1', '2020-06-25 05:18:55')
        self.boilerplate_function('independent_2.html', 'independent_2', '2020-08-26 12:23:47')
        self.boilerplate_function('independent_3.html', 'independent_3', '2020-09-24 14:49:51')
        self.boilerplate_function('independent_4.html', 'independent_4', '2020-11-26 12:56:01')
        self.boilerplate_function('independent_5.html', 'independent_5', '2020-12-31 15:08:07')

        self.boilerplate_function('india_today_1.html', 'india_today_1', '2021-01-13 13:32:42')
        self.boilerplate_function('india_today_2.html', 'india_today_2', '2021-01-13 13:16:20')
        self.boilerplate_function('india_today_3.html', 'india_today_3', '2021-01-13 13:10:42')
        self.boilerplate_function('india_today_4.html', 'india_today_4', '2021-01-13 09:51:17')
        self.boilerplate_function('india_today_5.html', 'india_today_5', '2021-01-13 07:55:46')

        self.boilerplate_function('ndtv_1.html', 'ndtv_1', '2009-12-08 16:22:00')
        self.boilerplate_function('ndtv_2.html', 'ndtv_2', '2012-11-01 00:36:34')
        self.boilerplate_function('ndtv_3.html', 'ndtv_3', '2015-06-01 13:53:55')
        self.boilerplate_function('ndtv_4.html', 'ndtv_4', '2017-05-01 04:07:58')
        self.boilerplate_function('ndtv_5.html', 'ndtv_5', '2020-10-31 19:19:56')
        self.boilerplate_function('ndtv_6.html', 'ndtv_6', '2018-09-05 14:27:31')
        self.boilerplate_function('ndtv_7.html', 'ndtv_7', '2020-11-02 15:40:45')
        self.boilerplate_function('ndtv_8.html', 'ndtv_8', '2019-01-01 18:39:48')
        self.boilerplate_function('ndtv_9.html', 'ndtv_9', '2021-02-04 10:58:38')

        self.boilerplate_function('new_york_post_1.html', 'new_york_post_1', '2010-09-28 09:10:53')
        self.boilerplate_function('new_york_post_2.html', 'new_york_post_2', '2015-05-22 09:10:34')
        self.boilerplate_function('new_york_post_3.html', 'new_york_post_3', '2017-06-09 10:01:25')
        self.boilerplate_function('new_york_post_4.html', 'new_york_post_4', '2019-10-31 04:35:10')
        self.boilerplate_function('new_york_post_5.html', 'new_york_post_5', '2021-01-01 03:33:12')

        self.boilerplate_function('new_york_times_1.html', 'new_york_times_1', '2020-01-27 23:07:40')
        self.boilerplate_function('new_york_times_2.html', 'new_york_times_2', '2020-01-15 02:38:21')
        self.boilerplate_function('new_york_times_3.html', 'new_york_times_3', '2020-01-31 15:30:09')
        self.boilerplate_function('new_york_times_4.html', 'new_york_times_4', '2020-01-09 18:03:08')
        self.boilerplate_function('new_york_times_5.html', 'new_york_times_5', '2020-01-08 02:21:47')

        self.boilerplate_function('one_india_1.html', 'one_india_1', '2020-11-25 09:03:38')
        self.boilerplate_function('one_india_2.html', 'one_india_2', '2020-11-25 10:39:50')
        self.boilerplate_function('one_india_3.html', 'one_india_3', '2020-11-25 11:09:26')
        self.boilerplate_function('one_india_4.html', 'one_india_4', '2020-11-25 19:20:33')
        self.boilerplate_function('one_india_5.html', 'one_india_5', '2020-11-25 20:30:25')

        self.boilerplate_function('scroll_news_1.html', 'scroll_news_1', '2020-11-25 08:56:00')
        self.boilerplate_function('scroll_news_2.html', 'scroll_news_2', '2020-11-25 09:21:00')
        self.boilerplate_function('scroll_news_3.html', 'scroll_news_3', '2020-11-25 09:50:00')
        self.boilerplate_function('scroll_news_4.html', 'scroll_news_4', '2020-11-25 11:30:00')
        self.boilerplate_function('scroll_news_5.html', 'scroll_news_5', '2020-11-25 13:11:00')
        self.boilerplate_function('scroll_news_6.html', 'scroll_news_6', '2021-02-03 10:30:00')
        self.boilerplate_function('scroll_news_7.html', 'scroll_news_7', '2021-02-03 09:00:00')

        self.boilerplate_function('the_indian_express_1.html', 'the_indian_express_1', '2019-05-12 00:10:37')
        self.boilerplate_function('the_indian_express_2.html', 'the_indian_express_2', '2018-10-07 23:18:12')
        self.boilerplate_function('the_indian_express_3.html', 'the_indian_express_3', '2017-12-23 20:19:27')
        self.boilerplate_function('the_indian_express_4.html', 'the_indian_express_4', '2017-09-13 23:14:11')
        self.boilerplate_function('the_indian_express_5.html', 'the_indian_express_5', '2017-09-10 06:04:27')
        self.boilerplate_function('the_indian_express_6.html', 'the_indian_express_6', '2014-01-03 05:28:00')
        self.boilerplate_function('the_indian_express_7.html', 'the_indian_express_7', '2014-01-03 05:23:00')
        self.boilerplate_function('the_indian_express_8.html', 'the_indian_express_8', '2014-01-03 12:54:00')

        self.boilerplate_function('the_pioneer_1.html', 'the_pioneer_1', '2020-12-31 00:00:00')
        self.boilerplate_function('the_pioneer_2.html', 'the_pioneer_2', '2020-12-31 00:00:00')
        self.boilerplate_function('the_pioneer_3.html', 'the_pioneer_3', '2020-12-31 00:00:00')
        self.boilerplate_function('the_pioneer_4.html', 'the_pioneer_4', '2020-12-31 00:00:00')
        self.boilerplate_function('the_pioneer_5.html', 'the_pioneer_5', '2020-12-31 00:00:00')

        self.boilerplate_function('times_of_india_1.html', 'times_of_india_1', '2002-03-15 00:15:00')
        self.boilerplate_function('times_of_india_2.html', 'times_of_india_2', '2009-02-28 04:33:00')
        self.boilerplate_function('times_of_india_3.html', 'times_of_india_3', '2012-09-20 00:00:00')
        self.boilerplate_function('times_of_india_4.html', 'times_of_india_4', '2018-10-25 08:40:00')
        self.boilerplate_function('times_of_india_5.html', 'times_of_india_5', '2020-12-31 04:12:00')
        self.boilerplate_function('times_of_india_6.html', 'times_of_india_6', '2021-02-04 08:00:00')
        self.boilerplate_function('times_of_india_7.html', 'times_of_india_7', '2021-02-04 06:00:22')

        self.boilerplate_function('usa_today_1.html', 'usa_today_1', '2020-12-08 05:47:31')
        self.boilerplate_function('usa_today_2.html', 'usa_today_2', '2020-12-08 07:34:48')
        self.boilerplate_function('usa_today_3.html', 'usa_today_3', '2020-12-08 08:47:55')
        self.boilerplate_function('usa_today_4.html', 'usa_today_4', '2020-12-08 10:41:39')
        self.boilerplate_function('usa_today_5.html', 'usa_today_5', '2020-12-08 17:41:13')

        self.boilerplate_function('date_extractor_dummy_1.html', 'date_extractor_dummy_1', '2021-01-13 08:56:00')
        self.boilerplate_function('date_extractor_dummy_2.html', 'date_extractor_dummy_2', '2020-10-11 19:37:05')
        self.boilerplate_function('date_extractor_dummy_3.html', 'date_extractor_dummy_3', '2003-11-01 10:39:56')
        self.boilerplate_function('date_extractor_dummy_4.html', 'date_extractor_dummy_4', '2019-07-01 04:05:28')
        self.boilerplate_function('date_extractor_dummy_5.html', 'date_extractor_dummy_5', '2022-12-30 18:00:54')
        self.boilerplate_function('date_extractor_dummy_6.html', 'date_extractor_dummy_6', '2019-07-01 04:05:28')
        self.boilerplate_function('date_extractor_dummy_7.html', 'date_extractor_dummy_7', '2021-08-17 15:53:41')
        self.boilerplate_function('date_extractor_dummy_8.html', 'date_extractor_dummy_8', '2023-04-09 03:23:57')
        self.boilerplate_function('date_extractor_dummy_9.html', 'date_extractor_dummy_9', '2016-05-25 17:20:31')
        self.boilerplate_function('date_extractor_dummy_10.html', 'date_extractor_dummy_10', '2013-05-09 08:41:07')
        self.boilerplate_function('date_extractor_dummy_11.html', 'date_extractor_dummy_11', '2007-09-02 15:46:36')
        self.boilerplate_function('date_extractor_dummy_12.html', 'date_extractor_dummy_12', '2024-06-17 02:48:53')
        self.boilerplate_function('date_extractor_dummy_13.html', 'date_extractor_dummy_13', '2020-11-19 03:07:01')
        self.boilerplate_function('date_extractor_dummy_14.html', 'date_extractor_dummy_14', '2012-11-14 09:52:44')
        self.boilerplate_function('date_extractor_dummy_15.html', 'date_extractor_dummy_15', '2009-07-02 21:28:20')
        self.boilerplate_function('date_extractor_dummy_16.html', 'date_extractor_dummy_16', '1918-12-08 12:34:56')
        self.boilerplate_function('date_extractor_dummy_17.html', 'date_extractor_dummy_17', '2008-02-02 16:24:20')
        self.boilerplate_function('date_extractor_dummy_18.html', 'date_extractor_dummy_18', '2025-08-04 05:53:15')
        self.boilerplate_function('date_extractor_dummy_19.html', 'date_extractor_dummy_19', '2002-12-12 13:13:07')
        self.boilerplate_function('date_extractor_dummy_20.html', 'date_extractor_dummy_20', '2003-03-10 11:30:41')
        self.boilerplate_function('date_extractor_dummy_21.html', 'date_extractor_dummy_21', '2007-02-14 01:46:48')
        self.boilerplate_function('date_extractor_dummy_22.html', 'date_extractor_dummy_22', '2000-07-26 00:35:00')
        self.boilerplate_function('date_extractor_dummy_23.html', 'date_extractor_dummy_23', '2005-04-05 08:28:12')
        self.boilerplate_function('date_extractor_dummy_24.html', 'date_extractor_dummy_24', '2007-05-13 07:18:38')
        self.boilerplate_function('date_extractor_dummy_25.html', 'date_extractor_dummy_25', '2004-01-23 09:32:37')
        self.boilerplate_function('date_extractor_dummy_26.html', 'date_extractor_dummy_26', '2007-11-22 10:50:35')
        self.boilerplate_function('date_extractor_dummy_27.html', 'date_extractor_dummy_27', '2007-04-03 23:04:08')
        self.boilerplate_function('date_extractor_dummy_28.html', 'date_extractor_dummy_28', '2000-02-29 22:20:22')
        self.boilerplate_function('date_extractor_dummy_29.html', 'date_extractor_dummy_29', '2005-10-27 02:06:10')
        self.boilerplate_function('date_extractor_dummy_30.html', 'date_extractor_dummy_30', '2009-12-30 03:15:07')
        self.boilerplate_function('date_extractor_dummy_31.html', 'date_extractor_dummy_31', '2004-04-29 00:43:51')
        self.boilerplate_function('date_extractor_dummy_32.html', 'date_extractor_dummy_32', '2007-05-13 07:18:38')
        self.boilerplate_function('date_extractor_dummy_33.html', 'date_extractor_dummy_33', '2002-12-12 13:13:07')
        self.boilerplate_function('date_extractor_dummy_34.html', 'date_extractor_dummy_34', '2025-08-04 05:53:15')
        self.boilerplate_function('date_extractor_dummy_35.html', 'date_extractor_dummy_35', '2009-12-30 03:15:07')
        self.boilerplate_function('date_extractor_dummy_36.html', 'date_extractor_dummy_36', '2020-12-08 19:16:03')
        self.boilerplate_function('date_extractor_dummy_37.html', 'date_extractor_dummy_37', '2015-03-10 08:41:45')
        self.boilerplate_function('date_extractor_dummy_38.html', 'date_extractor_dummy_38', '2024-08-16 11:43:35')
        self.boilerplate_function('date_extractor_dummy_39.html', 'date_extractor_dummy_39', '2006-08-14 12:06:40')
        self.boilerplate_function("date_extractor_dummy_40.html", "date_extractor_dummy_40", "2014-02-01 04:20:00")
        self.boilerplate_function("date_extractor_dummy_41.html", "date_extractor_dummy_41", "2020-08-26 12:23:47")
        self.boilerplate_function("date_extractor_dummy_42.html", "date_extractor_dummy_42", "2021-04-13 05:30:00")
        self.boilerplate_function("date_extractor_dummy_43.html", "date_extractor_dummy_43", "2020-06-24 17:18:55")


if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
