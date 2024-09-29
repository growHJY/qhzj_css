import pymysql


class MysqlOperation:
    def __init__(self):
        self.conn = None

        self.host = 'localhost'
        self.port = 3306
        self.user = 'root'
        self.password = '12345678'
        self.database = 'kf_sys'

    def connect(self):
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.database)
        return self.conn

    def disconnect(self):
        self.conn.close()
