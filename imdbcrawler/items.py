# -*- coding: utf-8 -*-

from scrapy.item import Item, Field

class PostItem(Item):
    _id = Field()
    title = Field()
    imdb_id = Field()
    user = Field()
    content = Field()
    timestamp = Field()
    reply_id = Field()
