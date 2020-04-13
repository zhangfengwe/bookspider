# -*- coding: utf-8 -*-
import scrapy
import re
from os import path
from concurrent.futures import ThreadPoolExecutor

from bookspider.items import BookContent, BookInfo
from bookspider.util.common import FileUtil
from bookspider.util import BOOK_NO_RE, CHAPTER_CODE_RE, BOOK_ABS_URL_RE, BOOK_REL_URL_RE
from bookspider.settings import BASE_PATH


class BookSpider(scrapy.Spider):

    name = 'book'
    allowed_domains = ['www.booktxt.net']
    start_urls = ['https://www.booktxt.net']

    log = None

    def __init__(self):
        super().__init__()
        self.book_href = set()
        # 用于存放各个小说的chapter_no,形式book_no_chapter:chapter_no
        # 后期可考虑存放在redis中，做持久化处理
        # self._param_dict = {}
        # 因小说章节顺序问题

    def parse(self, response):
        href_list = response.xpath('//a/@href').getall()
        for href in href_list:
            checked, href = self.check_url(href)
            if checked:
                if href in self.book_href:
                    break
                self.book_href.add(href)
                self.logger.info('爬取小说主页url:{}'.format(href))
                yield scrapy.Request(href, meta={'depth': 0}, callback=self.parse_book)
            else:
                self.logger.info('爬取其他url{}'.format(href))
                yield response.follow(href, callback=self.parse)

    def parse_book(self, response):
        """
        解析小说主页
        :param response:
        :return:
        """
        book = self.get_book_inf(response)
        chapter_list = response.xpath('//div[@id="list"]/dl/dt[2]/following-sibling::dd/a/@href').getall()
        param_dict = {'book_no': book['book_no']}
        chapter_no_list = []
        for chapter in chapter_list:
            chapter_no_list.append(chapter[:-5])
            yield response.follow(chapter, meta={'param_dict': param_dict}, callback=self.parse_chapter)
        book['chapter_no_list'] = chapter_no_list
        yield book
        self.logger.info('{} 基本信息解析完成'.format(book['book_name']))

    def parse_chapter(self, response):
        """
        解析小说章节内容
        :param response:
        :return:
        """
        if response.status == 200:
            book_content = self.get_chapter(response)
            book_no = response.meta['param_dict']['book_no']
            with ThreadPoolExecutor(max_workers=2) as pool:
                file = path.join(BASE_PATH, 'data/source/', book_no, str(book_content['chapter_code']) + '.html')
                pool.submit(FileUtil.write, file, response.text)
            yield book_content
            self.logger.info('小说章节{}爬取解析成功'.format(response.url))

    def get_book_inf(self, response):
        """
        解析html生成BookInf
        :param response:
        :return:
        """
        book = BookInfo()
        book['book_url'] = response.xpath('//meta[@property="og:novel:read_url"]/@content').get()
        book['book_author'] = response.xpath('//meta[@property="og:novel:author"]/@content').get()
        book['book_name'] = response.xpath('//meta[@property="og:novel:book_name"]/@content').get()
        book['book_type'] = response.xpath('//meta[@property="og:novel:category"]/@content').get()
        book['book_introduce'] = response.xpath('//meta[@property="og:description"]/@content').get()
        book['book_status'] = response.xpath('//meta[@property="og:novel:status"]/@content').get()
        book['book_no'] = re.search(BOOK_NO_RE, book['book_url'])['book_no']
        book['book_img'] = path.join(BASE_PATH, 'data/img/') + book['book_no'] + '.jpg'
        book['book_img_url'] = response.xpath('//div[@id="fmimg"]/img/@src').get()

        return book

    def get_chapter(self, response):
        """
        解析html生成BookContent
        :param response:
        :return:
        """
        chapter = BookContent()
        chapter['chapter_name'] = response.xpath('//div[@class="bookname"]/h1/text()').get()
        # chapter['chapter_no'] = self._param_dict.get(response.meta['param_dict'].get('book_no'))
        chapter['chapter_url'] = response.url
        chapter['chapter_code'] = re.search(CHAPTER_CODE_RE, response.url)['chapter_code']
        content = response.xpath('//div[@id="content"]/text()').getall()
        chapter['chapter_content'] = ''.join([line.replace('\xa0', '') for line in content
                                              if line != '\n' and '（本章未完，请翻页）' not in line])
        return chapter

    @staticmethod
    def check_url(url):
        """
        校验url是否为小说主页
        :param url:
        :return:
        """
        if not url:
            return False, url
        if re.match(BOOK_REL_URL_RE, url):
            return True, BookSpider.start_urls[0] + url
        if re.match(BOOK_ABS_URL_RE, url):
            return True, url
        return False, url

