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
        print('ERROR: Input File I/O Error')

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
    listings_url = 'https://' + "".join(city.split(" ")).lower() + '.craigslist.org/search/cta?postal=' + str(zip_code) #TODO Change for gasbuddy scraper!

    listing_info = {}

    max_attempts = 5                #NOTE arbitrarily set this value. Update later!
    proxy_rotation_interval = 15    #NOTE also arbitrarily set also subject to change

    #TODO START HERE:
        #1) Connection error trapping code,
        #2) Integration Test '$' Exclusion logic!
        #3) ADD $0 / $1 /$1234 exclusion logic!
        #4) get peter's feedback on 'TODO ASK PETER' points below!

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
            #print("attempting to connect to: " + str(listings_url))    #TODO REMOVE FOR PROD
            listings_page = requests.get(listings_url, headers = {'user-agent':listings_ua.random}, proxies = proxy_info, timeout = 5)
            listings_soup = BeautifulSoup(listings_page.content,'lxml')
            listings_ptags = listings_soup.find_all('p', class_ = "result-info")

            for indidividual_posting in listings_ptags:
                post_zip = zip_code
                post_date = indidividual_posting.find('time', class_='result-date').get('datetime')
                post_id = indidividual_posting.find('a').get('data-id')
                post_url = indidividual_posting.find('a').get('href')
                post_title = indidividual_posting.find('a').string
                post_price = (indidividual_posting.find('span', class_='result-price').string)[1:]  #NOTE Added '$' exclusion to sort by cost!

                #write each entry to listing_info dictionary keyed on post id
                listing_info[post_id] = {'post_zip' : post_zip, 'post_date' : post_date, 'post_url' : post_url, 'post_title' : post_title, 'post_price' : post_price}

            #print("connected successfully: " + str(listings_page)) #TODO REMOVE FOR PROD

            request_count += 1
            failed_attempts = max_attempts #NOTE set failed_attempts to max_attempts so loop terminates instead of making further requests upon successful connection!

            break

        #ADD THE ERROR TRAPPING HERE!

        except Exception as error_message: # If error, cycle to next proxy and reset request count for that proxy to 0 TODO make more specific error conditions!!
            if current_proxy_number < (proxy_count - 1):
                current_proxy_number += 1
            elif current_proxy_number == (proxy_count - 1):
                current_proxy_number = 0

            request_count = 0
            failed_attempts += 1
            print("connection error: '" + str(error_message) + "' encountered, rotating to proxy number: " + str(current_proxy_number))

            #TODO Possibly add proxy deletion capacity here

    #TODO Add empty listing/failed connection > 5 handling logic here.. (eg ZIP doesnt exist..)
    #print("current proxy number: " + str(current_proxy_number) + " current request count: " + str(request_count)) #TODO REMOVE FOR PROD
    return current_proxy_number, request_count, listing_info

def db_write(listing_info):
    connection = psycopg2.connect(  host='',
                                    database='',
                                    user='',
                                    password = '') #TODO GITIGNORE THIS!

    cursor = connection.cursor()

    #TODO ASK PETER: Possibly change or remove this...
    # Clear car_listings table before writing in latest data:
    cursor.execute("DELETE FROM car_listings")
    print("deleted current car_listings records")

    # TODO ASK PETER: IF THIS IS OK? OR BATCH FROM CSV?
    # Read all listings from listing_info and load them into postgres car_listings table
    for key,values in listing_info.items():
        cursor.execute("INSERT INTO car_listings(post_zip,post_id,post_url,post_date,post_title,post_price) VALUES (%s, %s, %s, %s, %s, %s)",(values['post_zip'], key, values['post_url'], values['post_date'], values['post_title'], values['post_price']))

    print("wrote successfully!!")
    connection.commit()

def main():
    proxy_list = import_proxy_list()
    zip_list   = import_zip_list()
    proxy_count = len(proxy_list)
    current_proxy_number, request_count = 0, 0    #TODO: Can I initialize in the loop?

    #scrapes all listings by zip and write to file (in S3) for every zip in user's range of interest
    for zip_code,city in zip_list.items():
        current_proxy_number, request_count, listing_info = scrape_by_location(zip_code, city, current_proxy_number, proxy_count, proxy_list, request_count)
        db_write(listing_info)
main()
