# -*- coding: utf-8 -*-
# @Date    : 2016/9/1
# @Author  : hrwhisper
from __future__ import print_function
import re
import time
import requests

from LoginUCAS import LoginUCAS, PasswordError


class NoLoginError(Exception):
    pass


def read_course_file():
    with open("./course_list.txt") as f:
        courses = []
        for i, line in enumerate(f):
            courses.append(line.strip().split())
    return courses


class UcasCourse(object):
    def __init__(self):
        self.session = None
        self.headers = None
        self._init_session()
        self.course = UcasCourse._read_course_info()

    def _init_session(self):
        t = LoginUCAS().login_sep()
        self.session = t.session
        self.headers = t.headers

    @classmethod
    def _read_course_info(self):
        with open("./course_list.txt") as f:
            courses = []
            for i, line in enumerate(f):
                courses.append(line.strip().split())
        return courses

    def login_jwxk(self):
        # 从sep中获取Identity Key来登录选课系统
        url = "http://sep.ucas.ac.cn/portal/site/226/821"
        r = self.session.get(url, headers=self.headers)
        try:
            code = re.findall(r'"http://jwxk.ucas.ac.cn/login\?Identity=(.*)"', r.text)[0]
        except IndexError:
            raise NoLoginError

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
        if not self.course: return None
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
            return self.course.pop(0)[0]
        else:
            info = re.findall('<label id="loginError" class="error">([\S]+)</label>', r.text)[0]
            print(info)
            return None

    def start(self):
        while True:
            try:
                res = self.select_course()
                if res is not None:
                    print('课程编号为 {} 的选课成功'.format(res))
                elif not self.course:
                    print('全部选完')
                    exit(0)
            except PasswordError:
                print('用户密码错误，请检查private文件')
                exit(1)
            except NoLoginError:
                self._init_session()
            except IndexError:
                print('课程编号出错，可能已被选上')
                self.course.pop(0)
            except Exception as e:
                print(e)
            time.sleep(5)


if __name__ == '__main__':
    cnt = 0
    UcasCourse().start()
    # while True:
    #     s = UcasCourse()
    #     try:
    #         res = s.start()
    #         if res == -1:
    #             print('全部选完')
    #             exit(0)
    #         elif res == 1:
    #             print(cnt + 1, ' success')
    #             cnt += 1
    #     except ValueError as e:
    #         print('用户密码错误，请检查private文件')
    #         exit(1)
    #     except IndexError as e:
    #         print('课程编号出错，可能已被选上')
    #         s.course.pop(0)
    #         cnt += 1
    #     except Exception as e:
    #         print(e)
    #     time.sleep(2)
