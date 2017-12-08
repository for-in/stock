# -*- coding: utf-8 -*-

from ext import db
from datetime import datetime
from flask_sqlalchemy import sqlalchemy
from utils import format_datetime_str
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


class BaseModel(db.Model):
    __abstract__ = True

    creator_id = db.Column(db.Integer)
    created_time = db.Column(db.DateTime, default=datetime.now)
    modifier_id = db.Column(db.Integer)
    modified_id = db.Column(db.DateTime, default=datetime.now)

    def __init__(self,
                 creator_id=None,
                 modifier_id=None,
                 created_time=None,
                 modified_time=None):
        self.creator_id = creator_id
        self.created_time = created_time
        self.modifier_id = modifier_id
        self.modified_time = modified_time

    def to_json_data(self, fields_list=None, extr=None):
        """返回对象json数据"""
        json_data = {}

        column_list = fields_list or [
            column.name for column in self.__table__.columns
        ]

        for name in column_list:
            v = getattr(self, name, None)
            if isinstance(v, datetime):
                v = format_datetime_str(v)
            if isinstance(v, db.Model):
                v = self.to_json_data()
            json_data[name] = v

        if extr:
            for k in extr:
                json_data[k] = self.extension_data().get(k)

        return json_data

    @classmethod
    def create(cls, **kwargs):
        """创建数据"""
        instance = cls(**kwargs)
        return instance.save()

    @classmethod
    def create_from_dict(cls, d):
        """创建数据"""
        assert isinstance(d, dict)
        instance = cls(**d)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """更新数据"""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """数据保存"""
        db.session.add(self)
        if commit:
            try:
                db.session.commit()
            except Exception, e:
                if isinstance(e, sqlalchemy.exc.IntegrityError):
                    return ({'message': '重复录入', 'log_error': e.message}, 409)
                return ({'message': '录入错误', 'log_error': e.message}, 500)
        return self

    def delete(self, commit=True):
        """数据删除"""
        db.session.delete(self)
        return commit and db.session.commit()


class CommodityType(BaseModel):
    """货品类型"""
    __tablename__ = 'commodity_type'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(30), nullable=False)

    __table_args__ = (db.UniqueConstraint('number', name='type_number'), )

    def __init__(self, number, name, *args, **kwargs):
        self.number = number
        self.name = name
        super(BaseModel, self).__init__(*args, **kwargs)


class CommodityCount(BaseModel):
    """库存数量"""
    __tablename__ = 'commodity_count'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(
        db.String(20), db.ForeignKey('commodity_type.number'), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    __table_args__ = (db.UniqueConstraint('number', name='number'), )

    def __init__(self, number, count, *args, **kwargs):
        self.number = number
        self.count = count
        super(BaseModel, self).__init__(*args, **kwargs)


class InCommodity(BaseModel):
    """入库记录"""
    __tablename__ = 'commodity_in'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(
        db.String(20), db.ForeignKey('commodity_type.number'), nullable=False)
    in_count = db.Column(db.Integer, nullable=False)
    in_time = db.Column(db.DateTime, nullable=False)
    remark = db.Column(db.String(240))

    def __init__(self, number, in_count, in_time, remark=None, *args,
                 **kwargs):
        self.number = number
        self.in_count = in_count
        self.int_time = in_time
        self.remark = remark
        super(BaseModel, self).__init__(*args, **kwargs)


class OutCommodity(BaseModel):
    """出库记录"""
    __tablename__ = 'commodity_out'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(
        db.String(20), db.ForeignKey('commodity_type.number'), nullable=False)
    out_count = db.Column(db.Integer, nullable=False)
    out_time = db.Column(db.DateTime, nullable=False)
    remark = db.Column(db.String(10))

    def __init__(self,
                 number,
                 out_count,
                 out_time,
                 remark=None,
                 *args,
                 **kwargs):
        self.number = number
        self.out_count = out_count
        self.out_time = out_time
        self.remark = remark
        super(BaseModel, self).__init__(*args, **kwargs)


class User(BaseModel):
    """用户"""
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(128))
    nickname = db.Column(db.String(50))
    avatar = db.Column(db.String(255))
    phone = db.Column(db.String(11))

    def __init__(self,
                 name,
                 password,
                 nickname=None,
                 avatar=None,
                 phone=None,
                 *args,
                 **kwargs):
        self.name = name
        self.password = generate_password_hash(password)
        self.nickname = nickname
        self.avatar = avatar
        self.phone = phone
        super(BaseModel, self).__init__(*args, **kwargs)

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)
