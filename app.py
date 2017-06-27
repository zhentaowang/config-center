# -*- coding: utf-8 -*-
# Created by Hans on 16-5-22

import os
from tornado.options import options
from tornado.ioloop import IOLoop
from config_center import make_app
from config_center import handler
from config_center import app_handler

router = [
    (r'/createApp', app_handler.CreateAppHandler),
    (r'/', handler.IndexHandler),
    (r'/create', handler.CreateHandler),
    (r'/edit', handler.EditHandler),
    (r'/show', handler.ShowHandler),
    (r'/delete', handler.DeleteHandler),
]
if __name__ == '__main__':
    template_path = os.path.join(os.path.dirname(__file__), "templates")
    static_path = os.path.join(os.path.dirname(__file__), "static")
    app = make_app(router, template_path=template_path, static_path=static_path, debug=True)
    app.listen(options.port, address=options.bind)

try:
    app.zk.start()
    IOLoop.current().start()
except KeyboardInterrupt:
    app.zk.stop()
    IOLoop.current().stop()
