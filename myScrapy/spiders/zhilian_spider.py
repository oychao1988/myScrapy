import datetime
import json

import requests
import scrapy

from myScrapy.items import ZhilianItem
from myScrapy.settings import DUPLICATE_CHECKING_SERVER


class ZhilianAjaxSpider(scrapy.spiders.Spider):
    name = 'ZhilianAjaxSpider'
    custom_settings = {
        'ITEM_PIPELINES': {'myScrapy.pipelines.ZhilianMongoPipeline': 300},
        'DEFAULT_REQUEST_HEADERS': {
            'Host': 'fe-api.zhaopin.com',
            'Origin': 'https://sou.zhaopin.com',
            'Referer': 'https://sou.zhaopin.com/?pageSize=60&jl=765&kw=python&kt=3',
            'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        }
    }

    def __init__(self, pages, *args, **kwargs):
        super(ZhilianAjaxSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://fe-api.zhaopin.com/c/i/sou'
        self.params = {
            'start': '{}',
            'pageSize': kwargs['pageSize'] if kwargs.get('pageSize', None) else '60',
            'cityId': kwargs['cityId'] if kwargs.get('cityId', None) else '765',
            'workExperience': kwargs['workExperience'] if kwargs.get('workExperience', None) else '-1',
            'education': kwargs['education'] if kwargs.get('education', None) else '-1',
            'companyType': kwargs['companyType'] if kwargs.get('companyType', None) else '-1',
            'employmentType': kwargs['employmentType'] if kwargs.get('employmentType', None) else '-1',
            'jobWelfareTag': kwargs['jobWelfareTag'] if kwargs.get('jobWelfareTag', None) else '-1',
            'kw': kwargs['kw'] if kwargs.get('kw', None) else 'python',
            'kt': kwargs['kt'] if kwargs.get('kt', None) else '3',
            '_v': kwargs['_v'] if kwargs.get('_v', None) else '0.36034137',
        }

        self.pages = int(pages) if int(pages) else 10
        self.count = 0
        self.page_size = kwargs['pageSize'] if kwargs.get('pageSize', None) else '60'
        # 待拼接的起始数量为空的url
        self.without_start_page_url = self.base_url +'?'+ '&'.join(['{k}={v}'.format(k=k, v=v) for k, v in self.params.items()])
        # 拼接start_url
        self.start_urls = [self.without_start_page_url.format(self.count*int(self.page_size))]
        self.allowed_domain = ['zhaopin.com']

    # 验证指纹
    def duplicateCheck(self, position_dict):
        updateDate_struct = datetime.datetime.strptime(position_dict["updateDate"], '%Y-%m-%d %H:%M:%S')
        updateDate_stamp = int(datetime.datetime.timestamp(updateDate_struct))
        check_dict = {
            "number": position_dict["number"],
            "updateDate": updateDate_stamp
        }

        check = requests.get(url=DUPLICATE_CHECKING_SERVER, params=check_dict).json()
        return  check

    def parse(self, response):
        self.count += 1
        print('第%d页' % self.count)
        try:
            result_dict = json.loads(response.text)
            results_dict_list = result_dict['data']['results']
        except Exception as e:
            print('爬取失败', e)
            return
        for position_dict in results_dict_list:
            # 生成指纹
            check = self.duplicateCheck(position_dict)
            # 如果指纹不一致，　
            if not check['errno'] == 0:
                # 判断
                # 保存职位数据
                position_item = ZhilianItem()
                for k, v in position_dict.items():
                    try:
                        position_item[k] = v
                    except Exception as e:
                        # print(k, v, e)
                        continue
                # 记录指纹
                try:
                    #
                    updateDate_struct = datetime.datetime.strptime(position_dict["updateDate"], '%Y-%m-%d %H:%M:%S')
                    updateDate_stamp = int(datetime.datetime.timestamp(updateDate_struct))
                    check_dict = {
                        "number": position_dict["number"],
                        "updateDate": updateDate_stamp
                    }
                    result = requests.post(DUPLICATE_CHECKING_SERVER, params=check_dict).json()
                    if not result['result']:
                        print(result)
                        continue
                except Exception as e:
                    continue
                yield position_item
        print('爬取成功')
        if self.count <= self.pages:
            next_url = self.without_start_page_url.format(self.count*int(self.page_size))
            yield scrapy.Request(next_url, callback=self.parse)

