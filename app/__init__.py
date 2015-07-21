# Created by cxy on 15/1/14 with PyCharm
# -*- coding: utf-8 -*-
from flask import Flask
from config import config
from .views.affair import affair
from .views.group import group
from .views.user import user
from .views.notification import nft


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(affair, url_prefix='/api/affair')
    app.register_blueprint(group, url_prefix='/api/group')
    app.register_blueprint(user, url_prefix='/api/user')
    app.register_blueprint(nft, url_prefix='/api/nft')
    return app


app = create_app()