"""
File to store values of essential constants used throughout the
Archive-Crawling service.
"""

# flake8: noqa

HOST = 'localhost'
PORT = '3306'
DBNAME = 'cms_major'
USER = 'db'
PASSWORD = 'newzer@'    # nosec
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + USER + ':' + PASSWORD + '@' + HOST + ':' + PORT + '/' + DBNAME

MONGODB_DATABASE = 'cms_major'
PER_DAY = 30    # Number of URLs to process per date in every thread, in crawling_pipeline.py
DAYS_AT_A_TIME = 10    # Number of dates to crawl in every batch, in crawling_pipeline.py
NUM_PROCESSES_EXTRACTION = 10    # Number of processes to use in extraction_pipeline.py
NUM_ARTICLES_BATCH_EXTRACTION = 3600    # Number of articles' data to extract in a batch, in extraction_pipeline.py

HEADERS_MAIN = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'
}

proxies_ip_list = [
    "https://ishjoatt-1:lrm30lf8w0dg@p.webshare.io:80",
    "https://ishjoatt-2:lrm30lf8w0dg@p.webshare.io:80",
    "https://ishjoatt-3:lrm30lf8w0dg@p.webshare.io:80",
    "https://ishjoatt-4:lrm30lf8w0dg@p.webshare.io:80",
    "https://ishjoatt-5:lrm30lf8w0dg@p.webshare.io:80"
]