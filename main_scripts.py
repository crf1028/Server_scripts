from script_settings import PLATFORM

if PLATFORM == "pc":
    BASE_ROOT = "C:\\Users\\rongfeng\\Dropbox\\"
    SITE_ROOT = BASE_ROOT + "mysite_on_pi_main\\"
    SCRIPT_ROOT = BASE_ROOT + "Python Projects\\Server_scripts\\"
    DATA_DIR = SITE_ROOT + "Data\\"
    STATIC_DIR = SITE_ROOT + "static\\"
    DOWNLOAD_DIR = SCRIPT_ROOT+"OWDown\\"
elif PLATFORM == "pi":
    BASE_ROOT = '/home/rc/'
    SITE_ROOT = BASE_ROOT + 'PySites/ourcase/'
    SCRIPT_ROOT = BASE_ROOT + 'Documents/PyScripts/'
    DATA_DIR = SITE_ROOT + "Data/"
    STATIC_DIR = SITE_ROOT + "static/"
    DOWNLOAD_DIR = BASE_ROOT + "Downloads/"
elif PLATFORM == "osx":
    BASE_ROOT = "/Users/apple/Documents/"
    SITE_ROOT = BASE_ROOT + "mysite_on_pi_main/"
    SCRIPT_ROOT = BASE_ROOT + "Server_scripts/"
    DATA_DIR = SITE_ROOT + "Data/"
    STATIC_DIR = SITE_ROOT + "static/"
    DOWNLOAD_DIR = SCRIPT_ROOT + "OWDown/"


def logging_python_quest(msg):
    if PLATFORM == "pc" or PLATFORM == "osx":
        print msg
    elif PLATFORM == "pi":
        import datetime
        with open(DATA_DIR+ 'python_quest_log.txt', 'a') as pql:
            pql.write(str(datetime.datetime.now().date())+'\t'+msg+'\n')


def file_downloader(url, path2f, file_name):
    import urllib2

    f = urllib2.urlopen(url)
    with open(path2f+file_name, 'wb') as code:
        code.write(f.read())


def ensure(mtd, n):
    import time
    try:
        mtd()
    except:
        if n < 5:
            time.sleep(120)
            n += 1
            ensure(mtd, n)
        else:
            logging_python_quest('fail to perform '+mtd.__name__)


def get_bing_pic_url():
    def process():
        import json, re
        from urllib2 import urlopen

        bing_pic_json_url = 'http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN'

        pic_url = 'http://www.bing.com' + json.load(urlopen(bing_pic_json_url))['images'][0]['urlbase'] + '_1920x1080.jpg'

        k = open(STATIC_DIR + 'home_page.css', 'r')
        t = k.read()
        z = re.sub(r'(http).*(jpg)', pic_url, t)
        k = open(STATIC_DIR + 'home_page.css', 'w')
        k.write(z)
        k.close()

        logging_python_quest('bing pic url changed')
    ensure(process, 0)


def get_smm_price():
    def process():
        from bs4 import BeautifulSoup
        from urllib2 import urlopen, Request
        import re, datetime, json

        hdr = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36(KHTML, like Gecko) Chrome",
        "Accept":"text/html,application/xhtml+xml,application/xml;q = 0.9, image / webp, * / *;q = 0.8"}

        url = 'http://hq.smm.cn/qian'
        soup = BeautifulSoup(urlopen(Request(url, headers=hdr)), "html.parser")
        main_sec = soup.find('span', text=re.compile("SMM"), attrs={'class': 'value1'}).parent
        price_range = main_sec.find('span', {"class", 'value2'}).get_text().strip()
        price_avg = main_sec.find('span', {"class", 'value3'}).get_text().strip()
        price_change = main_sec.find('span', {"class", 'value4'}).get_text().strip()
        increase = True if main_sec.find('span', {"class", 'red'}) else False
        # time_updated = main_sec.parent.find('div', {"class", "itemDateTime"}).get_text().strip()
        today = str(datetime.datetime.now().date())
        data2save = {today:[price_range, price_avg, price_change, increase]}
        # print data2save

        try:
            k = open(DATA_DIR + 'smm_price', 'r')
            old_data = json.load(k)
        except ValueError:
            old_data = {}
        old_data.update(data2save)
        k = open(DATA_DIR + 'smm_price', 'w')
        json.dump(old_data, k)
        k.close()
        with open(DATA_DIR + 'smm_price_daily', 'w') as z:
            json.dump(data2save, z)

        logging_python_quest('smm price get')
    ensure(process, 0)


