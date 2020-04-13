# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookInfo(scrapy.Item):

    """
    小说基本信息类
    """
    # 作者
    book_author = scrapy.Field()
    # 编号
    book_no = scrapy.Field()
    # 名称
    book_name = scrapy.Field()
    # 所属分类
    book_type = scrapy.Field()
    # 主页url
    book_url = scrapy.Field()
    # 简介
    book_introduce = scrapy.Field()
    # 当前状态
    book_status = scrapy.Field()
    # 封面图片本地路径
    book_img = scrapy.Field()
    # 封面图片源地址
    book_img_url = scrapy.Field()
    # 小说章节编号列表，按先后顺序存储
    chapter_no_list = scrapy.Field()


class BookContent(scrapy.Item):

    """
    小说章节内容类
    """
    # 章节名
    chapter_name = scrapy.Field()
    # 章节内容
    chapter_content = scrapy.Field()
    # 章节url
    chapter_url = scrapy.Field()
    # 章节源编号
    chapter_code = scrapy.Field()
