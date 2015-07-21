# Created by cxy on 15/1/18 with PyCharm
# -*- coding: utf-8 -*-
from . import *
from app import app
from ..utils.utils import token_required, is_valid_email_pwd, to_json, gen_token, is_valid_email
from ..models.operations import Model
from ..models.model import User, UserInfo, UserAffGroupRel


@app.route("/")
def index():
    return app.config['HELLO_STRING']


@app.route("/api/signup", methods=['POST'])
def signup():
    model = Model()
    email = request.form['email']
    pwd = request.form['pwd']
    if not is_valid_email_pwd(email, pwd):
        return to_json('invalid email or password')
    else:
        new_user = model.add_user(email, pwd)
        if new_user != 'user exists':
            # 创建用户默认事务组
            dft_aff_group = model.add_aff_group("默认事务组", new_user.id)
            user_aff_group_rel = UserAffGroupRel(new_user.id, dft_aff_group.id)
            model.session.add(user_aff_group_rel)
            model.session.commit()
            # 添加用户详细信息
            model.add_user_info(new_user.id, dft_aff_group.id, nickname=email)  # 创建用户时用户的昵称为其邮箱
            data = dict(user_id=new_user.id, dft_aff_group_id=dft_aff_group.id)
            return to_json(data, success=True)
        else:
            return to_json('user exists')


@app.route("/api/login", methods=['POST'])
def login():
    email = request.form['email']
    pwd = request.form['pwd']
    if not is_valid_email_pwd(email, pwd):
        return to_json('invalid email or password')

    model = Model()
    user = model.get_user_by_email_pwd(email, pwd)
    if not user:
        return to_json('wrong email or password')
    user_info = model.session.query(UserInfo).filter_by(user_id=user.id).first()
    print user_info.data()
    print user.id

    token = gen_token(user)
    data = dict(token=token)
    data.update(user_info.data())
    print data
    return to_json(data, success=True)


@app.route("/api/suicide", methods=['POST'])
@token_required
def suicide():
    pass


@app.route('/api/checkEmail', methods=['GET'])
def check_email_exist():
    email = request.args['email']
    if not is_valid_email(email):
        return to_json('invalid email')
    model = Model()
    user = model.session.query(User).filter_by(email=email).first()
    if user:
        return to_json('exist')
    return to_json('', success=True)


@app.errorhandler(404)
def handle_404(error):
    return jsonify({'status': 'fail', 'data': {'msg': '404 not found'}})


@app.errorhandler(403)
def handle_403(error):
    return jsonify({'status': 'fail', 'data': {'msg': '403 forbidden'}})


@app.errorhandler(405)
def handle_405(error):
    return jsonify({'status': 'fail', 'data': {'msg': '405 method not allowed'}})


@app.errorhandler(500)
def handle_500(error):
    return jsonify({'status': 'fail', 'data': {'msg': '500 internal error'}})