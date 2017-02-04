# -*- coding: utf-8 -*-
# @Date    : 2017/2/4
# @Author  : hrwhisper


def read_file():
    with open("./private") as f:
        username = password = None
        courses = []
        for i, line in enumerate(f):
            if i == 0:
                username = line.strip()
            elif i == 1:
                password = line.strip()
            else:
                courses.append(line.strip().split())
    return username, password, courses
