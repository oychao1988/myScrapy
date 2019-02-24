import time
from scrapy.cmdline import execute
import threading

# execute(['scrapy', 'crawl', 'LagouGETRecruitSpider'])
# execute(['scrapy', 'crawl', 'LagouGETRecruitSpider', '-o', 'positions_data.json'])
def get_lagou_position(city, keyword, pageSise):
    execute(['scrapy',
             'crawl',
             'LagouPOSTRecruitSpider',
             # 给spider传参
             '-a', 'city=%s' % city,
             '-a', 'keyword=%s' % keyword,
             '-a', 'pageSize=%d' % pageSise])

def get_tencent_position():
    execute(['scrapy',
             'crawl',
             'TencentRecruitCrawlSpider'])


def get_zhilian_position():
    execute(['scrapy',
             'crawl',
             'ZhilianAjaxSpider',
             '-a', 'pages=%d' % 0])

# get_lagou_position('深圳', 'python', 0)
keywords = ['Python 爬虫', 'python 数据分析', 'python 全栈开发', 'python 运维开发', 'python 机器学习', 'python 架构师', '人工智能', 'Python']

while True:
    for keyword in keywords:
        try:
            print(keyword, ' 爬取开始')
            get_lagou_position('深圳', keyword, 0)
            print(keyword, ' 爬取结束')
        except Exception as e:
            pass
        time.sleep(20)


# threads = []

# for keyword in keywords:
#     thread = threading.Thread(target=get_lagou_position, args=('深圳', keyword, 0))
#     threads.append(thread)
#
# for thread in threads:
#     thread.start()


# get_tencent_position()
# get_zhilian_position()