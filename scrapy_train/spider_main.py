# -*- coding: utf-8 -*-

import argparse

from scrapy.crawler import CrawlerProcess

from scrapy.utils.project import get_project_settings


def main(args):
    if not args.name:
        return
    settings = get_project_settings()
    settings['DOWNLOAD_DELAY'] = settings.get('DOWNLOAD_DELAY_SETTING', {}).get(args.name, 1)
    process = CrawlerProcess(settings)
    process.crawl(args.name, args.url)
    process.start()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-n', '--name', default='yangcong', type=str, help='spider name')
    ap.add_argument('-u', '--url', type=str, help='start url')
    args = ap.parse_args()
    main(args)
