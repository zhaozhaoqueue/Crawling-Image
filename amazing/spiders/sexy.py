# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from ..items import AmazingItem
from scrapy.linkextractors import LinkExtractor


class SexySpider(scrapy.Spider):
    name = 'sexy'
    # allowed_domains = ['www.mm131.net']
    # start_urls = ['https://www.mm131.net/xinggan/']
    main_page_url = "https://www.mm131.net/"
    start_urls = ["https://www.mm131.net/"]
    num_page_to_crawl = 3

    def start_requests(self):
        yield Request(url=self.main_page_url, callback=self.parse_main_page)


    def parse_main_page(self, response):
        le = LinkExtractor(restrict_xpaths="//div[@class='nav']")
        links = le.extract_links(response)
        cat_urls = [link.url for link in links if link.url!=response.url]
        # yield from super().start_requests()
        for cat_url in cat_urls:
            yield Request(url=cat_url, callback=self.parse_cat)

    def parse_cat(self, response):
        le = LinkExtractor(restrict_xpaths="//dd[@class='page']")
        links = le.extract_links(response)
        # parse the first page of the category
        self.parse(response)
        # crawl other pages
        for i in range(self.num_page_to_crawl):
            yield Request(url=links[i].url, callback=self.parse)


    def parse(self, response):
        sels = response.xpath("//div[@class='main']/dl/dd")
        headers = {
                'Referer':self.start_urls[0]
            }
        cat_name = response.url.split("/")[-2]
        for sel in sels[:-1]:
            item = AmazingItem()
            item["category"] = cat_name
            name = sel.xpath("./a/text()").extract_first()
            item["name"] = name
        	# item["image_urls"] = []
        	# item["referer"] = headers
            url = sel.xpath("./a/@href").extract_first()
            yield Request(url=url, callback=self.parse_one, meta={"item": item}, headers=headers)

    def parse_one(self, response):
    	item = response.meta["item"]
    	img_url = response.xpath("//div[@class='content-pic']//img/@src").extract()
    	item["image_urls"] = img_url
    	item["referer"] = response.url
    	# find total number of images and current page number
    	total_page = int(response.xpath("//div[@class='content-page']/span[@class='page-ch']/text()").re_first("\d+"))
    	cur_page = int(response.xpath("//div[@class='content-page']/span[@class='page_now']/text()").re_first("\d+"))
    	yield item
    	
    	if (cur_page < total_page):
    		le = LinkExtractor(restrict_xpaths="//div[@class='content-pic']")
    		link = le.extract_links(response)[0].url
    		headers = {
                'Referer': self.start_urls[0]
            }
    		yield Request(url=link, callback=self.parse_one, headers=headers, meta={"item": item})