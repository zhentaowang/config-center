#!/usr/bin/env bash
sudo yum install openssl-devel
pip install kazoo
pip install tornado
pip install pymysql
pip install pycrypto
python /code/app.py