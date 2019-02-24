import json
import re
from lxml import etree

import requests
import scrapy
import time

from myScrapy.items import LagouRecruitItem
from urllib.parse import urlencode

from myScrapy.utils.utils import cookie_transfer

lagou_cookie = "user_trace_token=20181003162424-bc2e8234-c6e5-11e8-a8cf-525400f775ce; LGUID=20181003162424-bc2e8853-c6e5-11e8-a8cf-525400f775ce; index_location_city=%E6%B7%B1%E5%9C%B3; WEBTJ-ID=20181008082215-166510d9256373-0c1c9d5e3a71e-3e70055f-1049088-166510d925740e; sajssdk_2015_cross_new_user=1; _gid=GA1.2.1131033380.1538975278; JSESSIONID=ABAAABAAADEAAFI2AA9D579308DA2197B701A300CA7B0A0; TG-TRACK-CODE=jobs_code; SEARCH_ID=1b2e80f29fa7414eb6b7f1dbd29fcaf7; X_MIDDLE_TOKEN=7db0d3b86be2c0e99615dfe2e6441f01; X_HTTP_TOKEN=84a16a5dc6d5de3f8be58743a2b0fe71; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22166527cbe742a0-094a56f8fc244b-3e70055f-1049088-166527cbe762e7%22%2C%22%24device_id%22%3A%22166527cbe742a0-094a56f8fc244b-3e70055f-1049088-166527cbe762e7%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _ga=GA1.2.1686656861.1538555064; _gat=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1538555064,1538555073,1538958136,1538958145; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1539011656; LGSID=20181008221248-3c47a43e-cb04-11e8-bb9c-5254005c3644; LGRID=20181008231416-d2773919-cb0c-11e8-ac8f-525400f775ce"

class LagouGETRecruitSpider(scrapy.spiders.Spider):
    name = 'LagouGETRecruitSpider'
    start_urls = ['https://www.lagou.com']
    allowed_domains = ['lagou.com']
    cookie = cookie_transfer(lagou_cookie)

    def parse(self, response):
        for item in response.xpath('//div[@class="menu_box"]/div/dl/dd/a'):
            category = item.xpath('text()').extract()
            category_url = item.xpath('@href').extract_first()

            RecruitItem = LagouRecruitItem()
            RecruitItem['category'] = category
            RecruitItem['category_url'] = category_url

            # 粗暴的添加分页
            for i in range(30):
                try:
                    category_sub_url = category_url + str(i+1)
                    yield scrapy.Request(url=category_sub_url, cookies=self.cookie, callback=self.parse_url)
                except:
                    pass

            # yield RecruitItem

    def parse_url(self, response):
        login_url = 'https://passport.lagou.com/login/login.html?msg=validation&uStatus=2&clientIp=183.237.64.70'
        if response.url != login_url:
            print('response.url =', response.url)
            for sel in response.xpath('//ul[@class="item_con_list"]/li'):
                try:
                    # adWord = scrapy.Field()
                    # appShow = scrapy.Field()
                    # approve = scrapy.Field()
                    # businessZones = scrapy.Field()  # 商业区域
                    # city = scrapy.Field()  # 城市
                    companyFullName = sel.xpath('div/div/div/a/text()').extract()[-1]  # 公司全称
                    # companyId = scrapy.Field()
                    # companyLabelList = scrapy.Field()  # 公司标签列表
                    # companyLogo = scrapy.Field()  # 公司logo
                    # companyShortName = scrapy.Field()  # 公司简称
                    # companySize = scrapy.Field()  # 公司规模
                    createTime = sel.xpath('div/div/div/span/text()').extract()[0]  # 发布时间
                    # deliver = scrapy.Field()
                    # district = scrapy.Field()  # 地区
                    education = sel.xpath('div[1]/div[1]/div[2]/div/text()').extract()[-1].split(' / ')[-1].split('\n')[0]  # 学历
                    # explain = scrapy.Field()
                    # financeStage = scrapy.Field()  # 融资阶段
                    # firstType = scrapy.Field()  # 工作类型1
                    # formatCreateTime = scrapy.Field()
                    # gradeDescription = scrapy.Field()
                    # hitags = scrapy.Field()
                    # imState = scrapy.Field()
                    # industryField = scrapy.Field()
                    # industryLables = scrapy.Field()
                    # isSchoolJob = scrapy.Field()
                    # jobNature = scrapy.Field()
                    # lastLogin = scrapy.Field()
                    # linestaion = scrapy.Field()
                    # latitude = scrapy.Field()  # 纬度
                    # longitude = scrapy.Field()  # 经度
                    # pcShow = scrapy.Field()
                    # plus = scrapy.Field()
                    positionAdvantage = sel.xpath('div[2]/div[1]/span/text()').extract()  # 职位优势
                    # positionId = scrapy.Field()
                    # positionLables = scrapy.Field()  # 职位标签
                    positionName = sel.xpath('div/div/div/a/h3/text()').extract()[0]  # 职位名称
                    # promotionScoreExplain = scrapy.Field()
                    # publisherId = scrapy.Field()  # 职位编号
                    # resumeProcessDay = scrapy.Field()
                    # resumeProcessRate = scrapy.Field()
                    salary = sel.xpath('div/div/div/div/span/text()').extract()[0]  # 薪资
                    # score = scrapy.Field()
                    # secondType = scrapy.Field()  # 工作类型2
                    # skillLables = scrapy.Field()  # 技能标签
                    # stationname = scrapy.Field()  # 站点名称
                    # subwayline = scrapy.Field()  # 地铁线路
                    # thirdType = scrapy.Field()  # 工作类型3
                    workYear = sel.xpath('div[1]/div[1]/div[2]/div/text()').extract()[-1].split(' / ')[0]  # 工作年限

                    position_item = LagouRecruitItem()
                    position_item['companyFullName'] = companyFullName
                    position_item['createTime'] = createTime
                    position_item['education'] = education
                    position_item['positionAdvantage'] = positionAdvantage
                    position_item['positionName'] = positionName
                    position_item['salary'] = salary
                    position_item['workYear'] = workYear

                    yield position_item
                except Exception:
                    continue


