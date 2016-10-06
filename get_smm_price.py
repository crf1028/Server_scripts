#!/usr/bin/env python
from logger import ensure


def get_smm_price():
    from bs4 import BeautifulSoup
    from urllib2 import urlopen, Request
    import re, datetime, json
    from logger import logging_python_quest

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
        k = open('/home/rc/PySites/ourcase/Data/smm_price', 'r')
        old_data = json.load(k)
    except ValueError:
        old_data = {}
    old_data.update(data2save)
    k = open('/home/rc/PySites/ourcase/Data/smm_price', 'w')
    json.dump(old_data, k)
    k.close()
    with open('/home/rc/PySites/ourcase/Data/smm_price_daily', 'w') as z:
        json.dump(data2save, z)

    logging_python_quest('smm price get')


ensure(get_smm_price,0)
