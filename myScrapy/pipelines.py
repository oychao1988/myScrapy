# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

import pymongo

from myScrapy import settings


class JsonWriterPipeline(object):
    def __init__(self):
        self.file = codecs.open('items.json', 'wb', encoding='utf-8')
        self.file.write('[')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + ',\n'
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.write(']')
        self.file.close()


class MongoPipeline(object):
    # def __init__(self):
    #     self.collection_name = None
    #     self.mongo_uri = settings.MONGO_URI
    #     self.mongo_db = settings.MONGO_DB
    #     self.user = settings.MONGO_USER
    #     self.pwd = settings.MONGO_PWD
    #
    # def open_spider(self, spider):
    #     self.client = pymongo.MongoClient(self.mongo_uri)
    #     # 用户登录验证
    #     self.client.scrapydb.authenticate(self.user, self.pwd)
    #     self.db = self.client[self.mongo_db]
    #
    # def process_item(self, item, spider):
    #     self.db[self.collection_name].insert(dict(item))
    #     return item
    #
    # def close_spider(self, spider):
    #     self.client.close()
    pass

class LagouMongoPipeline(MongoPipeline):
    def __init__(self):
        super(LagouMongoPipeline, self).__init__()
        self.collection_name = settings.MONGO_COLL_LAGOU


class TencentMongoPipeline(MongoPipeline):
    def __init__(self):
        super(TencentMongoPipeline, self).__init__()
        self.collection_name = settings.MONGO_COLL_TENCENT


class ZhilianMongoPipeline(MongoPipeline):
    def __init__(self):
        super(ZhilianMongoPipeline, self).__init__()
        self.collection_name = settings.MONGO_COLL_ZHILIAN
