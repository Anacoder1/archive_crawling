"""
Code is from the news-please source code and hasn't been modified.

Categories aren't being extracted in the pipeline (as of now).
xpath_extractor mentioned here is deprecated and used nowhere
"""


class ComparerCategory:
    """Compares the category of the list of ArticleCandidates and sends the result back to the Comparer."""
    def extract(self, item, list_article_candidate):  # pylint: disable=inconsistent-return-statements,no-self-use,unused-argument # noqa: E501
        """
        Compares the extracted authors.
        :param item: The corresponding NewscrawlerItem
        :param list_article_candidate: A list, the list of ArticleCandidate-Objects which have been extracted
        :return: A string, the most likely category
        """
        for article_candidate in list_article_candidate:
            if article_candidate.extractor == 'xpath':
                return article_candidate.category
