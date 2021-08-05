import time
import pandas
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

email = 'fikl2020'

#firefox_opt = Options()
#firefox_opt.headless = True #Режим без интерфейса
driver = webdriver.Firefox()

def autorisation():
    
    driver.get('https://mail.yandex.ru/')
    enter_link = driver.find_element_by_xpath('/html/body/div/div/div[2]/div/div/div[4]/a[2]').get_attribute('href')
    driver.get(enter_link)
    driver.find_element_by_id('passp-field-login').send_keys(email) # заполняем логин
    enter_button = driver.find_element_by_id('passp:sign-in')
    enter_button.click()   
    time.sleep(1)
    driver.find_element_by_id('passp-field-passwd').send_keys(input()) # заполняем пароль
    driver.find_element_by_id('passp:sign-in').click()
    '''яндекс может что-то начать предлагать'''
    time.sleep(1)
    '''try:
        driver.find_element_by_class_name('mail-NestedList-Item-Name')
    except:
        driver.find_elements_by_class_name('passp-button')[1].click()'''

def all_scroller():
        
    while True:
        
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        try:
            driver.find_element_by_xpath('/html/body/div[2]/div[8]/div/div[3]/div[3]/div[3]/div[1]/div[5]/div[1]/div/div/div[4]/div/div/div[1]/button').click()
        except:
            break

def tab_closer(driver):
    
    while len(driver.window_handles) != 1:
        driver.switch_to.window(driver.window_handles[-1])
        driver.close()
    driver.switch_to.window(driver.window_handles[0])
    
def get_message_links(driver):
    
    time.sleep(2)
    all_mail = driver.find_element_by_xpath('/html/body/div[2]/div[8]/div/div[3]/div[3]/div[3]/div[1]/div[5]/div[1]/div/div/div[2]/div')
    message_links = [message.get_attribute('href') for message in all_mail.find_elements_by_xpath('//div/div/div/a[@class="mail-MessageSnippet js-message-snippet toggles-svgicon-on-important toggles-svgicon-on-unread"]')]
    thread_messages = [message.get_attribute('href') for message in all_mail.find_elements_by_xpath('//div/div/a[@class="mail-MessageSnippet js-message-snippet toggles-svgicon-on-important toggles-svgicon-on-unread mail-MessageSnippet_thread mail-MessageSnippet_type_widget mail-MessageSnippet_height_widget mail-MessageSnippet_height_attachment"]')]
    return message_links, thread_messages if len(thread_messages) != 0 else message_links

def message_getter(drive, message_links):
    
    data = []

    for link in message_links:
        if 'compose' in link:
            pass
        else:
            try:
                print(link)
                driver.execute_script('window.open('')')
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(link)
                time.sleep(3)
                data.append([driver.find_element_by_class_name('mail-Message-Toolbar-Subject-Wrapper').text, 
                             driver.find_element_by_xpath('//span[@class="mail-Message-Sender-Email mail-ui-HoverLink-Content"]').text, 
                             driver.find_element_by_xpath('//div[@class="js-message-body-content mail-Message-Body-Content"]').text, 
                             driver.find_element_by_xpath(f'''//div[@data-key = "view=message-head-date&ids={link.split('/')[-1]}"]''').text]
                             )
        
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:
                pass
    return data
  
def main():
    autorisation()
    time.sleep(5)
    all_scroller()
    
    message_links, thread_messages = get_message_links(driver)
    for thread_message in thread_messages:
        driver.execute_script('window.open('')')
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(thread_message)
        m, t = get_message_links(driver)
        message_links.extend(m)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
    del thread_messages
    tab_closer(driver)  # если вдруг что-то осталось

    data = message_getter(driver, message_links)
    data_df = pandas.DataFrame(data, columns=['Тема', 'Отправитель', 'Текст', 'Дата'], index=range(1, len(data) + 1))
    return data_df

driver.quit()
