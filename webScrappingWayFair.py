
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
#options.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

url = 'https://www.wayfair.ca/furniture/sb0/sofas-c413892.html?itemsperpage={}&curpage={}'

#response = requests.get(url.format(96, 1))
#soup=BeautifulSoup(response.content,'html.parser')

driver.get(url.format(96, 1))
skus = []
i = 1
for ele in driver.find_elements_by_class_name('TrackedProductCardWrapper'):
    ele1 = ele.find_element_by_class_name('ProductCard')
    skus.append(ele1.get_attribute('data-sku'))
    print("Got an SKU %s"%str(i))
    i = i+1
driver.quit()

productUrl = 'https://www.wayfair.ca/furniture/pdp/latitude-run-pola-90-velvet-square-arm-sleeper-{}.html'
for sku in skus:
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get(productUrl.format(sku))
    time.sleep(1)

url = 'https://www.wayfair.ca/graphql'
payload = {'sku': "C002179401", "language_code": "en", "sort_order": "RELEVANCE", "reviews_per_page": 10}
resp = requests.post(url, data =payload)

