import unittest
from dotmap import DotMap
from python.services.archive_crawling.extractor import *

HTML_DIR = "tests/archive_crawling/test_data/"
with open(HTML_DIR + 'independent_5.html', 'r') as html_file:
    independent_html_data = html_file.read()
with open(HTML_DIR + 'scroll_news_4.html', 'r') as html_file:
    scroll_html_data = html_file.read()

class UnitTestsExtractor(unittest.TestCase):
    def setUp(self):
        self.scroll_authors = ['Scroll.in', 'Naveen Bharathi', 'Deepak Malghan', 'Andaleeb Rahman']
        self.scroll_description = '‘The extent of intra-village segregation in Karnataka is greater than the local black-white segregation in the American South.’'
        self.scroll_filename = 'https%3A%2F%2Fscroll.in%2Farticle%2F979318%2Fwhat-is-the-extent-of-caste-segregation-in-indian-villages-today-new-data-gives-us-an-idea.json'
        self.scroll_image = 'https://s01.sgp1.cdn.digitaloceanspaces.com/book/151099-akzmzflqnt-1606300636.jpeg'
        self.scroll_title = 'What is the extent of caste segregation in Indian villages today? New data gives us an idea'
        self.scroll_maintext = '''
        Even a beginning student of rural India with only a passing familiarity with its complex social organization can wax eloquent about one stylized fact—the near-perfect segregation of residential space by caste and religion. Introductory textbooks have immortalized spatial segregation as a constitutive feature of social life in agrarian India. When BR Ambedkar famously characterised the Indian village as a “sink of localism,” and a “den [of] narrow-mindedness,” he was partly railing against such spatial segregation in the Indian countryside. Figure 1: Amminabhavi, Dharwad District, c. 1950. (Digitized and remastered by authors using original sketch from Spate and Learmonth, 1954, p. 200) Generations of detailed ethnographic research has documented how residential space in rural India is not only segregated, but actually mirrors the hierarchical ordering of caste groups. Figure 1 depicts residential segregation in Amminabhavi, situated on the outskirts of the city of Dharwad in Karnataka, and made famous by Spate and Learmonth (1954) as the quintessential example of spatial organization in village India. This large village shows how Dalits (the formerly “untouchable” caste groups shown as “Harijans” in the original figure) are consigned to the periphery of the village. The dominant landholding castes occupy the center of the village. Other worker castes in the figure—Talwars, Shepherds, and Washermen—are also relegated to the spatial margins. The village headman and his kin occupy the best land parcel and live in a palatial “manor house.” Even as cartographic accounts detailing Amminabhavis around India have proliferated, we do not yet have a systematic quantification of the degree of segregation rural India. Consequently, quantitative studies of rural political economy are besieged with an important “missing variable.” While the actual extant of intra-village segregation remains unknown, the Indian national census data records the presence of multiple hamlet clusters in select districts across the country. Our summary is derived from preliminary findings of an ongoing project to develop the first ever largescale quantitative measurement of intra-village spatial segregation in India. We use micro-data from a survey conducted by the Government of Karnataka in 2015 (GOKS) to measure intra-village segregation. GOKS represents the first census-scale enumeration and coding of detailed caste (jati) and religion data since 1931, and the first ever micro dataset that allows for a quantitative characterization of intra-village spatial segregation. The data includes demographic information for all rural residents in Karnataka (approximately 36.5 million residents) from over 26,000 villages. We measure intra-village segregation by comparing the actual spatial arrangement of households in a village with the hypothetical case where the households are randomly distributed in the village. Figure 2 describes how we measure intra-village spatial segregation. Panel A of the figure depicts an actual village hamlet in the GOKS dataset. The forty households in this village are drawn from four different jatis. Panel B shows these households arranged in a random order. To compute intra-village segregation, we simply compare the “runs,” or unbroken sequence of households that share a social identity in the actual village with the hypothetical random ordering. We adapt the well-established “runs test” metric that has previously been used to measure street-level micro-segregation to more than two categories to account for the multitude of jati and religion groups in a village. The actual village has nine “runs,” while a random arrangement of the same forty households corresponds to twenty-one expected runs. The fewer the actual “runs” relative to the hypothetical random organization of space, the greater the measured value of segregation. Figure 2: Wald-Wolfowitz Micro Segregation. Amminabhavi representation in Panel C uses the eight-fold administrative mapping of endogamous jati and religion groups. Halli in Panels A and B use endogamous jati and religion groups. Each square represents an individual household in all three panels. The 2,500 houses in the Amminabhavi grid are represented row-wise. Authors’ computation (data from GOKS). Panel C in Figure 2 shows the 2015 spatial distribution of households in Amminabhavi as recorded by GOKS (we have shown the eight-fold administrative mapping of jatis). Even as Amminabhavi is on the cusp of being designated “urban,” its spatial demography has remained remarkably stable—seventy years after it was first immortalized as the exemplar of spatial organization in village India. Our intra-village segregation metric is measured on a 0–1 scale with a 0 indicating perfect integration and 1, perfect segregation. Figure 3 shows the distribution of this intra-village (micro) segregation metric across all villages in Karnataka for jatis, census groups, as well as religion. The boundary between the “touchables” and “untouchables” is especially stark as seen by a high degree of segregation between SCs, STs., and others (census groups). As a point of reference, Amminabhavi in Figure 3 has an intra-village micro segregation score of approximately 0.55. The extent of intra-village segregation in Karnataka is greater than the local black-white segregation in the American South that continues to influence residential patterns to this day. Figure 3: Distribution of Micro (intra-village) Segregation for jatis, census groups and religion in Rural Karnataka. 0 indicates perfect integration and 1, perfect segregation. Figure reproduced from Bharathi et al. (2020). Our analysis also shows that the extent of intra-village segregation is uncorrelated with other metrics used to measure demographic diversity, so that not accounting for such segregation can potentially bias extant quantitative characterizations of rural political economy in India. Limited evidence suggests that accounting for intra-village segregation is important for characterizing India’s rural political economy. Local public goods placement, or even hydro-geological distribution of groundwater resources within a village intersect with intra-village segregation. Beyond the political economy of rural India, the measurement of “social distance” has been one of the central founts of modern social sciences. For example, Georg Simmel argued that the stranger is, above all, a product of prevailing social distances that are explicitly spatial—the “geometry” is a constitutive feature of social distance. In societies with clearly defined status ranks, the classical relationship between contact and prejudice is shaped by Simmel’s “geometry.” If inter-group solidarity is tied to inter-group contact, our analysis shows that spatial segregation remains one of the most significant barriers. Naveen Bharathi (naveenb@sas.upenn.edu) is a CASI Postdoctoral Research Fellow. Deepak Malghan (dmalghan@iimb.ac.in) is an Associate Professor at the Center for Public Policy, Indian Institute of Management, Bangalore. Andaleeb Rahman (ar687@cornell.edu) is a Postdoctoral Associate at the Tata-Cornell Institute (TCI), Cornell University. This article is based on the forthcoming Contemporary South Asia article: “A Permanent Cordon Sanitaire: Intra-Village Spatial Segregation and Social Distance in India” and first appeared as part of the India in Transition series from the Centre for the Advanced Study of India.
        '''

    def test_from_html(self):
        url = "https://www.independent.co.uk/arts-entertainment/tv/news/bridgerton-violet-actor-ruth-gemmell-tracy-beaker-b1780757.html"
        html = independent_html_data
        download_date = None
        listing_date = None
        authors = ['Isobel Lewis', 'The Independent']
        maintext = '''
        Bridgerton viewers have spotted an unlikely connection between one of the show’s stars and Tracy Beaker. Dropping on Christmas Day, Netflix’s lavish period drama is set among high society in Regency-era London, with the wealthy Bridgerton family and their eldest daughter Daphne (Phoebe Dynevor) at the centre. The family is led by Lady Violet Bridgerton (played by Ruth Gemmell), a widow and mother to eight children. But while Gemmell has previously appeared in TV series including Utopia and Penny Dreadful, it was her role in CBBC’s TV film Tracy Beaker: The Movie of Me that many fans were delighted to recognise her from. The actor starred as Carly Beaker, the absent mother of protagonist Tracy (Dani Harmer) who lives at a children’s home. “Just found out the actress playing Daphne’s mum in Bridgerton also played Tracy Beaker’s mum and I can’t unsee it now,” one Twitter user wrote as they made the connection. “Wondered where I recognised the actress playing Violet in Bridgerton from then realised she was Tracy Beaker’s mum. This is v demonstrative of my television tastes,” another joked. Independent Culture Newsletter The best in film, music TV & radio straight to your inbox every week Please enter your email address Please enter a valid email address Please enter a valid email address SIGN UP Thanks for signing up to the Independent Culture newsletter {{#verifyErrors}} {{message}} {{/verifyErrors}} {{^verifyErrors}} {{message}} {{/verifyErrors}} The Independent would like to keep you informed about offers, events and updates by email, please tick the box if you would like to be contacted Read our full mailing list consent terms here Independent Culture Newsletter The best in film, music TV & radio straight to your inbox every week The Independent would like to keep you informed about offers, events and updates by email, please tick the box if you would like to be contacted Read our full mailing list consent terms here “Meryl Streep *wishes* she had the range of the actress who plays both Lady Bridgerton AND Carly Beaker in Tracy Beaker: The Movie of Me - EGOT for Ruth Gemmell now!!” one fan tweeted. Many also joked that just like Tracy fantasises about her mother being a famous actor, Gemmell’s role in Bridgerton may have proven her right. “The fact that Tracy Beaker’s mum is in Bridgerton,” one joked. “She really was a famous actress after all, I knew Tracy wasn’t lying.” “I absolutely LOVED #Bridgerton on Netflix but I could not see Lady Violet Bridgerton as anyone but Tracy Beaker’s mum - she really was a famous actress after all,” another fan wrote.
        '''
        for author in authors:
            self.assertIn(author, from_html(html, url, download_date, listing_date).authors)
        self.assertEqual(from_html(html, url, download_date, listing_date).date_download, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).date_modify, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).date_publish.strftime("%Y-%m-%d %H:%M:%S"), '2020-12-31 15:08:07')
        self.assertEqual(from_html(html, url, download_date, listing_date).description,
                         'Gemmell starred in the 2004 CBBC film Tracy Beaker: The Movie of Me')
        self.assertEqual(from_html(html, url, download_date, listing_date).filename,
                         'https%3A%2F%2Fwww.independent.co.uk%2Farts-entertainment%2Ftv%2Fnews%2Fbridgerton-violet-actor-ruth-gemmell-tracy-beaker-b1780757.html.json')
        self.assertEqual(from_html(html, url, download_date, listing_date).localpath, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).title,
                         'Bridgerton viewers learn that Lady Violet actor Ruth Gemmell played Tracy Beaker’s mum: ‘She really was a famous actress after all’')
        self.assertEqual(from_html(html, url, download_date, listing_date).title_page, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).title_rss, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).source_domain, 'www.independent.co.uk')
        self.assertEqual(' '.join(from_html(html, url, download_date, listing_date).maintext.split()),
                         ' '.join(maintext.split()))
        self.assertEqual(from_html(html, url, download_date, listing_date).url, url)
        self.assertEqual(from_html(html, url, download_date, listing_date).category, None)


        url = "https://scroll.in/article/979318/what-is-the-extent-of-caste-segregation-in-indian-villages-today-new-data-gives-us-an-idea"
        html = scroll_html_data
        download_date = None
        listing_date = None
        for author in self.scroll_authors:
            self.assertIn(author, from_html(html, url, download_date, listing_date).authors)
        self.assertEqual(from_html(html, url, download_date, listing_date).date_download, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).date_modify, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).date_publish.strftime("%Y-%m-%d %H:%M:%S"), '2020-11-25 11:30:00')
        self.assertEqual(from_html(html, url, download_date, listing_date).description, self.scroll_description)
        self.assertEqual(from_html(html, url, download_date, listing_date).filename, self.scroll_filename)
        self.assertEqual(from_html(html, url, download_date, listing_date).localpath, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).title, self.scroll_title)
        self.assertEqual(from_html(html, url, download_date, listing_date).title_page, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).title_rss, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).source_domain, 'scroll.in')
        self.assertEqual(' '.join(from_html(html, url, download_date, listing_date).maintext.split()),
                         ' '.join(self.scroll_maintext.split()))
        self.assertEqual(from_html(html, url, download_date, listing_date).url, url)
        self.assertEqual(from_html(html, url, download_date, listing_date).category, None)


        url = None
        html = scroll_html_data
        download_date = None
        listing_date = None
        for author in self.scroll_authors:
            self.assertIn(author, from_html(html, url, download_date, listing_date).authors)
        self.assertEqual(from_html(html, url, download_date, listing_date).date_download, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).date_modify, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).date_publish.strftime("%Y-%m-%d %H:%M:%S"), '2020-11-25 11:30:00')
        self.assertEqual(from_html(html, url, download_date, listing_date).description, self.scroll_description)
        self.assertEqual(from_html(html, url, download_date, listing_date).filename, '.json')
        self.assertEqual(from_html(html, url, download_date, listing_date).localpath, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).title, self.scroll_title)
        self.assertEqual(from_html(html, url, download_date, listing_date).title_page, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).title_rss, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).source_domain, None)
        self.assertEqual(' '.join(from_html(html, url, download_date, listing_date).maintext.split()),
                         ' '.join(self.scroll_maintext.split()))
        self.assertEqual(from_html(html, url, download_date, listing_date).url, None)
        self.assertEqual(from_html(html, url, download_date, listing_date).category, None)

    def test_extract_information(self):
        data = {
            'html': scroll_html_data,
            'url': "https://scroll.in/article/979318/what-is-the-extent-of-caste-segregation-in-indian-villages-today-new-data-gives-us-an-idea",
            'listing_date': None,
            'download_date': None
        }
        for author in self.scroll_authors:
            self.assertIn(author, extract_information(data).authors)
        self.assertEqual(extract_information(data).date_modify, None)
        self.assertEqual(extract_information(data).date_publish.strftime("%Y-%m-%d %H:%M:%S"), '2020-11-25 11:30:00')
        self.assertEqual(extract_information(data).description, self.scroll_description)
        self.assertEqual(extract_information(data).filename, self.scroll_filename)
        self.assertEqual(extract_information(data).image_url, None)
        self.assertEqual(extract_information(data).language, None)
        self.assertEqual(extract_information(data).localpath, None)
        self.assertEqual(extract_information(data).title, self.scroll_title)
        self.assertEqual(extract_information(data).title_page, None)
        self.assertEqual(extract_information(data).title_rss, None)
        self.assertEqual(extract_information(data).source_domain, 'scroll.in')
        self.assertEqual(' '.join(extract_information(data).maintext.split()), ' '.join(self.scroll_maintext.split()))
        self.assertEqual(extract_information(data).url, data['url'])
        self.assertEqual(extract_information(data).category, None)

if __name__ == '__main__':
    unittest.main(argv=['first-arg=-is-ignored'], exit=False, verbosity=2)
