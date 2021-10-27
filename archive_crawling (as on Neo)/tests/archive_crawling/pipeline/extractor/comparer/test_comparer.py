import unittest
from python.services.archive_crawling.pipeline.extractor.comparer.comparer import Comparer
from python.services.archive_crawling.pipeline.extractor.comparer.comparer_author import ComparerAuthor
from python.services.archive_crawling.pipeline.extractor.comparer.comparer_description import ComparerDescription
from python.services.archive_crawling.pipeline.extractor.comparer.comparer_title import ComparerTitle
from python.services.archive_crawling.pipeline.extractor.comparer.comparer_text import ComparerText
from python.services.archive_crawling.pipeline.extractor.comparer.comparer_date import ComparerDate
# from python.services.archive_crawling.pipeline.extractor.article_candidate import ArticleCandidate
from python.resources.newsplease.pipeline.extractor.article_candidate import ArticleCandidate


class ArticlebodyExtractor:
    def __init__(self):
        self.extractor = "articlebody_extractor"
        self.text = "dummy text"


class AuthorsExtractor:
    def __init__(self):
        self.extractor = "authors_extractor"
        self.author = "dummy authors"


class DateExtractor:
    def __init__(self):
        self.extractor = "date_extractor"
        self.publish_date = "2020-02-02 12:12:12"


class DateExtractorIndependent:
    def __init__(self):
        self.extractor = "date_extractor_independent"
        self.publish_date = "2020-02-02 12:12:12"


class DescriptionExtractor:
    def __init__(self):
        self.extractor = "description_extractor"
        self.description = "dummy description"


class TitleExtractor:
    def __init__(self):
        self.extractor = "title_extractor"
        self.title = "dummy title"


class NewspaperExtractor:
    def __init__(self):
        self.extractor = "newspaper"
        self.title = "dummy title"
        self.description = "dummy description"
        self.publish_date = "2020-02-02 12:12:12"
        self.author = "dummy authors"
        self.text = "dummy text"


class UnitTestsComparer(unittest.TestCase):
    def setUp(self):
        self.comparer_object = Comparer()
        self.comparer_author = ComparerAuthor()
        self.comparer_date = ComparerDate()
        self.comparer_desciption = ComparerDescription()
        self.comparer_text = ComparerText()
        self.comparer_title = ComparerTitle()
        self.article_candidate_object = ArticleCandidate()
        self.article_candidate_object.title = self.comparer_title.extract('dummy item', [TitleExtractor(), NewspaperExtractor()])
        self.article_candidate_object.description = self.comparer_desciption.extract('dummy item', [DescriptionExtractor(), NewspaperExtractor()])
        self.article_candidate_object.text = self.comparer_text.extract('dummy item', [ArticlebodyExtractor(), NewspaperExtractor()])
        self.article_candidate_object.author = self.comparer_author.extract('dummy item', [AuthorsExtractor()])
        self.article_candidate_object.publish_date = self.comparer_date.extract('dummy item', [DateExtractor(), DateExtractorIndependent()])

    def test_compare(self):
        self.assertEqual(self.comparer_object.compare('dummy item', [NewspaperExtractor()]).title,
                         self.article_candidate_object.title)
        self.assertEqual(self.comparer_object.compare('dummy item', [NewspaperExtractor()]).description,
                         self.article_candidate_object.description)
        self.assertEqual(self.comparer_object.compare('dummy item', [NewspaperExtractor()]).text,
                         self.article_candidate_object.text)
        self.assertEqual(self.comparer_object.compare('dummy item', [NewspaperExtractor()]).author,
                         self.article_candidate_object.author)
        self.assertEqual(self.comparer_object.compare('dummy item', [NewspaperExtractor()]).publish_date,
                         None)


if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
