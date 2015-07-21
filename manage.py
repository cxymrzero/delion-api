# Created by cxy on 15/1/14 with PyCharm
# -*- coding: utf-8 -*-
from app import app
from app.views import view, affair, group, user


if __name__ == '__main__':
    app.run(debug=True)