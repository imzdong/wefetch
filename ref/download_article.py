# -*- coding:utf-8 -*-

import json
import re
import time
from bs4 import BeautifulSoup
import requests
import os



# 保存页面到本地
def save_html(url_content, htmlDir, file_name):
    f = open(htmlDir + "\\" + file_name + '.html', 'wb')
    f.write(url_content.content)  # save to page.html
    f.close()
    return url_content


# 修改文件,将图片路径改为本地的路径
def update_file(old, new, htmlDir, file_name):
    with open(htmlDir + "\\" + file_name + '.html', encoding='utf-8') as f, open(
            htmlDir + "\\" + file_name + '_bak.html', 'w',
            encoding='utf-8') as fw:  # 打开两个文件，原始文件用来读，另一个文件将修改的内容写入
        for line in f:  # 遍历每行，取出来的是字符串，因此可以用replace 方法替换
            new_line = line.replace(old, new)  # 逐行替换
            new_line = new_line.replace("data-src", "src")
            fw.write(new_line)  # 写入新文件
    os.remove(htmlDir + "\\" + file_name + '.html')  # 删除原始文件
    time.sleep(10)
    os.rename(htmlDir + "\\" + file_name + '_bak.html', htmlDir + "\\" + file_name + '.html')  # 修改新文件名， old -> new
    print('当前保存文件为：' + file_name + '.html')


# 保存图片到本地
def save_file_to_local(htmlDir, targetDir, search_response, domain, file_name):
    obj = BeautifulSoup(save_html(search_response, htmlDir, file_name).content,
                        'lxml')  # 后面是指定使用lxml解析，lxml解析速度比较快，容错高。
    imgs = obj.find_all('img')
    # 将页面上图片的链接加入list
    urls = []
    for img in imgs:
        if 'data-src' in str(img):
            urls.append(img['data-src'])
        elif 'src=""' in str(img):
            pass
        elif "src" not in str(img):
            pass
        else:
            urls.append(img['src'])
    # 遍历所有图片链接，将图片保存到本地指定文件夹，图片名字用0，1，2...
    i = 0
    for each_url in urls:  # 看下文章的图片有哪些格式，一一处理
        if each_url.startswith('//'):
            new_url = 'https:' + each_url
            r_pic = requests.get(new_url)
        elif each_url.startswith('/') and each_url.endswith('gif'):
            new_url = domain + each_url
            r_pic = requests.get(new_url)
        elif each_url.endswith('png') or each_url.endswith('jpg') or each_url.endswith('gif') or each_url.endswith(
                'jpeg'):
            r_pic = requests.get(each_url)
        t = os.path.join(targetDir, str(i) + '.jpeg')  # 指定目录
        print('当前保存图片为：' + t)
        fw = open(t, 'wb')  # 指定绝对路径
        fw.write(r_pic.content)  # 保存图片到本地指定目录
        i += 1
        update_file(each_url, t, htmlDir, file_name)  # 将老的链接(有可能是相对链接)修改为本地的链接，这样本地打开整个html就能访问图片
        fw.close()


# 下载html页面和图片
def save(search_response, file_name):
    htmlDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    targetDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name + '\\imgs1')  # 图片保存的路径，eg,向前文件夹为'D:\Coding', 即图片保存在'D:\Coding\imgs1\'
    if not os.path.isdir(targetDir):  # 不存在创建路径
        os.makedirs(targetDir)
    domain = 'https://mp.weixin.qq.com/s'
    save_html(search_response, htmlDir, file_name)
    save_file_to_local(htmlDir, targetDir, search_response, domain, file_name)


'''

 # 获得登录所需cookies
with open("cookies.txt", "r") as file:
    cookie = file.read()
cookies = json.loads(cookie)
url = "https://mp.weixin.qq.com"
response = requests.get(url, cookies=cookies)
token = re.findall(r'token=(\d+)', str(response.url))[0]
print(token)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Referer": "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token=" + token + "&lang=zh_CN",
    "Host": "mp.weixin.qq.com",
}
f = open("article_link.txt", encoding='utf-8')  # 返回一个文件对象
line = f.readline()  # 调用文件的 readline()方法
for line in open("article_link.txt", encoding='UTF-8'):
    new_line = line.strip()
    line_list = new_line.split("<=====>")
    file_name = line_list[0]
    dir_name = line_list[1]
    requestUrl = line_list[2]
    search_response = requests.get(requestUrl, cookies=cookies, headers=headers)
    save(search_response, file_name)
    print(file_name + "----------------下载完毕：" + dir_name + "----------------下载完毕：" + requestUrl)
    time.sleep(2)
file.close()

 '''

if __name__ == '__main__':
    requestUrl = 'http://mp.weixin.qq.com/s?__biz=MzUzMjY0NDY4Ng==&mid=2247502370&idx=3&sn=20224ddc9f63ffd03037f56264a7ee9f&chksm=fab29c03cdc515153901ff2edf664aaac50b671c7ac97d69d4b027d24a9797d8c9341d77ee12#rd'
    search_response = requests.get(requestUrl)
    save(search_response, "winter")
