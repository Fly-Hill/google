# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class AppSpider(CrawlSpider):
    name = 'App'
    allowed_domains = ['google.com']
    start_urls = ['https://play.google.com/store']

    #
    # start_urls = ['https://play.google.com/store/apps',
    #               'https://play.google.com/store/apps/details?id=com.viber.voip']
    # 详情页匹配规则
    rules = (
        Rule(LinkExtractor(allow=(r"https://play\.google\.com/store/apps/details",)), callback='parse_item2',
             follow=True),
        Rule(LinkExtractor(allow=(r"https://play\.google\.com/store/apps/collection/recommended_for_you",)),
             follow=True),
        Rule(LinkExtractor(allow=(r"https://play\.google\.com/store/apps/collection/cluster",)),
             follow=True),
        Rule(LinkExtractor(allow=(r"https://play\.google\.com/store/apps/dev",)),
             follow=True),
    )

    # 生成泰国版的url
    # def parse_item1(self, response):
    #     # i = {}
    #     # i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
    #     # i['name'] = response.xpath('//div[@id="name"]').extract()
    #     # i['description'] = response.xpath('//div[@id="description"]').extract()
    #     real_url = response.url + "&hl=th"
    #     yield scrapy.Request(
    #         url=real_url,
    #         callback=self.parse_item2
    #     )

    # 详情页信息提取
    def parse_item2(self, response):
        print(response.url)
        item = {}
        item["APP名称"] = response.xpath('//h1[@class="AHFaub"]/span/text()').extract_first()
        # "https://play.google.com/store/apps/details?id=com.google.android.youtube&hl=th"
        # print(response.url)
        # print(re.findall(r"\?id=(.*)", response.url))
        # print(response.url)
        item["App包名"] = re.findall(r"\?id=(.*?)&", response.url)[0]
        # item["App包名"] = re.findall(r"\?id=(.*)", response.url)[0]
        # print(response.url)
        # print(item["App包名"])
        item["发行者"] = response.xpath('//div[@class="i4sPve"]/span[1]//text()').extract_first()
        cate1 = response.xpath('//div[@class="i4sPve"]/span[2]//text()').extract_first()
        cate2 = response.xpath('//div[@class="i4sPve"]/span[3]//text()').extract_first()
        if cate2:
            item["APP类别1"] = cate2
            item["APP类别2"] = cate1
        else:
            item["APP类别1"] = cate1
            item["APP类别2"] = "null"
        describe = response.xpath('//div[@class="i4sPve"][2]//text()').extract_first()
        if describe:
            item["描述"] = describe
        else:
            item["描述"] = "null"
        com = response.xpath('//span[@class="AYi5wd TBRnV"]/span[1]/text()').extract_first()
        if com:
            item["评论数"] = com.replace(",", "")
        else:
            item["评论数"] = "0"
        item["下载费用"] = response.xpath('//span[@class="oocvOe"]//text()').extract_first()
        flag = response.xpath('//div[@class="BHMmbe"]//text()').extract_first()
        if flag:
            item["评分"] = flag
        else:
            item["评分"] = 'null'
        # item["评分"] = response.xpath('//div[@class="BHMmbe"]//text()').extract_first()
        length = len(response.xpath('//div[@class="hAyfc"]//text()').extract())
        if length >= 12:
            update = response.xpath('//div[@class="hAyfc"]//text()').extract()[1]
            if update:
                item["更新日期"] = update.replace(",", "")
            item["大小"] = response.xpath('//div[@class="hAyfc"]//text()').extract()[3]
            item["安装数"] = response.xpath('//div[@class="hAyfc"]//text()').extract()[5]
            item["当前版本"] = response.xpath('//div[@class="hAyfc"]//text()').extract()[7]
            item["Andriod系统要求"] = response.xpath('//div[@class="hAyfc"]//text()').extract()[9]
            item["适用人群"] = response.xpath('//div[@class="hAyfc"]//text()').extract()[11]
            item["开发者邮箱"] = response.xpath('//a[@class="hrTbp KyaTEc"]//text()').extract_first()
        return item
