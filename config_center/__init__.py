# -*- coding: utf-8 -*-
# Created by Hans on 16-5-22

from tornado.web import Application
from tornado.options import options, define
from kazoo.client import KazooClient

define('port', default=8000, type=int, help='Server port')
define('bind', default='0.0.0.0', type=str, help='Server bind')

define('connect', default='127.0.0.1:2181', type=str, help='zookeeper connect')
define('root', default='/conf', type=str, help='zookeeper root')
define('workspace', default='/tmp/workspace', type=str, help='config center workspace')

define('db_host', default='127.0.0.1', type=str, help='Server bind')
define('db_port', default='3306', type=int, help='zookeeper connect')
define('db_user', default='root', type=str, help='zookeeper root')
define('db_password', default='123456', type=str, help='config center workspace')
define('db_schema', default=None, type=str, help='config center workspace')

define('auth_server', default=None, type=str, help='config center workspace')


def make_app(router, **settings):
    app = Application(router, **settings)
    print(options.connect)
    zk = KazooClient(hosts=options.connect)
    setattr(app, 'zk', zk)
    setattr(app, 'options', options)

    return app
