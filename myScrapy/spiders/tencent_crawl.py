import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from myScrapy.items import TencentRecruitItme


class TencentRecruitCrawlSpider(CrawlSpider):
    name = 'TencentRecruitCrawlSpider'
    allowed_domains = ['hr.tencent.com']
    start_urls = ['http://hr.tencent.com/position.php?&start=0#a']
    # 提取匹配'http://hr.tencent.com/position.php?&start=\d+#a'的链接
    page_lx = LinkExtractor(allow=('start=\d+'))
    rules = [Rule(page_lx, callback='parseContent', follow=True)]
    custom_settings = {
        'ITEM_PIPELINES': {'myScrapy.pipelines.TencentMongoPipeline': 300},
    }

    def parseContent(self, response):
        print(response.url)
        for sel in (response.xpath('//*[@class="even"]') + response.xpath('//*[@class="odd"]')):
            name = sel.xpath('./td[1]/a/text()').extract()[0]
            detailLink = sel.xpath('./td[1]/a/@href').extract()[0]
            catalog = None
            if sel.xpath('./td[2]/text()'):
                catalog = sel.xpath('./td[2]/text()').extract()[0]
            recruitNumber = sel.xpath('./td[3]/text()').extract()[0]
            workLocation = sel.xpath('./td[4]/text()').extract()[0]
            publishTime = sel.xpath('./td[5]/text()').extract()[0]

            item = TencentRecruitItme()
            item['name'] = name
            item['detailLink'] = detailLink
            if catalog:
                item['catalog'] = catalog
            item['recruitNumber'] = recruitNumber
            item['workLocation'] = workLocation
            item['publishTime'] = publishTime

            yield item
