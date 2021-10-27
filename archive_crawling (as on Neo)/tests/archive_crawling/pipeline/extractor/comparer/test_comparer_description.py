import unittest
import itertools
from python.services.archive_crawling.pipeline.extractor.comparer.comparer_description import ComparerDescription


class DescriptionExtractor:
    def __init__(self, description):
        self.extractor = "description_extractor"
        self.description = description


class NewspaperExtractor:
    def __init__(self, description):
        self.extractor = "newspaper"
        self.description = description


class UnitTestsComparerDescription(unittest.TestCase):
    def setUp(self):
        self.comparer_description_object = ComparerDescription()

    def test_extract(self):
        self.assertEqual(self.comparer_description_object.extract('dummy item', [
            DescriptionExtractor('description extracted from description_extractor'),
            NewspaperExtractor('description extracted from newspaper_extractor')
        ]), 'description extracted from newspaper_extractor')
        self.assertEqual(self.comparer_description_object.extract('dummy item', [
            DescriptionExtractor('description extracted from description_extractor'),
            NewspaperExtractor(None)
        ]), 'description extracted from description_extractor')
        self.assertEqual(self.comparer_description_object.extract('dummy item', [
            DescriptionExtractor(None),
            NewspaperExtractor('description extracted from newspaper_extractor')
        ]), 'description extracted from newspaper_extractor')
        self.assertEqual(self.comparer_description_object.extract('dummy item', [
            DescriptionExtractor(None),
            NewspaperExtractor(None)
        ]), None)


if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
