## Archive Crawling service

This service is responsible for crawling news articles from the web archives of 21 (as of now) publishers, Indian and international, and extracting actionable information (such as title, description, article body, publish time, etc.) from them.
<br>

### Files

1. `crawling_pipeline.py` — This script contains<br>
    - Archive Crawling code for 21 publishers
    - Function to iterate over Archive URLs of a date range provided as input and extract the Article URLs from these pages.
    - Function to extract HTML of an article and save to a MongoDB collection, and save other details (URL, resource_id, etc.) to a MySQL table (`raw-articles`)
    - The code uses threading to speed up the process
        - Number of days to crawl at a time (set to 10)
        - Number of Article URLs to crawl for each date (set to 30)<br>
        [ *These numbers were arrived after extensive trial-and-error, this pair gave the best results (#articles resulting in CRAWL_FAIL were the lowest)* ]<br><br>
2. `extraction_pipeline.py` — This script contains<br>
    - Code to fetch Article data (like URL, HTML, publisher it belongs to, etc.) from a MySQL table (`raw-articles`), run the extraction pipeline on it and save the data to a MySQL table (`processed-articles`)
    - At present, we have extractors for {title, description, article_body, publish_time, authors, and images}
        - `images_extractor` is *not* in a final stage as the data it extracts won't be used anywhere. But still it's a part of the commit as it can extract distinct URLs of images in an article.
    - The extraction process utilizes multiple CPU cores for execution with the `multiprocessing` library (set to 10 CPU cores)<br><br>
3. `models.py` — This script contains<br>
    - SQLAlchemy code to create a MySQL database (`cms_major`) and the tables inside — `global-id`, `raw-articles` and `processed-articles`
    - Utility functions for the conversion between UUID and Binary formats for an ID.<br><br>
4. `extractor.py` — Gets the Article info from the Crawling pipeline , initializes the extractors to be run in the Extraction pipeline, and feeds the extractors with the Article data.<br><br>
5. `config.py` — Contains essential variables used throughout the major files.<br><br>
6. `publishers_headers.py` — Contains custom *headers* dictionaries for each publisher crawled in the Crawling pipeline.
    - Incorporating custom headers for each publisher has resulted in much better performance at crawling time than without, & some publishers return 404, 502 and other errors if headers aren't fed.<br><br>
7. `pipeline/extractor/comparer/` — Contains *comparer* codes - they store entity data from every candidate, then return the values in the order the candidates are listed in these files.
    - Example. `comparer_title.py` contains code to get the extracted title from 2 candidates, `newspaper_extractor.py` and `title_extractor.py` in that order. If the first candidate has extracted a non-None and non-'' title, it returns it, otherwise it checks whether the second candidate has returned a non-None and non-'' title - if yes, it returns it, otherwise it returns None.<br><br>
8. `pipeline/extractor/extractors` — Contains *extractor* codes - they run a list of custom extraction rules on every article, store all the extracted data in a list, and return the best (the longest) value
    - This holds for *title, description, and articlebody* extractors.
    - For *authors* extraction, all distinct values found in an article are returned in a concatenated string, separated by commas.
    - For *publish_datetime* extraction (done by `date_extractor.py`), the first publish_datetime value found in an article is returned after converting it to the IST timezone (if not already done).
    - `date_extractor_independent.py` — Custom publish_datetime extractor for the `INDEPENDENT` publisher, because their articles contain wrong datetime values in the rules used by `date_extractor.py` to extract this info.
    - `listing_date_extractor.py`, `readability_extractor.py`, `lang_detect_extractor.py` and `xpath_extractor.py` aren't used in the extraction pipeline.
        - The first is used in the Realtime-Crawling project and has been kept just for compatibility.
        - The second and third files came with the default `news-please` clone, they aren't used.
        - The last one was written a while back, but its purpose has been solved by one custom extractor each for title, description, etc.<br><br>
9. `test_extractors.py` (inside python.services.Archive_Crawling) — Unit tests for the extractors inside `pipeline/extractor/extractors`.
    - Apart from authors extraction, newspaper_extractor is the first extractor that is used. If it fails, the custom extractors come into play.<br><br>
10. `test_crawling_extraction_pipeline.py` (inside python.services.Archive_Crawling) — Mocking tests for Crawling and Extraction pipeline.<br><br>
11. `url_dict.py` — Contains a dict containing urls used in `test_extractors.py`
<br><br>


### How To

[Ensure there's a database named `cms_major` in your MySQL shell. If there's one and it already has some data, use another database.]

1. **Run the Crawling code**

```
python crawling_pipeline.py -P "PUBLISHER_NAME" -S "START_DATE" -E "END_DATE"

e.g.
python crawling_pipeline.py -P "NEW_YORK_TIMES" -S "2021-01-29" -E "2021-01-29"
```
<br>

2. **Run the Extraction code**

Once begun, the extraction code keeps on running until as long as `CRAWL_SUCCESS` articles exist in the `raw-articles` table.
<br>

```
python extraction_pipeline.py
```

<br>

### Dependencies

All Python libraries listed in `requirements.txt`
