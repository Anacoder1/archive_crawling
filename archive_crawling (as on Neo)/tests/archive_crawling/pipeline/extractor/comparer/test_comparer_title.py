import unittest
import itertools
from python.services.archive_crawling.pipeline.extractor.comparer.comparer_title import ComparerTitle


class TitleExtractor:
    def __init__(self, title):
        self.extractor = "title_extractor"
        self.title = title


class NewspaperExtractor:
    def __init__(self, title):
        self.extractor = "newspaper"
        self.title = title


class UnitTestsComparerTitle(unittest.TestCase):
    def setUp(self):
        self.comparer_title_object = ComparerTitle()

    '''
    def test_find_matches(self):
        self.assertEqual(self.comparer_title_object.find_matches(['Hello', 'Hello there', 'Hello']), ['Hello'])
        self.assertEqual(self.comparer_title_object.find_matches(["Title One", "It's a Pleasant Day", "It's a Pleasant Day", "Title Two", "Title One"]),
                         ['Title One', "It's a Pleasant Day"])

    def test_extract_match(self):
        self.assertEqual(self.comparer_title_object.extract_match(['Title One', 'Title One', 'Title Two']), 'Title One')
        self.assertEqual(self.comparer_title_object.extract_match([]), None)
        self.assertEqual(self.comparer_title_object.extract_match(['Some Title']), None)

    def test_choose_shortest_title(self):
        self.assertEqual(self.comparer_title_object.choose_shortest_title(['Some Title', 'Some Longer Title', 'An Even Longer Title']), 'Some Title')
        self.assertRaises(ValueError, lambda: self.comparer_title_object.choose_shortest_title([]))
    '''

    def test_extract(self):
        self.assertEqual(self.comparer_title_object.extract('dummy item', [
            TitleExtractor('title extracted from title_extractor'),
            NewspaperExtractor('title extracted from newspaper_extractor')
        ]), 'title extracted from newspaper_extractor')
        self.assertEqual(self.comparer_title_object.extract('dummy item', [
            TitleExtractor(''),
            NewspaperExtractor('')
        ]), None)
        self.assertEqual(self.comparer_title_object.extract('dummy item', [
            TitleExtractor('title extracted from title_extractor'),
            NewspaperExtractor('')
        ]), 'title extracted from title_extractor')



if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
