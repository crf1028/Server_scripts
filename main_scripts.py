from script_settings import PLATFORM

if PLATFORM == "pc":
    BASE_ROOT = "C:\\Users\\rongfeng\\Dropbox\\"
    SITE_ROOT = BASE_ROOT + "mysite_on_pi_main\\"
    SCRIPT_ROOT = BASE_ROOT + "Python Projects\\Server_scripts\\"
    DATA_DIR_ROOT = SITE_ROOT + "Data\\"
    STATIC_DIR_ROOT = SITE_ROOT + "static\\"
elif PLATFORM == "pi":
    BASE_ROOT = '/home/rc/'
    SITE_ROOT = BASE_ROOT + 'PySites/ourcase/'
    SCRIPT_ROOT = BASE_ROOT + 'Documents/PyScripts/'
    DATA_DIR_ROOT = SITE_ROOT + "Data/"
    STATIC_DIR_ROOT = SITE_ROOT + "static/"


def logging_python_quest(msg):
    import datetime
    with open(DATA_DIR_ROOT+'python_quest_log.txt', 'a') as pql:
        pql.write(str(datetime.datetime.now().date())+'\t'+msg+'\n')


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

        k = open(STATIC_DIR_ROOT+'home_page.css', 'r')
        t = k.read()
        z = re.sub(r'(http).*(jpg)', pic_url, t)
        k = open(STATIC_DIR_ROOT+'home_page.css', 'w')
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
            k = open(DATA_DIR_ROOT+'smm_price', 'r')
            old_data = json.load(k)
        except ValueError:
            old_data = {}
        old_data.update(data2save)
        k = open(DATA_DIR_ROOT+'smm_price', 'w')
        json.dump(old_data, k)
        k.close()
        with open(DATA_DIR_ROOT+'smm_price_daily', 'w') as z:
            json.dump(data2save, z)

        logging_python_quest('smm price get')
    ensure(process, 0)

