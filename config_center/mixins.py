# -*- coding: utf-8 -*-
# Created by Hans on 16-5-22

import json
from tornado.web import HTTPError


class RestMixin:
    def jsonify(self, **kwargs):
        """ 将python数据转化为json数据,返回给浏览器 """

        self.set_header('content-type', 'application/json')
        self.write(json.dumps(kwargs))

    def get_payload(self):
        """ 将json类型数据转化为python类型数据 """

        try:
            return json.loads(self.request.body.decode())
        except Exception as e:
            raise HTTPError(400, log_message=str(e))

    def _handle_request_exception(self, e):
        """ 处理请求异常，并将异常信息返回给浏览器 """

        if isinstance(e, HTTPError):
            self.set_status(e.status_code, reason=e.reason)
            self.jsonify(code=e.status_code, message=e.reason)
            self.finish()
            return

        self.set_status(500, reason=str(e))
        self.jsonify(code=e.status_code, message=str(e), exception=e.__class__)
