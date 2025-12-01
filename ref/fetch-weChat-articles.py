import requests
import datetime
import config
import time

'''
关键字解释：
cooike帮我们绕过登录过程
fakeid是目标公众号的唯一标识符
user-agent可以模拟浏览器请求至此信息获取部分完成，下面开始开始代码部分。
'''

headers = {
    "cookie": "appmsglist_action_3094473706=card; ua_id=ux3LuOWf6ocUYGvpAAAAAHuBi-Ig1E1HhD6Q7B9NLxg=; wxuin=10469175239859; _qimei_uuid42=185100b362c100066c02924fda63204ab606aea5a0; _qimei_fingerprint=4b609d3d1c5c156310315cbfe2e03de0; _qimei_q36=; _qimei_h38=fded78e16c02924fda63204a0200000a118510; mm_lang=zh_CN; ETCI=e3e5d3e1a1ea40da9bf2c4809a00d72f; _clck=3094473706|1|fnr|0; uuid=bc53c5ed137b5a9ebd88ba785a76ac65; rand_info=CAESIB1n4FNRqXU/CYHOT/YUY5kCiGUFMP1XUeBxYWLC1bNp; slave_bizuin=3094473706; data_bizuin=3094473706; bizuin=3094473706; data_ticket=FwuMP6TlpAG3LybOPQpXG2/aT8Aud7ltAuFjPbDFpsFY6UlkbXwY/UsGdCG28If8; slave_sid=SHp4Tm1pZlFsd2hDeFFNcEJFUlM5S1ByZXRuenlDTkR0MFZWemJhTjYzbEszRlI1MHRRd3hIZ3BZenJIUnBRQ2JkNmRwVEZfYU04MUJUS2xMUGwxYk9BOF80aFpHVVp0RWFnSEYwTnlSbFpranFUMTZGYjV5dkhvalVJMWhNOU43SFFWQTBESHJOVVE1aWlz; slave_user=gh_195ed1058a3c; xid=6b509838f192f6142e6e7a2ff5fac532; rewardsn=; wxtokenkey=777; _clsk=7dx3qc|1721878774146|1|1|mp.weixin.qq.com/weheat-agent/payload/record",
    "X-Requested-With": "XMLHttpRequest",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
}

url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'
fad = 'MzUzMjY0NDY4Ng%3D%3D'
token = ''# 爬不同公众号只需要更改 fakeid

# sub=list&search_field=null&begin=0&count=5&query=&fakeid=MjM5MzU1NzkxNQ%3D%3D&type=101_1&free_publish_type=1&sub_action=list_ex&token=1857985110&lang=zh_CN&f=json&ajax=1

# 会封锁的，但是隔一段时间就会解封了。拉取间隔长一点，像同一个公众号的不同文章间隔30s获取一次，不同公众号间隔1分钟，这样就基本不会被封。虽然总体时间长了点，但是胜在稳定

def do_query_list():
    count = 5
    for item in config.FAKE_ID_LIST:
        num = 0
        while True:
            infoList = do_acquire(num, item['fakeId'], count, item['name'])
            for info in infoList:
                db.insert_info_reptile_data(info)
            if count > len(infoList):
                break
            # 间隔10秒防止被封
            time.sleep(10)
            num += 5

# 查询回来的文章对象
""""
{
  "aid": "2658870927_1",
  "album_id": "0",
  "appmsg_album_infos": [],
  "appmsgid": 2658870927,
  "checking": 0,
  "copyright_type": 0,
  "cover": "https://mmbiz.qlogo.cn/sz_mmbiz_jpg/ibQ2cXpBDzUO30PiaMTpymX1DO8UfrZSJVBvSMksJqvKqQMcic0d6l9npiaMHxWLUbxthrylK2zYdU6dibsB0UnNTCg/0?wx_fmt=jpeg",
  "create_time": 1688882993,
  "digest": "",
  "has_red_packet_cover": 0,
  "is_pay_subscribe": 0,
  "item_show_type": 11,
  "itemidx": 1,
  "link": "http://mp.weixin.qq.com/s?__biz=MjM5NzI3NDg4MA==&mid=2658870927&idx=1&sn=644b8b17ba102ebdc61b09a5991720ec&chksm=bd53f2e08a247bf6816c4ef12c2692785f9e95259c54eec20a1643eeff0a41822a1fa51f6550#rd",
  "media_duration": "0:00",
  "mediaapi_publish_status": 0,
  "pay_album_info": {"appmsg_album_infos": []},
  "tagid": [],
  "title": "“现实版许三多”，提干了！",
  "update_time": 1688882992
}
"""


# 获取文章
def do_acquire(number, fakeId, count, author):
    """
    需要提交的data
    以下个别字段是否一定需要还未验证。
    注意修改yourtoken,number
    number表示从第number页开始爬取，为5的倍数，从0开始。如0、5、10……
    token可以使用Chrome自带的工具进行获取
    fakeid是公众号独一无二的一个id，等同于后面的__biz
    """
    data = {
        "token": token,
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "action": "list_ex",
        "begin": number*5,
        "count": count,
        "query": "",
        "fakeid": fakeId,
        "type": "9",
    }
    # 使用get方法进行提交
    content_json = requests.get(url, headers=headers, params=data).json()
    article_list = []
    now_time = datetime.now()
    # 返回了一个json，里面是每一页的数据
    for item in content_json["app_msg_list"]:
        # 提取每页文章的标题及对应的url
        dt = datetime.fromtimestamp(item["create_time"])
        diff = now_time - dt
        if diff.days <= config.QUERY_TIME_RANGE:
            content = get_article_content(item["link"])
            if filerInfo(content):
                article_list.append(
                    make_data_obj(item["title"], author, item["cover"], "", author, item["link"], content, dt))
                print(item["title"])
            # 间隔5秒防止被封
            time.sleep(5)
        else:
            break
    return article_list

def make_soup(curl):
    hdr = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }
    req = urllib.request.Request(curl, headers=hdr)
    html = urllib.request.urlopen(req).read()
    return BeautifulSoup(html,'html.parser')

def get_content(curl):
    data = {}
    soup = make_soup(curl)
    if soup.find('h1', attrs={'id': 'activity-name'}) == None:
        data['title'] = "Nonetipycal Type"
    else:
        # Get Document Title
        data['title'] = soup.find('h1', attrs={'id': 'activity-name'}).string.strip()
        # Get the publish date parameter
        dateframe = re.findall(r'var ct\s*=\s*.*\d{10}', str(soup))
        # split the parameter as a list
        date = re.split('"', dateframe[0])
        #format the publish date
        data['date'] = time.strftime("%Y-%m-%d",time.localtime(int(date[1])))
        data['time'] = time.strftime("%Y-%m-%d %H:%M",time.localtime(int(date[1])))
        # Get the content
        data['content'] = soup.find('div', attrs={'id': 'js_content'})
        #this makes a list of bs4 element tags img
        data['images'] = [img for img in soup.find('div', attrs={'id': 'js_content'}).find_all('img')]
    return data

# 将内容换成字符串类型
def get_article_content(url):
    bf = get_beautiful_soup(url)
    div = bf.find(id='page-content')
    js_content = div.find(id='js_content')
    js_content['style'] = 'visibility: initial'
    filter_tag_src(div)
    return str(div)

if __name__ == '__main__':
    do_query_list()
