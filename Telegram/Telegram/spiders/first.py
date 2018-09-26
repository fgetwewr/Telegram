#!/usr/bin/python3
#-*-coding:utf-8 -*-
import scrapy
import re

import requests

from Telegram.items import TelegramItem


class GrameSpider(scrapy.Spider):
    name = 'gram'
    allowed_domains = ['www.google.com', 't.me']
    start_urls = ['https://www.google.com.hk/search?q=site:t.me+%E4%B8%AD&start=0&filter=0']
    total_re = re.compile(r"\d")

    # def make_requests_from_url(self, url):
    #     self.logger.debug('Try first time')
    #     return scrapy.Request(url=url, meta={'download_timeout': 10}, callback=self.parse, dont_filter=False)

    def start_requests(self):
        for url in self.start_urls:
            # proxies = 'https://' + requests.get('http://192.168.52.159:5000/random').text
            proxy = requests.get('http://192.168.52.159:5000/random').text
            proxies = {
                'https://': proxy,
                'http://': proxy
            }

            response = requests.get("https://www.google.com.hk/search?q=site:t.me+%E4%B8%AD&start=0&filter=0", proxies=proxies)
            if response.status_code == 200:
                print("--" * 80)
                print(response.text)
                print("--" * 80)
                print("The proxy is ....")
                yield scrapy.Request(url, callback=self.parse, meta={'proxy': proxies})

    def parse(self, response):
        print("---"*90)
        print(response.headers)
        print("---"*90)

        # 得到群组列表
        div_lists = response.xpath('//div[@class="bkWMgd"]/div[@class="srg"]/div[@class="g"]')

        # 遍历这个列表得到每个群组的链接
        for div_list in div_lists:
            item = TelegramItem()
            link = div_list.xpath('.//div[@class="rc"]/h3/a/@href').extract_first()
            item['gaddr'] = link
            yield scrapy.Request(
                url=link,
                callback=self.details,
                meta={'item': item}
            )

        # 得到下一页的链接，
        next_url = response.xpath("//a[@id='pnnext']/@href").extract_first()
        if next_url is not None:
            next_url = response.urljoin(next_url)
            # 如果有下一页，回调自身，实现翻页
            yield scrapy.Request(
                next_url,
                callback=self.parse
            )

    # 群组详情页的提取
    def details(self, response):
        item = response.meta['item']
        title = response.xpath('//div[@class="tgme_page_wrap"]//div[@class="tgme_page_title"]/text()').extract_first().replace('\n', '').replace(" ", "")
        total = response.xpath('//div[@class="tgme_page_wrap"]//div[@class="tgme_page_extra"]/text()').extract_first()
        total = "".join(self.total_re.findall(total))
        item['gname'] = title
        item['gnum'] = total
        yield item
