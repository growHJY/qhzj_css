import pymysql

from flask import current_app


class MysqlOperation:
    def __init__(self):
        self.conn = None
        self.host = current_app.config['MYSQL_HOST']
        self.port = current_app.config['MYSQL_PORT']
        self.user = current_app.config['MYSQL_USER']
        self.password = current_app.config['MYSQL_PASSWORD']
        self.database = current_app.config['MYSQL_DB']

    def connect(self):
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.database)
        return self.conn

    def disconnect(self):
        self.conn.close()
