# -*- coding: utf-8 -*-
# @Date    : 2017/2/1
# @Author  : hrwhisper
import codecs
import os
import time
from sys import exit
import requests
from MyOCR import image_to_string


class LoginUCAS(object):
    def __init__(self, vercode_save_name='certCode.jpg'):
        self.username, self.password = LoginUCAS._read_username_and_password()
        self.cnt = 0
        self.__BEAUTIFULSOUPPARSE = 'html5lib'  # or use 'lxml'
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
        self.vercode_save_name = vercode_save_name

    @classmethod
    def _read_username_and_password(cls):
        with codecs.open(r'./private.txt', "r", 'utf-8') as f:
            username = password = None
            for i, line in enumerate(f):
                if i == 0:
                    line = bytes(line.encode('utf-8'))
                    if line[:3] == codecs.BOM_UTF8:
                        line = line[3:]
                    username = line.decode('utf-8').strip()
                elif i == 1:
                    password = line.strip()
                else:
                    break
        return username, password

    def _download_verification_code(self):
        r = self.session.get('http://sep.ucas.ac.cn/changePic', stream=True, headers=self.headers)
        with open(self.vercode_save_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return self.vercode_save_name

    def login_sep(self):
        # 登录sep
        if not self.cnt:
            print('Login....')
        url = "http://sep.ucas.ac.cn/slogin"
        cert_code = image_to_string(self._download_verification_code())
        while not cert_code or len(cert_code) < 4:
            cert_code = image_to_string(self._download_verification_code())
        post_data = {
            "userName": self.username,
            "pwd": self.password,
            "sb": "sb",
            "certCode": cert_code,
            "rememberMe": 1,
        }
        html = self.session.post(url, data=post_data, headers=self.headers).text
        if html.find('密码错误') != -1:
            print('用户名或者密码错误，请检查private文件')
            os.system("pause")
            exit(1)
        elif html.find('验证码错误') != -1:
            time.sleep(2)
            self.cnt += 1
            return self.login_sep()
        print("登录成功 {}".format(self.cnt))
        return self


if __name__ == '__main__':
    LoginUCAS().login_sep()
    # total = 0
    # test_num = 50
    # for i in range(test_num):
    #     UcasLogin = LoginUCAS()
    #     UcasLogin.login_sep()
    #     total += UcasLogin.cnt
    #     print(i, total, '\n------------\n')
    # print(total, total / test_num)
