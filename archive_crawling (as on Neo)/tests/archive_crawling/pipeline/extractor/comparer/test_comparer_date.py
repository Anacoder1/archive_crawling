import unittest
from python.services.archive_crawling.pipeline.extractor.comparer.comparer_date import ComparerDate


class DateExtractor:
    def __init__(self, publish_date):
        self.extractor = "date_extractor"
        self.publish_date = publish_date


class DateExtractorIndependent:
    def __init__(self, publish_date):
        self.extractor = "date_extractor_independent"
        self.publish_date = publish_date


class UnitTestsComparerDate(unittest.TestCase):
    def setUp(self):
        self.comparer_date_object = ComparerDate()

    def test_extract(self):
        self.assertEqual(self.comparer_date_object.extract('dummy item', [
            DateExtractor('2021-01-10 19:36:57')
        ]), '2021-01-10 19:36:57')
        self.assertEqual(self.comparer_date_object.extract('dummy item', [
            DateExtractor(None)
        ]), None)
        # self.assertEqual(self.comparer_date_object.extract('dummy item', [
        #     DateExtractorIndependent('2021-01-10 19:36:57')
        # ]), '2021-01-10 19:36:57')
        # self.assertEqual(self.comparer_date_object.extract('dummy item', [
        #     DateExtractorIndependent(None)
        # ]), None)
        # self.assertEqual(self.comparer_date_object.extract('dummy item', [
        #     DateExtractor('2021-01-10 19:36:57'),
        #     DateExtractorIndependent('2021-05-09 20:21:22')
        # ]), '2021-01-10 19:36:57')
        # self.assertEqual(self.comparer_date_object.extract('dummy item', [
        #     DateExtractor(None),
        #     DateExtractorIndependent('2021-05-09 20:21:22')
        # ]), '2021-05-09 20:21:22')
        # self.assertEqual(self.comparer_date_object.extract('dummy item', [
        #     DateExtractor(None),
        #     DateExtractorIndependent(None)
        # ]), None)


if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
