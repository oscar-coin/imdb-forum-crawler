import pymongo


class MongoPipeline(object):
    def __init__(self, source_mongo_uri, source_mongo_db, source_collection, source_user, source_password,
                 target_mongo_uri, target_mongo_db, target_collection, target_user, target_password, from_year, to_year):
        self.source_mongo_uri = source_mongo_uri
        self.source_mongo_db = source_mongo_db
        self.source_collection = source_collection
        self.source_user = source_user
        self.source_password = source_password
        self.target_mongo_uri = target_mongo_uri
        self.target_mongo_db = target_mongo_db
        self.target_collection = target_collection
        self.target_user = target_user
        self.target_password = target_password
        self.from_year = from_year
        self.to_year = to_year

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            source_mongo_uri=crawler.settings.get('SOURCE_MONGO_URI'),
            source_mongo_db=crawler.settings.get('SOURCE_MONGO_DATABASE'),
            source_collection=crawler.settings.get('SOURCE_COLLECTION'),
            source_user=crawler.settings.get('SOURCE_USER'),
            source_password=crawler.settings.get('SOURCE_PASSWORD'),
            target_mongo_uri=crawler.settings.get('TARGET_MONGO_URI'),
            target_mongo_db=crawler.settings.get('TARGET_MONGO_DATABASE'),
            target_collection=crawler.settings.get('TARGET_COLLECTION'),
            target_user=crawler.settings.get('TARGET_USER'),
            target_password=crawler.settings.get('TARGET_PASSWORD'),
            from_year=crawler.settings.get('FROM_YEAR'),
            to_year=crawler.settings.get('TO_YEAR'),

        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.target_mongo_uri)
        self.db = self.client[self.target_mongo_db]
        if self.target_user and self.target_password and not self.db.authenticate(self.target_user, self.target_password):
            spider._signal_shutdown(9,0)
            raise "Failed to authenticate to MongoDB database {0} using given username and password!".format(self.source_mongo_uri)

        client = pymongo.MongoClient(self.source_mongo_uri)
        db = client[self.source_mongo_db]
        if self.source_user and self.source_password and not db.authenticate(self.source_user, self.source_password):
            spider._signal_shutdown(9,0)
            raise "Failed to authenticate to MongoDB database {0} using given username and password!".format(self.source_mongo_uri)

        spider.client = client
        spider.db = db
        spider.collection_name = self.source_collection
        spider.from_year = self.from_year
        spider.to_year = self.to_year

    def close_spider(self, spider):
        spider.client.close()
        self.client.close()

    def process_item(self, item, spider):
        if self.db[self.target_collection].find({'_id': item['_id']}, {'_id': 1}).limit(1).count() == 0:
            self.db[self.target_collection].insert(dict(item))
        return item
