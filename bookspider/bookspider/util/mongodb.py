# mongodb工具类


class Connect(object):

    def __init__(self, *dbs):
        self.dbs = dbs

    @classmethod
    def from_crawler(cls, crawler):
        connect = cls()
        cls.configs = {db: crawler.settings.get('MONGODB_' + db.upper())
                       for db in connect.dbs}
        return connect
