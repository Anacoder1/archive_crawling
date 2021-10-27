"""
Script to compare the descriptions of the list of ArticleCandidates and send
the result back to the Comparer.
"""

# pylint: disable=pointless-string-statement


class ComparerDescription:
    """
    Compares the descriptions of the list of ArticleCandidates and sends the result
    back to the Comparer.
    """
    def extract(self, item, list_article_candidate):  # pylint: disable=no-self-use,unused-argument,inconsistent-return-statements,too-many-branches
        """
        Compares the extracted descriptions.
        :param item: The corresponding NewscrawlerItem
        :param list_article_candidate: A list, the list of ArticleCandidate-Objects which have been extracted
        :return: A string, the most likely description
        """

        list_description = []

        '''
        The descriptions of the article candidates and the respective extractors are saved
        in a tuple in list_description.
        '''
        for article_candidate in list_article_candidate:
            if article_candidate.description is not None:
                list_description.append((article_candidate.description,
                                         article_candidate.extractor))

        '''
        1. If list_description is empty, return None.
        2. If list_description is not empty and newspaper_extractor has extracted description, return it.
        3. Else-if custom description_extractor has extracted description, return it.
        '''

        # If there is no value in the list, return None.
        if not list_description:
            return None

        list_newspaper = [x for x in list_description if x[1] == "newspaper"]
        list_custom_desc = [
            x for x in list_description if x[1] == "description_extractor"
        ]
        if not list_newspaper:
            if len(list_custom_desc) == 1:
                return list_custom_desc[0][0]
        elif list_newspaper and list_newspaper[0][0] is not None:
            return list_newspaper[0][0]
