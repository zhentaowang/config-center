import untils
from jdbc_utils import DatabaseHelper


class AppDao:
    def __init__(self):
        self.db_executor = DatabaseHelper(host=untils.get_property('db_host'),
                                          port=untils.get_property('db_port'),
                                          user=untils.get_property('db_user'),
                                          password=untils.get_property('db_password'),
                                          schema=untils.get_property('db_schema'))

    def add_app(self, app_name, secret_key=None, owner=None):
        sql = '''
        insert into app(app_name, secret_key, owner) VALUES ('%s', '%s', '%s')
        ON DUPLICATE KEY UPDATE secret_key=(secret_key), owner=(owner)
        ''' % (app_name, secret_key, owner)
        self.db_executor.do(sql)

    def get_app(self, app_name=None, owner=None):
        sql = '''
        SELECT * FROM app WHERE 1=1
        '''
        if app_name is not None:
            sql += " and app_name='%s'" % app_name
        if owner is not None:
            sql += " and owner='%s'" % owner
        return self.db_executor.do(sql)
