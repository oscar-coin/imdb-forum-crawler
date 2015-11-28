# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime, time
from dateutil import parser

from imdbcrawler.items import PostItem


class ImdbSpider(scrapy.Spider):
    name = "ImdbForumCrawler"
    allowed_domains = ["imdb.com"]
    url_bases = ["http://www.imdb.com/"]
    base_url = "http://www.imdb.com"
    db = None
    collection_name = None
    year = 2015
    imdb_title_endpoint = "title/"
    imdb_board_endpoint = "board/"
    imdb_page_del = "?p="
    imdb_thread_del = "thread/"
    imdb_ids = []

    @staticmethod
    def get_thread_id(url):
        k = url.rfind("/")
        return url[k+1:]

    def start_requests(self):
        if len(self.imdb_ids) == 0:
            query = self.db[self.collection_name].find({
                'releaseDate': {'$gte': datetime(self.year, 1, 1), '$lte': datetime(self.year, 12, 31)},
                'languages': 'English'
            })
            self.logger.info("Number of elements to crawl forums for: %s", query.count())
            for doc in query:
                self.imdb_ids.append(doc["imdbId"])

        for imdb_id in self.imdb_ids:
            url = self.base_url + "/" + self.imdb_title_endpoint + imdb_id + "/"
            yield scrapy.Request(url + self.imdb_board_endpoint, meta={'url': url, 'page': 1, 'imdb_id': imdb_id},
                                 callback=self.parse_board)

    def parse_board(self, response):
        threads_table = response.xpath("//*[@class='threads']")
        if threads_table:
            for idx, thread in enumerate(threads_table.xpath("*[contains(@class, 'thread') and not(contains(@class, 'header'))]")):
                url = self.base_url + self.get_xpath(thread, "*[@class='title']/a/@href", 0)
                thread_id = self.get_thread_id(url)
                yield scrapy.Request(url, meta={'thread_id': thread_id, 'page': response.meta['page'] + 1,
                                       'imdb_id': response.meta['imdb_id'],
                                       'url': response.meta['url'], }, callback=self.parse_thread)

            url = response.meta['url'] + self.imdb_board_endpoint + self.imdb_page_del + str(response.meta['page'] + 1)
            yield scrapy.Request(url, meta={'page': response.meta['page'] + 1, 'imdb_id': response.meta['imdb_id'],
                                       'url': response.meta['url'], }, callback=self.parse_board)

    def parse_thread(self, response):
        post_table = response.xpath("//*[starts-with(@class, 'thread')]")
        if post_table:
            thread_id = response.meta['thread_id']
            for idx, thread in enumerate(post_table.xpath("*[contains(@class, 'comment') and not(contains(@class, 'comment-summary'))]")):
                post = self.parse_post(thread)
                if not post:
                    continue
                post['imdb_id'] = response.meta['imdb_id']
                if thread_id != post["id"]:
                    post["reply_id"] = thread_id
                yield post

            url = response.meta['url'] + self.imdb_board_endpoint + self.imdb_thread_del + thread_id + "/" + \
                  self.imdb_page_del + str(response.meta['page'] + 1)
            yield scrapy.Request(url,
                                 meta={'thread_id': thread_id, 'page': response.meta['page'] + 1,
                                       'imdb_id': response.meta['imdb_id'],
                                       'url': response.meta['url'], }, callback=self.parse_thread)

    @staticmethod
    def get_comment_id(id):
        k = id.rfind("-")
        return id[k+1:]

    def parse_post(self, xml):
        post = PostItem()
        user = self.get_xpath(xml, ".//a[contains(@class,'nickname')]/text()", 0)
        if not user:
            return None
        self.set_item(post, "user", user)
        self.set_item(post, "id", self.get_comment_id(self.get_xpath(xml, "@id", 0)))
        self.set_item(post, "title", self.get_xpath(xml, "h2/text()", 0))
        try:
            self.set_item(post, "timestamp", parser.parse(self.get_xpath(xml, ".//span[@class='timestamp']/a/text()", 0)))
        except:
            try:
                self.set_item(post, "timestamp", parser.parse(self.get_xpath(xml, ".//span[@class='timestamp']/span/a/text()", 0)))
            except:
                self.logger.warning("Could not fetch date for object %s", post["id"])
        self.set_item(post, "content", self.get_xpath(xml, ".//div[@class='body']//text()", 0))
        return post

    @staticmethod
    def set_item(item, key, prop):
        if not prop or (hasattr(prop, "__len__") and not len(prop)>0):
            return
        item[key] = prop

    @staticmethod
    def get_xpath(response, path, index):
        parsed = response.xpath(path)
        if parsed:
            striped = [x.strip() for x in parsed.extract()]
            if index < 0 or index > len(striped)-1:
                return striped
            return striped[index]
        return None