import requests
import random
import csv
import time
import psycopg2
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def import_proxy_list():
    active_proxies = []

    try:
        with open('active_proxies.csv', mode = 'r') as proxy_file:
            reader = csv.DictReader(proxy_file)

            #reads input file one row at a time
            for row in reader:
                ip     = row["IP"]
                port   = row["PORT"]

                active_proxies.append({
                    'ip':   ip,
                    'port': port
                })

            return active_proxies

    except IOError:
        print('ERROR: Input File I/O Error - Proxy List')

def import_zip_list():
    try:
        with open('us_zips.csv', mode = 'r') as zip_code_file:
            reader = csv.DictReader(zip_code_file)
            location_info = {row['zip']:row['city'] for row in reader}

            return location_info

    except IOError:
        print('ERROR: Input File I/O Error - Zip Codes')

    return location_info

def scrape_by_location(zip_code, city, current_proxy_number, proxy_count, proxy_list, request_count):
    listings_ua = UserAgent()
    listings_url = 'https://' + "".join(city.split(" ")).lower() + '.craigslist.org/search/cta?postal=' + str(zip_code)

    listing_info = {}

    max_attempts = 5                #NOTE arbitrarily set this value. Update later!
    proxy_rotation_interval = 15    #NOTE also arbitrarily set also subject to change

    for failed_attempts in range(max_attempts):
        #iterate to next proxy once proxy rotation interval has been exceeded
        if request_count >= proxy_rotation_interval:
            if current_proxy_number < (proxy_count - 1):
                current_proxy_number += 1
            elif current_proxy_number == (proxy_count - 1):
                current_proxy_number = 0
            request_count = 0

        proxy_info = {'http': 'http://'+ proxy_list[current_proxy_number]['ip'] + ':' + proxy_list[current_proxy_number]['port']}

        try:
            print("attempting to connect to: " + str(listings_url))  
            listings_page = requests.get(listings_url, headers = {'user-agent':listings_ua.random}, proxies = proxy_info, timeout = 5)
            listings_soup = BeautifulSoup(listings_page.content,'lxml')
            listings_ptags = listings_soup.find_all('p', class_ = "result-info")

            # Reads all 16 listings on first page of Craigslist into listing_info dictionary
            for indidividual_posting in listings_ptags:
                post_zip = zip_code
                post_date = indidividual_posting.find('time', class_='result-date').get('datetime')
                post_id = indidividual_posting.find('a').get('data-id')
                post_url = indidividual_posting.find('a').get('href')
                post_title = indidividual_posting.find('a').string
                post_price = (indidividual_posting.find('span', class_='result-price').string)

                # Basic Data Quality Logic
                if post_price[0:1] != '$':
                    continue

                #'$' exclusion to sort listings by cost
                post_price = post_price[1:]

                #filtering out non-numeric 'prices'
                if post_price.isnumeric() == False:
                    continue

                #filtering out common invalid prices
                if int(post_price) == 0:
                    continue
                elif int(post_price) == 1:
                    continue
                elif int(post_price) == 1234:
                    continue
                elif int(post_price) == 12345:
                    continue

                # print("listing info before pg2 scrape:")
                # print(listing_info)
                post_model_year, post_make, post_model, post_thumbnail_url = scrape_pg_2(post_url, proxy_info)
                print("Updated year/make/model is : " + str(post_model_year) + " " + str(post_make) + " " + str(post_model) + " car thumbnail url is: " + str(post_thumbnail_url))

                #write each entry to listing_info dictionary keyed on post id
                listing_info[post_id] = {'post_zip' : post_zip, 'post_date' : post_date, 'post_url' : post_url, 'post_title' : post_title, 'post_price' : post_price, 'post_model_year': post_model_year, 'post_make': post_make, 'post_model': post_model, 'post_thumbnail_url' : post_thumbnail_url}

            request_count += 1
            failed_attempts = max_attempts #NOTE set failed_attempts to max_attempts so loop terminates instead of making further requests upon successful connection!

            break
      
        except Exception as error_message: # If error, cycle to next proxy and reset request count for that proxy to 0 TODO make more specific error conditions!!
            if current_proxy_number < (proxy_count - 1):
                current_proxy_number += 1
            elif current_proxy_number == (proxy_count - 1):
                current_proxy_number = 0

            request_count = 0
            failed_attempts += 1
            
    return current_proxy_number, request_count, listing_info

def scrape_pg_2(post_url, proxy_info):
    pg2_ua = UserAgent()
    pg2_url = post_url

    pg2_page = requests.get(pg2_url, headers = {'user-agent':pg2_ua.random}, proxies = proxy_info, timeout = 5)
    pg2_soup = BeautifulSoup(pg2_page.content,'lxml')

    car_info = pg2_soup.find('p', class_ = "attrgroup").find_next('span').find_next('b').text.split(" ")
    car_year = int(car_info[0])
    car_make = car_info[-2]
    car_model = car_info[-1]

    car_thumbnail = pg2_soup.find('meta', property = 'og:image', content = True).get('content')

    return car_year, car_make, car_model, car_thumbnail

def db_write(listing_info):
    connection = psycopg2.connect(  host='',
                                    database='',
                                    user='',
                                    password = '')

    cursor = connection.cursor()


    # Read all listings from listing_info and load them into postgres car_listings table
    for key,values in listing_info.items():
        cursor.execute("INSERT INTO car_listings_test(zip,id,url,date,title,price,make,model,model_year,thumbnail_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  ON CONFLICT ON CONSTRAINT car_listings_test_pkey DO NOTHING",(values['post_zip'], key, values['post_url'], values['post_date'], values['post_title'], values['post_price'], values['post_make'], values['post_model'], values['post_model_year'], values['post_thumbnail_url']))
    connection.commit()

def main():
    proxy_list = import_proxy_list()
    zip_list   = import_zip_list()
    proxy_count = len(proxy_list)
    current_proxy_number, request_count = 0, 0    
    #scrapes all listings by zip and writes to database for every zip 
    for zip_code,city in zip_list.items():
        current_proxy_number, request_count, listing_info = scrape_by_location(zip_code, city, current_proxy_number, proxy_count, proxy_list, request_count)
        # do not write to database if listing_info is empty (which is the case when URL for currrent city/ZIP doesnt exist)
        if(listing_info):
            db_write(listing_info)
main()
