class ComparerAuthor():
    """This class compares the titles of the list of ArticleCandidates and sends the result back to the Comparer."""

    def extract(self, item, list_article_candidate):
        """Compares the extracted authors.
        :param item: The corresponding NewscrawlerItem
        :param list_article_candidate: A list, the list of ArticleCandidate-Objects which have been extracted
        :return: A string, the most likely authors
        """
        # for article_candidate in list_article_candidate:
        #    if article_candidate.extractor == 'xpath':
        #        if article_candidate.author is not None:
        #            return article_candidate.author

        list_author = []

        # The authors of the ArticleCandidates and the respective extractors are saved in a tuple in list_author.
        for article_candidate in list_article_candidate:
            if (article_candidate.author is not None) and (article_candidate.author != '[]'):
                list_author.append((article_candidate.author, article_candidate.extractor))

        # If there is no value in the list, return None.
        if len(list_author) == 0:
            return None

        # If there are more options than one, return the result from newspaper.
        list_newspaper = [x for x in list_author if x[1] == "newspaper"]
        list_custom_author = [x for x in list_author if x[1] == "authors_extractor"]

        if len(list_custom_author) == 1:
            return list_custom_author[0][0]
        elif len(list_newspaper) == 0:
            return list_author[0][0]
        else:
            if type(list_newspaper[0][0]) == list:
                return ",".join(list_newspaper[0][0])
            return list_newspaper[0][0]
