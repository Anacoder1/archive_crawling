import unittest
from python.services.archive_crawling.pipeline.extractor.comparer.comparer_author import ComparerAuthor


class AuthorsExtractor:
    def __init__(self, author):
        self.extractor = "authors_extractor"
        self.author = author


class NewspaperExtractor:
    def __init__(self, author):
        self.extractor = "newspaper"
        self.author = author


class UnitTestsComparerAuthor(unittest.TestCase):
    def setUp(self):
        self.comparer_author_object = ComparerAuthor()

    def test_extract(self):
        self.assertEqual(self.comparer_author_object.extract('dummy item', [
            AuthorsExtractor('Some people extracted by authors_extractor'),
            NewspaperExtractor('Some people extracted by newspaper_extractor')
        ]), 'Some people extracted by authors_extractor')
        self.assertEqual(self.comparer_author_object.extract('dummy item', [
            AuthorsExtractor('Some people extracted by authors_extractor'),
            NewspaperExtractor(None)
        ]), 'Some people extracted by authors_extractor')
        self.assertEqual(self.comparer_author_object.extract('dummy item', [
            AuthorsExtractor(None),
            NewspaperExtractor('Some people extracted by newspaper_extractor')
        ]), 'Some people extracted by newspaper_extractor')
        self.assertEqual(self.comparer_author_object.extract('dummy item', [
            AuthorsExtractor(None),
            NewspaperExtractor(None)
        ]), None)
        self.assertEqual(self.comparer_author_object.extract('dummy item', [
            AuthorsExtractor(None),
            NewspaperExtractor(['Some', 'people', 'extracted', 'by', 'newspaper_extractor'])
        ]), 'Some, people, extracted, by, newspaper_extractor')


if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
