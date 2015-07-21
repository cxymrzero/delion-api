# Created by cxy on 15/2/3 with PyCharm
# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from ..utils.utils import token_required, to_json, get_user_by_token, is_time_fmt_ok
from ..models.operations import Model
from ..models.model import Aff
from config import config


affair = Blueprint('affair', __name__)


@affair.route("/add", methods=['POST'])
@token_required
def add_aff(user_id):
    subject = request.form['subject']
    detail = request.form.get('detail', None)
    start_time = request.form['start_time']  # TODO 测试空数据
    end_time = request.form['end_time']
    freq = request.form['freq']
    loc = request.form.get('loc', None)
    level = request.form['level']

    if start_time >= end_time:
        return to_json('time error')

    # 添加事务
    model = Model()
    dft_aff_group = model.get_user_dft_aff_group(user_id)
    dft_aff_group_id = dft_aff_group.id
    aff = model.add_aff(subject=subject, aff_group_id=dft_aff_group_id,
                        start_time=start_time, end_time=end_time, user_id=user_id, detail=detail,
                        freq=freq, loc=loc, level=int(level))

    # 添加用户-事务关系
    # aff_id = aff.id
    # model.add_user_aff_rel(user_id, aff_id)

    # 修改默认事务组内容
    if (not dft_aff_group.start_time) or (dft_aff_group.start_time.strftime(config.TIME_STRING) > start_time):
        dft_aff_group.start_time = start_time
    if (not dft_aff_group.end_time) or (dft_aff_group.end_time.strftime(config.TIME_STRING) < end_time):
        dft_aff_group.end_time = end_time
    dft_aff_group.aff_num += 1
    model.session.add(dft_aff_group)
    model.session.commit()

    data = dict(aff_id=aff.id)
    return to_json(data, success=True)


@affair.route("/addTo", methods=['POST'])
@token_required
def add_affair_to_group(user_id):
    aff_id = request.form['aff_id']
    aff_group_id = request.form['aff_group_id']

    model = Model()
    aff_group = model.get_aff_group_by_id(aff_group_id)
    if not (aff_group.user_id == user_id):
        return to_json('no access')
    # TODO add aff to aff_group
    return 'todo'


@affair.route("/edit", methods=['POST'])
@token_required
def edit_affair(user_id):
    aff_id = request.form['aff_id']
    subject = request.form['subject']
    detail = request.form.get('detail', None)
    start_time = request.form['start_time']  # TODO 测试空数据
    end_time = request.form['end_time']
    freq = request.form['freq']
    loc = request.form.get('loc', None)
    level = request.form['level']

    if start_time >= end_time:
        return to_json('time error')

    model = Model()
    aff = model.get_aff_by_id(aff_id)
    if user_id != aff.user_id:
        return to_json('no access')
    new_aff = Aff(subject, aff.aff_group_id, start_time, end_time, user_id, detail,
                  freq, loc, level, pre_aff_id=aff_id)
    # self, subject, aff_group_id, start_time, end_time, user_id, detail=None,
    #              freq='n', loc=None, level=1, pre_aff_id=None
    model.session.add(new_aff)
    model.session.commit()  # TODO: delete origin affair from affair group

    data = new_aff.data()
    return to_json(data, success=True)


# GET: aff_id
# POST: token, aff_id
@affair.route("/get", methods=['GET', 'POST'])
def get_aff_info():
    model = Model()
    aff_id = request.args['aff_id'] if request.method == 'GET' else request.form['aff_id']
    aff = model.get_aff_by_id(aff_id=aff_id)
    aff_group = model.get_aff_group_by_id(aff.aff_group_id)
    data = aff.data()
    if request.method == 'GET':
        if aff_group.is_private:
            return to_json('private affair require token')
        else:
            return to_json(data, success=True)
    if request.method == 'POST':
        token = request.form['token']
        aff_id = request.form['aff_id']
        res = get_user_by_token(token)
        if isinstance(res, dict):
            return jsonify(res)
        else:
            user = res
        aff = model.get_aff_by_id(aff_id)
        aff_group = model.get_aff_group_by_id(aff.aff_group_id)
        if aff.user_id != user.id and aff_group.is_private:
            return to_json('no access for others affair')
        else:
            return to_json(data, success=True)


@affair.route("/time", methods=['POST'])
@token_required
def get_aff_between_time(user_id):
    # 获取用户某段时间内的所有事务, 以事务组形式返回
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    if not is_time_fmt_ok([start_time, end_time]):
        return to_json('wrong time format')

    model = Model()
    aff_groups = model.get_aff_groups_between_time(user_id, start_time, end_time)
    print aff_groups

    res = []
    for aff_group in aff_groups:
        data = {}
        data['aff_group_info'] = aff_group.data()
        data['aff_info'] = []
        affs = model.get_affs_in_group(aff_group.id)
        for aff in affs:
            if start_time <= aff.start_time.strftime(config.TIME_STRING) \
                    and aff.end_time.strftime(config.TIME_STRING) <= end_time:
                data['aff_info'].append(aff.data())
        # 若包含满足时间条件的事务, 则将data字典添加到返回内容中
        if data['aff_info']:
            res.append(data)

    return to_json(res, success=True)


# @affair.route("/delete", methods=['POST'])
# @token_required
# def delete_affair(user_id, aff_id, aff_group_id):
#     aff_id = request.form['aff_id']
#     aff_group_id = request.form['aff_group_id']
#
#     model = Model()
#     user = model.get_user_by_aff_id(aff_id)
#     try:
#         user_id = user.id
#     except:
#         return to_json('wrong affair id, user not exists')