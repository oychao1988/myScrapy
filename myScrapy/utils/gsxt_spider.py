import os

import requests
from faker import Factory
import time
from selenium import webdriver

from myScrapy.settings import PROXY_POOL_SERVER


class GsxtSpider():
    name = 'GsxtSpider'
    def __init__(self, keyword):
        self.keyword = keyword
        self.fake = Factory.create('zh_CN')
        self.user_agent = self.fake.user_agent()
        self.proxy = 'http://' + requests.get(PROXY_POOL_SERVER).text

        # seleniuim 登录、验证、爬取
        self.chromeOptions = webdriver.ChromeOptions()
        self.chromeOptions.add_argument('--user-agent=%s' % self.user_agent)
        self.chromeOptions.add_argument('--proxy-server=%s' % self.proxy)
        self.driver = webdriver.Chrome(os.getcwd() + '/chromedriver')
        # driver.set_page_load_timeout(10)  # 10秒
        self.save_dir = ''

    # 获取查询结果页面
    def index(self):
        # 打开首页
        index_url = 'http://www.gsxt.gov.cn/'
        spider_detect_url = 'http://www.gsxt.gov.cn/spider'
        global save_dir
        save_dir = './' + self.keyword + '/'
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)

        while True:
            try:
                self.driver.get(index_url)
                time.sleep(10)
                # 在输入框输入关键字
                self.driver.find_element_by_id('keyword').send_keys(self.keyword)
                time.sleep(5)
                self.driver.find_element_by_id('btn_query').click()
                time.sleep(20)
                # 获取页面源码
                page_source = self.driver.page_source
            except Exception as e:
                print(e)
                self.driver.refresh()
                continue
            # 如果返回内容为有效信息，则继续
            if 'class="search_result g9"' in page_source:
                break
        with open(save_dir + self.keyword + '_search_list.txt', 'w') as f:
            f.write(page_source)
        print(self.keyword + '_search_list.txt已保存')

    # 定位点击进入详情页位置
    def detail_elements(self):
        # result_count = html_.xpath('//div[@id="advs"]/div/div[2]/a')
        # urls_lsit = result_count[0].xpath('./@href')
        _elements = self.driver.find_elements_by_tag_name('h1')
        elements = [(element, element.text) for element in _elements]
        return elements

    def detail(self, element):
        file_name = element[1] + '_detail.txt'
        if os.path.exists(save_dir + file_name):
            print(file_name + '已存在')
            return
        while True:
            try:
                element[0].click()
                time.sleep(10)
                # 切换到新开的窗口
                windows = self.driver.window_handles
                self.driver.switch_to.window(windows[-1])
                # 滚动到页面最底部，需要多次下拉 # TODO 具体下拉次数，详情页的下一页
                for i in range(7):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(5)
            except Exception as e:
                print(e)
                time.sleep(10)
                continue
            # 判断公司名是否存在
            page_source = self.driver.page_source
            # 关闭标签页
            self.driver.close()
            windows = self.driver.window_handles
            # 切换回搜索列表页
            self.driver.switch_to.window(windows[0])
            # 如果返回内容包含公司名，则继续
            if element[1] in page_source:
                break
        with open(save_dir + file_name, 'w') as f:
            f.write(page_source)
        print(file_name + '已保存')

    # 搜索列表的下一页
    def next_page(self):
        for i in range(3):
            try:
                next_page_element = self.driver.find_element_by_xpath('//a[text()="下一页"]')
                # 点击进入下一页
                next_page_element.click()
                break
            # 找不到下一页报错
            except Exception as e:
                print('next_page:', e)
                time.sleep(5)
                continue
        else:
            return 'Done'


    def run(self):
        print('spider:' + self.name + ' 开始工作，关键字：'+self.keyword)
        self.index()
        while True:
            # 获取当前页面的所有结果
            elements = self.detail_elements()
            for element in elements:
                self.detail(element)
            # 进入下一页
            status = self.next_page()
            if status == 'Done':
                break
            time.sleep(5)
        self.driver.quit()
        print('spider:' + self.name + ' 已关闭')


if __name__ == '__main__':
    spider = GsxtSpider('传智播客')
    spider.run()
