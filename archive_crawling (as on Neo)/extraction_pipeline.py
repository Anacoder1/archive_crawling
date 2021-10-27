"""Extraction code for Archive-Crawling Service."""

import logging
import time
import uuid
from multiprocessing import Process
from pymongo import MongoClient
from retrying import retry
from sqlalchemy.orm import sessionmaker
import models as db
from python.services.archive_crawling.extractor import extract_information
from python.services.archive_crawling.config import MONGODB_DATABASE, NUM_PROCESSES_EXTRACTION, NUM_ARTICLES_BATCH_EXTRACTION

client = MongoClient()
mydb = client[MONGODB_DATABASE]
raw_articles_mongodb = mydb.data

logging.basicConfig(filename='extraction_log.log',
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')


@retry(stop_max_attempt_number=3,
       wait_exponential_multiplier=1000,
       wait_exponential_max=3000)
def extract_content(data):
    """
    Gets resource_id, html, publisher, date_crawled from the crawling code
    and runs the extraction pipeline using that info, returning the article
    title, description, body, etc.
    """
    session_object = sessionmaker(bind=db.get_db_engine(), autoflush=False)
    session = session_object()
    processed_articles = []
    for rid, url, html, publisher, date_crawled in data:
        try:
            result = extract_information({
                'html': html,
                'publisher': db.Publishers[publisher],
                'url': url,
                'listing_date': None
            })
            status = db.ArticleState.EXTRACT_SUCCESS
            date_published = result.date_publish
            if date_published is None:
                date_published = date_crawled

            if result.title is None or result.description is None or result.maintext is None:
                status = db.ArticleState.EXTRACT_FAIL
            if result.title is not None:
                result.title = str(result.title[:2000])
            if result.description is not None:
                result.description = str(result.description[:5000])
            if result.authors is not None:
                result.authors = str(result.authors[:2000])
            if result.image_url is not None:
                result.image_url = str(result.image_url[:2000])
            processed_articles.append(
                db.ProcessedArticles(resource_id=rid,
                                     url=url,
                                     title=result.title,
                                     publish_time=date_published,
                                     authors=result.authors,
                                     description=result.description,
                                     clean_body=result.maintext,
                                     images=result.image_url,
                                     language=result.language,
                                     category=result.category))

            row_to_change = session.query(db.RawArticles).filter(db.RawArticles.resource_id == rid).all()
            row_to_change[0].state = status
            logging.info("Extraction complete for url ==> {}".format(url))
        except Exception as exception:    # pylint: disable=broad-except
            row_to_change = session.query(db.RawArticles).filter(db.RawArticles.resource_id == rid).all()
            row_to_change[0].state = db.ArticleState.EXTRACT_FAIL
            logging.exception("Extraction FAILED for url ==> {}, exception ====> {}".format(url, exception))

    session.add_all(processed_articles)
    try:
        session.commit()
    except Exception as exception:    # pylint: disable=broad-except
        session.rollback()
        logging.exception("EXCEPTION: Commit failed due to exception ===> %s", exception)
    session.close()


def driver_code(num_processes):
    """Calls extract_content in multiprocessing fashion."""
    count_zero = 0
    while True:
        session_obj = sessionmaker(bind=db.get_db_engine(), autoflush=False)
        session_main = session_obj()
        logging.info("Began session")
        offset = 0
        past_data = session_main.query(db.RawArticles).filter(
            db.RawArticles.state == db.ArticleState.CRAWL_SUCCESS).offset(offset).limit(NUM_ARTICLES_BATCH_EXTRACTION).all()
        if len(past_data) == 0:
            count_zero += 1
            time.sleep(60)
            continue
        if count_zero > 20:
            break
        article_per_process = int(len(past_data) / num_processes)
        article_per_process += 1
        article_index = 0

        processes = []
        for _ in range(num_processes):
            subdata = []
            for row in past_data[article_index:article_index + article_per_process]:
                mongo_id = uuid.UUID(bytes=row.resource_id).hex
                subdata.append([row.resource_id, row.url,
                                raw_articles_mongodb.find_one({'_id': mongo_id})['html_body'],
                                row.publisher.name, row.date_crawled])
            article_index += article_per_process
            processes.append(Process(target=extract_content, args=(subdata, )))

        for process_element in processes:
            process_element.start()
        for process_element in processes:
            process_element.join()

        session_main.close()
        logging.info("Ending session")
        offset += NUM_ARTICLES_BATCH_EXTRACTION
        logging.info("Sleeping")


if __name__ == '__main__':
    driver_code(NUM_PROCESSES_EXTRACTION)
