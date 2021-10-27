"""Base class for all extractors."""

from abc import ABCMeta, abstractmethod

from python.resources.newsplease.pipeline.extractor.article_candidate import ArticleCandidate


class AbstractExtractor:
    """Abstract class for article extractors."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """Init function."""
        self.name = None

    def _name(self):
        """Returns the name of the article extractor."""
        return self.name

    def _title(self, item):  # pylint: disable=no-self-use,unused-argument
        """Returns the title of the extracted article."""
        return None

    def _description(self, item):  # pylint: disable=no-self-use,unused-argument
        """Returns the description/lead paragraph of the extracted article."""
        return None

    def _text(self, item):  # pylint: disable=no-self-use,unused-argument
        """Returns the main text of the extracted article."""
        return None

    def _author(self, item):  # pylint: disable=no-self-use,unused-argument
        """Returns the authors of the extracted article."""
        return None

    def _publish_date(self, item):  # pylint: disable=no-self-use,unused-argument
        """Returns the publish date of the extracted article."""
        return None

    def extract(self, item):    # pylint: disable=unused-argument
        """
        Executes all implemented functions on the given article and returns an
        object containing the recovered data.
        :param item: A NewscrawlerItem to parse.
        :return: ArticleCandidate containing the recovered article data.
        """

        article_candidate = ArticleCandidate()
        article_candidate.extractor = self._name()
        article_candidate.title = self._title(item)  # pylint: disable=assignment-from-none
        article_candidate.description = self._description(item)  # pylint: disable=assignment-from-none
        article_candidate.text = self._text(item)  # pylint: disable=assignment-from-none
        article_candidate.author = self._author(item)  # pylint: disable=assignment-from-none
        article_candidate.publish_date = self._publish_date(item)  # pylint: disable=assignment-from-none
        return article_candidate
