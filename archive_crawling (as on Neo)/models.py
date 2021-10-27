"""
Code to create the MySQL database with tables necessary to store data from
Crawling and Extraction pipelines.
"""

import enum
import uuid
from sqlalchemy import (VARCHAR, Column, Enum, ForeignKey, Index,
                        create_engine, text, types)
from sqlalchemy.dialects.mysql import LONGTEXT, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP
from python.services.archive_crawling.config import SQLALCHEMY_DATABASE_URI

Base = declarative_base()


def get_db_engine():
    """Function to get DB engine."""
    engine = create_engine(SQLALCHEMY_DATABASE_URI,
                           max_overflow=100,
                           pool_timeout=300)
    Base.metadata.create_all(engine, checkfirst=True)
    return engine


class ArticleState(enum.Enum):
    """States an article in raw-articles table can be."""
    ADDED = 1
    CRAWL_FAIL = 2
    CRAWL_SUCCESS = 3
    EXTRACT_FAIL = 4
    EXTRACT_SUCCESS = 5


class CategoryType(enum.Enum):
    """Categories an article can be divided into."""
    BUSINESS = 1
    ENTERTAINMENT = 2
    POLITICS = 3
    SCI_TECH = 4
    SPORTS = 5
    WORLD = 6


class Publishers(enum.Enum):
    """
    List of all publishers common in Archive-Crawling,
    Real-Time Crawling, and CMS projects.
    """
    ABC_NEWS = 1
    ABP_LIVE = 2
    AL_JAZEERA = 3
    ALL_INDIA_RADIO = 4
    ANI = 5
    BAR_AND_BENCH = 6
    BBC_NEWS = 7
    BLOOMBERG_QUINT = 8
    BOMBAY_TIMES = 9
    BUSINESS_INSIDER_INDIA = 10
    BUSINESS_STANDARD = 11
    BUSINESS_UPTURN = 12
    CNBCTV18 = 13
    CNBC_WORLD = 14
    DAIJI_WORLD_MEDIA = 15
    DAILY_MAIL = 16
    DAWN = 17
    DECCAN_CHRONICLE = 18
    DECCAN_HERALD = 19
    DEVDISCOURSE = 20
    DNA = 21
    DOWN_TO_EARTH = 22
    EBM_NEWS = 23
    ECONOMIC_TIMES = 24
    ENGLISH_MATHRUBHUMI = 25
    ESPN_CRICINFO = 26
    EURO_NEWS = 27
    EVENING_STANDARD = 28
    EXPRESS = 29
    FIRST_POST = 30
    FORBES_INDIA = 31
    FREE_PRESS_JOURNAL = 32
    GREAT_ANDRA = 33
    GREATER_KASHMIR = 34
    HINDU_BUSINESS_LINE = 35
    HINDUSTAN_TIMES = 36
    HW_NEWS = 37
    INDEPENDENT = 38
    INDIA_DOT_COM = 39
    INDIAN_EXPRESS = 40
    INDIA_TIMES = 41
    INDIA_TODAY = 42
    INDIA_TV = 43
    JAGRAN = 44
    LIVE_LAW = 45
    MINT = 46
    MONEY_CONTROL = 47
    NATIONAL_HERALD = 48
    NDTV = 49
    NEWS18 = 50
    NEWS_LIVE = 51
    NEWS_MINUTE = 52
    NEW_YORK_POST = 53
    NEW_YORK_TIMES = 54
    NORTHEAST_NOW = 55
    ONE_INDIA = 56
    OP_INDIA = 57
    OUTLOOK = 58
    PINKVILLA = 59
    REPUBLIC_WORLD = 60
    SCROLL_NEWS = 61
    SWARAJYA = 62
    TELANGANA_TODAY = 63
    THE_FINANCIAL_EXPRESS = 64
    THE_HANS_INDIA = 65
    THE_HINDU = 66
    THE_LOGICAL_INDIAN = 67
    THE_NEW_INDIAN_EXPRESS = 68
    THE_PIONEER = 69
    THE_PRINT = 70
    THE_QUINT = 71
    THE_SIASAT_DAILY = 72
    THE_STATESMAN = 73
    THE_TELEGRAPH = 74
    THE_TRIBUNE = 75
    THE_WASHINGTON_POST = 76
    THE_WIRE = 77
    TIME = 78
    TIMES_NOW = 79
    TIMES_OF_INDIA = 80
    USA_TODAY = 81
    WION_NEWS = 82
    WSJ = 83
    YAHOO_NEWS = 84
    ZEE_NEWS = 85


