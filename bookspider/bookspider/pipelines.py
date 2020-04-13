# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
import re

from bookspider.items import BookContent, BookInfo
from bookspider.util import BOOK_NO_CHAPTER_RE


class BookSpiderPipeline(object):

    # clients存放MongoClient 格式{数据库名：对应MongoClient}
    # db_server存放mongodb数据库连接 格式{数据库名：数据库连接}
    # 支持多个mongodb数据库，同时支持校验密码

    def __init__(self, *args):
        self.db_configs = [db_config for db_config in args]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.getdict('MONGODB_DB_STORY'),
        )

    def open_spider(self, spider):
        self.logger = spider.logger
        self.db_server = {}
        self.clients = {}
        for db_config in self.db_configs:
            self.clients[db_config['db']] = MongoClient(host=db_config['host'], port=db_config['port'])
            self.db_server[db_config['db']] = self.clients[db_config['db']][db_config['db']]
            if db_config['auth']:
                self.db_server[db_config['db']].authenticate(db_config['user'], db_config['password'])

    def close_spider(self, spider):
        for client in self.clients.values():
            client.close()

    def process_item(self, item, spider):
        if isinstance(item, BookInfo):
            # 处理BookInfo
            self.process_book_inf(item, spider)
        elif isinstance(item, BookContent):
            # 处理BookContent
            self.process_book_content(item, spider)
        else:
            raise TypeError('{} 类型错误'.format(type(item)))

    def process_book_inf(self, item, spider):
        book_inf, book_img = self.split(dict(item))
        if not self.db_server['story'].book_inf.find({'book_no': book_inf['book_no']}).count():
            spider.logger.info('{} 基本信息入库'.format(book_inf['book_name']))
            self.db_server['story'].book_inf.insert_one(book_inf)
        if not self.db_server['story'].book_img.find({'book_no': book_inf['book_no']}).count():
            self.db_server['story'].book_img.insert_one(book_img)

    def process_book_content(self, item, spider):
        book_no = re.search(BOOK_NO_CHAPTER_RE, item['chapter_url'])['book_no']
        table_name = 'content_' + book_no
        self.db_server['story'][table_name].update(
            {'chapter_code': item['chapter_code']},
            {'$set': dict(item)},
            upsert=True
        )

    @staticmethod
    def split(source):
        """
        分解BookInfo
        :param source:
        :return:
        """
        try:
            book_img = {k: source[k] for k in ['book_img_url', 'book_no']}
            source.pop('book_img_url')
            return source, book_img
        except Exception as e:
            raise e