def get_reddit_hot_info():
    from bs4 import BeautifulSoup
    from urllib2 import urlopen, Request
    import re, json, time
    from datetime import datetime

    NOW = datetime.utcnow()
    base_url = 'https://www.reddit.com/r/Overwatch/hot/?limit=100'

    hdr = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36(KHTML, like Gecko) Chrome",
           "Accept": "text/html,application/xhtml+xml,application/xml;q = 0.9, image / webp, * / *;q = 0.8"}

    soup = BeautifulSoup(urlopen(Request(base_url, headers=hdr)), "html.parser")

    high_light = soup.findAll("span", {"class": "linkflairlabel", "title": lambda s: "Highlight" in s or "Humor" in s})
    dict2store = {}
    for item in high_light:
        if item.parent.find("span", {"class": "domain"}).a.get_text() != "gfycat.com":
            continue
        try:
            comment_n = int(item.parent.parent.find("ul", {"class": "flat-list buttons"}).find('li', {
                "class": "first"}).a.get_text().split(' ')[0])
        except ValueError:
            comment_n = 0
        if not comment_n:
            continue
        item_time = datetime.strptime(
            item.parent.parent.find("p", {"class": "tagline "}).time['datetime'].replace("+00:00", ''),
            "%Y-%m-%dT%H:%M:%S")
        dif = (NOW - item_time).days * 24 + (NOW - item_time).seconds // 3600
        if dif > 47:
            continue
        if not dif:
            dif = 1
        if dif * 4 < comment_n:
            title = item.parent.a.get_text()
            anchor_to_top = item.parent.parent.parent
            gfycat_url = anchor_to_top["data-url"]
            item_id = anchor_to_top["id"]
            unique_code = re.findall(r'\.com/(.*)', gfycat_url)[0]
            gfycat_mp4_url = "https://thumbs.gfycat.com/" + unique_code + "-mobile.mp4"
            gfycat_img_url = "https://thumbs.gfycat.com/" + unique_code + "-mobile.jpg"
            time_added = int(time.time())
            dict2store.update({item_id: [title, gfycat_mp4_url, gfycat_img_url, time_added]})

    d = open(DATA_DIR + 'gfycat_down', 'r')
    try:
        old_dict = json.load(d)
    except ValueError:
        old_dict = {}
    for item in dict2store.keys():
        try:
            old_dict[item]
        except KeyError:
            pass
        else:
            del dict2store[item]
    old_dict.update(dict2store)
    d = open(DATA_DIR + 'gfycat_down', 'w')
    json.dump(old_dict, d)
    logging_python_quest(str(dict2store)+' added')
    d.close()


def download_reddit_video():
    import json
    from time import sleep
    from time import time as t

    d = open(DATA_DIR + 'gfycat_down', 'r')
    old_dict = json.load(d)
    item_list2del = []
    for item in old_dict.keys():
        if len(old_dict[item]) < 5:
            file_name = old_dict[item][0].replace(' ', '_')
            file_downloader(old_dict[item][1], DOWNLOAD_DIR, file_name + ".mp4")
            sleep(5)
            file_downloader(old_dict[item][2], DOWNLOAD_DIR, file_name + ".jpg")
            sleep(5)
            text_f = open(DOWNLOAD_DIR+file_name+".txt", 'wb')
            text_f.write("https://gfycat.com/"+old_dict[item][1].encode('utf-8')[26:-11])
            text_f.close()
            logging_python_quest(file_name + " downloaded")
            old_dict[item].append("downloaded")
            d = open(DATA_DIR + 'gfycat_down', 'w')
            json.dump(old_dict, d)
            d.close()
        elif len(old_dict[item]) == 5:
            time_added = int(old_dict[item][3])
            time_now = int(t())
            if time_now - time_added > 172800:
                item_list2del.append(item)
    else:
        logging_python_quest("gfycat downloaded")
    if item_list2del:
        f = open(DATA_DIR + 'gfycat_down', 'r')
        data1 = json.load(f)
        for item in item_list2del:
            del data1[item]
        f = open(DATA_DIR + 'gfycat_down', 'w')
        json.dump(data1, f)
        f.close()
        logging_python_quest("gfycat record deleted")


