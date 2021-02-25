import scrapy
from scrapy.spiders import Spider
from urllib import parse as urlparse


class BaseSpider(Spider):
    name = 'base'
    headers = ''
    cookies = ''

    def __init__(self, url=None, **kwargs):
        super().__init__(**kwargs)
        self.url = url

    def scrapy_request(self, url, *args, **kwargs):
        if self.headers:
            if 'headers' in kwargs:
                kwargs['headers'].update(self.headers)
            else:
                kwargs['headers'] = self.headers
        if self.cookies:
            kwargs['cookies'] = self.build_cookie(self.cookies)
        return scrapy.Request(url, *args, **kwargs)

    def get_url_params(self, url):
        url_parts = list(urlparse.urlparse(url))
        return dict(urlparse.parse_qsl(url_parts[4]))

    def build_cookie(self, cookie_str):
        cookies = {}
        for item in cookie_str.split(";"):
            items = item.split("=")
            cookies[items[0]] = items[1]
        return cookies

    def remove_url_params(self, url, param_keys=None):
        url_parts = list(urlparse.urlparse(url))
        if param_keys:
            query = dict(urlparse.parse_qsl(url_parts[4]))
            for param_key in param_keys:
                query.pop(param_key, None)
            url_parts[4] = urlparse.urlencode(query, doseq=True)
            return urlparse.urlunparse(url_parts)
        else:
            return '%s://%s%s' % (url_parts[0], url_parts[1], url_parts[2])

    def append_url_params(self, url, params):
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlparse.urlencode(query, doseq=True)
        return urlparse.urlunparse(url_parts)
