# -*- coding: utf-8 -*-

from flask import Flask
from ext import db
import config
from utils import before_first_request_check_db
import logging
import os

conf = os.getenv('STOCK_SET') or 'test'


def create_app(conf):
    app = Flask(__name__)

    # 自定义日志
    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(name)s][%(lineno)s][%(levelname)s]: %(message)s')
    handler.setFormatter(formatter)

    app.log = logging.getLogger()
    app.log.addHandler(handler)
    app.log.setLevel(logging.INFO)

    # 初始化配置
    app.config.from_object(config.setting[conf])

    # 初始化数据库连接字符串
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'mysql://{user}:{password}@{host}:{port}/{database}'.format(
            user=app.config['USER'],
            password=app.config['PASSWORLD'],
            host=app.config['HOST'],
            port=app.config['PORT'],
            database=app.config['DATABASE']))

    db.init_app(app)

    before_first_request_check_db(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/api/stock')

    return app
