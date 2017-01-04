# -*- coding: utf-8 -*-
# @Date    : 2016/9/1
# @Author  : hrwhisper
from __future__ import print_function
import re
import time
import requests


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


class UcasCourse(object):
    username, password, course = read_file()

    def __init__(self):
        self.session = requests.session()
        self.headers = {
            "Host": "sep.ucas.ac.cn",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        }

    def login_sep(self):
        # 登录sep
        url = "http://sep.ucas.ac.cn/slogin"
        post_data = {
            "userName": self.username,
            "pwd": self.password,
            "sb": "sb"
        }
        html = self.session.post(url, data=post_data, headers=self.headers).text
        if html.find(u'<div class="alert alert-error">密码错误</div>') != -1:
            raise ValueError('用户密码错误，请检查private文件')

    def login_jwxk(self):
        # 从sep中获取Identity Key来登录选课系统
        url = "http://sep.ucas.ac.cn/portal/site/226/821"
        r = self.session.get(url, headers=self.headers)
        code = re.findall(r'"http://jwxk.ucas.ac.cn/login\?Identity=(.*)"', r.text)[0]

        url = "http://jwxk.ucas.ac.cn/login?Identity=" + code
        self.headers['Host'] = "jwxk.ucas.ac.cn"
        self.session.get(url, headers=self.headers)
        url = 'http://jwxk.ucas.ac.cn/courseManage/main'
        r = self.session.get(url, headers=self.headers)
        return r.text

    def get_course(self):
        # 获取课程开课学院的id，以及选课界面HTML
        html = self.login_jwxk()
        regular = r'<label for="id_([\S]+)">' + self.course[0][0][:2] + r'-'
        institute_id = re.findall(regular, html)[0]

        url = 'http://jwxk.ucas.ac.cn' + \
              re.findall(r'<form id="regfrm2" name="regfrm2" action="([\S]+)" \S*class=', html)[0]
        post_data = {'deptIds': institute_id, 'sb': '0'}

        html = self.session.post(url, data=post_data, headers=self.headers).text
        return html, institute_id

    def select_course(self):
        if not self.course: return -1
        # 选课，主要是获取课程背后的ID
        html, institute_id = self.get_course()
        url = 'http://jwxk.ucas.ac.cn' + \
              re.findall(r'<form id="regfrm" name="regfrm" action="([\S]+)" \S*class=', html)[0]
        sid = re.findall(r'<span id="courseCode_([\S]+)">' + self.course[0][0] + '</span>', html)[0]
        post_data = {'deptIds': institute_id, 'sids': sid}
        if self.course[0][1] == '1':
            post_data['did_' + sid] = sid

        r = self.session.post(url, data=post_data, headers=self.headers)
        if r.text.find(u'选课成功') != -1:
            print('选课成功')
            self.course.pop(0)
            return 1
        else:
            info = re.findall('<label id="loginError" class="error">([\S]+)</label>', r.text)[0]
            print(info)
            return 0

    def start(self):
        self.login_sep()
        return self.select_course()


if __name__ == '__main__':
    cnt = 0
    while True:
        s = UcasCourse()
        try:
            res =  s.start()
            if res== -1:
                print('全部选完')
                exit(0)
            elif res == 1:
                print(cnt + 1,' success')
                cnt += 1
        except ValueError as e:
            print('用户密码错误，请检查private文件')
            exit(1)
        except IndexError as e:
            print('课程编号出错，可能已被选上')
            s.course.pop(0)
        except Exception as e:
            print(e)
        time.sleep(5)
