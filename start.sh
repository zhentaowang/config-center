#!/usr/bin/env bash
apt install -y --force-yes openssl
pip install kazoo
pip install tornado
pip install pymysql
pip install pycrypto
python /code/app.py