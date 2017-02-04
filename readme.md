# 国科大选课助手说明 #
## 使用方法 ##
修改private文件即可。
private中，各行表示意义如下：

1. 第一行为登录选课系统的账号
2. 第二行为密码
3. 第三行之后每一行为选课的账号，接着是一个数字表示是否为学位课（0为否1为是）

### 注意 ###
程序假设课程不冲突，每10S尝试选课一次


## 环境说明

- python 3.5.2 or python 2.7.6
- requests 2.11

### 环境安装方法
- pip install requests
- pip install Pillow
- Tesseract-OCR
  - windows下安装：http://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-setup-3.05.00dev.exe
    - 安装时候勾选Registry settings
  - Linux  \  MAC OS X安装见 https://github.com/tesseract-ocr/tesseract/wiki



## 更新说明

- 提升用户体验
- 增加python2支持
- 支持验证码识别