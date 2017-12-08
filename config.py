# -*- coding: utf-8 -*-

import os


class Config(object):
    USER = ''
    PASSWORLD = ''
    HOST = '127.0.0.1'
    PORT = 4306
    DATABASE = ''
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True


class TestConfig(Config):
    pass


class ProductionConfig(Config):
    DEBUG = False
    USER = os.getenv('DB_USERNAME')
    HOST = os.getenv('DB_ADDR')
    DATABASE = os.getenv('DB_NAME')
    PASSWORLD = os.getenv('DB_PWD')


setting = {'test': TestConfig, 'production': ProductionConfig}
