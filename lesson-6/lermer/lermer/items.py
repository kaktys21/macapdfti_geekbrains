import scrapy
from scrapy.loader.processors import TakeFirst

class LermerItem(scrapy.Item):
    
    file_urls = scrapy.Field()
    files = scrapy.Field()
    file_name = scrapy.Field(output_processor=TakeFirst())