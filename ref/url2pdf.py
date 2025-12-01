import pdfkit
import datetime
import wechatsogou

ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)



1 requests.get("https://mp.weixin.qq.com/cgi-bin/appmsg", headers={
 2     "Cookie": "cookie内容根据自己接口修改",
 3     "User-Agent": "根据自己接口修改"
 4 }, params = {
 5     "action": "list_ex",
 6     "begin": "0",
 7     "count": "1",
 8     "fakeid": "根据自己接口的fakeid修改",
 9     "type": "9",
10     "token": "根据自己接口的token修改",
11     "lang": "zh_CN",
12     "f": "json",
13     "ajax": "1"
14 }, verify=False).json()

爬取单个接口


1 import json
 2 import requests
 3 import time
 4 import random
 5 import yaml
 6 import os
 7
 8 # headers解析
 9 with open("headers.yaml", 'rb') as fp:
10     config = yaml.load(fp, Loader=yaml.SafeLoader)
11
12 headers = {
13     "Cookie": config['cookie'],
14     "User-Agent": config['user_agent']
15 }
16
17 # 请求参数设置
18 url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
19 begin = "0"         # begin 为开始页码，0代表第1页，从最新开始抓
20 count = "5"         # count 为每页获取的文章个数
21 params = {
22     "action": "list_ex",
23     "begin": begin,
24     "count": count,
25     "fakeid": config['fakeid'],
26     "type": "9",
27     "token": config['token'],
28     "lang": "zh_CN",
29     "f": "json",
30     "ajax": "1"
31 }
32
33 # 结果文件设置
34 wechat_spider_json_file = "wechat_spider_data.json"
35
36 # 获取当前json文件内容，计算已爬取的页数
37 if os.path.exists(wechat_spider_json_file):
38     with open(wechat_spider_json_file, "r") as file:
39         wechat_app_msg_list = json.load(file)
40         #print("之前已抓取{}页文章,将从下一页开始抓取".format(1+len(wechat_app_msg_list))
41 else:
42     wechat_app_msg_list = []
43
44 i = len(wechat_app_msg_list)
45 print("之前已抓取{}页文章,将从下一页开始抓取".format(i)
46
47 # 使用while循环获取, 直至抓取完成
48 while True:
49
50     init = i  * int(count)
51     params["begin"] = str(init)
52
53     # 随机等待几秒，避免被微信识别到
54     num = random.randint(1,10)
55     print("等待{0}秒，准备抓取第{1}页，每页{2}篇".format(num, (i+1), count))
56     time.sleep(num)
57
58     # 执行抓取接口
59     resp = requests.get(url, headers=headers, params = params, verify=False)
60
61     # 抓取失败，退出
62     if resp.json()['base_resp']['ret'] == 200013:
63         print("触发微信机制，抓取失败，当前抓取第{0}页，每页{1}篇".format((i+1), count))
64         break
65
66     # 抓取完成，结束
67     if len(resp.json()['app_msg_list']) == 0:
68         print("已抓取完所有文章，共抓取{0}篇".format((i+1)*int(count))
69         break
70
71     # 抓取成功，json格式保存返回的接口信息
72     wechat_app_msg_list.append(resp.json())
73     print("抓取第{0}页成功，每页{1}篇, 共抓取了{2}篇".format((i+1), count, (i+1)*int(count)))
74
75     # 循环下一页
76     i += 1
77
78 # json格式保存结果至文件
79 with open(wechat_spider_json_file, "w") as file:
80     file.write(json.dumps(wechat_app_msg_list, indent=2, ensure_ascii=False))

爬取所有文章


'''
第四种：使用pdfkit。直接将url处理成pdf文档，该方法简单方便，转换的pdf文档内容与原文章排版一致，文档内容可以自行加批注，文内链接也可点击，还可以自己设置标题和正文，推荐使用。

使用该方法的时候，我发现如果直接用的话，会显示不了文章中的图片，所以优化了下代码。
'''
def url2pdf(url, title):
    '''
    使用pdfkit生成pdf文件
    :param url: 文章url
    :param title: 文章标题
    :param targetPath: 存储pdf文件的路径
    '''

    try:
        content_info = ws_api.get_article_content(url)
        path_wkthmltopdf = r'D:\wkhtmltox\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

    except:
        return False

    # 处理后的html
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
    </head>
    <body>
    <h2 style="text-align: center;font-weight: 400;">{title}</h2>
    {content_info['content_html']}
    </body>
    </html>
    '''

    pdfkit.from_string(html, 'test.pdf', configuration=config)


url2pdf
方法