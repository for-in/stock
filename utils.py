# -*- coding: utf-8 -*-


from ext import db
import re
import json
from datetime import datetime, timedelta
from aniso8601 import parse_datetime
import time


def db_init(app):
    """命令行数据库初始化"""
    with app.app_context():
        db.create_all()


def before_first_request_check_db(app):
    """数据库初始化"""
    @app.before_first_request
    def db_check():
        db.create_all()


def format_datetime_str(date_time):
    """时间格式化"""
    date_time_str = '{}T{}.000+08:00'.format(
        date_time.strftime('%Y-%m-%d'), date_time.strftime('%H:%M:%S'))

    return date_time_str


def str_format_datetime(date_time_str):
    """字符串转时间"""
    try:
        datetime_zone = parse_datetime(date_time_str)
        time_stamp = time.mktime(datetime_zone.timetuple())
        date_time = datetime.fromtimestamp(time_stamp)
        if datetime_zone.tzinfo.__str__() == '+0:00:00 UTC':
            date_time = date_time + timedelta(hours=8)
    except:
        raise ValueError('datetime string is invalid')

    return date_time


def verify_list(list_str):
    """验证list"""
    try:
        new_list = json.loads(list_str)
    except:
        raise ValueError('list is invalid json string')

    if new_list == []:
        raise ValueError('list can`t empty')

    return new_list


def create_sqlalchemy_text(table, params, extr={}):
    """生成sql text
       extr = {
           'field': (transform_field, operaotr)
           }
    """

    def transform(field):
        t_f = extr.get(field)
        if t_f:
            return t_f
        return None

    def create_condition(par_key, operaotr, field):
        tf = transform(field)
        if tf:
            cond = '{expr} {op} {value}'.format(
                expr=tf[0], op=tf[1], value=':{e_v}'.format(
                    e_v=par_key))  # 当field需要转换时,传入的operator失效
        else:
            cond = '{expr} {op} {value}'.format(
                expr=field, op=operaotr, value=':{f_v}'.format(
                    f_v=par_key))
        return cond

    def match_params(params):
            if re.match(r'(.*)(LessThanOrEquals)', k):
                field = re.match(r'(.*)(LessThanOrEquals)', k).group(1)
                return field, '<='
            elif re.match(r'(.*)(GreaterThanOrEquals)', k):
                field = re.match(r'(.*)(GreaterThanOrEquals)', k).group(1)
                return field, '>='
            elif re.match(r'(.*)(LessThan)', k):
                field = re.match(r'(.*)(LessThan)', k).group(1)
                return field, '<'
            elif re.match(r'(.*)(GreaterThan)', k):
                field = re.match(r'(.*)(GreaterThan)', k).group(1)
                return field, '>'
            elif re.match(r'(.*)(Like)', k):
                field = re.match(r'(.*)(Like)', k).group(1)
                return field, 'like'
            elif re.match(r'(.*)(In)', k):
                field = re.match(r'(.*)(In)', k).group(1)
                return field, 'in'
            elif k in ['sort', 'order', 'size', 'start']:
                return None
            else:
                return params, '='

    if params:
        condition = []
        for k in params.keys():
            if k in extr:           # 当k在extr中需要转换时不进行匹配
                m_r = k, '='
            else:
                m_r = match_params(k)
            if m_r:
                field = m_r[0]
                operator = m_r[1]
                cond = create_condition(k, operator, field)
                condition.append(cond)

        if condition:
            where_condition = ' and '.join(condition)
            text = '''
                select *
                from
                    {tb_name}
                where
                    {condition}
            '''.format(
                tb_name=table, condition=where_condition)
        else:
            text = '''
                select *
                from
                    {tb_name}
            '''.format(tb_name=table)

        sort_limit = """
            order by {sort} {order} limit :start_index,:size
        """.format(sort=params['sort'], order=params['order'])

        return text, sort_limit


def get_excel_field_index(w_s, field_type):
    """获取excel数据表字段column index"""
    field_index = {}
    for row in w_s.iter_rows(min_row=1, max_row=1):
        for col in row:
            for k, v in field_type.items():
                if col.value == v:
                    field_index[k] = col.column - 1
    return field_index


def format_excel_to_model_data(data):
    """格式化excel数据"""
    format_data = {k: v for k, v in data.items()}
    for k, v in data.items():
        if k in ['longitude', 'latitude']:
            if v:
                try:
                    r_v = re.match(ur'\D*(\d+\.\d+)', str(v))
                except Exception:
                    r_v = None
            else:
                r_v = None
            if r_v:
                format_data[k] = float(r_v.group(1))
            else:
                format_data[k] = None
        elif k in ['totalFloor', 'elevator']:
            r_v = re.match(ur'(\d+)\D*', v)
            if r_v:
                format_data[k] = int(r_v.group(1))
            else:
                format_data[k] = None
        elif k in ['roomRate', 'greenRate']:
            if isinstance(v, float):
                format_data[k] = 100 * v
            else:
                format_data[k] = None
        elif k in ['levelHigh']:
            r_v = re.match(ur'(\d.*\d)\D*', v)
            if r_v:
                format_data[k] = float(r_v.group(1))
            else:
                r_v = re.match(ur'(\d)\D*', v)
                if r_v:
                    format_data[k] = float(r_v.group(1))
                else:
                    format_data[k] = None
        elif k in ['floorArea', 'buildingArea']:
            r_v = re.match(ur'(\d.*\d)', v)
            if r_v:
                format_data[k] = float(r_v.group(1))
            else:
                r_v = re.match(ur'(\d+)', v)
                if r_v:
                    format_data[k] = r_v.group(1)
                else:
                    format_data[k] = None
        else:
            format_data[k] = v

    return format_data


def create_custorm_params(params_list):
    """生成自定义参数
       params_list: [{'params': params_type}, ...]
    """
    custom_params = [
        {
            'sort': dict(
                type=str, required=False, location='args', default='id')
        },
        {
            'order': dict(
                type=str, required=False, location='args', default='asc')
        },
        {
            'start': dict(
                type=int, required=False, location='args', default=0)
        },
        {
            'size': dict(
                type=int, required=False, location='args', default=10)
        }
    ]

    params = [
        {
            k['name']: dict(type=k['_type'], required=False, location='args',
                            store_missing=False)
        } for k in params_list
    ]

    custom_params.extend(params)

    return custom_params
