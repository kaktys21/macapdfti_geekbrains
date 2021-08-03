import scrapy
from scrapy.http import HtmlResponse
from job_searcher.items import JobSearcherItem

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['http://superjob.ru/']

    def parse(self, response):
        
        next_page = response.css('a.f-test-link-dalshe::attr(href)').extract_first()        
        yield response.follow(next_page, callback=self.parse)
        
        vacansy = response.css(
            'div.f-test-vacancy-item a[class*=f-test-link][href^="/vakansii"]::attr(href)'
        ).extract()
        
        for link in vacansy:
            yield response.follow(link, callback=self.vacansy_parse)      
            
    def vacansy_parse(self, response: HtmlResponse):
        
        name = response.css('h1 ::text').extract_first()
        salary = response.css('div._3MVeX span[class="_3mfro _2Wp8I ZON4b PlM3e _2JVkc"] ::text').extract()
        yield JobSearcherItem(name=name,salary=salary)