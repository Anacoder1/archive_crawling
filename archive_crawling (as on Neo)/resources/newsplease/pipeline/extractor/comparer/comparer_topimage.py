"""
Script to compare the topimages of the list of ArticleCandidates and send the
result back to the Comparer.
"""

import re

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

# to improve performance, regex statements are compiled only once per module
re_http = re.compile('http://*')


class ComparerTopimage():
    """Compares the topimages of the list of ArticleCandidates and sends the result back to the Comparer."""
    def image_absoulte_path(self, url, image):  # pylint: disable=no-self-use
        """
        If the image url does not start with 'http://' it will take the absolute
        path from the url and fuses them with urljoin.
        """
        if not re.match(re_http, image):
            topimage = urljoin(url, image)
            return topimage
        return image

    def extract(self, item, list_article_candidate):  # pylint: disable=no-self-use,unused-argument,too-many-branches
        """Compares the extracted top images.
        :param item: The corresponding NewscrawlerItem
        :param list_article_candidate: A list, the list of ArticleCandidate-Objects which have been extracted
        :return: A string (url), the most likely top image
        """

        list_topimage = []

        for article_candidate in list_article_candidate:
            if article_candidate.topimage is not None:
                # Changes a relative path of an image to the absolute path of the given url.
                # article_candidate.topimage = self.image_absoulte_path(item['url'], article_candidate.topimage)
                list_topimage.append(
                    (article_candidate.topimage, article_candidate.extractor))

        list_custom_images = [
            x for x in list_topimage if x[1] == "images_extractor"
        ]
        if len(list_custom_images) == 1:
            return list_custom_images[0][0]

        # If there is no value in the list, return None.
        if not list_topimage:
            return None

        # If there are more options than one, return the result from newspaper.
        list_newspaper = [x for x in list_topimage if x[1] == "newspaper"]
        if not list_newspaper:

            # If there is no topimage extracted by newspaper, return the first result of list_topimage.
            return list_topimage[0][0]
        # else:
        return list_newspaper[0][0]

        # xpath_extractor not used
        # for article_candidate in list_article_candidate:
        #     if article_candidate.extractor == 'xpath':
        #         if article_candidate.topimage is not None:
        #             return article_candidate.topimage
