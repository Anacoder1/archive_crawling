import enum
import pytz
import uuid

from datetime import datetime
from sqlalchemy import create_engine, types, CHAR, BIGINT, Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import SMALLINT, INT
from sqlalchemy import VARCHAR
from sqlalchemy.dialects.mysql import TEXT, LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import Date, DateTime
from sqlalchemy_utils import UUIDType

IST = pytz.timezone('Asia/Kolkata')
HOST = 'localhost'
PORT = '3306'
DBNAME = 'cms_major'
USER = 'db'
PASSWORD = 'newzer@'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + USER + ':' + PASSWORD + '@' + HOST + ':' + PORT + '/' + DBNAME


Base = declarative_base()


def get_dbEngine():
    """Function to get db engine."""
    engine = create_engine(SQLALCHEMY_DATABASE_URI, max_overflow=100, pool_timeout=300)
    Base.metadata.create_all(engine, checkfirst=True)
    return engine


class ArticleState(enum.Enum):
    ADDED = 1
    CRAWL_FAIL = 2
    CRAWL_SUCCESS = 3
    EXTRACT_FAIL = 4
    EXTRACT_SUCCESS = 5


class CategoryType(enum.Enum):
    Business = 1
    Entertainment = 2
    Politics = 3
    Sci_Tech = 4
    Sports = 5
    World = 6


class PublishersType(enum.Enum):
    ABCNews = 1
    Aljazeera = 2
    BBCNews = 3
    BusinessStandard = 4
    CNBCWorld = 5
    DailyMail = 6
    Dawn = 7
    DeccanChronicle = 8
    DeccanHerald = 9
    EBMNews = 10
    ESPNCricInfo = 11
    EconomicTimes = 12
    EuroNews = 13
    EveningStandard = 14
    Firstpost = 15
    ForbesIndia = 16
    FreePressJournal = 17
    HinduBusinessLine = 18
    HindustanTimes = 19
    Independent = 20
    IndiaToday = 21
    TheIndianExpress = 22
    MoneyControl = 23
    NDTV = 24
    NewYorkPost = 25
    News18 = 26
    OneIndia = 27
    ScrollNews = 28
    TheFinancialExpress = 29
    TheHindu = 30
    ThePioneer = 31
    TheQuint = 32
    TheTelegraph = 33
    TheWashingtonPost = 34
    TheWire = 35
    Time = 36
    TimesofIndia = 37
    USAToday = 38
    WSJ = 39
    YahooNews = 40
    DNA = 41
    IndiaTV = 42
    RepublicWorld = 43
    Express = 44
    NYTimes = 45


class ResourceType(enum.Enum):
    ARTICLE = 1
    BOOST = 2
    COMMENT = 3
    ENTITY = 4
    EVENT = 5
    POLL = 6
    POLL_OPTION = 7
    POST = 8
    RAVEN = 9
    REACTION = 10
    STORYLINE = 11
    USER = 12


class UUIDConversion:
    @staticmethod
    def uuid_to_bin(cid, flag):
        id_ = cid.hex
        if flag:
            string_form = id_[12:16]
        else:
            string_form = id_[0:8]
        string_form += id_[8:12]
        if flag:
            string_form += id_[0:8]
        else:
            string_form += id_[12:16]
        string_form += id_[16:]
        val = uuid.UUID(string_form)
        return val.bytes

    @staticmethod
    def bin_to_uuid(cid, flag):
        id_ = uuid.UUID(bytes=cid).hex
        if flag:
            string_form = id_[8:16]
        else:
            string_form = id_[0:8]
        if flag:
            string_form = string_form + '-' + id_[4:8]
        else:
            string_form = string_form + '-' + id_[8:12]
        if flag:
            string_form = string_form + '-' + id_[0:4]
        else:
            string_form = string_form + '-' + id_[12:16]
        string_form = string_form + '-' + id_[16:]
        return string_form

    @staticmethod
    def mongodb_uuid(cid):
        """
        Converts UUID string to the same format as stored in raw-articles.
        The format of the returned id is exactly equal to lower(hex(resource_id))
        in raw-articles.
        """
        id_ = cid.hex
        string_form = id_[12:16]
        string_form += id_[8:12]
        string_form += id_[0:8]
        string_form += id_[16:]
        string_form = string_form.replace("-", "")
        return string_form


class globalID(Base):
    __tablename__ = 'global-id'

    t_create = Column(DateTime, default=datetime.now(tz=IST))
    t_update = Column(DateTime, onupdate=datetime.now(tz=IST))
    resource_id = Column(types.BINARY(16), unique=True, nullable=False, primary_key=True)
    resource_type = Column(Enum(ResourceType))

    raw_articles = relationship("rawArticles", uselist=False, back_populates="global_id")

    def __repr__(self):
        return "<globalID(t_create='{}', t_update='{}', resource_id='{}', resource_type='{}')>".format(
            self.t_create,
            self.t_update,
            self.resource_id,
            self.resource_type.name
        )


