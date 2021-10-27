import unittest
from python.services.archive_crawling.pipeline.extractor.extractors.abstract_extractor import AbstractExtractor
from python.resources.newsplease.pipeline.extractor.article_candidate import ArticleCandidate

class NewspaperExtractor:
    def __init__(self):
        self.name = "newspaper"
        self.title = "dummy title"
        self.description = "dummy description"
        self.publish_date = "2020-02-02 12:12:12"
        self.author = "dummy authors"
        self.text = "dummy text"


class UnitTestsAbstractExtractor(unittest.TestCase):
    def setUp(self):
        self.abstract_extractor_object = AbstractExtractor()

    def test_extract(self):
        article_candidate_object = ArticleCandidate()
        article_candidate_object.extractor = "newspaper"
        article_candidate_object.title = None
        article_candidate_object.description = None
        article_candidate_object.text = None
        article_candidate_object.author = None
        article_candidate_object.publish_date = None
        self.assertEqual(article_candidate_object.title,
                         self.abstract_extractor_object.extract(NewspaperExtractor()).title)
        self.assertEqual(article_candidate_object.description,
                         self.abstract_extractor_object.extract(NewspaperExtractor()).description)
        self.assertEqual(article_candidate_object.text,
                         self.abstract_extractor_object.extract(NewspaperExtractor()).text)
        self.assertEqual(article_candidate_object.author,
                         self.abstract_extractor_object.extract(NewspaperExtractor()).author)
        self.assertEqual(article_candidate_object.publish_date,
                         self.abstract_extractor_object.extract(NewspaperExtractor()).publish_date)


if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
