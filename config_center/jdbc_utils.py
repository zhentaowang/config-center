# coding=utf-8
import logging
import pymysql

logger = logging.getLogger(__name__)


class DatabaseHelper:
    def __init__(self, host, port, user, password, schema=None, charset='utf8mb4'):
        self.connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=schema,
            charset=charset,
            cursorclass=pymysql.cursors.DictCursor)

    # sql_cmd: str, 需要执行的SQL语句，带转换符
    # data: list of list, 转换符对应的数据，第一维个数是批量执行数，第二维个数必须与转换符个数相等
    #       None表示没有转换符，空list表示没有需要执行的操作
    def do(self, sql_cmd, data=None):
        logger.debug(sql_cmd)
        # 空串，直接返回
        if data is not None and not data:
            return []

        retry = 0
        while retry < 3:
            try:
                with self.connection.cursor() as cursor:
                    # print('Database.do, data len: '+str(len(data)))
                    if data:  # 非空串
                        cursor.executemany(sql_cmd, data)
                    else:  # 没有转换符
                        cursor.execute(sql_cmd)

                    self.connection.commit()
                    return cursor.fetchall()
            except pymysql.err.OperationalError as e:
                self.connection.close()
                self.connection.connect()
                retry += 1
                logger.warning(repr(e) + ', retry %d' % retry)
