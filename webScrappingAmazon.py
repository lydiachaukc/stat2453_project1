
import os
from datetime import datetime
import requests
import pandas as pd
from multiprocessing import Pool
from bs4 import BeautifulSoup
from pathlib import Path

now = datetime.now()
dt_string = now.strftime("%d_%m_%Y_%H_%M")
if not Path(dt_string).is_dir():
    os.mkdir(dt_string)
os.chdir(dt_string)


class Amazon_product_reviews:
    def __init__(self, query_term):
        self.search_term = query_term
        self.cookie = {}
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
        self.base_url = 'https://www.amazon.in'
        self.amazon_search = '/s?k='
        self.page_param = '&page={}'
        self.product_search = '/dp/'
    def search_amazon(self, page_number):
        url = self.base_url + self.amazon_search + self.search_term + self.page_param.format(page_number)
        page = requests.get(url, cookies = self.cookie, headers = self.header)
        if page.status_code == 200:
            return page
        else:
            print('Search went unsuccessful')
            return "Error"
    def search_product_page(self, product_num):
        url =  self.base_url + self.product_search + product_num
        page = requests.get(url, cookies = self.cookie, headers = self.header)
        if page.status_code == 200:
            return page
        else:
            print('Search went unsuccessful')
            return "Error"
    def search_reviews(self, review_link):
        url = self.base_url + review_link
        page = requests.get(url, cookies = self.cookie, headers = self.header)
        if page.status_code == 200:
            return page
        else:
            print('Search went unsuccessful')
            return "Error"

def collect_reviews(query_term):
    page_num = query_term[1]
    query_term = query_term[0]
    try:
        amazon_reviews_collector = Amazon_product_reviews(query_term)
        # Collecting product names
        product_names = []
        resp = amazon_reviews_collector.search_amazon(page_number=page_num)
        soup = BeautifulSoup(resp.content)
        print('Going to collect product names')
        for i in soup.findAll("span", {'class': 'a-size-base-plus a-color-base a-text-normal'}):
            product_names.append(i.text)
        print('Collected product names')
        # Collecting product numbers
        data_asin = []
        resp = amazon_reviews_collector.search_amazon(page_number=page_num)
        soup = BeautifulSoup(resp.content)
        #print('Going to collect product numbers')
        for i in soup.findAll("div", {'class': "sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20"}):
            data_asin.append(i['data-asin'])
        print('Collected product numbers')
        # Collecting Link to reviews
        link = []
        #print('Going to collect links')
        for i in range(len(data_asin)):
            resp = amazon_reviews_collector.search_product_page(data_asin[i])
            soup = BeautifulSoup(resp.content)
            #print('collecting links')
            for i in soup.findAll("a", {'data-hook': "see-all-reviews-link-foot"}):
                link.append(i['href'])
        print('All links collected')
        # Collecting Reviews
        reviews, starRating = [], []
        #print('Going to collect Reviews')
        for j in range(len(link)):
            for k in range(50):
                response = amazon_reviews_collector.search_reviews(link[j] + '&pageNumber=' + str(k))
                soup = BeautifulSoup(response.content)
                print('Collecting reviews')
                for i in soup.findAll("span", {'data-hook': "review-body"}):
                    reviews.append(i.text)
                    starRating.append(i.parent.parent.find('span', {'class': 'a-icon-alt'}).text)
                    if len(reviews) % 100 == 0:
                        revAndRating = {'reviews': reviews, 'starRating': starRating}
                        review_data = pd.DataFrame.from_dict(revAndRating)
                        print('Saving Reviews {} of {}'.format(str(len(reviews)), query_term))
                        review_data.to_csv('Amazon_reviews_' + query_term + '_' + str(page_num) + '.csv')
            if len(reviews) > 10000:
                break
        print('Collected all reviews')
        # Creating DataFrame
        revAndRating = {'reviews': reviews, 'starRating': starRating}
        review_data = pd.DataFrame.from_dict(revAndRating)
        print('Saving Reviews {} of {}'.format(str(len(reviews)), query_term))
        review_data.to_csv('Amazon_reviews_' + query_term + '_'+ str(page_num) + '.csv')
    except Exception as e:
        print(e)
        print("Error encountered while collecting data for term %s"%query_term)

if __name__ == '__main__':
    query_terms = [('jeans', 1),
                   ('jeans', 2),
                   ('jeans', 3),
                   ('jeans', 4),
                   #('shoes', 1),
                   #('shoes', 2),
                   ('shirts', 3),
                   ('shirts', 2),
                   ('sweaters', 1),
                   ('sweaters', 2),
                   ('Jackets', 1),
                   ('Jackets', 2),
                   ('Tshirts', 1),
                   ('Tshirts', 2),
                   ('Pajama', 1),
                   ('Pajama', 2)]
    #with Pool(4) as p:
    #    print(p.map(collect_reviews, query_terms))
    collect_reviews(query_terms[0])
