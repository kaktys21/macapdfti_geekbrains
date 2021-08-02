import requests
from bs4 import BeautifulSoup
import pandas
import json

def superjob(vacancy, pages):   
    
    def next_page_getter(link, soup):
        
        return sj_url + soup.find(lambda tag: tag.name == 'span' and 'Дальше' in tag.text).parent.get('href')
    
    def next_page_solve():
        
        vac_list = []
        link = sj_search_url + vacancy
        
        for page in range(pages):
            # print(link)
            soup = BeautifulSoup(requests.get(link).text, features='lxml')
            vac_list.extend([vac for vac in soup.findAll(class_='f-test-search-result-item') if not vac.find('div', {'class':'_30RdK _1ilsI'}) and vac.find('button')])
            link = next_page_getter(link, soup) if pages != 1 else 'last_page'
        return vac_list
    
    sj_search_url = 'https://www.superjob.ru/vacancy/search/?keywords='
    sj_url = 'https://www.superjob.ru'
    
    vac_list = next_page_solve()        # через получаение ссылки на следующую страницу на каждой странице. Дольше, но безопаснее
    vac_dict = dict()
    for i in range(len(vac_list)):
        try:
            salary = vac_list[i].find('span', {'class':'_1h3Zg _2Wp8I _2rfUm _2hCDz _2ZsgW'}).text
        except AttributeError:
            salary = ''
        vac_dict[i + 1] = [vac_list[i].find('a').text, salary, sj_url + vac_list[i].find('a').get('href'), sj_url]

    return pandas.DataFrame.from_dict(vac_dict, columns=['Вакансия', 'ЗП', 'Ссылка', 'Сайт'], orient='index')

def hh(vacancy, pages):
    
    hh_url = 'https://hh.ru/'

    params = {'text': 'NAME:' + vacancy, 'page' : 0, 'per_page': 20 * pages}
    req = requests.get('https://api.hh.ru/vacancies', params).json()
    i = 1
    vac_dict = {}
    for vac in req['items']:
        name = vac['name']
        url = vac['alternate_url']
        try:
            sal = list(vac['salary'].values())
            if sal[0] is None:
                if sal[1] is None:
                    salary = 'No info'
                else:
                    salary = f"До {sal[1]} {sal[2]}"
            else:
                if sal[1] is None:
                    salary = f"От {sal[0]} {sal[2]}"
                else:
                    salary  = f"{sal[0]} - {sal[1]} {sal[2]}"
            # print(*sal, salary)
        except AttributeError:
            salary = 'No info'
        vac_dict[i] = [name, salary, url, hh_url]
        i += 1
        
    return pandas.DataFrame.from_dict(vac_dict, columns=['Вакансия', 'ЗП', 'Ссылка', 'Сайт'], orient='index')
 
def main():
      
    vacancy = input('Enter vacancy to search:\t')
    pages = int(input('Enter how many pages to parse:\t'))
    
    result = pandas.concat([superjob(vacancy, pages), hh(vacancy, pages)], ignore_index=True)
    result.to_excel(r'C:\Users\epish\Desktop\учеба\GeekBrains\internet_search\result.xlsx')
