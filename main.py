# -*- coding: utf-8 -*-
# @Date    : 2016/9/1
# @Author  : hrwhisper
from __future__ import print_function
import re
import time
from LoginUCAS import LoginUCAS


class UcasCourse(object):
    def __init__(self):
        t = LoginUCAS().login_sep()
        self.session = t.session
        self.headers = t.headers
        self.course = t.courses

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
        return self.select_course()


if __name__ == '__main__':
    cnt = 0
    while True:
        s = UcasCourse()
        try:
            res = s.start()
            if res == -1:
                print('全部选完')
                exit(0)
            elif res == 1:
                print(cnt + 1, ' success')
                cnt += 1
        except ValueError as e:
            print('用户密码错误，请检查private文件')
            exit(1)
        except IndexError as e:
            print('课程编号出错，可能已被选上')
            s.course.pop(0)
            cnt += 1
        except Exception as e:
            print(e)
        time.sleep(2)
