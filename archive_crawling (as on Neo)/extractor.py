"""
News-Please script to get primary info of articles like resource_id, html,
etc. and calls the extractors listed here in the Extraction pipeline.
"""

import datetime
import urllib
from dotmap import DotMap
from python.resources.newsplease.pipeline.extractor import article_extractor
from python.resources.newsplease.pipeline.pipelines import ExtractedInformationStorage


def from_html(html,
              url=None,
              download_date=None,
              listing_date=None):  # pylint: disable=unused-argument
    """
    Extracts relevant information from an HTML page given as a string. This function does not invoke scrapy but only
    uses the article extractor. If you have the original URL make sure to provide it as this helps NewsPlease
    to extract the publishing date and title.
    :param html:
    :param url:
    :return:
    """

    extractor = article_extractor.Extractor([
        'date_extractor', 'authors_extractor', 'title_extractor',
        'newspaper_extractor', 'description_extractor',
        'articlebody_extractor'
    ])
    # 'xpath_extractor' 'listing_date_extractor', 'lang_detect_extractor', 'images_extractor', 'readability_extractor'
    # These extractors aren't used in the pipeline

    title_encoded = ''.encode()
    if not url:
        url = ''

    filename = urllib.parse.quote_plus(url) + '.json'

    item = {}
    item['spider_response'] = DotMap()
    item['spider_response'].body = html
    item['url'] = url
    item['source_domain'] = urllib.parse.urlparse(
        url).hostname.encode() if url != '' else ''.encode()
    item['html_title'] = title_encoded
    item['rss_title'] = title_encoded
    item['local_path'] = None
    item['filename'] = filename
    item['download_date'] = download_date
    item['modified_date'] = None
    item["article_publish_date"] = None  # listing_date
    item = extractor.extract(item)

    tmp_article = ExtractedInformationStorage.extract_relevant_info(item)
    final_article = ExtractedInformationStorage.convert_to_class(tmp_article)
    return final_article


def extract_information(data):
    """
    Gets primary info of an article from Crawling code, and sends it to
    from_html() for extraction.
    """
    html = data['html']
    url = data['url']
    listing_date = data['listing_date']
    url = url.replace('"', '')
    download_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = from_html(html, url, download_date, listing_date)
    return result
