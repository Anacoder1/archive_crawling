from .abstract_extractor import AbstractExtractor
from bs4 import BeautifulSoup
import json
from retrying import retry


class ImagesExtractor(AbstractExtractor):
    def __init__(self):
        self.name = "images_extractor"

    def _topimage(self, item):
        self.html_item = item['spider_response']
        self.publisher = item['publisher']
        html = BeautifulSoup(self.html_item.body, 'html5lib')
        images = ""

        try:
            if self.publisher == 'EconomicTimes':
                images = self.images_ET(html)
            if self.publisher == 'TimesofIndia':
                images = self.images_TOI(html)
            if self.publisher == 'DeccanHerald':
                images = self.images_DH(html)
            if self.publisher == 'NDTV':
                images = self.images_NDTV(html)
            if self.publisher == 'Independent':
                images = self.images_Independent(html)
            if self.publisher == 'EveningStandard':
                images = self.images_EveningStandard(html)
            if self.publisher == 'NewYorkPost':
                images = self.images_NewYorkPost(html)
            if self.publisher == 'Express':
                images = self.images_Express(html)
            if self.publisher == 'USAToday':
                images = self.images_USAToday(html)
            if self.publisher == 'DailyMail':
                images = self.images_DailyMail(html)
            if self.publisher == 'IndiaToday':
                images = self.images_IndiaToday(html)
            if self.publisher == 'OneIndia':
                images = self.images_OneIndia(html)
            if self.publisher == 'HinduBusinessLine':
                images = self.images_HinduBusinessLine(html)
            if self.publisher == 'ScrollNews':
                images = self.images_ScrollNews(html)
            if self.publisher == 'CNBCWorld':
                images = self.images_CNBC(html)

        except:
            pass
        return images


    def clean_images(self, image):
        return image.strip().lstrip().rstrip()


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_ET(self, html):
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
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
                except:
                    pass
        except:
            pass
        try:
            figures = html.find_all('figure')
            for figure in figures:
                for image in figure.find_all('img'):
                    if image.get('data-original') and image.get('data-original') not in images_list:
                        images_list.append(image.get('data-original'))
        except:
            pass
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_TOI(self, html):
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
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
                except:
                    pass
        except:
            pass
        try:
            figures = html.find_all('figure')
            for figure in figures:
                for image in figure.find_all('img'):
                    if image.get('src') and image.get('src') not in images_list:
                        images_list.append(image.get('src'))
        except:
            pass
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_DH(self, html):
        images_list = []
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["image"] and type(data["image"]) is not list:
                        images_list.append(data["image"]["url"])
                    elif data["image"] and type(data["image"]) is list:
                        images_list.append(data["image"][0]["url"])
                        break
                except:
                    pass
        except:
            pass
        try:
            caption_images = html.find_all('img', {'class': 'caption'})
            for caption_image in caption_images:
                if caption_image["src"] not in images_list:
                    images_list.append(caption_image["src"])
        except:
            pass
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_NDTV(self, html):
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:
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
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["image"]["url"].strip() != '':
                        images_list.append(data["image"]["url"])
                except:
                    pass
        except:
            pass
        try:
            main_images = html.find_all('img', {'id': 'story_image_main'})
            for main_image in main_images:
                if main_image.get('data-src'):
                    images_list.append(main_image.get('data-src'))
                    break
                if main_image.get('src'):
                    if "http://" in main_image.get('src') or "https://" in main_image.get('src'):
                        images_list.append(main_image.get('src'))
                        break
        except:
            pass
        try:
            main_images = html.find_all('img', {'class': 'story_image_main'})
            for main_image in main_images:
                if main_image.get('data-src'):
                    images_list.append(main_image.get('data-src'))
                    break
                if main_image.get('src'):
                    if "http://" in main_image.get('src') or "https://" in main_image.get('src'):
                        images_list.append(main_image.get('src'))
                        break
        except:
            pass
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_Independent(self, html):
        images_list = []
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
            pass
        try:
            og_image_secure = html.find('meta', {'property': 'og:image:secure_url'})
            images_list.append(og_image_secure['content'])
        except:
            pass
        try:
            images_srcset = html.find_all('amp-img')
            for image in images_srcset:
                images_list.append(image['src'])
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    images_list.append(data["image"])
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    images_list.append(data["thumbnailUrl"])
                except:
                    pass
        except:
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_EveningStandard(self, html):
        images_list = []
        try:
            twitter_image = html.find('meta', {'property': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
            pass
        try:
            og_image_secure = html.find('meta', {'property': 'og:image:secure_url'})
            images_list.append(og_image_secure['content'])
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["image"]:
                        images_list.append(data["image"])
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and data["thumbnailUrl"]:
                        images_list.append(data["thumbnailUrl"])
                except:
                    pass
        except:
            pass
        try:
            amp_images = html.find_all('amp-img')
            for amp_image in amp_images:
                images_list.append(amp_image['src'])
        except:
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_NewYorkPost(self, html):
        images_list = []
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:
            pass
        try:
            twitter_image_src = html.find('meta', {'name': 'twitter:image:src'})
            images_list.append(twitter_image_src['content'])
        except:
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
            pass
        try:
            og_image_secure = html.find('meta', {'property': 'og:image:secure_url'})
            images_list.append(og_image_secure['content'])
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle" and type(data["image"]) is list:
                        images_list.append(data["image"][0]["url"])
                    elif data["@type"] == "NewsArticle" and type(data["image"]) is not list:
                        images_list.append(data["image"]["url"])
                except:
                    pass
        except:
            pass
        try:
            images = html.find_all('img')
            for image in images:
                try:
                    if "standard-article-image" in image["id"]:
                        images_list.append(image["src"])
                except:
                    pass
                try:
                    for cl in image["class"]:
                        if "wp-image" in cl:
                            images_list.append(image["data-srcset"])
                except:
                    pass
        except:
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_Express(self, html):
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
            pass
        try:
            twitter_image = html.find('meta', {'property': 'twitter:image:src'})
            images_list.append(twitter_image['content'])
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if data["@type"] == "NewsArticle":
                        if type(data["image"]) is list:
                            images_list.append(data["image"][0]["url"])
                        elif type(data["image"]) is not list:
                            images_list.append(data["image"]["url"])
                except:
                    pass
        except:
            pass
        try:
            article = html.find('article', {'itemprop': 'mainEntity'})
            pictures = article.find_all('picture')
            for picture in pictures:
                for img in picture.find_all('img'):
                    images_list.append(img['data-src'])
        except:
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_USAToday(self, html):
        images_list = []
        try:
            article = html.find('article')
            images = article.find_all('img')
            for image in images:
                try:
                    images_list.append(image['data-gl-src'])
                except:
                    pass
                try:
                    images_list.append(image['src'])
                except:
                    pass
        except:
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["thumbnailUrl"]:
                        images_list.append(data["thumbnailUrl"])
                    if data["image"]:
                        if type(data["image"]) is list:
                            images_list.append(data["image"][0]["url"])
                        elif type(data["image"]) is not list:
                            images_list.append(data["image"]["url"])
                    if data[1] and data[1]["url"]:
                        images_list.append(data[1]["url"])
                except:
                    pass
        except:
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_DailyMail(self, html):
        images_list = []
        try:
            twitter_image = html.find('meta', {'property': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
            pass
        try:
            thumbnail_image = html.find('meta', {'itemprop': 'thumbnailurl'})
            images_list.append(thumbnail_image['content'])
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle" or data["@WebPage"]:
                        if data["image"] and type(data["image"]) is list:
                            images_list.append(data["image"][0]["url"])
                        elif data["image"] and type(data["image"]) is not list:
                            images_list.append(data["image"]["url"])
                except:
                    pass
        except:
            pass
        try:
            article_body = html.find('div', {'itemprop': 'articleBody'})
            images = article_body.find_all('img')
            for img in images:
                images_list.append(img['src'])
        except:
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_IndiaToday(self, html):
        images_list = []
        try:
            images = html.find_all('img')
            for image in images:
                images_list.append(image['data-src'])
                images_list.append(image['src'])
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "ImageObject" and data["url"]:
                        images_list.append(data["url"])
                except:
                    pass
        except:
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'])
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'description ', 'itemprop': 'articleBody'})
            images = article_body.find_all('img')
            for img in images:
                images_list.append(img['src'])
                images_list.append(img['data-src'])
        except:
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_OneIndia(self, html):
        images_list = []
        try:
            link_href = html.find('link', {'rel': 'image_src'})
            images_list.append(self.clean_images(link_href['href']))
        except:
            pass
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(self.clean_images(og_image['content']))
        except:
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(self.clean_images(twitter_image['content']))
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data["image"]:
                        if type(data["image"]["url"]) is list:
                            images_list.append(self.clean_images(data["image"]["url"][0]))
                        if type(data["image"]["url"]) is not list:
                            images_list.append(self.clean_images(data["image"]["url"]))
                except:
                    pass
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    images_list.append(self.clean_images(data["thumbnailUrl"]))
                except:
                    pass
        except:
            pass
        try:
            images = html.find_all('img', {'class': 'image_listical'})
            for img in images:
                images_list.append(self.clean_images("https://www.oneindia.com" + img['data-pagespeed-lazy-src']))
        except:
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_HinduBusinessLine(self, html):
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'].strip())
        except:
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image'})
            images_list.append(twitter_image['content'].strip())
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data["image"]:
                        if type(data["image"]) is list:
                            images_list.append(data["image"][0]["url"].strip())
                        if type(data["image"]) is not list:
                            images_list.append(data["image"]["url"].strip())
                except:
                    pass
        except:
            pass
        try:
            article_body = html.find('div', {'class': 'contentbody inf-body'})
            images = article_body.find_all('img')
            for img in images:
                images_list.append(img['src'].strip())
        except:
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_ScrollNews(self, html):
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
            pass
        try:
            twitter_image_src = html.find('meta', {'name': 'twitter:image:src'})
            images_list.append(twitter_image_src['content'])
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data["image"]:
                        if type(data["image"]) is list:
                            images_list.append(data["image"][0]["url"])
                        if type(data["image"]) is not list:
                            images_list.append(data["image"]["url"])
                except:
                    pass
        except:
            pass
        try:
            article_body = html.find('article')
            for aside in article_body.find_all('aside'):
                aside.decompose()
            figures = article_body.find_all('figure')
            for figure in figures:
                images_list.append(figure.img['src'])
        except:
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return "[ScrollNews] COULDN'T FIND IMAGES"
        images_list = ", ".join(images_list)
        return images_list


    @retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
    def images_CNBC(self, html):
        images_list = []
        try:
            og_image = html.find('meta', {'property': 'og:image'})
            images_list.append(og_image['content'])
        except:
            pass
        try:
            twitter_image = html.find('meta', {'name': 'twitter:image:src'})
            images_list.append(twitter_image['content'])
        except:
            pass
        try:
            primary_image = html.find('meta', {'itemprop': 'primaryImageOfPage'})
            images_list.append(primary_image['content'])
        except:
            pass
        try:
            scripts = html.find_all('script', {'type': 'application/ld+json'})
            scripts = [script for script in scripts if script is not None]
            for script in scripts:
                try:
                    data = json.loads(script.string, strict=False)
                    if type(data) is list:
                        data = data[0]
                    if data["@type"] == "NewsArticle" and data["image"]:
                        if type(data["image"]) is list:
                            images_list.append(data["image"][0]["url"])
                        if type(data["image"]) is not list:
                            images_list.append(data["image"]["url"])
                    if data["@type"] == "NewsArticle" and data["thumbnailUrl"]:
                        if type(data["thumbnailUrl"]) is list:
                            images_list.append(data["thumbnailUrl"][0])
                        if type(data["thumbnailUrl"]) is not list:
                            images_list.append(data["thumbnailUrl"])
                except:
                    pass
        except:
            pass
        try:
            pictures = html.find_all('picture')
            for picture in pictures:
                for image in picture.find_all('img'):
                    images_list.append(image['src'])
        except:
            pass
        images_list = [image for image in images_list if image is not None]
        images_list = [image for image in images_list if "https://" in image]
        images_list = list(set(images_list))
        if len(images_list) == 0:
            return " "
        images_list = ", ".join(images_list)
        return images_list
