import untils
from jdbc_utils import DatabaseHelper


class ConfigDao:
    def __init__(self):
        self.db_executor = DatabaseHelper(host=untils.get_property('db_host'),
                                          port=untils.get_property('db_port'),
                                          user=untils.get_property('db_user'),
                                          password=untils.get_property('db_password'),
                                          schema=untils.get_property('db_schema'))

    def add_config(self, app_name, config_name, config_content, version=None, encrypt=False, config_owner=None):
        if version is None:
            version = untils.version()
        sql = '''
        insert into config(app_name, config_name, config_content, version, encrypt, config_owner) 
        VALUES ('%s', '%s', '%s', '%s', %s, '%s')
        ''' % (app_name, config_name, config_content, version, 1 if encrypt else 0, config_owner)
        self.db_executor.do(sql)

    def get_config_by_condition(self, app_name=None, config_name=None, effective=True, version=None, encrypt=None,
                                config_owner=None):
        sql = '''
        SELECT * FROM config WHERE 1=1
        '''
        if app_name is not None:
            if type(app_name) == list:
                if len(app_name) > 0:
                    sql += ' and app_name in (' + untils.joinPath(',', map(lambda x: '\'' + x + '\'', app_name)) + ')'
            else:
                sql += ' and app_name=\'%s\'' % app_name
        if config_name is not None:
            sql += ' and config_name=\'%s\'' % config_name
        if effective is not None:
            sql += ' and effective=%s' % effective
        if version is not None:
            sql += ' and version=\'%s\'' % version
        if encrypt is not None:
            sql += ' and encrypt=%s' % encrypt
        if config_owner is not None:
            sql += ' and config_owner=\'%s\'' % config_owner
        print sql
        return self.db_executor.do(sql_cmd=sql)

    def delete_by_config_name(self, app_name, config_name):
        sql = '''
        delete from config WHERE app_name='%s' and config_name='%s'
        ''' % (app_name, config_name)
        self.db_executor.do(sql)

    def roll_back_config(self, app_name, config_name, version):
        sql = '''
        update config set effective=0 WHERE app_name='%s' and config_name='%s'
        ''' % (app_name, config_name)
        self.db_executor.do(sql)
        sql = '''
        update config set effective=1 WHERE app_name='%s' and config_name='%s' and version='%s'
        ''' % (app_name, config_name, version)
        self.db_executor.do(sql)

    def un_effective_from(self, app_name, config_name, version):
        sql = '''
        update config set effective=0 WHERE app_name='%s' and config_name='%s' and version<'%s'
        ''' % (app_name, config_name, version)
        print sql
        self.db_executor.do(sql)

    def get_app_of_owner(self, owner):
        if owner is None:
            return []
        sql = '''
        select distinct app_name from config where config_owner='%s'
        ''' % owner
        return map(lambda x: x['app_name'], self.db_executor.do(sql))
