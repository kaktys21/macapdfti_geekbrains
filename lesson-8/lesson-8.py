import time
import pandas
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class OpenDataSearcher():
    
    def __init__(self):
        
        self.driver = webdriver.Firefox()
    
    def tab_closer(self):
        
        while len(self.driver.window_handles) != 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
            
    def europa(self, request, datasets_col=1, file_format='csv', location_filter=None, random_data=False):
        
        def europa_next_page():
            
            try:
                self.driver.find_element_by_xpath('//button[@class = "page-link next-button"]').click()
                time.sleep(5)
            except ElementClickInterceptedException:
                return False        
            
        def data_link_getter():
            
            result_data = self.driver.find_elements_by_xpath('//div[@class = "data-info-box card mt-3 dataset"]')
            if len(result_data) < datasets_col:
                while len(result_data) < datasets_col:
                    
                    if europa_next_page():
                        result_data.extend(self.driver.find_elements_by_xpath('//div[@class = "data-info-box card mt-3 dataset"]'))
                    else:
                        print('No more pages')
                        break
            else:
                result_data = result_data[:datasets_col]
                
            return [dataset.find_element_by_xpath('.//a[@class = "text-dark text-decoration-none"]').get_attribute('href') for dataset in result_data]

        def downloader():
            
            for link in data_links:
                
                self.driver.execute_script('window.open('')')
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(link)
                time.sleep(2)
                
                try:
                    files = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="mt-1"]/div/ul/div/div')))
                except:
                    print('Everybody is lying here!')
                    
                for file in files:
                    if file_format.lower() == file.find_element_by_xpath('.//div[@class = "circle float-md-right text-center text-white"]/span').text.lower():
                        try:
                            file.find_element_by_xpath('.//span[@class = "download dropdown d-inline-block"]/div/button[@class = "btn btn-sm btn-primary p-0 pl-2 w-100 rounded-lg btn-color"]').click()
                            file.find_element_by_xpath('.//i[@class = "material-icons align-bottom"]').click()
                            time.sleep(5)
                        except:
                            file.find_element_by_xpath('.//span/span/a[@class = "btn btn-sm btn-primary p-0 pl-2 pr-2 w-100 rounded-lg btn-color"]').click()
                            time.sleep(5)

        
        self.driver.get('https://data.europa.eu/data/datasets?locale=en&minScoring=0')
        time.sleep(2)
        self.driver.find_element_by_xpath('//input[@class = "form-control rounded-lg"]').send_keys(request)
        self.driver.find_element_by_xpath('//div[@class = "d-flex align-items-center mr-3"]').click()

        for file_format_amount in self.driver.find_elements_by_xpath('//div[2]/div/div/div[8]/div/div[2]/div'):
            button = file_format_amount.find_element_by_xpath('.//button')
            if button.find_element_by_xpath('.//span[1]').text.lower() == file_format.lower():
                button.click()
                time.sleep(3)
                break
            
        data_links = data_link_getter()
        file = downloader()
        
    def quit(self):
        
        self.driver.quit()

