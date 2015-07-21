# Created by cxy on 15/2/24 with PyCharm
# -*- coding: utf-8 -*-
from flask import Blueprint, request
from ..utils.utils import token_required, to_json, check_aff_group_exist, \
    check_aff_group_access
from config import config
from ..models.model import Nft, NftUserRel, AffGroup, UserInfo
from ..models.operations import Model
from sqlalchemy import and_


nft = Blueprint('nft', __name__)


@nft.route('/inviteJoinAffGroup', methods=['POST'])
@token_required
def send_nft(user_id):  # TODO: 检查是否已经邀请过, 不能重复邀请
    receivers = request.form['receivers']
    aff_group_id = request.form['aff_group_id']

    model = Model()
    aff_group = model.session.query(AffGroup).get(aff_group_id)
    res = check_aff_group_exist(aff_group)
    if res:
        return res
    res = check_aff_group_access(aff_group, user_id)
    if res:
        return res

    user = model.session.query(UserInfo).filter_by(user_id=user_id).first()
    user_nickname = user.nickname

    if not receivers:
        return to_json('no receivers')
    receiver_id_list = map(int, receivers.strip("'").split(','))
    NFT_TYPE = 1
    nft = Nft(NFT_TYPE, len(receiver_id_list), aff_group_id=aff_group_id, user_id=user_id)
    model.session.add(nft)
    model.session.commit()

    for receiver_id in receiver_id_list:
        if receiver_id == user_id:
            continue
        nft_str = config.NFT_CONTENT[1] % (user_nickname, aff_group.subject)
        nft_user_rel = NftUserRel(nft.id, receiver_id, nft_str, sender_id=user_id)
        model.session.add(nft_user_rel)
    model.session.commit()
    return to_json('', success=True)


@nft.route('/get', methods=['POST'])  # TODO: 获取请求中已经同意加入的用户
@token_required
def get_user_nfts(user_id):
    model = Model()
    nfts = model.session.query(NftUserRel).filter(
        and_(NftUserRel.receiver_id == user_id, NftUserRel.is_check == False)).all()
    # data = [nft.data() for nft in nfts]
    data = [model.get_nft_detail(nft.id) for nft in nfts]
    return to_json(data, success=True)


@nft.route('/ac', methods=['POST'])
@token_required
def accept_invitation(user_id):
    nft_user_rel_id = request.form['nft_user_rel_id']

    model = Model()
    nft_user_rel = model.session.query(NftUserRel).get(nft_user_rel_id)
    nft_user_rel.is_check = True

    # 防止多次同意一个邀请
    nft = model.session.query(Nft).get(nft_user_rel.nft_id)
    if not nft_user_rel.is_ac:
        nft_user_rel.is_ac = True
        nft.ac_num += 1
        nft.check_num += 1
        model.session.add(nft)

    model.session.add(nft_user_rel)

    NFT_TYPE = 2
    ac_nft = Nft(NFT_TYPE, total_num=1, aff_group_id=nft.aff_group_id, user_id=user_id)
    model.session.add(ac_nft)
    model.session.commit()

    user = model.session.query(UserInfo).filter_by(user_id=user_id).first()
    nickname = user.nickname
    aff_group = model.session.query(AffGroup).get(nft.aff_group_id)
    subject = aff_group.subject
    nft_content = config.NFT_CONTENT[NFT_TYPE] % (nickname, subject)
    ac_nft_user_rel = NftUserRel(ac_nft.id, nft_user_rel.receiver_id, nft_content, sender_id=user_id)
    model.session.add(ac_nft_user_rel)
    model.session.commit()

    data = aff_group.data()
    return to_json(data, success=True)  # TODO: bug to fix


@nft.route('/decline', methods=['POST'])
@token_required
def decline_invitation(user_id):  # TODO: 拒绝要发通知? 已经同意了再拒绝?
    nft_user_rel_id = request.form['nft_user_rel_id']

    model = Model()
    nft_user_rel = model.session.query(NftUserRel).get(nft_user_rel_id)
    nft_user_rel.is_check = True
    model.session.add(nft_user_rel)

    nft = model.session.query(Nft).get(nft_user_rel.nft_id)
    nft.check_num += 1
    model.session.add(nft)

    model.session.commit()
    return to_json('', success=True)


@nft.route('/reply', methods=['POST'])
@token_required
def reply_invitation(user_id):
    method = request.form['method']
    nft_user_rel_id = request.form['nft_user_rel_id']

    if method == 'accept':
        pass

    elif method == 'decline':
        pass

    elif method == 'ignore':
        pass


@nft.route('/check', methods=['POST'])
@token_required
def check_nft(user_id):
    nft_user_rel_id = request.form['nft_user_rel_id']

    model = Model()
    nft_user_rel = model.session.query(NftUserRel).get(nft_user_rel_id)
    nft_user_rel.is_check = True
    model.session.add(nft_user_rel)
    model.session.commit()
    return to_json('', success=True)


@nft.route('/getAll', methods=['POST'])
@token_required
def get_all_notifications(user_id):
    model = Model()
    nft_user_rels = model.session.query(NftUserRel).filter_by(receiver_id=user_id).all()
    data = [model.get_nft_detail(rel.id) for rel in nft_user_rels]
    return to_json(data, success=True)