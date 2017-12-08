# -*- coding: utf-8 -*-

import pytest
from flask import url_for
from app import create_app
import json
import os

header = ''

conf = os.getenv('STOCK_SET') or 'test'


@pytest.fixture
def app():
    app = create_app(conf)
    return app


@pytest.fixture
def client(app):
    client = app.test_client()
    return client


def test_commodity_type_add(client):
    """新增商品类型"""
    commodity_type_data = {
        'number': '20170001',
        'name': '测试商品'
    }

    res = client.post(
        url_for('main.commodity_types'), data=commodity_type_data)
    res_data = json.loads(res.data)

    assert 'name' in res_data if res.status_code == 201 else 'message' in res_data


def test_user_add(client):
    """新增用户"""
    user_data = {
        'name': '测试',
        'password': '123456',
        'nickname': 'test',
        'avatar': 'test',
        'phone': 'test'
    }

    res = client.post(url_for('main.users'), data=user_data)
    res_data = json.loads(res.data)

    assert 'name' in res_data if res.status_code == 201 else 'message' in res_data
