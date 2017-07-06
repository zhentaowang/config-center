# -*- coding: utf-8 -*-
# Created by Hans on 16-5-22

from tornado.web import RequestHandler
from tornado.options import options
from tornado.web import HTTPError
from config_center.untils import joinPath
from config_dao import ConfigDao
from app_dao import AppDao
import untils

config_dao = ConfigDao()
app_dao = AppDao()


def auth(p_type, apps, access_token):
    if type(apps) == list:
        for app in apps:
            permission = p_type + app
            permit = untils.auth(access_token, permission)
            if permit:
                return True
    else:
        permission = p_type + apps
        return untils.auth(access_token, permission)


class CreateHandler(RequestHandler):
    # 写数据库，并更新当前版本为可用版本
    def persistence_conf(self, app_name, config_name, content, version, encrypt=False, username=None):
        config_dao.add_config(app_name, config_name, content, version, encrypt=encrypt, config_owner=username)
        config_dao.un_effective_from(app_name, config_name, version)

    def get(self):
        app_name = self.get_argument('data', None)
        self.render('create.html', app_name=app_name)

    def post(self):
        username = self.get_cookie('username', None)
        access_token = self.get_cookie('access_token', None)
        appid = self.get_argument('appid')
        if not auth(untils.Permission['WRITE'], [untils.Permission['APP_ALL'], appid], access_token):
            raise HTTPError(403, reason='Permission deny')
        conf_name = self.get_argument('conf_name')
        content = self.get_argument('content')
        encrypt = self.get_argument('encrypt', False) == 'on'
        content = content.replace('\r\n', '\n')
        root = '/' + options.root
        if encrypt:
            # 获取密钥
            secret_key = app_dao.get_app(appid)[0]['secret_key']
            content = untils.encrypt(content, secret_key)
        # 更新zookeeper
        node = joinPath('/', [root, appid, conf_name])
        self.application.zk.ensure_path(node)
        try:
            if self.application.zk.exists(node):
                self.application.zk.set(joinPath('/', [node]), content.encode())
            else:
                self.application.zk.create(joinPath('/', [node]), content.encode())
        except Exception as e:
            raise HTTPError(500, reason=str(e))
        self.persistence_conf(appid, conf_name, content, untils.version(), encrypt, username)
        self.redirect('/')


class IndexHandler(RequestHandler):
    def get(self):
        username = self.get_cookie('username', [])
        app_names = map(lambda x: x['app_name'], app_dao.get_app(owner=username))
        configs = {}
        if len(app_names) == 0:
            self.render('index.html', apps=configs)
        else:
            for app_name in app_names:
                configs[app_name] = []
            data = config_dao.get_config_by_condition(app_name=app_names, effective=1)
            for config in data:
                app_name = config['app_name']
                configs[app_name].append(config)
            self.render('index.html', apps=configs)


def get_uniq_config(app_name, config_name, version):
    data = config_dao.get_config_by_condition(app_name, config_name, version=version)
    conf_content = {
        'appid': app_name,
        'conf_name': config_name,
        'content': data[0]['config_content'],
        'encrypt': data[0]['encrypt']
    }
    return conf_content


class ShowHandler(RequestHandler):
    def get(self, *args, **kwargs):
        data = self.get_argument('data')
        appid, conf_name, current_version = data.split('(')
        access_token = self.get_cookie('access_token', None)
        if not auth(untils.Permission['READ'], [untils.Permission['APP_ALL'], appid], access_token):
            raise HTTPError(403, reason='Permission deny')
        self.render('show.html', conf_content=get_uniq_config(appid, conf_name, current_version))


class EditHandler(RequestHandler):
    def get(self, *args, **kwargs):
        data = self.get_argument('data')
        appid, conf_name, current_version = data.split('(')
        access_token = self.get_cookie('access_token', None)
        if not auth(untils.Permission['UPDATE'], [untils.Permission['APP_ALL'], appid], access_token):
            raise HTTPError(403, reason='Permission deny')
        self.render('edit.html', conf_content=get_uniq_config(appid, conf_name, current_version))


class DeleteHandler(RequestHandler):
    def get(self, *args, **kwargs):
        data = self.get_argument('data')
        appid, conf_name, current_version = data.split('(')
        access_token = self.get_cookie('access_token', None)
        if not auth(untils.Permission['DELETE'], [untils.Permission['APP_ALL'], appid], access_token):
            raise HTTPError(403, reason='Permission deny')
        # delete from zookeeper
        node = joinPath('/', [options.root, appid, conf_name])
        try:
            self.application.zk.delete(node, recursive=True)
        except Exception as e:
            raise HTTPError(500, reason=str(e))
        # delete from mysql
        config_dao.delete_by_config_name(appid, conf_name)
        self.redirect('/conf')
