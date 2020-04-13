# util包

# 从小说主页url中提取book_no
BOOK_NO_RE = r'^https://www.booktxt.net/[0-9]*_(?P<book_no>[0-9]*)'
# 从小说章节url中提取book_no
BOOK_NO_CHAPTER_RE = r'^https://www.booktxt.net/[0-9]*_(?P<book_no>[0-9]*)/[0-9]*\.html$'
# 从小说章节url中提取chapter_code
CHAPTER_CODE_RE = r'^https://www.booktxt.net/[0-9]*_[0-9]*/(?P<chapter_code>[0-9]*)\.html$'

# 匹配小说章节url
BOOK_CHAPTER_URL_RE = r'^https://www.booktxt.net/[0-9]*_[0-9]*/[0-9]*.html$'
# 匹配小说主页url--绝对路径--兼容url末尾字符不为/
BOOK_ABS_URL_RE = r'^https://www.booktxt.net/[0-9]*_[0-9]*'
# 匹配小说主页url--相对路径
BOOK_REL_URL_RE = r'^/[0-9]*_[0-9]*'

# bloomfilter默认大小
BLOOMFILTER_BIT = 30

# bloomfilter默认字符串块
BLOOMFILTER_BLOCK_NUM = 2

# bloomfilter默认hash方法个数
BLOOMFILTER_HASH_NUM = 5

__all__ = ['BOOK_NO_RE', 'BOOK_NO_CHAPTER_RE', 'CHAPTER_CODE_RE', 'BOOK_CHAPTER_URL_RE',
           'BLOOMFILTER_BIT', 'BLOOMFILTER_BLOCK_NUM', 'BLOOMFILTER_HASH_NUM', 'BOOK_ABS_URL_RE', 'BOOK_REL_URL_RE']

if __name__ == '__main__':
    pass
