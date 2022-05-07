# 获取网络时间
import logging
import threading
import time
import os

from future.backports.http.client import HTTPConnection #高并发用
# from http.client import HTTPConnection


def getBeijinTime():
    """获取北京时间www.beijing-time.org"""
    try:
        conn = HTTPConnection("www.beijing-time.org")
        conn.request("GET", "/t/time.asp", headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"})
        response = conn.getresponse()
        # print(response.status, response.reason)
        if response.status == 200:
            # 解析响应的消息
            result = response.read().decode()
            data = result.split(";")
            year = data[1][len("nyear") +3 : len(data[1])]
            month = data[2][len("nmonth") + 3: len(data[2]) ]
            day = data[3][len("nday") + 3: len(data[3])]
            wday = data[4][len("nwday")+3 : len(data[4])]  #星期
            hours = data[5][len("nhrs") + 3: len(data[5]) ] #小时
            minute = data[6][len("nmin") + 3: len(data[6]) ] #分
            second = data[7][len("nsec") + 3: len(data[7]) ] #秒
            beijinTimeStr = "%s-%s-%s %s:%s:%s" % (year, month, day, hours, minute, second)
            beijinTime = {'year':year,'month':month, 'day':day, 'hours':hours, 'minute':minute, 'second':second, 'wday':wday}
            print('获取网络日期',beijinTimeStr)
            return beijinTime,beijinTimeStr
    except:
        logging.exception("获取网络北京时间异常")
        syncLocalTime()
        return None



def syncLocalTime():
    """同步本地时间"""
    print(time.localtime()[:6].__str__())
    print(f"电脑本地时间为: %d-%d-%d %d:%d:%d 星期{time.localtime().tm_wday == 7 if 0 else time.localtime().tm_wday+1}" % time.localtime()[:6])
    beijinTime = getBeijinTime()
    if beijinTime is None:
        logging.error("获取北京时间失败，3秒后重新获取")
        timer = threading.Timer(3.0, syncLocalTime)
        timer.start()   #失败，我就起一个线程，并且不关闭
    else:
        # logging.warning(f"获取到的北京时间为:{beijinTime[1]}" )
        year, month, day, hours, minute, second, wday = beijinTime[0].values()
        os.system("date %d-%d-%d" % (int(year), int(month),int(day)))  # 设置日期
        os.system("time %d:%d:%d" % (int(hours), int(minute),int(second)))  # 设置时间
        logging.warning("同步后电脑,现在本地时间: %d-%d-%d %d:%d:%d \n" % time.localtime()[:6])

syncLocalTime()