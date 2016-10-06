#!/usr/bin/env python
from logger import ensure


def get_bing_pic_url():
    import json, re
    from urllib2 import urlopen
    from logger import logging_python_quest

    bing_pic_json_url = 'http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN'

    pic_url = 'http://www.bing.com' + json.load(urlopen(bing_pic_json_url))['images'][0]['urlbase'] + '_1920x1080.jpg'

    k = open('/home/rc/PySites/ourcase/static/home_page.css', 'r')
    t = k.read()
    z = re.sub(r'(http).*(jpg)', pic_url, t)
    k = open('/home/rc/PySites/ourcase/static/home_page.css', 'w')
    k.write(z)
    k.close()

    logging_python_quest('bing pic url changed')


ensure(get_bing_pic_url, 0)
