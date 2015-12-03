# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from dateutil import parser
from imdbcrawler.items import PostItem


class ImdbSpider(scrapy.Spider):
    name = "ImdbForumCrawler"
    allowed_domains = ["imdb.com"]
    url_bases = ["http://www.imdb.com/"]
    base_url = "http://www.imdb.com"

    client = None
    db = None
    collection_name = None
    from_year = None
    to_year = None

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
                'releaseDate': {'$gte': datetime(self.from_year, 1, 1), '$lte': datetime(self.to_year, 12, 31)},
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
            for idx, thread in enumerate(threads_table.xpath(".//*[contains(@class, 'thread') and not(contains(@class, 'header'))]")):
                url = self.base_url + thread.xpath(".//*[@class='title']/a/@href").extract_first()
                thread_id = self.get_thread_id(url)
                yield scrapy.Request(url, meta={'thread_id': thread_id, 'imdb_id': response.meta['imdb_id'],
                                       'url': response.meta['url'], }, callback=self.parse_thread)

            next = threads_table.xpath("//*[@class='pagination']/a[@class='current']/following-sibling::a[1]/@href")
            if next:
                url = response.urljoin(next.extract_first())
                yield scrapy.Request(url, meta={'imdb_id': response.meta['imdb_id'],
                                           'url': response.meta['url'], }, callback=self.parse_board)

    def parse_thread(self, response):
        posts_table = response.xpath("//*[starts-with(@class, 'thread')]")
        if posts_table:
            thread_id = response.meta['thread_id']
            for idx, thread in enumerate(posts_table.xpath("*[contains(@class, 'comment') and not(contains(@class, 'comment-summary'))]")):
                post = self.parse_post(thread)
                if not post:
                    continue
                post['imdb_id'] = response.meta['imdb_id']
                if thread_id != post["_id"]:
                    post["reply_id"] = thread_id
                yield post
            next = posts_table.xpath("//*[@class='pagination']/a[@class='current']/following-sibling::a[1]/@href")
            if next:
                url = response.urljoin(next.extract_first())
                yield scrapy.Request(url,
                                     meta={'thread_id': thread_id, 'imdb_id': response.meta['imdb_id'],
                                           'url': response.meta['url'], }, callback=self.parse_thread)

    @staticmethod
    def get_comment_id(string):
        k = string.rfind("-")
        return string[k+1:]

    def parse_post(self, xml):
        post = PostItem()
        user = xml.xpath(".//a[contains(@class,'nickname')]/text()").extract_first()
        if not user:
            return None
        self.set_item(post, "user", user)
        self.set_item(post, "_id", self.get_comment_id(xml.xpath("@id").extract_first()))
        self.set_item(post, "title", xml.xpath("h2/text()").extract_first())
        try:
            self.set_item(post, "timestamp",
                          parser.parse(xml.xpath(".//span[@class='timestamp']/a/text()").extract_first()))
        except:
            try:
                self.set_item(post, "timestamp", parser.parse(
                    xml.xpath(".//span[@class='timestamp']/span/a/text()").extract_first()))
            except:
                self.logger.warning("Could not fetch date for object %s", post["id"])
        self.set_item(post, "content", xml.xpath(".//div[@class='body']//text()").extract_first())
        return post

    @staticmethod
    def set_item(item, key, prop):
        if not prop or (hasattr(prop, "__len__") and not len(prop) > 0):
            return
        item[key] = prop
