# Created by cxy on 15/1/18 with PyCharm
# -*- coding: utf-8 -*-
from config import config
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from ..models.operations import Model
from flask import jsonify, request
from functools import wraps
import re


def gen_token(user, expiration=1440*31*60):  # 默认过期时间为60000s, 即1000min 1day=1440min
    s = Serializer(config.SECRET_KEY, expires_in=expiration)
    return s.dumps({'id': user.id})


def verify_token(token):
    s = Serializer(config.SECRET_KEY)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return 'expired token'
    except BadSignature:
        return 'useless token'
    model = Model()
    return model.get_user_by_id(data['id'])


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.form['token']
        s = Serializer(config.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return jsonify({'status': 'fail', 'data': {'msg': 'expired token'}})
        except BadSignature:
            print token
            return jsonify({'status': 'fail', 'data': {'msg': 'useless token'}})
        kwargs['user_id'] = data['id']
        return func(*args, **kwargs)
    return wrapper


def is_valid_email_pwd(email, pwd='pwd'):
    if not email or not pwd:
        return False
    if '@' not in email:
        return False
    return True


def is_valid_email(email):
    if '@' not in email:
        return False
    return True


def get_user_by_token(token):
    res = verify_token(token)
    if res == 'expired token' or res == 'useless token':
        return dict(status='fail', data={'msg': res})
    else:
        return res


def to_json(data, success=False):
    if success:
        return jsonify({'status': 'success', 'data': data})
    msg = data
    return jsonify({'status': 'fail', 'data': {'msg': msg}})


def is_time_fmt_ok(time_str_list):
    pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    for time_str in time_str_list:
        if not pattern.match(time_str):
            return False
    return True


def check_aff_group_exist(aff_group):
    if not aff_group:
        print aff_group, '...'
        return to_json('affair group not exist')


def check_aff_group_access(aff_group, user_id):
    if aff_group.user_id != user_id:
        if aff_group.is_private:
            return to_json('no access')