from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
import pymongo
import pandas
import json
import re


class JobSearcher():
    
    def __init__(self, vacancy, pages):
        
        self.vacancy = vacancy
        self.pages = pages
        self.search_flag = 0
        
        self.db = pandas.DataFrame(columns=['Вакансия', 'Зарплата','Минимальная ЗП', 'Максимальная ЗП', 'Валюта', 'Договорная зп', 'Ссылка', 'Сайт'])
              
    
    def search(self):
        
        self.db = pandas.concat([self.superjob_search(), self.hh_search()], ignore_index=True)
        self.search_flag = 1
        
    def superjob_search(self):   
        
        def next_page_getter(link, soup):
            
            return sj_url + soup.find('a', {'class':'icMQ_ bs_sM _3ze9n f-test-button-dalshe f-test-link-Dalshe'}).get('href')
        
        def next_page_solve():
            
            vac_list = []
            link = sj_search_url + self.vacancy + '&page='
            
            for page in range(self.pages):
                soup = BeautifulSoup(requests.get(link + str(page + 1)).text, features='lxml')
                try:
                    vac_list.extend([vac for vac in soup.findAll(class_='f-test-search-result-item') if not vac.find('div', {'class':'_30RdK _1ilsI'}) and vac.find('button')])
                except:
                    break
                
            return vac_list
        
        def salary_splitter(salary):
    
            sal = False
            min_sal = None
            max_sal = None
            mon = 'неизвестно'
            talk = 'False'
            
            if salary == 'По договорённости':
                sal = True
                talk = True
                
            if re.fullmatch(r'от\xa0.*', salary):
                min_sal, mon = re.findall(r'от ([1-9][0-9]*(?: ?[0-9]+)?) (.*)', re.sub(u'\xa0', ' ', salary))[0]
                min_sal = int(''.join(min_sal.split()))
                
            if re.fullmatch(r'до\xa0.*', salary):
                max_sal, mon = re.findall(r'до ([1-9][0-9]*(?: ?[0-9]+)?) (.*)', re.sub(u'\xa0', ' ', salary))[0]
                max_sal = int(''.join(max_sal.split()))
                sal = True
            
            if re.fullmatch(r'.*—.*', salary):
                min_sal, max_sal, mon = re.findall(r'([1-9][0-9]*(?: ?[0-9]+)?) — ([1-9][0-9]*(?: ?[0-9]+)?) (.*)', re.sub(u'\xa0', ' ', salary))[0]
                max_sal, min_sal = int(''.join(max_sal.split())), int(''.join(min_sal.split()))
                sal = True
                
            return [sal, min_sal, max_sal, mon, talk]

        sj_search_url = 'https://www.superjob.ru/vacancy/search/?keywords='
        sj_url = 'https://www.superjob.ru'
        
        vac_list = next_page_solve()        # через получаение ссылки на следующую страницу на каждой странице. Дольше, но безопаснее
        vac_dict = dict()
        
        for i in range(len(vac_list)):
            try:
                salary = vac_list[i].find('span', {'class':'_1h3Zg _2Wp8I _2rfUm _2hCDz _2ZsgW'}).text
                sal, min_sal, max_sal, mon, talk = salary_splitter(salary)
            except AttributeError:
                sal, min_sal, max_sal, mon, talk = False, None, None, 'неизвестно', 'False'
                
            vac_dict[i + 1] = [vac_list[i].find('a').text, sal, min_sal, max_sal, mon, talk, sj_url + vac_list[i].find('a').get('href'), sj_url]
    
        return pandas.DataFrame.from_dict(vac_dict, columns=['Вакансия', 'Зарплата','Минимальная ЗП', 'Максимальная ЗП', 'Валюта', 'Договорная зп', 'Ссылка', 'Сайт'], orient='index')
    
    def hh_search(self):
        
        hh_url = 'https://hh.ru/'
    
        params = {'text': 'NAME:' + self.vacancy, 'page' : 0, 'per_page': 20 * self.pages}
        req = requests.get('https://api.hh.ru/vacancies', params).json()
        i = 1
        vac_dict = {}
        for vac in req['items']:
            name = vac['name']
            url = vac['alternate_url']
            min_sal, max_sal, talk_sal = None, None, True
            no_sal = True
            mon = 'неизвестно'
            try:
                sal = list(vac['salary'].values())
                min_sal = sal[0]
                max_sal = sal[1]
                talk_sal = True if sal[0] is None and sal[1] is None else False
                mon = sal[2]
            except AttributeError:
                no_sal = False
            vac_dict[i] = [name, no_sal, min_sal, max_sal, mon, talk_sal, url, hh_url]
            i += 1
            
        return pandas.DataFrame.from_dict(vac_dict, columns=['Вакансия', 'Зарплата','Минимальная ЗП', 'Максимальная ЗП', 'Валюта', ' Договорная зп', 'Ссылка', 'Сайт'], orient='index')
    
    def to_file(self, path, db):
        
        db.to_excel(path)
    
    def more_money(self, min_salary):
        
        def more_money_searcher():
            
            new_db_index = 0
            for i in range(len(self.db)):
                if self.db.loc[i][2] > min_salary or self.db.loc[i][3] > min_salary:
                    #print(self.db.loc[i])
                    more_money_db.loc[new_db_index] = self.db.loc[i]
                    new_db_index += 1
            
            return more_money_db
        
        more_money_db = pandas.DataFrame(columns=['Вакансия', 'Зарплата','Минимальная ЗП', 'Максимальная ЗП', 'Валюта', 'Договорная зп', 'Ссылка', 'Сайт'])
        if self.search_flag == 0:
            self.search()
            more_money_db = more_money_searcher()
        else:
            more_money_db = more_money_searcher()
        
        print(more_money_db)
        
class Mongo():
        
        def __init__(self, df, collection_name, table_name, url='mongodb://172.17.0.2:27017/'):
            
            self.df = df
            self.collection_name = collection_name
            self.table_name = table_name
            self.url = url
            self.mongodb = MongoClient(url)
            self.db = self.mongodb[collection_name]
            self.collection = self.db[table_name]
            
        def to_database(self, collection, data):
            
            return collection.insert_one(data).inserted
            
        def from_database(self, collection, elements, multiple=False):
        
            if multiple:
                results = collection.find(elements)
                return [r for r in results]
            else:
                return collection.find_one(elements)   
            
        def insert_new(self, collection, data):
            
            if self.from_database(collection, data):
                return 'Already in db'
            else:
                self.to_database(collection, data)

def main():
    
    vacancy = input('Enter vacancy:\t')
    pages = int(input('Enter pages:\t'))
    searcher = JobSearcher(vacancy, pages)
    searcher.search()
    
    '''Написать функцию, которая производит поиск и выводит на экран вакансии с 
    заработной платой больше введённой суммы.'''
    
    searcher.more_money(int(input('More then? ')))
    
    '''Написать функцию, которая будет добавлять в вашу базу данных только новые 
    вакансии с сайта.'''
    
    searcher_test = JobSearcher('Python', 1)
    searcher_test.search()
    i = 0
    flag = 0
    mongo_db = Mongo(searcher_test.db, 'vacancy', 'vacancy_db')
    while i < len(searcher_test.db):
        print(i)
        result = mongo_db.insert_new(mongo_db.collection, {'Вакансия':searcher_test.db.loc[i]['Вакансия']})
        print(result)
                                     
        flag += 1
        i += 1 if flag % 2 == 0 else 0