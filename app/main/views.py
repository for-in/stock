# -*- coding: utf-8 -*-

from . import main
from flask_restful import reqparse, Api, Resource, current_app as app, fields, marshal_with
from app.models import CommodityType, CommodityCount, InCommodity, OutCommodity, User
from flask_sqlalchemy import sqlalchemy
from flask import url_for
from ext import db
from datetime import datetime
from utils import create_sqlalchemy_text, verify_list, str_format_datetime
# from utils import create_custorm_params, record_recommend_office_data
from functools import partial
from sqlalchemy import func, text

api = Api(main)


class BaseApi(Resource):
    @staticmethod
    def database_type_to_type(_type):
        if isinstance(_type, sqlalchemy.sql.sqltypes.Integer):
            return int
        if isinstance(_type, sqlalchemy.sql.sqltypes.Float):
            return float
        if isinstance(_type, sqlalchemy.sql.sqltypes.String):
            return unicode
        if isinstance(_type, sqlalchemy.sql.sqltypes.Text):
            return unicode
        if isinstance(_type, sqlalchemy.sql.sqltypes.DateTime):
            return partial(str_format_datetime)

    @classmethod
    def parameter_verify(cls, model, method, extr=None):
        """参数检查
            extr:除模型本身字段外的扩展参数
                extr = [
                    {
                        'name': dict(
                            type=str, required=True, location='form')
                    },
                    ...
                ]
        """
        parser = reqparse.RequestParser()

        attrs = [{
            k.name: {
                'type': cls.database_type_to_type(k.type),
                'required': (not k.nullable if method in ['POST'] else False),
                'store_missing': False,
                'location': 'args' if method in ['GET'] else ('json', 'form')
            }
        } for k in model.__table__.columns if k.name != 'id']

        if extr:
            for item in extr:
                attrs.append(item)

        for attr in attrs:
            for k, v in attr.items():
                parser.add_argument(k, **v)

        return parser.parse_args()

    @classmethod
    def create_response_data(cls,
                             model,
                             sql_text_str,
                             sql_params,
                             extr_fields=None):
        """生成响应数据"""
        try:
            data = db.session.query(model).from_statement(
                text(sql_text_str[0] + sql_text_str[1])).params(
                    sql_params).all()

            data_count = db.session.query(model).from_statement(
                text(sql_text_str[0])).params(sql_params).all().__len__()

            res_data = {
                'data': [k.to_json_data(extr=extr_fields) for k in data],
                'total': data_count,
                'sort': sql_params['sort'],
                'order': sql_params['order'],
                'size': sql_params['size'],
                'start': sql_params['start']
            }
        except Exception as e:
            app.log.error('%s' % e.message)
            return ({'message': e.message}, 500)

        return res_data


class CommodityTypeDetail(BaseApi):
    resource_fields = {
        'name': fields.String,
        'number': fields.String,
        'created_time': fields.DateTime(dt_format='iso8601'),
    }
    @marshal_with(resource_fields)
    def get(self, id):
        commodity_type = CommodityType.query.get_or_404(id)
        return commodity_type.to_json_data(), 200


class CommodityTypeList(BaseApi):
    resource_fields = {
        'name': fields.String,
        'number': fields.String,
        'created_time': fields.DateTime(dt_format='iso8601'),
        # 'created_time': fields.String,
    }
    @marshal_with(resource_fields)
    def get(self):
        commodity_types = CommodityType.query.all()
        data = {
            # 'data': [k.to_json_data() for k in commodity_types]
            'data': [k for k in commodity_types]
        }

        return data['data']

    def post(self):
        commodity_type_post = self.parameter_verify(CommodityType, 'POST')
        commodity_type = CommodityType.create(**commodity_type_post)
        if isinstance(commodity_type, tuple):
            return commodity_type
        return commodity_type.to_json_data(), 201


class UserDetail(BaseApi):
    def get(self, id):
        user = User.query.get_or_404(id)
        return user.to_json_data(), 200


class UserList(BaseApi):
    def post(self):
        user_post = self.parameter_verify(User, 'POST')
        user = User.create(**user_post)
        if isinstance(user, tuple):
            return user
        return user.to_json_data(), 201

api.add_resource(
    CommodityTypeDetail, '/commodity_types/<int:id>', endpoint='commodity_type')
api.add_resource(
    CommodityTypeList, '/commodity_types', endpoint='commodity_types')
api.add_resource(UserDetail, '/users/<int:id>', endpoint='user')
api.add_resource(UserList, '/users', endpoint='users')
