"""
Script to compare the extracted titles from the list of ArticleCandidates and
sends the result back to the Comparer.
"""

# pylint: disable=pointless-string-statement


class ComparerTitle:
    """
    Compares the title if the list of ArticleCandidates and sends the result back to the Comparer.

    Functions find_matches, extract_match and choose_shortest_title haven't been used.
    We're using only 2 candidates - newspaper_extractor and title_extractor, with the latter as fallback,
    so we don't require functions of selecting the best title, shortest title, etc.

    Any non-None and non-"" title extracted by newspaper_extractor will be returned.
    If this is not the case, and title_extractor extracts a non-None and non-"" title, then this will be returned.
    """

    def extract(self, item, list_article_candidate):  # pylint: disable=too-many-branches,unused-argument,inconsistent-return-statements,no-self-use
        """
        Compares the extracted titles.
        :param item: The corresponding NewscrawlerItem
        :param list_article_candidate: A list, the list of ArticleCandidate-Objects which have been extracted
        :return: A string, the most likely title
        """

        list_title = []  # Stores title extracted from newspaper_extractor
        list_custom_title = [
        ]  # Stores title extracted from custom title_extractor
        for article_candidate in list_article_candidate:
            if (article_candidate.title
                    is not None) and (article_candidate.title != ''):
                if article_candidate.extractor == "title_extractor":
                    list_custom_title.append(article_candidate.title)
                else:
                    list_title.append(article_candidate.title)

        '''
        1. If n3k extracts a non-None and non-'' title, return it
        2. If n3k isn't able to extract the title, but custom title_extractor did, return its extracted title
        3. If both couldn't extract anything, return None
        '''

        if len(list_title) != 0:
            return list_title[0]

        if len(list_custom_title) == 1:
            return list_custom_title[0]

        if len(list_title) == 0:
            return None
