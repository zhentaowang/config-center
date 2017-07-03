from tornado.web import RequestHandler
from app_dao import AppDao
from tornado.web import HTTPError
import untils

app_dao = AppDao()


class CreateAppHandler(RequestHandler):
    def post(self):
        username = self.get_cookie('username', None)
        access_token = self.get_cookie('access_token', None)
        if not untils.auth(access_token, 'create_app'):
            raise HTTPError(403, reason='Permission deny:create_app')
        app_name = self.get_argument('appName')
        secret_key = self.get_argument('secretKey', None)
        app_dao.add_app(app_name, secret_key, username)
        self.redirect('/')
