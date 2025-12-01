
def getwxlist(wxid, rootpath):
    with open("wechat.yaml", "r", encoding=('utf-8')) as file:
        file_data = file.read()
    config = yaml.safe_load(file_data)
    headers = {
        "Cookie": config['cookie'],
        "User-Agent": config['user_agent']
    }
    # 请求参数
    url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
    begin = "0"
    params = {
        "action": "list_ex",
        "begin": begin,
        "count": "5",
        "fakeid": wxid,
        "type": "9",
        "token": config['token'],
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1"
    }
    wxlistfile = rootpath + "/wxlist.xlsx"
    # 获取历史抓取记录
    history = geturl(wxid, rootpath)
    wb = openpyxl.load_workbook(wxlistfile)
    ws = wb.active
    # 在不知道公众号有多少文章的情况下，使用while语句
    # 也方便重新运行时设置页数
    i = 0
    # 新增抓取计数
    j = 0
    flag = False
    while True:
        begin = i * 5
        params["begin"] = str(begin)
        # 随机暂停几秒，避免过快的请求导致过快的被查到
        time.sleep(random.randint(1, 10))
        resp = requests.get(url, headers=headers, params=params, verify=False)
        # 微信流量控制, 退出
        if resp.json()['base_resp']['ret'] == 200013:
            print("frequencey control, stop at {}".format(str(begin)))
            time.sleep(3600)
            continue
        # 如果返回的内容中为空则结束
        if len(resp.json()['app_msg_list']) == 0:
            print("all ariticle parsed")
            break
        msg = resp.json()
        if "app_msg_list" in msg:
            for item in msg["app_msg_list"]:
                if item['link'] in history:
                    flag = True
                    break
                row = [item['title'], item['link']]
                ws.append(row)

                j += 1
            print(f"第{i}页爬取成功\n")
        if flag == True:
            print(f"新增页面抓取已完成,{j}篇文章已添加\n")
            break
        # 翻页
        i += 1
    wb.save(wxlistfile)


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


def saveData(curl, rootpath):
    data = get_content(curl)
    htmlroot = rootpath + '/html'
    image_links = []
    if data.get('images') != None:
        if len(data['images']) != 0:
            # compile our unicode list of image links
            image_links = [each.get('data-src') for each in data['images']]
            # create img folder
            # imgFolder = validateTitle (data['time'].split(' ')[0])
            imgFolder = validateTitle(data['date'])
            imgDst = os.path.join(htmlroot, 'imgs', imgFolder).replace('\\', '/')
            if not os.path.exists(imgDst):
                os.mkdir(imgDst)  # make directory
            for each in image_links:
                filename = each.split('/')[-2]
                # convert abs address
                each = urllib.parse.urljoin(curl, each)
                # save images
                urllib.request.urlretrieve(each, os.path.join(imgDst, filename).replace('\\', '/'))
                # join a file name with title and data & replace ilegal tags.
        filename = validateTitle(data['title'] + data['date'] + '.html')
        # replace ilegal tags
        saveDst = os.path.join(htmlroot, filename).replace('\\', '/')
        # copy an empty template
        shutil.copyfile(os.path.join(htmlroot, "content.html"), saveDst)
        with open(saveDst) as inf:
            txt = inf.read()
        soup = BeautifulSoup(txt, 'html.parser')
        soup.title.string = data['title']
        soup.find('h1', attrs={'id': 'activity-name'}).string = data['title']
        soup.find('em', attrs={'id': 'publish_time'}).string = data['time']

        cleanSoup = data['content']
        if len(image_links) != 0:
            for each in image_links:
                filename = each.split('/')[-2]
                srcNew = "./imgs/" + imgFolder + "/" + filename

                cleanSoup.find('img', {'data-src': each})['src'] = srcNew
                # cleanSoup = BeautifulSoup(str(originalSoup).replace(old, new))
                # cleanSoup = BeautifulSoup(str(cleanSoup).replace(each, srcNew),'html.parser')
        cleanSoup = BeautifulSoup(str(cleanSoup).replace('visibility: hidden;', ' '), 'html.parser')
        soup.find('div', attrs={'id': 'js_content'}).replace_with(cleanSoup)

        # Format the parsed html file
        htmlcontent = soup.prettify()
        # print(htmlcontent)

        with open(saveDst, "wt", encoding=("utf-8")) as f:
            f.write(htmlcontent)
        savetolist(curl, data['title'], saveDst, data['date'], rootpath)
    else:
        saveDst = "None"
        saveDate = time.strftime('%Y-%m-%d')
        savetolist(curl, data['title'], saveDst, saveDate, rootpath)


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # replace to _
    return new_title


def savetolist(curl, ctitle, lcfile, date, rootpath):
    lclist = rootpath + '/lclist.xlsx'
    wb = openpyxl.load_workbook(lclist)
    ws = wb.active
    row = [curl, ctitle, lcfile, date]
    ws.append(row)
    wb.save(lclist)