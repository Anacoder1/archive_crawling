"""
Script to extract image urls from a news article.
This extractor is NOT USED in the Archive-Crawling pipeline.
"""

import json
from bs4 import BeautifulSoup
from retrying import retry
from python.services.archive_crawling.pipeline.extractor.extractors.abstract_extractor import AbstractExtractor


class ImagesExtractor(AbstractExtractor):
    """Extracts urls of images from a news article."""
    def __init__(self):  # pylint: disable=super-init-not-called
        """Init function."""
        self.name = "images_extractor"

    def _topimage(self, item):  # noqa: C901
        """Returns a concatenated string of image urls found in a news article."""
        html_item = item['spider_response']
        publisher = item['publisher']
        html = BeautifulSoup(html_item.body, 'html5lib')
        images = ""

        try:
            if publisher == 'EconomicTimes':
                images = self.images_economic_times(html)
            if publisher == 'TimesofIndia':
                images = self.images_times_of_india(html)
            if publisher == 'DeccanHerald':
                images = self.images_deccan_herald(html)
            if publisher == 'NDTV':
                images = self.images_ndtv(html)
            if publisher == 'Independent':
                images = self.images_independent(html)
            if publisher == 'EveningStandard':
                images = self.images_evening_standard(html)
            if publisher == 'NewYorkPost':
                images = self.images_new_york_post(html)
            if publisher == 'Express':
                images = self.images_express(html)
            if publisher == 'USAToday':
                images = self.images_usa_today(html)
            if publisher == 'DailyMail':
                images = self.images_daily_mail(html)
            if publisher == 'IndiaToday':
                images = self.images_india_today(html)
            if publisher == 'OneIndia':
                images = self.images_one_india(html)
            if publisher == 'HinduBusinessLine':
                images = self.images_hindu_business_line(html)
            if publisher == 'ScrollNews':
                images = self.images_scroll_news(html)
            if publisher == 'CNBCWorld':
                images = self.images_cnbc(html)

        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        return images

    def clean_images(self, image):  # pylint: disable=no-self-use
        """Cleans the concatenated string of image urls."""
        return image.strip().lstrip().rstrip()

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_economic_times(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from an Economic Times article."""
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                data = json.loads(script.string, strict=False)
                try:
                    if data["image"]:
                        if data["image"]["url"] not in images_list:
                            images_list.append(data["image"]["url"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            figures = html.find_all('figure')
            for figure in figures:
                for image in figure.find_all('img'):
                    if image.get('data-original') and image.get(
                            'data-original') not in images_list:
                        images_list.append(image.get('data-original'))
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_times_of_india(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from a Times of India article."""
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                data = json.loads(script.string, strict=False)
                try:
                    if data["image"]:
                        if data["image"]["url"] not in images_list:
                            images_list.append(data["image"]["url"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            figures = html.find_all('figure')
            for figure in figures:
                for image in figure.find_all('img'):
                    if image.get('src') and image.get(
                            'src') not in images_list:
                        images_list.append(image.get('src'))
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_deccan_herald(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from a Deccan Herald article."""
        images_list = []
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["image"] and not isinstance(data["image"], list):
                        images_list.append(data["image"]["url"])
                    elif data["image"] and isinstance(data["image"], list):
                        images_list.append(data["image"][0]["url"])
                        break
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            caption_images = html.find_all('img', {'class': 'caption'})
            for caption_image in caption_images:
                if caption_image["src"] not in images_list:
                    images_list.append(caption_image["src"])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_ndtv(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from a NDTV article."""
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["image"]["url"]:
                        if data["image"]["url"].strip() != '':
                            images_list.append(data["image"]["url"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["image"]["url"].strip() != '':
                        images_list.append(data["image"]["url"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            main_images = html.find_all('img', {'id': 'story_image_main'})
            for main_image in main_images:
                if main_image.get('data-src'):
                    images_list.append(main_image.get('data-src'))
                    break
                if main_image.get('src'):
                    if "http://" in main_image.get(
                            'src') or "https://" in main_image.get('src'):
                        images_list.append(main_image.get('src'))
                        break
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            main_images = html.find_all('img', {'class': 'story_image_main'})
            for main_image in main_images:
                if main_image.get('data-src'):
                    images_list.append(main_image.get('data-src'))
                    break
                if main_image.get('src'):
                    if "http://" in main_image.get(
                            'src') or "https://" in main_image.get('src'):
                        images_list.append(main_image.get('src'))
                        break
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = list(set(images_list))
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_independent(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from an Independent article."""
        images_list = []
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            og_image_secure = html.find('meta',
                                        {'property': 'og:image:secure_url'})
            images_list.append(og_image_secure['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            images_srcset = html.find_all('amp-img')
            for image in images_srcset:
                images_list.append(image['src'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    images_list.append(data["image"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    images_list.append(data["thumbnailUrl"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_evening_standard(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from an Evening Standard article."""
        images_list = []
        try:
            twitter_image = html.find('meta', {'property': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            og_image_secure = html.find('meta',
                                        {'property': 'og:image:secure_url'})
            images_list.append(og_image_secure['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["image"]:
                        images_list.append(data["image"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["thumbnailUrl"]:
                        images_list.append(data["thumbnailUrl"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            amp_images = html.find_all('amp-img')
            for amp_image in amp_images:
                images_list.append(amp_image['src'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_new_york_post(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from a New York Post article."""
        images_list = []
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            twitter_image_src = html.find('meta',
                                          {'name': 'twitter:image:src'})
            images_list.append(twitter_image_src['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            og_image_secure = html.find('meta',
                                        {'property': 'og:image:secure_url'})
            images_list.append(og_image_secure['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and isinstance(
                            data["image"], list):
                        images_list.append(data["image"][0]["url"])
                    elif data["@type"] == "NewsArticle" and not isinstance(
                            data["image"], list):
                        images_list.append(data["image"]["url"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            images = html.find_all('img')
            for image in images:
                try:
                    if "standard-article-image" in image["id"]:
                        images_list.append(image["src"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
                try:
                    for class_element in image["class"]:
                        if "wp-image" in class_element:
                            images_list.append(image["data-srcset"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_express(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from an Express article."""
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            twitter_image = html.find('meta',
                                      {'property': 'twitter:image:src'})
            images_list.append(twitter_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle":
                        if isinstance(data["image"], list):
                            images_list.append(data["image"][0]["url"])
                        elif not isinstance(data["image"], list):
                            images_list.append(data["image"]["url"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            article = html.find('article', {'itemprop': 'mainEntity'})
            pictures = article.find_all('picture')
            for picture in pictures:
                for img in picture.find_all('img'):
                    images_list.append(img['data-src'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_usa_today(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from a USA Today article."""
        images_list = []
        try:
            article = html.find('article')
            images = article.find_all('img')
            for image in images:
                try:
                    images_list.append(image['data-gl-src'])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
                try:
                    images_list.append(image['src'])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["thumbnailUrl"]:
                        images_list.append(data["thumbnailUrl"])
                    if data["image"]:
                        if isinstance(data["image"], list):
                            images_list.append(data["image"][0]["url"])
                        elif not isinstance(data["image"], list):
                            images_list.append(data["image"]["url"])
                    if data[1] and data[1]["url"]:
                        images_list.append(data[1]["url"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_daily_mail(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from a Daily Mail article."""
        images_list = []
        try:
            twitter_image = html.find('meta', {'property': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            thumbnail_image = html.find('meta', {'itemprop': 'thumbnailurl'})
            images_list.append(thumbnail_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["@type"] == "NewsArticle" or data["@WebPage"]:
                        if data["image"] and isinstance(data["image"], list):
                            images_list.append(data["image"][0]["url"])
                        elif data["image"] and not isinstance(
                                data["image"], list):
                            images_list.append(data["image"]["url"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            article_body = html.find('div', {'itemprop': 'articleBody'})
            images = article_body.find_all('img')
            for img in images:
                images_list.append(img['src'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_india_today(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from an India Today article."""
        images_list = []
        try:
            images = html.find_all('img')
            for image in images:
                images_list.append(image['data-src'])
                images_list.append(image['src'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["@type"] == "ImageObject" and data["url"]:
                        images_list.append(data["url"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            article_body = html.find('div', {
                'class': 'description ',
                'itemprop': 'articleBody'
            })
            images = article_body.find_all('img')
            for img in images:
                images_list.append(img['src'])
                images_list.append(img['data-src'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_one_india(self, html):  # pylint: disable=too-many-branches
        """Returns the image urls extracted from a One India article."""
        images_list = []
        try:
            link_href = html.find('link', {'rel': 'image_src'})
            images_list.append(self.clean_images(link_href['href']))
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(self.clean_images(og_image['content']))
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(self.clean_images(twitter_image['content']))
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data["image"]:
                        if isinstance(data["image"]["url"], list):
                            images_list.append(
                                self.clean_images(data["image"]["url"][0]))
                        if not isinstance(data["image"]["url"], list):
                            images_list.append(
                                self.clean_images(data["image"]["url"]))
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    images_list.append(self.clean_images(data["thumbnailUrl"]))
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            images = html.find_all('img', {'class': 'image_listical'})
            for img in images:
                images_list.append(
                    self.clean_images("https://www.oneindia.com" +
                                      img['data-pagespeed-lazy-src']))
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_hindu_business_line(self, html):  # pylint: disable=too-many-branches,no-self-use
        """
        Returns the image urls extracted from a Hindu Business
        Line article.
        """
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'].strip())
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'].strip())
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data["image"]:
                        if isinstance(data["image"], list):
                            images_list.append(data["image"][0]["url"].strip())
                        if not isinstance(data["image"], list):
                            images_list.append(data["image"]["url"].strip())
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            article_body = html.find('div', {'class': 'contentbody inf-body'})
            images = article_body.find_all('img')
            for img in images:
                images_list.append(img['src'].strip())
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_scroll_news(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from a Scroll News article."""
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            twitter_image_src = html.find('meta',
                                          {'name': 'twitter:image:src'})
            images_list.append(twitter_image_src['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data["image"]:
                        if isinstance(data["image"], list):
                            images_list.append(data["image"][0]["url"])
                        if not isinstance(data["image"], list):
                            images_list.append(data["image"]["url"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            article_body = html.find('article')
            for aside in article_body.find_all('aside'):
                aside.decompose()
            figures = article_body.find_all('figure')
            for figure in figures:
                images_list.append(figure.img['src'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if not images_list:
            return "[ScrollNews] COULDN'T FIND IMAGES"
        images_list = ", ".join(images_list)
        return images_list

    @retry(stop_max_attempt_number=2,
           wait_exponential_multiplier=1000,
           wait_exponential_max=3000)  # noqa: C901
    def images_cnbc(self, html):  # pylint: disable=too-many-branches,no-self-use
        """Returns the image urls extracted from a CNBC article."""
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image:src'})
            images_list.append(twitter_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            primary_image = html.find('meta',
                                      {'itemprop': 'primaryImageOfPage'})
            images_list.append(primary_image['content'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if isinstance(data, list):
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data["image"]:
                        if isinstance(data["image"], list):
                            images_list.append(data["image"][0]["url"])
                        if not isinstance(data["image"], list):
                            images_list.append(data["image"]["url"])
                    if data["@type"] == "NewsArticle" and data["thumbnailUrl"]:
                        if isinstance(data["thumbnailUrl"], list):
                            images_list.append(data["thumbnailUrl"][0])
                        if not isinstance(data["thumbnailUrl"], list):
                            images_list.append(data["thumbnailUrl"])
                except:  # pylint: disable=bare-except  # noqa: E722    # nosec
                    pass
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        try:
            pictures = html.find_all('picture')
            for picture in pictures:
                for image in picture.find_all('img'):
                    images_list.append(image['src'])
        except:  # pylint: disable=bare-except  # noqa: E722    # nosec
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if not images_list:
            return " "
        images_list = ", ".join(images_list)
        return images_list
