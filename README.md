# scrapy_train

scrapy 实际项目中的做法

### 准备

一个例子

```
cd scrapy_train/scrapy_train
python spider_main.py -n yangcong
```

### Forbidden by robots.txt

懂得都懂。自己琢磨。。。

```
# setting.py 
ROBOTSTXT_OBEY = False
```

### 设置 UA

- spider 文件 设置 UA
- 设置随机 UA

添加 RandomUserAgentMiddleware
 
```
class RandomUserAgentMiddleware(object):

    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if not request.headers.get('User-Agent', None):
            request.headers['User-Agent'] = self.random()

    def random(self):
        from tools.const import user_agent
        import random
        return user_agent[random.randint(0, len(user_agent) - 1)]
```

### DOWNLOAD_DELAY_SETTING

建议使用自定义的 spider_main application。可以自定义一些 settings

一些网站的限制比较高，可以调整 download delay 参数

https://docs.scrapy.org/en/latest/topics/settings.html#download-delay

```
# spider_main.py

settings = get_project_settings()
settings['DOWNLOAD_DELAY'] = settings.get('DOWNLOAD_DELAY_SETTING', {}).get(args.name, 1)
```

### scrapy.Request 下载失败

某些图片资源使用 scrapy.Request 下载失败。

实际遇到过，尝试修改 Twisted 版本也无济于事，但是用 requests 可以

so, 我们需要替换掉 scrapy 默认的 scrapy.Request 方式

可以在默认的 DownloaderMiddleware 处 (ScrapyTrainDownloaderMiddleware 本文)， 直接 return scrapy.Response 对象，
或者自己重新定义一个新的 DownloaderMiddleware。都是 process_request 方法

```
# 官网说的很清楚
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
```

例子：

某个网站的请求，都用 requests 来请求

```
# self.sesson (requests.Session)
def process_request(self, request, spider):
    if spider.name == 'xxxxx':
        if '.jpeg' in request.url:
            resp = self.session.get(request.url)
            return Response(url=request.url, body=resp.content)
        elif 'www.xxxx.com' in request.url:
            resp = self.session.get(request.url)
            return HtmlResponse(url=request.url, body=bytes(resp.text))
        else:
            # continue processing this request by others middleware
            return None
```

### 跳过 request

跳过一些 url, 不去发起 scrapy.Request()

- 场景

我们导入一个读文件的商家，这时候数据都是现成的，没必要真的发起一个请求。

可以添加一个 FakeRequestMiddleware

```
class FakeRequestMiddleware(object):

    def process_request(self, request, spider):
        if request.url.startswith(spider.fake_url):
            return Response(url=request.url)
```

spider:

```
fake_url = 'www.fake_url.com'
return scrapy.Request(fake_url, *args, **kwargs)
```

### 使用 selenium

同上，process_request 方法 返回 Response

例子：
```
class WebdriverMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.session = requests.Session()
        self.session.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36'
        }
        self.selenium_hub = 'http://selenium-hub.xxx.com:port/wd/hub'
        import selenium.webdriver as webdriver
        from selenium.webdriver.chrome.options import Options

        if not getattr(self, 'browser', None):
            prefs = {
                'profile.default_content_setting_values':
                    {
                        'notifications': 2
                    }
            }
            chrome_options = Options()
            chrome_options.add_experimental_option('prefs', prefs)
            self.browser = webdriver.Remote(command_executor=self.selenium_hub, desired_capabilities=chrome_options.to_capabilities())

    # This method can direct return HtmlResponse，then exit download middleware.
    # But always timeout.(In download image, session_id timeout)
    # So we transfer images by meta
    def process_request(self, request, spider):
        url = request.url
        if '.jpeg' in url or '.jpg' in url:
            # generally scrapy can handler image download
            return
        # use self.spider.webdriver_middleware_processing 
        return spider.webdriver_middleware_processing(self.browser, url, request)
```

spider：

```
def webdriver_middleware_processing(self, browser, url, request):
    browser.get(url)
    browser.execute_script("window.scrollTo(0,300);")

    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    browser.execute_script("window.scrollTo(0,300);")

    # If no *Add to cart* button, think url is not product url.
    if not browser.find_elements_by_xpath("//button[text()='Add to cart']"):
        logging.info('No Add to cart button. exit')
        return None

    click_img = '''
                document.evaluate("//button[text()='Add to cart']", document.body, null, 9, null).singleNodeValue.click()
                document.evaluate("(//div[@class='slick-track'])[1]/div[@data-index][last()]", document.body, null, 9, null).singleNodeValue.click()
            '''
    try:
        browser.execute_script(click_img)
    except:
        logging.warning("Use webdriver error! next use scrapy request!")
        return None

    return TextResponse(url=url, body=body, encoding='utf-8')
```

### 自定义下载位置

参考：

scrapy_train.pipelines.ImageDownloadPipeline.file_path

重写 file_path 方法


### 日志 logger kafka

可能的设置

```
handler = KafkaLoggingHandler()
logger = logging.getLogger()
logger.addHandler(hdlr=handler)
```

### 发送 Item 到 kafka


因为 每天的数据比较多，需要同步到别的系统，如果直接 scrapy 消费的话比较慢。

可以把 Item 写到 Kafka，其他应用来消费 Item.










