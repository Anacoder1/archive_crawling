"""
Script to compare the text of the list of ArticleCandidates and send the result
back to the Comparer.
"""

# pylint: disable=pointless-string-statement


class ComparerText:
    """
    Compares the text of the list of ArticleCandidates and sends the result back to the Comparer.

    The logic to return the best text in case of multiple text values has been commented because
    we're using only 2 candidates - newspaper_extractor and articlebody_extractor, with the latter as fallback,
    so we don't require functionality of selecting the best text.

    Any non-None, non-'' text which is longer than 15 words is kept, the rest are filtered.
    """
    def extract(self, item, article_candidate_list):  # noqa: C901
        """
        Compares the extracted texts.

        :param item: The corresponding NewscrawlerItem
        :param article_candidate_list: A list, the list of ArticleCandidate-Objects which have been extracted
        :return: A string, the most likely text
        """

        list_text = []

        # The minimal number of words a text needs to have
        min_number_words = 15

        # The texts of the article candidates and the respective extractors are saved in a tuple in list_text.
        for article_candidate in article_candidate_list:
            if (article_candidate.text
                    is not None) and (article_candidate.text.strip() != ''):
                list_text.append(
                    (article_candidate.text, article_candidate.extractor))

        # Remove texts whose length < min_number_words
        list_text = [
            tuple_element for tuple_element in list_text
            if len(tuple_element[0].split()) >= min_number_words
        ]

        '''
        1. If list_text is empty, return None
        2. If list_text is not empty, and list_newspaper_articlebody is not empty, return its extracted body
        3. If both lists above are empty, and list_custom_articlebody is not empty, return its extracted body
        '''

        # If there is no value in the list, return None.
        if len(list_text) == 0:
            return None

        list_newspaper_articlebody = [
            x for x in list_text if x[1] == "newspaper"
        ]
        if len(list_newspaper_articlebody) == 1:
            return list_newspaper_articlebody[0][0]

        list_custom_articlebody = [
            x for x in list_text if x[1] == "articlebody_extractor"
        ]
        if len(list_custom_articlebody) == 1:
            return list_custom_articlebody[0][0]
