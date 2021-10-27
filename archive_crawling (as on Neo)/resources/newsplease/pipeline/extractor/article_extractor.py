"""Code is from the news-please source code and hasn't been modified."""

import importlib
import inspect
import logging
from python.services.archive_crawling.pipeline.extractor.extractors.abstract_extractor import AbstractExtractor
from python.services.archive_crawling.pipeline.extractor.comparer.comparer import Comparer
from python.resources.newsplease.pipeline.extractor.cleaner import Cleaner


class Extractor:
    """
    Initializes all extractors and saves the results of them. When adding a new extractor, it needs to
    be initialized here and added to list_extractor.
    """
    def __init__(self, extractor_list):
        """
        Initializes all the extractors, comparers and the cleaner.
        :param extractor_list: List of strings containing all extractors to be initialized.
        """
        self.log = logging.getLogger(__name__)
        self.extractor_list = []
        for extractor in extractor_list:

            if extractor == 'newspaper_extractor':
                module = importlib.import_module('python.resources.newsplease.pipeline.extractor.extractors.' + extractor)
            else:
                module = importlib.import_module('python.services.archive_crawling.pipeline.extractor.extractors.' + extractor)

            # check module for subclasses of AbstractExtractor
            for member in inspect.getmembers(module, inspect.isclass):
                if issubclass(member[1], AbstractExtractor
                              ) and member[0] != 'AbstractExtractor':

                    # instantiate extractor
                    instance = getattr(module, member[0], None)()
                    if instance is not None:
                        self.log.info('Extractor initialized: %s', extractor)
                        self.extractor_list.append(instance)
                    else:
                        self.log.error(
                            "Misconfiguration: An unknown Extractor was found and"
                            " will be ignored: %s", extractor)

        self.cleaner = Cleaner()
        self.comparer = Comparer()

    def extract(self, item):
        """
        Runs the HTML-response trough a list of initialized extractors, a cleaner and compares the results.
        :param item: NewscrawlerItem to be processed.
        :return: An updated NewscrawlerItem including the results of the extraction
        """

        article_candidates = []

        for extractor in self.extractor_list:
            article_candidate = extractor.extract(item)
            article_candidates.append(article_candidate)

        article_candidates = self.cleaner.clean(article_candidates)
        article = self.comparer.compare(item, article_candidates)

        item['article_title'] = article.title
        item['article_description'] = article.description
        item['article_text'] = article.text
        item['article_image'] = article.topimage
        item['article_author'] = article.author
        item['article_publish_date'] = article.publish_date
        item['article_language'] = article.language
        item['category'] = article.category

        return item
