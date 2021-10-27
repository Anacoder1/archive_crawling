"""Implements Readability as an article extractor."""

from copy import deepcopy
from readability import Document
from python.resources.newsplease.pipeline.extractor.article_candidate import ArticleCandidate
from python.services.archive_crawling.pipeline.extractor.extractors.abstract_extractor import AbstractExtractor


class ReadabilityExtractor(AbstractExtractor):
    """
    Implements Readability as an article extractor. Readability is
    a subclass of Extractors and newspaper.Article.
    """
    def __init__(self):  # pylint: disable=super-init-not-called
        """Init function."""
        self.name = "readability"

    def extract(self, item):
        """
        Creates an readability document and returns an ArticleCandidate containing article title and text.
        :param item: A NewscrawlerItem to parse.
        :return: ArticleCandidate containing the recovered article data.
        """

        doc = Document(deepcopy(item['spider_response'].body))
        description = doc.summary()

        article_candidate = ArticleCandidate()
        article_candidate.extractor = self._name
        article_candidate.title = doc.short_title()
        article_candidate.description = description
        article_candidate.text = self._text(item)  # pylint: disable=assignment-from-none
        article_candidate.author = self._author(item)  # pylint: disable=assignment-from-none
        article_candidate.publish_date = self._publish_date(item)  # pylint: disable=assignment-from-none

        return article_candidate
