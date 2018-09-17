import scrapy
import re
from Telegram.items import TelegramItem


class GrameSpider(scrapy.Spider):
    name = 'gram'
    allowed_domains = ['www.google.com', 't.me']
    start_urls = ['https://www.google.com.hk/search?q=site:t.me+中&start=0&filter=0']
    total_re = re.compile(r"\d")

    def parse(self, response):

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
