import unittest
from python.services.archive_crawling.pipeline.extractor.comparer.comparer_text import ComparerText


class ArticlebodyExtractor:
    def __init__(self, text):
        self.extractor = "articlebody_extractor"
        self.text = text


class NewspaperExtractor:
    def __init__(self, text):
        self.extractor = "newspaper"
        self.text = text


class UnitTestsComparerText(unittest.TestCase):
    def setUp(self):
        self.comparer_text_object = ComparerText()

    def test_extract(self):
        self.assertEqual(self.comparer_text_object.extract('dummy item', [
            ArticlebodyExtractor('1 2 3 4 5 6'),
            NewspaperExtractor('1 2 3 4 5 6')
        ]), None)
        self.assertEqual(self.comparer_text_object.extract('dummy item', [
            ArticlebodyExtractor('1 2 3 4 5 6'),
            NewspaperExtractor('1 2 3 4 5 6 7 8 9 10 11 12 13 14 15')
        ]), '1 2 3 4 5 6 7 8 9 10 11 12 13 14 15')
        self.assertEqual(self.comparer_text_object.extract('dummy item', [
            ArticlebodyExtractor('1 2 3 4 5 6 7 8 9 10 11 12 13 14 15'),
            NewspaperExtractor('1 2 3 4 5 6')
        ]), '1 2 3 4 5 6 7 8 9 10 11 12 13 14 15')
        self.assertEqual(self.comparer_text_object.extract('dummy item', [
            ArticlebodyExtractor(None),
            NewspaperExtractor(None)
        ]), None)
        self.assertEqual(self.comparer_text_object.extract('dummy item', [
            ArticlebodyExtractor(''),
            NewspaperExtractor('')
        ]), None)


if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