class LagouPOSTRecruitSpider(scrapy.spiders.Spider):
    name = 'LagouPOSTRecruitSpider'
    custom_settings = {
        'ITEM_PIPELINES': {'myScrapy.pipelines.LagouMongoPipeline': 300},
    }
    def __init__(self, city='深圳', keyword='Python', pageSize=None, *args, **kwargs):
        super(LagouPOSTRecruitSpider, self).__init__(*args, **kwargs)
        self.url = 'https://www.lagou.com/jobs/positionAjax.json?'
        self.detail_url = 'https://www.lagou.com/jobs/%s.html'
        self.query_params = urlencode({"city": city,
                                  "needAddtionalResult": "false"})
        self.start_urls = [self.url + self.query_params]
        self.allowed_domains = ['lagou.com']
        self.pageSize = pageSize

        self.form_datas = {"first": "true",
                      "pn": "1",
                      "kd": keyword}

        self.lagouHeaders = {
                        "Referer": "https://www.lagou.com/jobs/list_%s?%s&cl=false&fromSearch=true&labelWords=&suginput=" %
                                   (urlencode({'keyword': keyword}).split('=')[-1], urlencode({'city': city})),
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
                        }
        self.cookie = cookie_transfer(lagou_cookie)

    def parse(self, response):
        # 获取数据
        res = requests.post(url=self.url, headers=self.lagouHeaders, params=self.query_params, data=self.form_datas)
        res_dict = json.loads(res.text)
        # 获取页码
        try:
            pageSize = res_dict['content']['pageSize']
        except Exception as e:
            print(res_dict['msg'])
        if (not int(self.pageSize)) or (int(self.pageSize) > int(pageSize)):
            self.pageSize = pageSize
        # 获取所有分页的数据
        for i in range(int(self.pageSize)):
            self.form_datas['pn'] = str(i+1)
            print(self.form_datas['kd'], '第%s页' % self.form_datas['pn'])
            if i > 0:
                self.form_datas['first'] = 'false'
            try:
                res = requests.post(url=self.url, headers=self.lagouHeaders, params=self.query_params, data=self.form_datas)
                res_dict = json.loads(res.text)
                position_result = res_dict['content']['positionResult']['result']
            except Exception as e:
                continue

            # 将职位信息保存至position_item
            for position in position_result:
                detail_url = self.detail_url % position['positionId']
                # 请求详情页，获取职位描述
                description = []
                for i in range(3):
                    try:
                        res = requests.session().get(detail_url, headers={
                                 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                             })
                        html = etree.HTML(res.text)
                        description = html.xpath('//*[@id="job_detail"]/dd[2]/div/p/text()')
                        if description:
                            break
                        self.logger.info('重新获取职位描述:%s' % detail_url)
                    except Exception as e:
                        pass
                    time.sleep(5)

                position_item = LagouRecruitItem()
                position_item['description'] = description
                position_item['detailUrl'] = detail_url
                for k in position.keys():
                    position_item[k] = position[k]
                yield position_item

                position['createTime'] = int(time.mktime(time.strptime(position['createTime'], "%Y-%m-%d %H:%M:%S")))
                position['description'] = description
                position['detailUrl'] = detail_url

                position['positionId'] = int(position['positionId'])
                position['updateDate'] =  int(position['createTime'])
                position['source'] = 'lagou'
                # 向数据库服务器保存该条信息
                for i in range(3):
                    result = requests.post('http://182.61.60.153:5020/recruits/lagou/', position).json()
                    print(result)
                    if result['errno'] == 0:
                        break
            time.sleep(10)

