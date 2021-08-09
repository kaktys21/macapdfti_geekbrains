import re
import pandas
from selenium import webdriver
import time
#firefox_options = Options()
#firefox_options.add_argument("--headless")
#driver = webdriver.Firefox(options=firefox_options)

driver = webdriver.Firefox()

def to_df(columns, columns_info):
    return pandas.DataFrame(columns_info, columns=columns)

def mvideo():
    
    url = 'https://www.mvideo.ru'
    driver.get(url)
    
    bestseller = driver.find_elements_by_xpath('//div[@class = "facelift gallery-layout products--shelve gallery-layout_products gallery-layout_product-set grid-view"]')[0]
    script = bestseller.find_elements_by_xpath('.//script')[0]
    script_text = script.get_attribute('text')
    script_text = re.sub(r'\n', '', script_text)
    positions = [position.strip(' }{,') for position in script_text.split(']')[0].split('[')[1].split('}')]
    columns = [info.split(':')[0].strip(' "') for info in positions[0].split(',')]
    columns_info = []
    for position in positions[:-1]:
        temp_list = []
        for col in position.split(','):
            info = col.split(':')[1].strip(' "')
            temp_list.append(info if info not in ['', '(none)'] else None)
        columns_info.append(temp_list)
        
    return to_df(columns, columns_info)

def onlinetrade():     
    url = 'https://www.onlinetrade.ru/'
    driver.get(url)
    bestsellers = driver.find_element_by_xpath('//div[@id = "tabs_hits"]')
    bestsellers_items = []
    bestsellers_items.extend(bestsellers.find_elements_by_xpath('.//div[@class = "swiper-slide indexGoods__item"]'))
    bestsellers_items.extend(bestsellers.find_elements_by_xpath('.//div[@class = "swiper-slide indexGoods__item swiper-slide-active"]'))
    bestsellers_items.extend(bestsellers.find_elements_by_xpath('.//div[@class = "swiper-slide indexGoods__item swiper-slide-next"]'))
    bestsellers_items.extend(bestsellers.find_elements_by_xpath('.//div[@class = "swiper-slide indexGoods__item swiper-slide-prev"]'))
    columns = ['Название', 'Код производителя', 'Официальная гарантия', 'Цена', 'Старая цена', 'Новая цена', 'Ссылка']
    columns_info = []
    for bestseller in bestsellers_items:
        link = bestseller.find_element_by_xpath('.//div[@class = "indexGoods__item__flexCover"]/a[@class = "indexGoods__item__image"]').get_attribute('href')
        driver.execute_script('window.open('')')
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(link)
        time.sleep(3)
        item_list = []
        info = driver.find_element_by_xpath('//div[@class = "descr__techicalBrand__item"]')
        try:
            item_list.append(driver.find_element_by_xpath('//div[@class = "productPage__card  "]/h1 | //div[@class = "productPage__card  productPage__card__WOslider "]/h1').text) #Название
            item_list.append(info.find_element_by_xpath('.//div[1]/span[2]').text)  #Код производителя
            try:
                item_list.append(info.find_element_by_xpath('.//div[2]/span[2]').text)  #Официальная гарантия
            except:
                item_list.append(None)
            item_list.append(int(''.join(driver.find_element_by_xpath('//div[@class = "catalog__displayedItem__actualPrice"]/span/span').text.split())))    #Цена
            item_list.extend([None, None])   #Старая цена, Новая цена
        except:
            full_text = driver.find_element_by_xpath('//div[@class = "productPage__card  productPage__card__WOslider "]').text.split('\n')
            item_list.append(full_text[0])  #Название
            for line in full_text:
                if 'Код производителя:' in line:
                    item_list.append(line.split(':')[1]) 
            item_list.append(full_text[16].split(':')[1])  #Официальная гарантия
            item_list.append(int(''.join(full_text[7].strip('₽').split())))  #Цена
            item_list.append(int(''.join(full_text[5].strip('₽').split())))  #Старая цена        
            item_list.append(int(''.join(full_text[7].strip('₽').split())))  #Новая цена
            
            
        item_list.append(link)  #Ссылка
        columns_info.append(item_list)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
    return to_df(columns, columns_info)
        
