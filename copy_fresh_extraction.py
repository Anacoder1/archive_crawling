from datetime import date, datetime, timedelta
import pandas as pd
import time
import logging
import uuid
import argparse
import fresh_models as db
from retrying import retry
from pymongo import MongoClient
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from extractor import extract_information
from multiprocessing import Process, Pool

client = MongoClient()
mydb = client['cms_major']
raw_articles_mongodb = mydb.data


logging.basicConfig(filename='test_extraction.log',
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S') # , encoding='utf-8'

def right_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000, wait_exponential_max=3000)
def extract_content(data):
    Sess = sessionmaker(bind=db.get_dbEngine(), autoflush=False)
    session = Sess()
    articles_status_update = []
    processed_articles = []

    for rid, url, html, publisher, date_crawled, publisher_id in data:
        try:
            result = extract_information({'html': html, 'publisher': db.PublishersType[publisher], 'url': url, 'listing_date': None})
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
            article_data_dict = {
                'resource_id': rid,
                'url': url,
                'title': result.title,
                'publish_time': date_published,
                'authors': result.authors,
                'description': result.description,
                'clean_body': result.maintext,
                'images': result.image_url,
                'language': result.language,
                'category': result.category,
                'publisher_id': publisher_id
            }
            processed_articles.append(article_data_dict)
            
            article_state_dict = {
                'resource_id': rid,
                'state': status
            }
            articles_status_update.append(article_state_dict)

            print("[ {} ]  Extraction complete for url ==> {}".format(right_now(), url))
            logging.info("Extraction complete for url ==> {}".format(url))
        except:
            article_state_dict = {
                'resource_id': rid,
                'state': db.ArticleState.EXTRACT_FAIL
            }
            articles_status_update.append(article_state_dict)
            print("[ {} ]  Extraction FAILED for url ==> {}".format(right_now(), url))
            logging.info("Extraction FAILED for url ==> {}".format(url))

    print("[ {} ]  Bulk inserting into processed-articles table".format(right_now()))
    session.bulk_insert_mappings(db.processedArticles, processed_articles)
    print("[ {} ]  Bulk updating state column in raw-articles table".format(right_now()))
    session.bulk_update_mappings(db.rawArticles, articles_status_update)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print("BATCH FAILURE.")
        logging.exception("EXCEPTION: Extraction failed for url ==> {}, exception ==> {}".format(url, e))
        print("EXCEPTION: Extraction failed for url ==> {}, exception ==> {}".format(url, e))
    session.close()


if __name__ == '__main__':
    count_zero = 0
    while True:
        Session = sessionmaker(bind=db.get_dbEngine(), autoflush=False)
        session = Session()
        start = time.time()
        print("[ {} ]  Began extraction session".format(right_now()))
        offset = 0
        past_data = session.query(db.rawArticles).filter(db.rawArticles.state == db.ArticleState.CRAWL_SUCCESS).offset(offset).limit(10000).all()    ## add some order in L76
        print("Length of past_data = {}".format(len(past_data)))
        # if len(past_data) == 0:
        #     count_zero += 1
        #     time.sleep(60)
        #     continue
        # else:
        #     count_zero = 0
        # if count_zero > 20:
        #     break

        article_per_process = int(len(past_data) / 10)
        article_per_process += 1
        article_index = 0

        with open("wrong_urls.txt", 'a') as filex:
            processes = []
            for batch_index in range(10):
                subdata = []
                for row in past_data[article_index:article_index + article_per_process]:
                    MONGO_ID = uuid.UUID(bytes=row.resource_id).hex
                    try:
                        subdata.append([row.resource_id, row.url,
                                        raw_articles_mongodb.find_one({'_id': MONGO_ID})['html_body'],
                                        row.publisher.name, row.date_crawled, row.publisher_id])
                    except:
                        filex.write(row.url)
                        filex.write('\n')
                article_index += article_per_process
                processes.append(Process(target=extract_content, args=(subdata,)))

        for p in processes:
            p.start()
        for p in processes:
            p.join()

        session.close()
        print("[ {} ]  Ending extraction session".format(right_now()))
        print("[  {} minutes taken for this batch of 10k docs  ]".format((time.time()-start) / 60))
        offset += 10000
        logging.info("Sleeping")
