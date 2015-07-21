# Created by cxy on 15/1/14 with PyCharm
# -*- coding: utf-8 -*-
from sqlalchemy import Column, create_engine, ForeignKey
from sqlalchemy import SmallInteger, String, Integer, DateTime, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from config import config

Base = declarative_base()  # 创建对象的基类

conn = config.MYSQL_CONN
engine = create_engine(conn)


# 1. 事务表
class Aff(Base):
    __tablename__ = 'aff'
    id = Column(Integer, primary_key=True)
    subject = Column(String(45), nullable=False)
    detail = Column(String(255))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    freq = Column(Enum('d', 'w', 'm', 'y', 'n'))
    loc = Column(String(255))
    level = Column(SmallInteger)  # 事务的等级, 默认为1, 1是最高级
    aff_group_id = Column(Integer)  # 事务组的id
    pre_aff_id = Column(Integer)  # 前置事务的id, 删除或修改一个事务数据库里并不改变原来的事务,
    # 而是重新创建, 通过保留前置事务id恢复该事务
    own_num = Column(Integer)  # 这条事务的拥有者数目
    user_id = Column(Integer, nullable=False)

    def __init__(self, subject, aff_group_id, start_time, end_time, user_id, detail=None,
                 freq='n', loc=None, level=1, pre_aff_id=None):
        self.subject = subject
        self.detail = detail
        self.start_time = start_time
        self.end_time = end_time
        self.user_id = user_id
        self.freq = freq
        self.loc = loc
        self.level = level
        self.aff_group_id = aff_group_id
        self.pre_aff_id = pre_aff_id
        self.own_num = 1

    def data(self):
        return dict(
            id=self.id,
            subject=self.subject,
            detail=self.detail,
            start_time=self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=self.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            freq=self.freq,
            loc=self.loc,
            level=self.level,
            aff_group_id=self.aff_group_id,
            pre_aff_id=self.pre_aff_id,
            own_num=self.own_num,
            user_id=self.user_id
        )


# 2. 事务组表
class AffGroup(Base):
    __tablename__ = 'aff_group'
    id = Column(Integer, primary_key=True)
    subject = Column(String(45), nullable=False)  # 事务组主题
    detail = Column(String(255))  # 事务组详情
    user_id = Column(Integer, nullable=False)  # 事务组创建者id
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    aff_num = Column(SmallInteger)  # 事务组包含事务数目
    owner_num = Column(Integer)  # 事务组拥有者数目
    is_private = Column(Boolean, default=True)

    def __init__(self, subject, user_id, detail=None, start_time=None, end_time=None):
        self.subject = subject
        self.detail = detail
        self.user_id = user_id
        self.start_time = start_time
        self.end_time = end_time
        self.aff_num = 0
        self.owner_num = 1
        self.is_private = True

    def data(self):
        return dict(
            id=self.id,
            subject=self.subject,
            detail=self.detail,
            user_id=self.user_id,
            start_time=self.start_time.strftime(config.TIME_STRING) if self.start_time else '',
            end_time=self.end_time.strftime(config.TIME_STRING) if self.end_time else '',
            aff_num=self.aff_num,
            owner_num=self.owner_num,
            is_private=self.is_private
        )


# 3. 用户主要信息表
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(64), nullable=False)
    pwd = Column(String(32), nullable=False)

    def __init__(self, email, pwd):
        self.email = email
        self.pwd = pwd

    # TODO hash pwd
    def gen_pwd_hash(self):
        pass


# 4. 用户详细信息表
class UserInfo(Base):
    __tablename__ = 'user_info'
    id = Column(Integer, primary_key=True)  # 详细信息id
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    sns = Column(String(16))  # 绑定的社交网站
    create_date = Column(DateTime, nullable=False)  # 账号创建时间
    nickname = Column(String(64))
    dft_aff_group_id = Column(Integer)  # 默认用户组id

    def __init__(self, user_id, dft_aff_group_id, nickname, sns=None):
        self.user_id = user_id
        self.sns = sns
        self.create_date = str(datetime.now()).split('.')[0]
        self.nickname = nickname
        self.dft_aff_group_id = dft_aff_group_id

    def data(self):
        return dict(
            user_info_id=self.id,
            user_id=self.user_id,
            sns=self.sns,
            create_date=self.create_date.strftime(config.YEAR_STRING),
            nickname=self.nickname,
            dft_aff_group_id=self.dft_aff_group_id
        )


# 5. 用户关系表
class UserRel(Base):
    __tablename__ = 'user_rel'
    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, nullable=False)
    followed_id = Column(Integer, nullable=False)

    def __init__(self, follower_id, followed_id):
        self.follower_id = follower_id
        self.followed_id = followed_id


# 6. 用户-事务关系表
class UserAffRel(Base):
    __tablename__ = 'user_aff_rel'
    id = Column(Integer, primary_key=True)  # 关系id
    user_id = Column(Integer, nullable=False)
    aff_id = Column(Integer, nullable=False)

    def __init__(self, user_id, aff_id):
        self.user_id = user_id
        self.aff_id = aff_id


# 7. 用户-事务组关系表
class UserAffGroupRel(Base):
    __tablename__ = 'user_aff_group_rel'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    aff_group_id = Column(Integer, nullable=False)

    def __init__(self, user_id, aff_group_id):
        self.user_id = user_id
        self.aff_group_id = aff_group_id


# 9. 通知表(别问我8去哪了
class Nft(Base):
    __tablename__ = 'nft'
    id = Column(Integer, primary_key=True)
    type = Column(SmallInteger)
    create_time = Column(DateTime, nullable=False)
    aff_id = Column(Integer)  # 相关联事务id
    aff_group_id = Column(Integer)  # 相关联事务组id
    user_id = Column(Integer)  # 创建通知的用户id, 若为系统通知则为NULL
    total_num = Column(SmallInteger, nullable=False)  # 收到通知的用户数
    check_num = Column(SmallInteger, nullable=False)  # 查看的用户数
    ac_num = Column(SmallInteger, nullable=False)  # 同意用户数

    def __init__(self, type, total_num, aff_id=None, aff_group_id=None, user_id=None):
        self.type = type
        self.create_time = str(datetime.now()).split('.')[0]
        self.aff_id = aff_id
        self.aff_group_id = aff_group_id
        self.user_id = user_id
        self.total_num = total_num
        self.check_num = 0
        self.ac_num = 0


# 10. 通知-用户关系表
class NftUserRel(Base):
    __tablename__ = 'nft_user_rel'
    id = Column(Integer, primary_key=True)
    nft_id = Column(Integer, nullable=False)
    sender_id = Column(Integer)
    receiver_id = Column(Integer, nullable=False)
    is_check = Column(Boolean, default=False)  # 通知是否被用户查看
    is_ac = Column(Boolean, default=False)  # 请求是否被用户同意
    content = Column(String(256), nullable=False)

    def __init__(self, nft_id, receiver_id, content, sender_id=None):
        self.nft_id = nft_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.is_check = False
        self.is_ac = False
        self.content = content

    def data(self):
        return dict(
            id=self.id,
            nft_id=self.nft_id,
            sender_id=self.sender_id,
            receiver_id=self.receiver_id,
            content=self.content,
            is_ac=self.is_ac,
            is_check=self.is_check,
        )


def init_db():
    # 使用SQLAlchemy创建数据库
    Base.metadata.create_all(bind=engine)


def drop_db():
    # 删除整个数据库
    Base.metadata.drop_all(bind=engine)