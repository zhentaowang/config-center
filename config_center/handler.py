# -*- coding: utf-8 -*-
# Created by Hans on 16-5-22

import time
import os
import shutil
from os import path as os_path
from tornado.web import RequestHandler
from tornado.options import options
from tornado.web import HTTPError
from kazoo.exceptions import NodeExistsError
from config_center.untils import joinPath


class CreateHandler(RequestHandler):
    @staticmethod
    def persistence_conf(filename, content):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'w') as f:
            f.write(content)

    @staticmethod
    def copy_file(src, dst):
        if os.path.isdir(src) and os.path.isdir(dst):
            for f in os.listdir(src):
                if os.path.isfile(joinPath('/', [src, f])):
                    shutil.copy(joinPath('/', [src, f]), joinPath('/', [dst, f]))

    def write_history(self, node, version):
        self.application.zk.ensure_path(joinPath('/', [node, 'history']))
        try:
            node = joinPath('/', [node, 'history'])
            self.application.zk.create(joinPath('/', [node, version]), b'')
        except NodeExistsError:
            raise HTTPError(500, reason='{0} is already exist !')
        except Exception as e:
            raise HTTPError(500, reason=str(e))

    def write_current(self, node, version):
        self.application.zk.ensure_path(joinPath('/', [node, 'current']))
        try:
            node = joinPath('/', [node, 'current'])
            self.application.zk.create(joinPath('/', [node, 'version']), version.encode())
        except NodeExistsError:
            self.application.zk.set(joinPath('/', [node, 'version']), version.encode())
        except Exception as e:
            raise HTTPError(500, reason=str(e))

    def get(self):
        self.render('create.html')

    def post(self):
        appid = self.get_argument('appid')
        conf_name = self.get_argument('conf_name')
        content = self.get_argument('content')
        content = content.replace('\r\n', '\n')
        # 创建节点/conf/emnp/jdbc.properties
        root = '/' + options.root
        node = joinPath('/', [root, appid, conf_name])
        self.application.zk.ensure_path(node)
        try:
            self.application.zk.create(joinPath('/', [node]), content.encode())
        except IndexError:
            pass
        except NodeExistsError:
            # 更新节点
            self.application.zk.set(joinPath('/', [node]), content.encode())
        except Exception as e:
            raise HTTPError(500, reason=str(e))

        # 持久化数据
        version = str(time.strftime("%Y%m%d%H%M%S", time.localtime(time.time())))
        latest_dir = ''
        new_dir = '/'.join([options.workspace, options.root, appid, version])

        path = '/'.join([options.workspace, options.root, appid])
        try:
            dirs = [d for d in os.listdir(path)]
            if dirs:
                latest_dir = joinPath('/', [path, max(dirs)])
                os.makedirs(new_dir)
                CreateHandler.copy_file(latest_dir, new_dir)
        except FileNotFoundError:
            pass

        file_path = '/'.join([new_dir, conf_name])
        CreateHandler.persistence_conf(file_path, content)
        # 写history
        node = '/'.join([root, appid, 'version'])
        self.write_history(node, version)
        # 写current
        self.write_current(node, version)

        self.redirect('/')


class IndexHandler(RequestHandler):
    def get(self):
        """
        test = {
            "app1":{
                "current_version":"2016",
                "history_version":['2015','2016'],
                "conf_files":["app1.conf","app2.conf","app2.conf"]
            },
            "app2": {
                "current_version": "1900",
                "history_version": ['1901', '1900'],
                "conf_files": ["cc1.conf", "cc2.conf", "cc3.conf"]
            }
        }
        """

        data = {}
        node = '/' + options.root
        self.application.zk.ensure_path(node)
        appids = self.application.zk.get_children(node)
        conf_files = None
        for app in appids:
            conf_files = self.application.zk.get_children(joinPath('/', [node, app]))
            conf_files.remove('version')
            current_version, _ = self.application.zk.get(joinPath('/', [node, app, 'version', 'current', 'version']))
            history_version = self.application.zk.get_children(joinPath('/', [node, app, 'version', 'history']))
            data[app] = {
                "current_version": current_version.decode('utf-8'),
                "history_version": history_version,
                "conf_files": conf_files,
            }

        self.render('index.html', apps=data)


class ShowHandler(RequestHandler):
    def get(self, *args, **kwargs):
        content = ''
        data = self.get_argument('data')
        appid, conf_name, current_version = data.split('(')

        path = '/'.join([options.workspace, options.root, appid, current_version, conf_name])
        with open(path) as f:
            content = f.read()

        conf_content = {
            'appid': appid,
            'conf_name': conf_name,
            'content': content
        }
        self.render('show.html', conf_content=conf_content)


class EditHandler(RequestHandler):
    def get(self, *args, **kwargs):
        content = ''
        data = self.get_argument('data')
        appid, conf_name, current_version = data.split('(')

        path = '/'.join([options.workspace, options.root, appid, current_version, conf_name])
        with open(path) as f:
            content = f.read()

        conf_content = {
            'appid': appid,
            'conf_name': conf_name,
            'content': content
        }
        self.render('edit.html', conf_content=conf_content)


class DeleteHandler(RequestHandler):
    def get(self, *args, **kwargs):
        content = ''
        data = self.get_argument('data')
        appid, conf_name, current_version = data.split('(')

        node = joinPath('/', [options.root, appid, conf_name])
        try:
            self.application.zk.delete(node, recursive=True)
        except Exception as e:
            raise HTTPError(500, reason=str(e))

        self.redirect('/')
