import requests
from lxml import html
import pandas

class NewsSearcher():
    
    def __init__(self):
        
        self.mailru_url = 'https://mail.ru/'
        self.lenta_url = 'https://lenta.ru/'
        lenta_df = self.lenta()
        mailru_df = self.mailru()
        self.result = pandas.concat([lenta_df, mailru_df], ignore_index=True)
    
    def html_prepare(self, link):
        try:
            response = requests.get(link)
            try:
                root = html.fromstring(response.text)
                temp_data = root.xpath('//*')
            except:
                print(f'Request error: {response}')
                return False
        except:
            print('Request error')
            return False
    
    def to_dataframe(self, news, links, times, url):
        
        return pandas.DataFrame.from_dict({'Новость':news, 'Ссылка':links, 'Дата публикации':times, 'Источник':[url for i in range(len(news))]})
        
    def mailru(self):
        
        root = self.html_prepare(self.mailru_url)
        if root:
            news = root.xpath('//span[@class="news__list__item__link__text"]/text()')
            links = root.xapth('//span[@class="news__list__item__link__text"]/../@href')
            times = self.lenta_df['Дата публикации']
            self.to_dataframe(news, links, times, self.mailru_url)
    
    def lenta(self):
        
        root = self.html_prepare(self.lenta_url)
        if root:
            news = root.xpath('''(//section[@class="row b-top7-for-main js-top-seven"]//div[@class="first-item"]/h2 | 
            //section[@class="row b-top7-for-main js-top-seven"]//div[@class="item"])/a/text()''')
            links = root.xpath('''(//section[@class="row b-top7-for-main js-top-seven"]//div[@class="first-item"]/h2 | 
            //section[@class="row b-top7-for-main js-top-seven"]//div[@class="item"])/a/@href''')
            times = [date.split(',')[1][1:] for date  in root.xpath('''(//section[@class="row b-top7-for-main js-top-seven"]//div[@class="first-item"]/h2 | //section[@class="row b-top7-for-main js-top-seven"]//div[@class="item"])/a/time/@datetime''')]
            self.lenta_df = self.to_dataframe(news, links, times, self.lenta_url)