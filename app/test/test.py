# Created by cxy on 15/2/14 with PyCharm
# -*- coding: utf-8 -*-
def f1():
    a = 1
    def f2():
        b = 2
        return a + b
    return f2()

print f1()