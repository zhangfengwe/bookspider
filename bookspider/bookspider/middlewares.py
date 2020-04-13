# -*- coding: utf-8 -*-

from scrapy import signals
import random
import redis
import re
import traceback
from scrapy.utils.request import request_fingerprint
from scrapy.exceptions import IgnoreRequest

from .util import BOOK_CHAPTER_URL_RE
from .util.urlfilter import BloomFilter


class BookSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class BookDownloaderMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class UserAgentDownloaderMiddleware(object):

    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.get('USER_AGENTS')
        )

    def process_request(self, request, spider):
        request.headers.setdefault(b'User-Agent', random.choice(self.agents))
        return None


class UrlFilterDownloaderMiddleware(object):

    def __init__(self, host, port, db, password=None):
        self.pool = redis.ConnectionPool(host=host, port=port, db=db,)
        if password:
            self.server = redis.Redis(connection_pool=self.pool, password=password)
        else:
            self.server = redis.Redis(connection_pool=self.pool)
        # 页面数量量级较小
        self.bloom_filter = BloomFilter(self.server, bit=15)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.get('REDIS_HOST'),
            crawler.settings.get('REDIS_PORT'),
            crawler.settings.getint('REDIS_DB'),
            crawler.settings.get('REDIS_PASSWORD')
        )

    def process_request(self, request, spider):
        """
        url去重处理
        只针对小说章节url进行重复判断
        :param request:
        :param spider:
        :return:
        """
        if re.match(BOOK_CHAPTER_URL_RE, request.url) and self.bloom_filter.exits(
                spider.name, request_fingerprint(request)):
            raise IgnoreRequest('重复url: {}'.format(request.url))
        return None

    def process_response(self, request, response, spider):
        """
        持久化去重，对爬取成功的小说章节url,记录其figerprint
        :param request:
        :param response:
        :param spider:
        :return:
        """
        if re.match(BOOK_CHAPTER_URL_RE, request.url) and response.status == 200:
            self.bloom_filter.add(spider.name, request_fingerprint(request))
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, IgnoreRequest):
            spider.logger.info(exception)
        else:
            spider.logger.error(traceback.format_exc())
