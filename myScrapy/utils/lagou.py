import os
import re
from retrying import retry
import time
from lxml import etree

import requests

def lagou():
    headers = {"Accept": "application/json,text/javascript, */*;q=0.01",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.8",
               "Connection": "keep-alive",
               "Content-Length": "25",
               "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
               "Host": "www.lagou.com",
               "Origin": "https://www.lagou.com",
               "Referer": "https://www.lagou.com/jobs/list_Python?city=%E6%B7%B1%E5%9C%B3&cl=false&fromSearch=true&labelWords=&suginput=",
               "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
               "X-Anit-Forge-Code": "0",
               "X-Anit-Forge-Token": "None",
               "X-Requested-With": "XMLHttpRequest"}

    url = 'https://www.lagou.com/jobs/positionAjax.json'
    query_params = {"city": "深圳",
                    "needAddtionalResult": "false"}
    form_datas = {"first": "true",
                  "pn": "1",
                  "kd": "人工智能"}

    response = requests.post(url, headers=headers, params=query_params, data=form_datas)
    print(response.text)

def lagou_detail(url):
    session = requests.session()
    response = session.get(url,
                     headers={
                         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                     })
    resHtml = response.text
    html = etree.HTML(resHtml)
    # 职位描述
    description = html.xpath('//*[@id="job_detail"]/dd[2]/div/p/text()')
    return html

@retry(stop_max_attempt_number=3)
def proxy_Test(proxy):
    print('processing:', proxy)
    response = requests.get('http://httpbin.org', proxies={'http': proxy}, timeout=5)
    assert response.status_code == 200
    return proxy

def proxy_pool(queue):
    for i in range(5):
        print(os.getpid(), i+1, '次')
        time.sleep(1)
        ip_port = requests.get("http://182.61.60.153:5010/get/").text
        proxy = "http://%s" % ip_port
        try:
            proxy = proxy_Test(proxy)
            queue.put(proxy)
        except Exception as e:
            print(e)

# def proxyTest():
#     while True:
#         # time.sleep(1)
#         ip_port = requests.get("http://182.61.60.153:5010/get/").text
#         proxy = "http://%s" % ip_port
#         for i in range(2):
#             print(os.getpid(), '第%d次:'%(i+1),proxy)
#             try:
#                 response = requests.get('http://httpbin.org', proxies={'http': proxy})
#                 status_code = response.status_code
#             except Exception as e:
#                 status_code = None
#             if status_code == 200:
#                 break
#             else:
#                 proxy = 'https://%s' % ip_port
#         else:
#             print(os.getpid(), 'all down')
#             continue
#         print(os.getpid(), 'ok:', proxy)
#         break


if __name__ == '__main__':
    # company_link = 'https://www.lagou.com/jobs/{pos_id}.html'.format(pos_id=3893733)
    # response = lagou_detail(company_link)
    # print(response.text)
    # lagou()
    # 183.233.89.222
    from multiprocessing import Pool
    from multiprocessing import Process
    from multiprocessing import JoinableQueue

    queue = JoinableQueue()
    # pool = Pool(processes=4)
    for i in range(4):
        Process(target=proxy_pool, args=(queue,)).start()
        # pool.apply_async(proxy_pool, args=(queue,))
    # pool.close()
    # pool.join()
    while True:
        print('queue =', queue.qsize())
        time.sleep(5)
    print('ending')