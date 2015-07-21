# Created by cxy on 15/2/3 with PyCharm
# -*- coding: utf-8 -*-
from flask import Blueprint, request
from app.utils.utils import token_required, to_json, check_aff_group_access
from ..models.operations import Model
from ..models.model import UserAffGroupRel, Aff, AffGroup, Nft, NftUserRel, UserInfo
from sqlalchemy import and_
from config import config


group = Blueprint('group', __name__)


@group.route("/add", methods=['POST'])
@token_required
def add_aff_group(user_id):
    subject = request.form['subject']
    detail = request.form.get('detail', None)
    # start_time = request.form.get('start_time', None)
    # end_time = request.form.get('end_time', None)
    #
    # if not start_time < end_time:
    #     return to_json('time error')

    model = Model()
    aff_group = model.add_aff_group(subject, user_id, detail, None, None)
    model.add_user_aff_group_rel(user_id, aff_group.id)

    data = dict(aff_group_id=aff_group.id)
    return to_json(data, success=True)


@group.route('/share', methods=['POST'])
@token_required
def share_group(user_id):
    group_id = request.form['aff_group_id']
    model = Model()
    aff_group = model.get_aff_group_by_id(group_id)
    if not aff_group:
        return to_json('affair group not exist')

    if (aff_group.user_id != user_id) and aff_group.is_private:
        return to_json('no access')

    aff_group.is_private = False
    model.session.add(aff_group)
    model.session.commit()
    return to_json('', success=True)


@group.route('/join', methods=['POST'])
@token_required
def join_shared_group(user_id):
    group_id = request.form['aff_group_id']
    model = Model()

    user_aff_group_rel = model.get_user_aff_group_rel(group_id, user_id)
    if user_aff_group_rel:
        return to_json('already saved')

    aff_group = model.get_aff_group_by_id(group_id)
    if not aff_group:
        return to_json('affair group not exist')
    if aff_group.is_private or user_id == aff_group.user_id:
        return to_json('no access')

    user_aff_group_rel = UserAffGroupRel(user_id, group_id)
    model.session.add(user_aff_group_rel)
    aff_group.owner_num += 1
    data = aff_group.data()
    print data
    model.session.add(aff_group)
    model.session.commit()
    return to_json(aff_group.data(), success=True)


@group.route('/exit', methods=['POST'])
@token_required
def exit_group(user_id):
    group_id = request.form['aff_group_id']
    model = Model()

    user_aff_group_rel = model.get_user_aff_group_rel(group_id, user_id)
    if not user_aff_group_rel:
        return to_json('not join')

    model.session.query(UserAffGroupRel).filter(
        and_(UserAffGroupRel.user_id == user_id, UserAffGroupRel.aff_group_id == group_id)).delete()
    group = model.session.query(AffGroup).get(group_id)
    group.owner_num -= 1
    model.session.add(group)
    model.session.commit()
    return to_json('', success=True)


@group.route('/edit', methods=['POST'])
@token_required
def edit_group(user_id):
    group_id = request.form['aff_group_id']
    subject = request.form['subject']
    detail = request.form['detail']

    model = Model()
    group = model.session.query(AffGroup).get(group_id)
    if not group:
        return to_json('affair group not exist')
    if group.user_id != user_id:
        return to_json('no access')
    group.subject = subject
    group.detail = detail
    model.session.add(group)
    model.session.commit()
    return to_json('', success=True)


@group.route('/analyze', methods=['POST'])
@token_required
def analyze_group(user_id):
    group_ids = request.form['aff_group_ids']
    try:
        group_id_list = group_ids.split(',')
        group_id_list = map(int, group_id_list)
    except:
        return to_json('invalid affair group list')

    data = []
    model = Model()
    for group_id in group_id_list:
        group_info = dict(aff_group_id=group_id)
        # 获取AffGroup对象并检测是否存在, 是否有权限访问
        group = model.session.query(AffGroup).get(group_id)
        if not group:
            continue
        error = check_aff_group_access(group, user_id)
        if error:
            return error

        # 获取用户发出的通知对象, 并检测其是否存在
        nft = model.session.query(Nft).filter_by(aff_group_id=group.id).first()
        try:
            accept_num = nft.ac_num
            total_num = nft.total_num
            check_num = nft.check_num
        except:
            return to_json('notification not exist')

        group_info.update(
            dict(accept_num=accept_num, total_num=total_num, check_num=check_num))

        # 获得同意加入事务组的用户信息
        accept_users_info = []
        nft_user_rels = model.session.query(NftUserRel).filter(
            and_(NftUserRel.nft_id == nft.id, NftUserRel.is_ac == True)).all()
        for nft_user_rel in nft_user_rels:
            user_info = {}
            new_user_info = model.session.query(UserInfo).filter(
                UserInfo.user_id == nft_user_rel.sender_id).first()
            try:
                user_id = new_user_info.user_id
                nickname = new_user_info.nickname
                user_info.update(dict(user_id=user_id, nickname=nickname))
            except:
                return to_json('user info not exist')
            accept_users_info.append(user_info)

        group_info['accept_users_info'] = accept_users_info
        data.append(group_info)

    return to_json(data, success=True)


