# -*- coding: utf-8 -*-
import re

import scrapy


class TencentSpider(scrapy.Spider):
    name = 'tencent'
    allowed_domains = ['tencent.com']
    start_urls = ['https://hr.tencent.com/position.php?']

    def parse(self, response):
        tr_list = response.xpath('//table[@class="tablelist"]//tr')[1:-1]
        for tr in tr_list:
            detailUrl = 'https://hr.tencent.com/' + tr.xpath('.//a/@href').extract_first()
            createTime = tr.xpath('./td[last()]/text()').extract_first()
            yield scrapy.Request(detailUrl, callback=self.parse_detail, meta={
                'detailUrl': detailUrl,
                'createTime': createTime,
            })

            next_page = 'https://hr.tencent.com/' + response.xpath('//*[@id="next"]/@href').extract_first()
            if next_page != 'javascript:;':
                yield scrapy.Request(next_page, callback=self.parse)

    def parse_detail(self, response):
        item = {}
        table = response.xpath('//*[@id="position_detail"]/div/table')[0]
        item['createTime'] = response.meta.get('createTime')
        item['detailUrl'] = response.meta.get('detailUrl')
        item['title'] = response.xpath('//td[@id="sharetitle"]/text()').extract_first()
        item['city'] = table.xpath('./tr[2]/td[1]/text()').extract_first()
        item['firstType'] = table.xpath('./tr[2]/td[2]/text()').extract_first()
        item['recruitNum'] = table.xpath('./tr[2]/td[3]/text()').extract_first()
        item['description'] = response.xpath('//ul[@class="squareli"]')[0].xpath('./li/text()').extract()
        item['requirements'] = response.xpath('//ul[@class="squareli"]')[1].xpath('./li/text()').extract()
        item['positionId'] = re.search(r'\d+', response.xpath('//button[@id="apppos"]/@onclick').extract_first()).group()
        yield item