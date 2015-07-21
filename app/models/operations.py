# Created by cxy on 15/1/18 with PyCharm
# -*- coding: utf-8 -*-
from .model import engine
from .model import Aff, AffGroup, User, UserAffRel, UserAffGroupRel, \
    UserInfo, UserRel, NftUserRel, Nft
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_
from config import config


class Model():
    def __init__(self):
        session = sessionmaker(bind=engine)
        self.session = session()

    def add_aff(self, subject, aff_group_id, start_time, end_time, user_id, detail=None,
                freq='n', loc=None, level=1, pre_aff_id=None):
        aff = Aff(subject=subject, aff_group_id=aff_group_id, detail=detail, start_time=start_time,
                  end_time=end_time, user_id=user_id, freq=freq, loc=loc, level=level, pre_aff_id=pre_aff_id)
        self.session.add(aff)
        self.session.commit()
        return aff

    def add_aff_group(self, subject, user_id, detail=None, start_time=None, end_time=None):
        aff_group = AffGroup(subject=subject, user_id=user_id, detail=detail,
                             start_time=start_time, end_time=end_time)
        self.session.add(aff_group)
        self.session.commit()
        return aff_group

    def add_user(self, email, pwd):
        is_exist = self.session.query(User).filter_by(email=email).first()
        if is_exist:
            return 'user exists'
        # TODO add email and password validation
        new_user = User(email, pwd)
        self.session.add(new_user)
        self.session.commit()
        return new_user

    def add_user_aff_rel(self, user_id, aff_id):
        user_aff_rel = UserAffRel(user_id, aff_id)
        self.session.add(user_aff_rel)
        self.session.commit()
        return user_aff_rel

    def add_user_aff_group_rel(self, user_id, aff_group_id):
        user_aff_group_rel = UserAffGroupRel(user_id, aff_group_id)
        self.session.add(user_aff_group_rel)
        self.session.commit()
        return user_aff_group_rel

    # 添加用户详细信息
    def add_user_info(self, user_id, dft_aff_group_id, nickname, sns=None):
        user_info = UserInfo(user_id=user_id,
                             dft_aff_group_id=dft_aff_group_id, nickname=nickname, sns=sns)
        self.session.add(user_info)
        self.session.commit()
        return user_info

    def get_aff_by_id(self, aff_id):
        aff = self.session.query(Aff).get(aff_id)
        return aff

    def get_aff_by_id_with_user_id(self, aff_id):
        return self.session.query(Aff, AffGroup.user_id).filter(Aff.aff_group_id==AffGroup.id).first()

    def get_affs_in_group(self, aff_group_id):
        affs = self.session.query(Aff).filter_by(aff_group_id=aff_group_id).all()
        return affs

    def get_aff_group_by_id(self, aff_group_id):
        aff_group = self.session.query(AffGroup).get(aff_group_id)
        return aff_group

    def get_aff_groups_between_time(self, user_id, start_time, end_time):
        aff_groups = self.session.query(AffGroup).filter_by(user_id=user_id).\
            filter(and_(AffGroup.start_time <= end_time, AffGroup.end_time >= start_time)).all()
        return aff_groups

    def get_nft_detail(self, nft_user_rel_id):
        nft_user_rel = self.session.query(NftUserRel).get(nft_user_rel_id)
        data = nft_user_rel.sdata()
        nft_id = data['nft_id']
        print nft_id
        nft = self.session.query(Nft).get(nft_id)
        if nft:
            nft_data = {'create_time': nft.create_time.strftime(config.TIME_STRING), 'type': nft.type}
            data.update(nft_data)
        return data

    def get_user_aff_group_rel(self, group_id, user_id):
        user_aff_group_rel = self.session.query(UserAffGroupRel).filter(
            and_(UserAffGroupRel.aff_group_id==group_id, UserAffGroupRel.user_id==user_id)).first()
        return user_aff_group_rel

    def get_user_by_aff_id(self, aff_id):
        s = self.session
        try:
            user = s.query(User).get(
                s.query(AffGroup).get(
                    s.query(Aff).get(aff_id).aff_group_id
                ))
        except Exception as e:
            return e
        return user

    def get_user_by_email_pwd(self, email, pwd):
        user = self.session.query(User).filter_by(email=email, pwd=pwd).first()
        return user

    def get_user_by_id(self, user_id):
        user = self.session.query(User).get(user_id)
        return user

    def get_user_info(self, user_id):
        user_info = self.session.query(UserInfo).filter_by(user_id=user_id).first()
        data = user_info.data() if user_info else {}
        user = self.session.query(User).get(user_id)
        if user and data:  # 如果用户存在并且前一次查询的用户详细信息存在则添加email信息, 否则返回空
            data.update({'email': user.email})
        return data

    def get_user_dft_aff_group(self, user_id):
        aff_group = self.session.query(AffGroup).filter_by(user_id=user_id).first()
        return aff_group

    def get_user_rel(self, follower_id, followed_id):
        user_rel = self.session.query(UserRel).filter(
            and_(UserRel.followed_id == followed_id, UserRel.follower_id == follower_id)).first()
        return user_rel

    def suicide(self, user_id):
        self.session.query(Aff).filter_by(user_id=user_id).delete()
        self.session.query(AffGroup).filter_by(user_id=user_id).delete()
        self.session.query(User).filter_by(id=user_id).delete()
        self.session.query(UserInfo).filter_by(user_id=user_id).delete()
        self.session.query(UserRel).filter(or_(UserRel.followed_id==user_id, UserRel.follower_id==user_id))
        self.session.query(UserAffRel).filter_by(user_id=user_id)
        self.session.query(UserAffGroupRel).filter_by(user_id=user_id)
        # TODO 重写