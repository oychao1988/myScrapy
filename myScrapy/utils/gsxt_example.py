# -*- encoding: utf-8 -*-
import os

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from lxml import etree
import requests
import re
import time
import json
import pymysql
import redis
import chardet

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,und;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 "
}

# set phantomJS's agent to Firefox
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = \
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 "

# 根据实际的path改写，我的是mac，路径为"/usr/local/bin/PhantomJS"
phantomjsPath = os.getcwd() + "/phantomjs-2.1.1-linux-x86_64/bin/phantomjs"
driver = webdriver.PhantomJS(executable_path=phantomjsPath, desired_capabilities=dcap)

conn = pymysql.connect(host="127.0.0.1", user="root", password="mysql", database="invoice2", port=3306,
                       charset='utf8')
curs = conn.cursor()
redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)


def get_cookies(url):
    cookie_list = {}
    driver.get(url)
    time.sleep(2)
    cookies = driver.get_cookies()
    for co in cookies:
        if co in cookies:
            if co['name'] == '__jsl_clearance' or co['name'] == '__jsluid':
                cookie_list[co['name']] = co['value']
    driver.quit()
    cookies = requests.utils.add_dict_to_cookiejar(cj=None, cookie_dict=cookie_list)
    return cookies


def make_session(url):
    global headers
    cookies = get_cookies(url)
    s = requests.Session()
    s.cookies = cookies
    s.headers = headers
    return s


def fetch(ids, version):
    redis.set('version', version)
    for province_id in ids:
        # target_url 对应每个省
        target_light_url = "http://www.gsxt.gov.cn/affiche-query-area-info-paperall.html?" \
                           "noticeType=11&areaid=100000&noticeTitle=&regOrg=" + province_id
        target_serious_url = "http://www.gsxt.gov.cn/affiche-query-area-info-paperall.html?" \
                             "noticeType=21&areaid=100000&noticeTitle=&regOrg=" + province_id
        time.sleep(2)
        print(target_light_url)
        print(target_serious_url)
        # 每省5页
        for i in range(1, 6):
            data = {'draw': i, 'start': (i - 1) * 10, 'length': 10}
            try:
                response = s.post(target_light_url, data=data, verify=False)
                res_obj = json.loads(response.content)
            except Exception as e:
                pass
            else:
                res_dict = res_obj.get('data', None)
                info_list = []
                if res_dict:
                    # 每页10条
                    for info in res_dict:
                        info_dict = {}
                        info_id = info.get('noticeId')
                        info_title = info.get('noticeTitle')
                        info_content = info.get('noticeContent')
                        info_dict['info_id'] = info_id
                        info_dict['info_title'] = info_title
                        info_dict['info_content'] = info_content
                        info_list.append(info_dict)
                parse(info_list, version, flag=0)

            try:
                response = s.post(target_serious_url, data=data, verify=False)
                res_obj = json.loads(response.content)
            except Exception as e:
                pass
            else:
                res_dict = res_obj.get('data', None)
                info_list = []
                if res_dict:
                    for info in res_dict:
                        info_dict = {}
                        info_id = info.get('noticeId')
                        info_title = info.get('noticeTitle')
                        info_content = info.get('noticeContent')
                        info_dict['info_id'] = info_id
                        info_dict['info_title'] = info_title
                        info_dict['info_content'] = info_content
                        info_list.append(info_dict)
                parse(info_list, version, flag=1)


def parse(info_list, version, flag):
    no_num_list = []
    num_list = []
    for info_dict in info_list:
        info_id = info_dict.get('info_id')
        info_title = info_dict.get('info_title').encode('utf-8')
        info_content = info_dict.get('info_content').encode('utf-8')
        try:
            pattern = re.compile(r'\w{14,19}')
            num = pattern.findall(info_content)
            if num[0]:
                num = num[0]
            else:
                num = None
        except Exception as e:
            pass
        if flag == 0:
            try:
                pattern = re.compile(
                    r"^关于将(.+)的列入经营|^关于将(.+)列入经营|^关于(.+)的列入经营|^关于(.+)列入|.+列入(.+)经营异常|^(.+)列入经营异常名录|个体工商户(.+)\(经营者")
                company = pattern.findall(info_title)
                for com in company[0]:
                    if com:
                        # com = com.encode('utf-8')
                        str_type = chardet.detect(com)
                        code = str_type['encoding']
                        print('111code==', code)

                        if num:
                            # num = num.encode('utf-8')
                            light = (com, num, info_id, 1, version)
                            num_list.append(light)
                        else:
                            light = (com, info_id, 1, version)
                            no_num_list.append(light)
            except Exception as e:
                pass

        else:
            try:
                pattern = re.compile(r"^关于(.+)列入严重违法|(.+)列入严重违法企业名单|.+列入(.+)严重违法")
                company = pattern.findall(info_title)
            except Exception as e:
                pass
            finally:
                if not company:
                    com = info_content.split('统一')[0].decode('utf-8')[:-1]
                    com = com.encode('utf-8')
                    str_type = chardet.detect(com)
                    code = str_type['encoding']
                    print('222code==', code)
                    if num:
                        # num = num.encode('utf-8')
                        serious = (com, num, info_id, 2, version)
                        num_list.append(serious)
                    else:
                        serious = (com, info_id, 2, version)
                        no_num_list.append(serious)

                else:
                    try:
                        for com in company[0]:
                            if com:
                                # com = com.encode('utf-8')
                                str_type = chardet.detect(com)
                                code = str_type['encoding']
                                print('333code==', code)
                                if num:
                                    # num = num.encode('utf-8')
                                    serious = (com, num, info_id, 2, version)
                                    num_list.append(serious)
                                else:
                                    serious = (com, info_id, 2, version)
                                    no_num_list.append(serious)
                    except Exception as e:
                        pass

    try:
        if num_list:
            execute_sql(num_list, 0)
        elif no_num_list:
            execute_sql(no_num_list, 1)
    except Exception as e:
        print(e)



def execute_sql(list, f):
    if f == 0:
        sql = "INSERT INTO company_black_list (xfmc, xfsbh, noticeid, degree, version) VALUES (%s, %s, %s, %s, %s)"
        print(sql)

        curs.executemany(sql, list)
        conn.commit()
    else:
        sql = "INSERT INTO company_black_list (xfmc, noticeid, degree, version) VALUES (%s, %s, %s, %s)"
        print(sql)

        curs.executemany(sql, list)
        conn.commit()


def delete_sql():
    version = redis.get('version')
    sql = "DELETE FROM company_black_list where version={}".format(int(version))
    curs.execute(sql)
    conn.commit()


if __name__ == '__main__':
    url = "http://www.gsxt.gov.cn/corp-query-entprise-info-xxgg-100000.html"
    s = make_session(url)
    r = s.get(url, verify=False)
    print(r)

    con = r.content.replace(b'\n', b'').replace(b'\t', b'').replace(b'\r', b'')
    content = etree.HTML(con)
    id_list = content.xpath('//div[@class="label-list"]/div/@id')
    version = redis.get('version')
    # version 更新，方便删除旧数据
    if version is None:
        version = 1
    else:
        version = int(version) + 1
    fetch(id_list, version)
    # delete_sql()
    curs.close()
    conn.close()
# ---------------------
# 作者：fenglei0415
# 来源：CSDN
# 原文：https: // blog.csdn.net / fenglei0415 / article / details / 81865379
# 版权声明：本文为博主原创文章，转载请附上博文链接！