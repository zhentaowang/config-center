#-*- coding: utf-8 -*-
#Created by Hans on 16-5-22

import os
from tornado.options import options
from tornado.ioloop import IOLoop
from config_center import make_app

from config_center.handler import IndexHandler,CreateHandler,ShowHandler,EditHandler,DeleteHandler

router = [
    (r'/', IndexHandler),
    (r'/create',CreateHandler),
    (r'/edit', EditHandler),
    (r'/show',ShowHandler),
    (r'/delete',DeleteHandler),
]


if __name__ == '__main__':
    if os.path.exists('/etc/confcenter-api.conf'):
        options.parse_config_file('/etc/confcenter-api.conf')
    if os.path.exists('/code/confcenter.conf'):
        options.parse_config_file('/code/confcenter.conf')
    if os.path.exists('./confcenter.conf'):
        options.parse_config_file('./confcenter.conf')
    options.parse_command_line()

    template_path = os.path.join(os.path.dirname(__file__), "templates")
    static_path = os.path.join(os.path.dirname(__file__), "static")
    app = make_app(router,template_path=template_path,static_path=static_path,debug=True)
    app.listen(options.port,address=options.bind)

    try:
        app.zk.start()
        IOLoop.current().start()
    except KeyboardInterrupt:
        app.zk.stop()
        IOLoop.current().stop()