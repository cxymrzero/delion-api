# Created by cxy on 15/2/22 with PyCharm
# -*- coding: utf-8 -*-
from flask import Blueprint, request
from ..utils.utils import token_required, to_json
from ..models.model import UserRel, User, UserInfo
from ..models.operations import Model
from sqlalchemy import and_


user = Blueprint('user', __name__)


@user.route('/follow', methods=['POST'])
@token_required
def follow_user(user_id):
    user_to_follow_id = request.form['user_id']
    user_rel = UserRel(user_id, user_to_follow_id)
    model = Model()
    if model.get_user_rel(user_id, user_to_follow_id):
        return to_json('already follow')
    user_to_follow = model.session.query(UserInfo).filter_by(user_id=user_to_follow_id).first()
    data = user_to_follow.data()
    # print data
    model.session.add(user_rel)
    model.session.commit()
    return to_json(data, success=True)


@user.route('/unfo', methods=['POST'])
@token_required
def unfo_user(user_id):
    user_to_unfo_id = request.form['user_id']
    model = Model()
    user_rel = model.get_user_rel(user_id, user_to_unfo_id)
    if not user_rel:
        return to_json('haven\'t follow')

    model.session.query(UserRel).filter(
        and_(UserRel.follower_id == user_id, UserRel.followed_id == user_to_unfo_id)).delete()
    model.session.commit()
    return to_json('', success=True)


@user.route('/search', methods=['GET'])
def search_user():
    email = request.args.get('email', '')
    email = email.strip(' ')
    if '@' not in email:
        return to_json('invalid email')

    model = Model()
    res = model.session.query(User, UserInfo).join(UserInfo).filter(User.email==email).first()
    if res:
        user, user_info = res
        if user and user_info:
            data = user_info.data()
            data['email'] = email
            return to_json(data, success=True)
    return to_json('user not exist')


@user.route('/editProfile', methods=['POST'])
@token_required
def edit_user_profile(user_id):
    nickname = request.form['nickname']

    model = Model()
    profile = model.session.query(UserInfo).filter_by(user_id=user_id).first()
    profile.nickname = nickname
    model.session.add(profile)
    model.session.commit()
    return to_json('', success=True)


@user.route('/followList', methods=['POST'])
@token_required
def get_follow_list(user_id):
    model = Model()
    follow_rel_list = model.session.query(UserRel).filter_by(follower_id=user_id).all()
    follow_id_list = [rel.followed_id for rel in follow_rel_list]
    print follow_id_list
    data = []
    for id in follow_id_list:
        # user_info = model.session.query(UserInfo).filter_by(user_id=id).first()
        user_info = model.get_user_info(id)
        if user_info:
            data.append(user_info)
    return to_json(data, success=True)


@user.route('/get', methods=['POST'])
def get_user_info_by_id_list():
    """
    通过user id列表获取用户信息
    :param user_id_list: "1,2,3"
    :return: 用户详细信息
    """
    user_id_list = request.form.get('user_id_list')
    model = Model()
    data = []
    l = user_id_list.split(',')
    user_id_list_int = map(int, [i.strip("'") for i in l])
    for id in user_id_list_int:
        user_info = model.get_user_info(id)
        if user_info:
            data.append(user_info)
    return to_json(data, success=True)