# url去重工具类

from bookspider.util import BLOOMFILTER_BIT, BLOOMFILTER_BLOCK_NUM, BLOOMFILTER_HASH_NUM

import redis


class HashMap(object):
    def __init__(self, m, seed):
        self.m = m
        self.seed = seed

    def hash(self, value):
        """
        Hash Algorithm
        :param value: Value
        :return: Hash Value
        """
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.m - 1) & ret


class BloomFilter(object):

    def __init__(self, server, bit=BLOOMFILTER_BIT, block_num=BLOOMFILTER_BLOCK_NUM, hash_num=BLOOMFILTER_HASH_NUM):
        self.server = server
        self.size = 1 << bit
        self.block_num = block_num
        self.seeds = range(hash_num)
        self.functions = [HashMap(self.size, seed) for seed in self.seeds]

    def exits(self, key, value):
        """
        判断是否存在
        :param key:
        :param value:
        :return:
        """
        if not key or not value:
            return False
        exits = True
        key = key + ':' + str(int(value[:2], 16) % self.block_num)
        for function in self.functions:
            offest = function.hash(value)
            exits = exits & self.server.getbit(key, offest)
        return exits

    def add(self, key, value):
        """
        添加
        :param key:
        :param value:
        :return:
        """
        if not key:
            raise KeyError('{} key is error'.format(key))
        if not value:
            raise KeyError('{} value is error'.format(value))
        key = key + ':' + str(int(value[:2], 16) % self.block_num)
        for function in self.functions:
            offest = function.hash(value)
            self.server.setbit(key, offest, 1)


if __name__ == '__main__':
    pool = redis.ConnectionPool()
    server = redis.Redis(connection_pool=pool, host='127.0.0.1', port=6379, db=1)
    # 暂时采取默认参数
    bloom_filter = BloomFilter(server)
    # bloom_filter.add('test', '1001')
    if bloom_filter.exits('test', '1001'):
        print(True)
    else:
        print(False)