def get_ow_reddit_hot():
    from bs4 import BeautifulSoup
    from urllib2 import urlopen, Request
    import re, json, time
    from datetime import datetime

    NOW = datetime.utcnow()
    base_url = 'https://www.reddit.com/r/Overwatch/hot/?limit=100'

    hdr = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36(KHTML, like Gecko) Chrome",
           "Accept": "text/html,application/xhtml+xml,application/xml;q = 0.9, image / webp, * / *;q = 0.8"}

    soup = BeautifulSoup(urlopen(Request(base_url, headers=hdr)), "html.parser")

    high_light = soup.findAll("span", {"class": "linkflairlabel", "title": lambda s: "Highlight" in s or "Humor" in s})
    dict2store = {}
    for item in high_light:
        if item.parent.find("span", {"class": "domain"}).a.get_text() != "gfycat.com":
            continue
        try:
            comment_n = int(item.parent.parent.find("ul", {"class": "flat-list buttons"}).find('li', {
                "class": "first"}).a.get_text().split(' ')[0])
        except ValueError:
            comment_n = 0
        if not comment_n:
            continue
        item_time = datetime.strptime(
            item.parent.parent.find("p", {"class": "tagline "}).time['datetime'].replace("+00:00", ''),
            "%Y-%m-%dT%H:%M:%S")
        dif = (NOW - item_time).days * 24 + (NOW - item_time).seconds // 3600
        if dif > 47:
            continue
        if not dif:
            dif = 1
        if dif * 4 < comment_n:
            title = item.parent.a.get_text()
            anchor_to_top = item.parent.parent.parent
            gfycat_url = anchor_to_top["data-url"]
            item_id = anchor_to_top["id"]
            gfycat_id = re.findall(r'\.com/(.*)', gfycat_url)[0]
            time_added = int(time.time())
            dict2store.update({item_id: [title, gfycat_id, time_added]})

    try:
        d = open(DATA_DIR + 'gfycat_hl', 'r')
        try:
            old_dict = json.load(d)
        except ValueError:
            old_dict = {}
    except IOError:
        d = open(DATA_DIR + 'gfycat_hl', 'wb')
        d.close()
        old_dict = {}

    for item in dict2store.keys():
        try:
            old_dict[item]
        except KeyError:
            pass
        else:
            del dict2store[item]
    old_dict.update(dict2store)
    d = open(DATA_DIR + 'gfycat_hl', 'w')
    json.dump(old_dict, d)
    logging_python_quest(str(dict2store) + ' added')
    d.close()


def update_ow_reddit_hot():
    import json
    from time import time as t
    d = open(DATA_DIR + 'gfycat_hl', 'r')
    old_dict = json.load(d)
    time_now = int(t())
    item2del = []
    for item in old_dict.keys():
        time_added = int(old_dict[item][2])
        if time_now-time_added > 172800:
            item2del.append(item)
    if item2del:
        for item in item2del:
            del old_dict[item]
    d = open(DATA_DIR + 'gfycat_hl', 'w')
    json.dump(old_dict, d)
    d.close()


def sim_get_ow_reddit_hot():
    from bs4 import BeautifulSoup
    from urllib2 import urlopen, Request
    import re, json
    from datetime import datetime

    NOW = datetime.utcnow()
    base_url = 'https://www.reddit.com/r/Overwatch/hot/?limit=100'

    hdr = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36(KHTML, like Gecko) Chrome",
           "Accept": "text/html,application/xhtml+xml,application/xml;q = 0.9, image / webp, * / *;q = 0.8"}

    soup = BeautifulSoup(urlopen(Request(base_url, headers=hdr)), "html.parser")

    # get highlights and make them into dict_raw
    high_light = soup.findAll("span", {"class": "linkflairlabel", "title": lambda s: "Highlight" in s or "Humor" in s})
    dict_raw = {}
    for item in high_light:
        if item.parent.find("span", {"class": "domain"}).a.get_text() != "gfycat.com":
            continue
        try:
            comment_n = int(item.parent.parent.find("ul", {"class": "flat-list buttons"}).find('li', {
                "class": "first"}).a.get_text().split(' ')[0])
        except ValueError:
            comment_n = 0
        if not comment_n:
            continue
        item_time = datetime.strptime(
            item.parent.parent.find("p", {"class": "tagline "}).time['datetime'].replace("+00:00", ''),
            "%Y-%m-%dT%H:%M:%S")
        dif = (NOW - item_time).days * 24 + (NOW - item_time).seconds // 3600
        if dif > 47:
            continue
        if not dif:
            dif = 1
        if dif * 5> comment_n:
            continue
        title = item.parent.a.get_text()
        anchor_to_top = item.parent.parent.parent
        upvotes = anchor_to_top.find('div', {'class': 'score unvoted'}).get_text().encode('utf-8')
        try:
            upvotes = int(upvotes)
        except ValueError:
            continue
        score = comment_n * 10 + upvotes
        gfycat_url = anchor_to_top["data-url"]
        item_id = anchor_to_top["id"]
        gfycat_id = re.findall(r'\.com/(.*)', gfycat_url)[0]
        dict_raw.update({item_id: [title, gfycat_id, score]})

    # find highlights that rank top 5 and store them in dict2store
    if len(dict_raw) > 5:
        dict2store = {}
        score_list = sorted([dict_raw[item][2] for item in dict_raw.keys()])[-5:]
        for item in dict_raw.keys():
            if not score_list:
                break
            elif dict_raw[item][2] in score_list:
                dict2store.update({item:dict_raw[item]})
                score_list.remove(dict_raw[item][2])
    else:
        dict2store = dict_raw

    # save to gfycat_hl
    d = open(DATA_DIR + 'gfycat_hl', 'wb')
    json.dump(dict2store, d)
    d.close()