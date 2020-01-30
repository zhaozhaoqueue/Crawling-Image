# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class AmazingPipeline(object):
    def process_item(self, item, spider):
        return item

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request

class AmazingImgPipeline(ImagesPipeline):
	def get_media_requests(self, item, info):
		for image_url in item["image_urls"]:
			headers = {
				"referer": item["referer"]
			}
			yield Request(url=image_url, meta={"item": item}, headers=headers)



	def item_completed(self, results, item, info):
		image_paths = [x["path"] for ok, x in results if ok]
		# print(results)
		if not image_paths:
			raise DropItem("Item contains no images")
		return item

	def file_path(self, request, response=None, info=None):
		item = request.meta["item"]
		category = item["category"]
		name = item["name"]
		img_name = "_".join(request.url.split("/")[-2:])
		file_path = "./%s/%s/%s" % (category, name, img_name)
		return file_path