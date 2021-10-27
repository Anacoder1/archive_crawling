"""Script to compare the dates of the list of ArticleCandidates and sends the result back to the Comparer."""


class ComparerDate:
    """
    Compares the dates of the list of ArticleCandidates and sends the result back to the Comparer.

    NOTE that newspaper_extractor's publish_date extraction hasn't been used, this is because it's results
    are poor compared to custom date_extractor.
    """
    def extract(self, item, list_article_candidate):  # pylint: disable=no-self-use,unused-argument,too-many-branches,inconsistent-return-statements
        """
        Compares the extracted publish dates.
        :param item: The corresponding NewscrawlerItem
        :param list_article_candidate: A list, the list of ArticleCandidate-Objects which have been extracted
        :return: A string, the most likely publish date
        """

        list_publish_date = []

        for article_candidate in list_article_candidate:
            if article_candidate.publish_date is not None:
                list_publish_date.append((article_candidate.publish_date,
                                          article_candidate.extractor))

        # If there is no value in the list, return None.
        if len(list_publish_date) == 0:
            return None

        # If there are more options than one, return the result from date_extractor.
        list_date_extractor = [
            x for x in list_publish_date if x[1] == "date_extractor"
        ]

        if len(list_date_extractor) == 1:
            return list_date_extractor[0][0]