class ResourceType(enum.Enum):
    """
    Possible resource types.
    Archive-Crawling project just uses ARTICLE.
    """
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
    """Utility functions for UUID-BIN conversion."""
    @staticmethod
    def uuid_to_bin(cid, flag):
        """Converts UUID string into binary."""
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
        """Converts binary to UUID string."""
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


class GlobalID(Base):
    """Primarily stores resource_id and resource_type of an archive article."""
    __tablename__ = 'global-id'

    t_create = Column(TIMESTAMP,
                      server_default=func.localtimestamp(),
                      nullable=False)
    t_update = Column(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
        nullable=False)
    resource_id = Column(types.BINARY(16),
                         unique=True,
                         nullable=False,
                         primary_key=True)
    resource_type = Column(Enum(ResourceType))

    raw_articles = relationship("RawArticles",
                                uselist=False,
                                back_populates="global_id")

    def __repr__(self):
        """String representation for a GlobalID object."""
        return "<GlobalID(t_create='{}', t_update='{}', resource_id='{}', resource_type='{}')>".format(
            self.t_create, self.t_update, self.resource_id,
            self.resource_type.name)


class RawArticles(Base):
    """
    Stores basic information of a crawled article.
    Dependent tables - processed-articles
    """
    __tablename__ = 'raw-articles'

    t_create = Column(TIMESTAMP,
                      server_default=func.localtimestamp(),
                      nullable=False)
    t_update = Column(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
        nullable=False)
    resource_id = Column(types.BINARY(16),
                         ForeignKey('global-id.resource_id'),
                         nullable=False,
                         primary_key=True)
    publisher = Column(Enum(Publishers))
    url = Column(VARCHAR(2083))
    date_crawled = Column(TIMESTAMP)
    state = Column(Enum(ArticleState))

    global_id = relationship("GlobalID", back_populates="raw_articles")
    processed_articles = relationship("ProcessedArticles",
                                      uselist=False,
                                      back_populates="raw_articles")

    __table_args__ = (Index('idx_state', 'state'), )

    def __repr__(self):
        """String representation for a RawArticles object."""
        return ("<RawArticles(t_create='{}', t_update='{}', "
                "resource_id='{}', publisher='{}', url='{}', "
                "date_crawled='{}', state='{}'>").format(
                    self.t_create, self.t_update, self.resource_id,
                    self.publisher.name, self.url, self.date_crawled,
                    self.state)


class ProcessedArticles(Base):
    """Stores information obtained from extraction pipeline for an article"""
    __tablename__ = 'processed-articles'

    t_create = Column(TIMESTAMP,
                      server_default=func.localtimestamp(),
                      nullable=False)
    t_update = Column(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
        nullable=False)
    resource_id = Column(types.BINARY(16),
                         ForeignKey('raw-articles.resource_id'),
                         primary_key=True)
    url = Column(VARCHAR(2083))
    publish_time = Column(TIMESTAMP)
    title = Column(VARCHAR(2000))
    description = Column(VARCHAR(5000))
    clean_body = Column(LONGTEXT)
    images = Column(TEXT)
    authors = Column(VARCHAR(2000))
    language = Column(VARCHAR(2))
    category = Column(Enum(CategoryType))

    raw_articles = relationship("RawArticles",
                                back_populates="processed_articles")

    def __repr__(self):
        """String representation for a ProcessedArticles object."""
        return (
            "<ProcessedArticles(t_create='{}', t_update='{}', resource_id='{}', "
            "url='{}', publish_time='{}', title='{}', description='{}', clean_body='{}', "
            "images='{}', authors='{}', language='{}', category='{}')>"
        ).format(self.t_create, self.t_update, self.resource_id, self.url,
                 self.publish_time, self.title, self.description,
                 self.clean_body, self.images, self.authors, self.language,
                 self.category)


if __name__ == '__main__':
    Session = sessionmaker(bind=get_db_engine())
    session = Session()
    try:
        session.commit()
    except Exception:  # pylint: disable=broad-except
        session.rollback()
        raise
    finally:
        session.close()
