# imdb-forum-crawler-python
A web crawler for IMDB's advanced title search.
Dumps data into a mongo database. It is designed to use two data sources.

You need to add a settings.py script to the project's main folder
```bash
# -*- coding: utf-8 -*-

BOT_NAME = 'imdbcrawler'

SPIDER_MODULES = ['imdbcrawler.spiders']
NEWSPIDER_MODULE = 'imdbcrawler.spiders'
LOG_LEVEL = 'INFO'

RETRY_HTTP_CODES = [503]
RETRY_TIMES = 10
DOWNLOAD_DELAY = 0.01
CONCURRENT_REQUESTS = 1
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'

DEPTH_PRIORITY = 1

SOURCE_MONGO_URI = '#'
SOURCE_MONGO_DATABASE = '#'
SOURCE_COLLECTION = '#'
SOURCE_USER = '#'
SOURCE_PASSWORD = '#'
TARGET_MONGO_URI = '#'
TARGET_MONGO_DATABASE = '#'
TARGET_COLLECTION = '#'
TARGET_USER = '#'
TARGET_PASSWORD = '#'

FROM_YEAR = 2014
TO_YEAR = 2014

# Prevent from Filtering
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'
ITEM_PIPELINES = {
    'imdbcrawler.pipelines.MongoPipeline': 0
}
```

Dependencies:
```bash
scrapy
dateutil
```

Instructions:
```bash
scrapy crawl ImdbForumCrawler
```