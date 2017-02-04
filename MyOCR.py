# -*- coding: utf-8 -*-
# @Date    : 2017/2/1
# @Author  : hrwhisper

import os
import re
import subprocess
from PIL import Image

devnull = open(os.devnull, 'w')
cut_size = 1


def pre_process(func):
    def _wrapper(filename):
        image = Image.open(filename).point(lambda p: 255 if p > 127 else 0).convert("1")
        w, h = image.size
        image = image.crop((cut_size, cut_size, w - cut_size, h - cut_size))
        save_name = filename  # + '1.jpg'
        image.save(save_name)
        res = func(save_name)
        os.remove(save_name)
        return res

    return _wrapper


@pre_process
def image_to_string(img):
    res = subprocess.check_output('tesseract ' + img + ' stdout', stderr=devnull).decode()  # tesseract a.png result
    return (re.subn('\W', '', res.strip()) if res else ('', ''))[0].lower()


if __name__ == '__main__':
    print(image_to_string('ucas_code1.jpg'))
    print(image_to_string('ucas_code2.jpg'))
