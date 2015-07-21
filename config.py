# Created by cxy on 15/1/14 with PyCharm
# -*- coding: utf-8 -*-
from os import environ


class Config:
    SECRET_KEY = # 自行填写
    HELLO_STRING = '这是一个很重要的网站, 删除前请联系陈翔宇(cxymrzero@gmail.com)'
    TIME_STRING = '%Y-%m-%d %H:%M:%S'
    YEAR_STRING = '%Y-%m-%d'
    NFT_CONTENT = {
        1: u'<%s>邀请你加入事务组<%s>',  # 用户昵称, 事务组主题
        2: u'<%s>已同意加入事务组<%s>'  # 同上
    }


class DevConfig(Config):
    MYSQL_CONN = 'mysql+mysqldb://root:password@localhost:3306/delion?charset=utf8'
    # 此处按照上面的格式填写你本地的配置

class RealConfig(Config):
    MYSQL_CONN = 'mysql+mysqldb://root:password@localhost:3306/delion?charset=utf8'
    # 同上

# 通过$USER判断是否为线上环境
user = environ.get("USER")
if user == 'mrzero':
    config = DevConfig()
else:
    config = RealConfig()