@group.route('/addAff', methods=['POST'])
@token_required
def add_aff_to_group(user_id):
    aff_id = request.form['aff_id']
    aff_group_id = request.form['aff_group_id']

    model = Model()
    aff = model.session.query(Aff).get(aff_id)
    aff_group = model.session.query(AffGroup).get(aff_group_id)
    if not (aff and aff_group):
        return to_json('affair or affair group not exist')

    if aff.user_id != user_id or aff_group.user_id != user_id:
        return to_json('no access')

    # 修改AffGroup信息
    if aff_group.start_time and aff_group.end_time:
        new_start_time = min(aff.start_time.strftime(config.TIME_STRING), aff_group.start_time.strftime(config.TIME_STRING))
        new_end_time = max(aff.end_time.strftime(config.TIME_STRING), aff_group.end_time.strftime(config.TIME_STRING))
    else:
        new_start_time = aff.start_time.strftime(config.TIME_STRING)
        new_end_time = aff.end_time.strftime(config.TIME_STRING)
    aff_group.start_time = new_start_time
    aff_group.end_time = new_end_time
    aff_group.aff_num += 1
    model.session.add(aff_group)

    # 修改Aff信息
    aff.aff_group_id = aff_group_id
    model.session.add(aff)

    model.session.commit()
    return to_json('', success=True)


@group.route('/addSingle', methods=['POST'])
@token_required
def add_single_affair_group(user_id):
    # TODO: @ here!
    pass


@group.route('/getAll', methods=['POST'])
@token_required
def get_all_aff_groups(user_id):
    model = Model()
    # 用户创建的事务组
    # groups = model.session.query(AffGroup).filter_by(user_id=user_id).all()
    # data = [group.data() for group in groups]

    # 用户加入的事务组
    data = []
    user_group_rels = model.session.query(UserAffGroupRel).filter_by(user_id=user_id).all()
    for rel in user_group_rels:
        group_id = rel.aff_group_id
        group = model.session.query(AffGroup).get(group_id)
        if group:
            data.append(group.data())
    return to_json(data, success=True)


@group.route('/<int:group_id>/users', methods=['GET'])
def get_people_in_group(group_id):
    """
    包括创建者在内的所有参与事务组的用户详细信息列表
    """
    model = Model()
    data = []

    user_aff_group_rel_list = model.session.query(UserAffGroupRel).filter_by(aff_group_id=group_id).all()
    for rel in user_aff_group_rel_list:
        user_id = rel.user_id
        user_info = model.get_user_info(user_id)
        if user_info:
            data.append(user_info)
    return to_json(data, success=True)


@group.route('/affairs', methods=['POST'])
@token_required
def get_affairs_in_group(user_id):
    model = Model()
    group_id = request.form['aff_group_id']

    # 检查该用户是否有权限访问该事务组
    aff_group = model.get_aff_group_by_id(group_id)
    print aff_group.id
    check_res = check_aff_group_access(aff_group, user_id)
    if check_res:
        return check_res

    affair_list = model.session.query(Aff).filter_by(aff_group_id=group_id).all()
    data = [affair.data() for affair in affair_list]
    return to_json(data, success=True)


@group.route('/<int:group_id>/affairsPublic', methods=['GET'])
def get_affairs_in_public_affair_group(group_id):
    model = Model()
    aff_group = model.get_aff_group_by_id(group_id)

    # 判断是否为私有事务组
    if aff_group.is_private:
        return to_json('no access')

    affair_list = model.session.query(Aff).filter_by(aff_group_id=group_id).all()
    data = [affair.data() for affair in affair_list]
    return to_json(data, True)