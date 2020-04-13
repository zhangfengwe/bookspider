# 常用工具类

from functools import wraps
from os import path, makedirs

import traceback


def singleton(cls):
    """
    单例模式的装饰器函数
    :param cls:
    :return:
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


def exception(logger):
    """
    打印exception信息
    :param: logger
    :return:
    """
    def exception_log(func):
        @wraps(func)
        def log(*args, **kwargs):
            try:
                return func(args, kwargs)
            except Exception:
                logger.error(traceback.format_exc())
        return log
    return exception_log


class FileUtil:

    @staticmethod
    def write(file, source, mode='w', encoding='utf-8'):
        if not path.exists(path.dirname(file)):
            makedirs(path.dirname(file))
        with open(file, mode, encoding=encoding) as f:
            f.write(source)
