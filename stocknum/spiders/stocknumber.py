from scrapy.spider import Spider
from scrapy.selector import Selector
from stocknum.items import StocknumItem
import re
from scrapy import log


class stocknum(Spider):

    #定义爬虫名称
    name = "stocknum"
    allowed_domains = ['eastmoney.com']
    start_urls = ["http://quote.eastmoney.com/stocklist.html#sh"]

    #解析数据
    def parse(self, response):

        sel = Selector(response)
        cont = sel.xpath('//div[@class="qox"]/div[@class="quotebody"]/div/ul')[0].extract()
        item = StocknumItem()

        for ii in re.findall(r'<li>.*?<a.*?target=.*?>(.*?)</a>', cont):
            item["stockName"] = ii.split("(")[0].encode('utf-8')
            item["stockCode"] = ("sh" + ii.split("(")[1][:-1]).encode('utf-8')
            log.msg(ii.encode('utf-8'), level=1)
            yield item

            # item["stockCode"]="+------------------------------------------------------------------+"
        # yield item
        cont1 = sel.xpath('//div[@class="qox"]/div[@class="quotebody"]/div/ul')[1].extract()

        for iii in re.findall(r'<li>.*?<a.*?target=.*?>(.*?)</a>', cont1):
            item["stockName"] = iii.split("(")[0].encode('utf-8')
            item["stockCode"] = ("sz" + iii.split("(")[1][:-1]).encode('utf-8')
            # log.msg(iii.encode('utf-8'),level="INFO")
            yield item