# -*- coding: utf-8 -*-

import scrapy

from scrapy_train.items import ScrapyTrainItem
from scrapy_train.spiders.base import BaseSpider


class YangCongSpider(BaseSpider):
    name = 'yangcong'
    allowed_domains = ['yctxbb.com']
    domain = 'http://www.yctxbb.com'
    start_urls = [
        'http://www.yctxbb.com/qingchun/'
    ]

    def is_product(self, response):
        _url = response.url
        index = _url.split('/')[-1]
        if not index:
            return False
        if index.split('.')[0].isdigit():
            return True
        return False

    def get_full_url(self, url):
        # 简单拼接
        if url:
            return self.domain + url

    def get_next_page_url(self, response):
        url = response.xpath("//a[@class='next page-numbers']/@href").extract_first()
        if url:
            return self.get_full_url(url)

    def get_product_urls(self, response):
        return response.xpath('//*[@class="update_area_content"]//a/@href').extract()

    def parse(self, response):
        if not self.is_product(response):
            urls = self.get_product_urls(response)
            if urls:
                for url in urls:
                    yield scrapy.Request(self.get_full_url(url), self.parse)
                next_url = self.get_next_page_url(response)
                if next_url:
                    yield scrapy.Request(next_url, self.parse)
        else:
            yield self.parse_product(response)

    def parse_product(self, response):
        urls = response.xpath("//div[@class='content_left']//img/@src").extract()
        item = ScrapyTrainItem()
        item['img_urls'] = [self.get_full_url(_url) for _url in urls]
        return item
