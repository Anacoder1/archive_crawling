"""
Extracts dates from publishers like EBM News.
NOT USED in the Archive-Crawling pipeline.
"""

import re
from retrying import retry
from python.services.archive_crawling.pipeline.extractor.extractors.abstract_extractor import AbstractExtractor

# to improve performance, regex statements are compiled only once per module
re_pub_date = re.compile(
    r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9][\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?'  # noqa: E501
)
re_class = re.compile(
    "pubdate|timestamp|article_date|articledate|date|posted-on", re.IGNORECASE)


class DateExtractor(AbstractExtractor):
    """Extracts the publish_date from a HTML page using 3 functions."""
    def __init__(self):  # pylint: disable=super-init-not-called
        """Init function."""
        self.name = "listing_date_extractor"

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)
    def _publish_date(self, item):
        """  # noqa: D406, D413
        Returns the publish_date of the extracted article, using 3 functions.

        Args:
            item: A dictionary containing a HTML page as element.

        Returns:
            publish_date: The publish_date of the HTML page, if present.
                          Otherwise, None is returned.
                          If language detected by detect_lang() is not English,
                          publish_date is returned as None instantly.
        """

        return item['article_publish_date']
