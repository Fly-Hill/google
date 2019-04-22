# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time

from scrapy import signals
import random
from scrapy.http.response.html import HtmlResponse
from selenium import webdriver
from GoogleApp.settings import IS_DEVELOPMENT
from scrapy_redis import picklecompat
from scrapy.utils.reqser import request_to_dict
import redis
# from urllib.parse import unquote


from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError


class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError)

    # def process_response(self, request, response, spider):
    #     # 捕获状态码为40x/50x的response
    #     if str(response.status).startswith('4') or str(response.status).startswith('5'):
    #         # 随意封装，直接返回response，spider代码中根据url==''来处理response
    #         response = HtmlResponse(url='')
    #         return response
    #     # 其他状态码不处理
    #     return response

    def process_exception(self, request, exception, spider):
        # 捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            # 在日志中打印异常类型
            print('Got exception: %s' % (exception))
            # 随意封装一个response，返回给spider
            
            
            # obj = request_to_dict(request, spider)
            # serializer = picklecompat
            # value = serializer.dumps(obj)
            #
            # r = redis.Redis(host='127.0.0.1', port=6379, db=0, password=123456, decode_responses=True)
            # point = random.randint(1, 10000000)
            # r.zadd("App_en:requests", {value: point})
            # #time.sleep(30)
            # #print("网络错误sleep...")
            # spider.crawler.engine.close_spider(spider, '网络错误关闭爬虫')
            response = HtmlResponse(url='exception')
            return response
        # 打印出未捕获到的异常
        print('not contained exception: %s' % exception)


class GoogleAppChangeAreaDownloaderMiddleware(object):
    def process_request(self, request, spider):
        if "https://play.google.com/store/apps?" in request.url:
            # return None
            # print("first")
            if IS_DEVELOPMENT:
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                browser = webdriver.Chrome(r"C:\Users\hp\Downloads\安装包\chromedriver.exe", options=options)
            else:
                browser = webdriver.PhantomJS()
            browser.get(request.url)
            for i in range(4):
                time.sleep(5)
                # 将滚动条移动到页面的顶部
                js = "var q=document.documentElement.scrollTop=0"
                browser.execute_script(js)
                # 将滚动条移动到页面的底部
                js = "var q=document.documentElement.scrollTop=100000"
                browser.execute_script(js)
            time.sleep(6)
            response = HtmlResponse(
                browser.current_url,
                status=200,
                body=browser.page_source,
                encoding="utf-8",
                request=request)
            browser.quit()
            # print("end")
            return response
        elif "https://play.google.com/store/apps/details" in request.url:
            if spider.country_code:
                code = "&hl={}".format(spider.country_code)
                # url = unquote(request.url, 'utf-8')
                new_url = request.url + code
                request._set_url(new_url)
            return None
        else:
            return None


class GoogleAppRandomUserAgentDownloaderMiddleware(object):
    def process_request(self, request, spider):
        # print("RandomUserAgentMiddleware")
        request.headers["User_Agent"] = self.get_ua()
        return None

    @staticmethod
    def get_ua():
        first_num = random.randint(55, 62)
        third_num = random.randint(0, 3200)
        fourth_num = random.randint(0, 140)
        os_type = [
            '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)', '(X11; Linux x86_64)',
            '(Macintosh; Intel Mac OS X 10_12_6)'
        ]
        chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

        ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                       '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
                      )
        return ua


class GetFailedUrlMiddleware(object):

    def process_response(self, response, request, spider):
        # print("xx")
        if response.status != 200:

            with open("fail_url.txt", 'a') as file:
                file.write(response.url)
                file.write("\n")

                return response
        else:
            return response


class GoogleappSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class GoogleappDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
