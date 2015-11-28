# -*- coding: utf-8 -*-

BOT_NAME = 'imdbcrawler'

SPIDER_MODULES = ['imdbcrawler.spiders']
NEWSPIDER_MODULE = 'imdbcrawler.spiders'
LOG_LEVEL = 'INFO'

DOWNLOAD_DELAY = 0.6
CONCURRENT_REQUESTS = 1
USER_AGENT = "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3"

DEPTH_PRIORITY = 1

MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'hauptseminar'

# Prevent from Filtering
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'
ITEM_PIPELINES = {
    'imdbcrawler.pipelines.MongoPipeline': 0
}
