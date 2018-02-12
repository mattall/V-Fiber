from settings import DB_PARAMS
import pymysql
from common import get_logger

class DBConnection(object):
    def __init__(self):
        '''
        Initialize DB Class
        '''
        self.__host = DB_PARAMS['address']
        self.__username = DB_PARAMS['username']
        self.__password = DB_PARAMS['password']
        self.__db = DB_PARAMS['database']
        self.__logger = get_logger("DBConnection")
        self.connect()

    def connect(self):
        try:
            self.conn = pymysql.connect(self.__host, \
                                        self.__username, \
                                        self.__password, \
                                        self.__db)
        except (AttributeError, pymysql.OperationalError), e:
            raise e

    def query(self, sql, params = ()):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
        except (AttributeError, pymysql.OperationalError) as e:
            self.__logger.error('Exception generated during DB connection: ', e)
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
        return cursor

    def close(self):
        try:
            if self.conn:
                self.conn.close()
                self.__logger.info('...Closed DB Connection: ' + str(self.conn))
            else:
                self.__logger.info('...No Database Connection to Close.')
        except (AttributeError, pymysql.OperationalError) as e:
            raise e
