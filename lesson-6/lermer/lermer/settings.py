BOT_NAME = 'lermer'

SPIDER_MODULES = ['lermer.spiders']
NEWSPIDER_MODULE = 'lermer.spiders'

ROBOTSTXT_OBEY = True
DEFAULT_REQUEST_HEADERS = {'Accept': '*/*',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4; rv:52.6.0) '
                           'Gecko/20100101 Firefox/52.6.0'
                           }

ITEM_PIPELINES = {'lermer.pipelines.LermerPipeline': 1}

FILES_STORE = r'downloaded'

DOWNLOAD_DELAY = 0
