import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from ..items import LermerItem
from urllib.parse import urljoin
from scrapy.loader.processors import MapCompose

class LermerSpiderSpider(scrapy.Spider):
    
    name = 'lermer_spider'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/catalogue/napolnye-pokrytiya/']
    
    rules = (
        Rule(LinkExtractor(restrict_xpaths="//a[@class = 'bex6mjh_plp s15wh9uj_plp l7pdtbg_plp r1yi03lb_plp sj1tk7s_plp']/@href")),
        Rule(LinkExtractor(restrict_xpaths="phytpj4_plp largeCard']/div/a/@href"), callback='parse_item') 
    )

    def parse_item(self, response):
        
        l = ItemLoader(item=LermerItem(), response=response)
        l.add_xpath('file_name', '//h1/text()',
                    MapCompose(lambda i: i.replace(':', ''))),
        #l.add_xpath('file_urls', '//*[@id="thumb-box-id-generated-0"]/@src',
        #            MapCompose(lambda i: urljoin(response.url, i)))
        l.add_xpath('xaracter')
        return l.load_item()