class rawArticles(Base):
    """
    Description for the doc table.
    Columns - t_create, doc_id, source, headline, location, time, body, url
    Dependent tables - Ner, Images
    """
    __tablename__ = 'raw-articles'

    t_create = Column(DateTime, default=datetime.now(tz=IST))
    t_update = Column(DateTime, onupdate=datetime.now(tz=IST))
    resource_id = Column(types.BINARY(16), ForeignKey('global-id.resource_id'), nullable=False, primary_key=True)
    publisher = Column(Enum(PublishersType))
    url = Column(VARCHAR(2083))  # https://web.archive.org/web/20060218052923/http://www.boutell.com/newfaq/misc/urllength.html
    # html_body = Column(LONGTEXT)
    date_crawled = Column(DateTime)
    state = Column(Enum(ArticleState))
    publisher_id = Column(types.BINARY(16))

    global_id = relationship("globalID", back_populates="raw_articles")
    processed_articles = relationship("processedArticles", uselist=False, back_populates="raw_articles")
    # articles_seen = relationship("articlesSeen", uselist=False, back_populates="raw_articles")

    def __repr__(self):
        return "<rawArticles(t_create='{}', t_update='{}', resource_id='{}', publisher='{}', url='{}', date_crawled='{}', state='{}', publisher_id='{}'>".format(
            self.t_create,
            self.t_update,
            self.resource_id,
            self.publisher.name,
            self.url,
            self.date_crawled,
            self.state,
            self.publisher_id
        )


# class articlesSeen(Base):
#     __tablename__ = "articles-seen"
#
#     t_create = Column(DateTime, default=datetime.now(tz=IST))
#     t_update = Column(DateTime, onupdate=datetime.now(tz=IST))
#     resource_id = Column(types.BINARY(16), ForeignKey('raw-articles.resource_id'), primary_key=True)
#     hashval = Column('hash', String(256), nullable=False, unique=True)
#     state = Column(Enum(ArticleState))
#
#     raw_articles = relationship("rawArticles", back_populates="articles_seen")
#
#     def __repr__(self):
#         return "<Seen(t_create='{}', t_update='{}', resource_id='{}', hashval='{}', state='{}')>".format(
#             self.t_create,
#             self.t_update,
#             self.resource_id,
#             self.hashval,
#             self.state.name)


# class articleCrawlingCheckpoint(Base):
#     __tablename__ = "articles-crawling-checkpoint"
#
#     t_create = Column(DateTime, default=datetime.now(tz=IST))
#     t_update = Column(DateTime, onupdate=datetime.now(tz=IST))
#     publisher = Column(Enum(PublishersType), primary_key=True)
#     publish_date = Column(Date, primary_key=True)
#     state = Column(Enum(ArticleState), primary_key=True)
#     count = Column(INT)
#
#     def __repr__(self):
#         return "<articleCrawlingCheckpoint(t_create='{}', t_update='{}', publisher='{}', publish_date='{}', state='{}', count='{}')>".format(
#             self.t_create,
#             self.t_update,
#             self.publisher.name,
#             self.publish_date,
#             self.state.name,
#             self.count
#         )


# TODO: Finalize partition logic and add it.

'''
partition = select(
    articleCrawlingCheckpoint,
    func.row_number()
    .over(partition_by=articleCrawlingCheckpoint.publish_date),
).alias()
'''


class processedArticles(Base):
    """
    Description for the doc table.
    Columns - t_create, doc_id, source, headline, location, time, body, url
    Dependent tables - Ner, Images
    """
    __tablename__ = 'processed-articles'

    t_create = Column(DateTime, default=datetime.now(tz=IST))
    t_update = Column(DateTime, onupdate=datetime.now(tz=IST))
    resource_id = Column(types.BINARY(16), ForeignKey('raw-articles.resource_id'), primary_key=True)
    url = Column(VARCHAR(2083))
    publish_time = Column(DateTime)
    title = Column(VARCHAR(2000))
    description = Column(VARCHAR(5000))
    clean_body = Column(LONGTEXT)
    images = Column(TEXT)
    authors = Column(VARCHAR(2000))
    language = Column(VARCHAR(2))
    category = Column(Enum(CategoryType))
    publisher_id = Column(types.BINARY(16))

    raw_articles = relationship("rawArticles", back_populates="processed_articles") # can remove

    def __repr__(self):
        return "<processedArticles(t_create='{}', t_update='{}', resource_id='{}', url='{}', publish_time='{}', " \
               "title='{}', description='{}', clean_body='{}', images='{}', authors='{}', language='{}', " \
               "category='{}', publisher_id='{}')>".format(
            self.t_create,
            self.t_update,
            self.resource_id,
            self.url,
            self.publish_time,
            self.title,
            self.description,
            self.clean_body,
            self.images,
            self.authors,
            self.language,
            self.category,
            self.publisher_id
        )


if __name__ == '__main__':
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=get_dbEngine())
    session = Session()
    try:
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
