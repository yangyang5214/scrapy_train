# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from w3lib.util import to_bytes
import hashlib
import mimetypes
import os

import scrapy
from scrapy.pipelines.files import FilesPipeline


class ScrapyTrainPipeline:
    def process_item(self, item, spider):
        return item


class ImageDownloadPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        urls = item.get('img_urls')
        if urls:
            for url in urls:
                yield scrapy.Request(url)

    def file_path(self, request, response=None, info=None, *, item=None):
        media_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        media_ext = os.path.splitext(request.url)[1]
        # Handles empty and wild extensions by trying to guess the
        # mime type then extension or default to empty string otherwise
        if media_ext not in mimetypes.types_map:
            media_ext = ''
            media_type = mimetypes.guess_type(request.url)[0]
            if media_type:
                media_ext = mimetypes.guess_extension(media_type)
        return f'{self.spiderinfo.spider.name}/{media_guid}{media_ext}'
