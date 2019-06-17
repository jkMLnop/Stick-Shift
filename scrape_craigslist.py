import requests
import random
import csv
import boto3
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
    #NOTE this assumes that zip codes for a given city will be concurrent.. Might need to change later
    zip_code = range(10001,11700)
    city = ['New York']*(11700-10001)
    location_info = {x:y for x,y in zip(zip_code,city)}
    return location_info

    #TODO update this later to obtain range of all ZIP/cities within x mile radius of user's search

def scrape_by_location(zip_code, city, current_proxy_number, proxy_count, proxy_list, request_count):
    listings_ua = UserAgent()
    listings_url = 'https://' + "".join(city.split(" ")).lower() + '.craigslist.org/search/cta?postal=' + str(zip_code) #TODO Change for gasbuddy scraper!

    listing_info = {}

    max_attempts = 5                #NOTE arbitrarily set this value. Update later!
    proxy_rotation_interval = 15    #NOTE also arbitrarily set also subject to change

    #TODO START HERE:
        #5) add timestamp and zip code fields
        #6) push to AWS
        #7) run on AWS without issues!
        #8) implement boto3 S3 bucket writing functionality

    for failed_attempts in range(max_attempts):
        #iterate to next proxy once proxy rotation interval has been exceeded
        if request_count >= proxy_rotation_interval:
            if current_proxy_number < (proxy_count - 1):
                current_proxy_number += 1
            elif current_proxy_number == (proxy_count - 1):
                current_proxy_number = 0
            request_count = 0

        proxy_info = {'http': 'http://'+ proxy_list[current_proxy_number]['ip'] + ':' + proxy_list[current_proxy_number]['port']}

        try:    #
            print("attempting to connect to: " + str(listings_url))
            listings_page = requests.get(listings_url, headers = {'user-agent':listings_ua.random}, proxies = proxy_info, timeout = 5)
            listings_soup = BeautifulSoup(listings_page.content,'lxml')
            listings_ptags = listings_soup.find_all('p', class_ = "result-info")

            for indidividual_posting in listings_ptags:
                post_date = indidividual_posting.find('time', class_='result-date').get('datetime')
                post_id = indidividual_posting.find('a').get('data-id')
                post_url = indidividual_posting.find('a').get('href')
                post_title = indidividual_posting.find('a').string
                post_price = indidividual_posting.find('span', class_='result-price').string

                #write each entry to listing_info dictionary keyed on post id
                listing_info[post_id] = {'post_date' : post_date, 'post_url' : post_url, 'post_title' : post_title, 'post_price' : post_price}

            print("connected successfully: " + str(listings_page))

            request_count += 1
            failed_attempts = max_attempts #NOTE set failed_attempts to max_attempts so loop terminates instead of making further requests upon successful connection!

            break

        except: # If error, cycle to next proxy and reset request count for that proxy to 0 TODO make more specific error conditions!!
            if current_proxy_number < (proxy_count - 1):
                current_proxy_number += 1
            elif current_proxy_number == (proxy_count - 1):
                current_proxy_number = 0

            request_count = 0
            failed_attempts += 1
            print("connection error encountered, rotating to proxy number: " + str(current_proxy_number))

            #TODO Possibly add proxy deletion capacity here

    #TODO Add empty listing/failed connection > 5 handling logic here.. (eg ZIP doesnt exist..)
    print("current proxy number: " + str(current_proxy_number) + " current request count: " + str(request_count))
    return current_proxy_number, request_count, listing_info

def write_to_file(listing_info):
    try:
        with open('recent_listings.csv', 'a') as outfile:
            out_head = ['POST_ID','POST_URL','POST_DATE','POST_TITLE','POST_PRICE']

            writer = csv.DictWriter(outfile, fieldnames=out_head)

            for key, values in listing_info.items():
                writer.writerow(
                        {   'POST_ID'   :    key,
                            'POST_URL'  :    values['post_url'],
                            'POST_DATE' :    values['post_date'],
                            'POST_TITLE':    values['post_title'],
                            'POST_PRICE':    values['post_price']}
                )

    except IOError:
        print("I/O ERROR: file not found!")

def main():
    proxy_list = import_proxy_list()
    zip_list   = import_zip_list()
    proxy_count = len(proxy_list)
    current_proxy_number, request_count = 0, 0    #TODO: Can I initialize in the loop?

    #scrapes all listings by zip and write to file (in S3) for every zip in user's range of interest
    for zip_code,city in zip_list.items():
        current_proxy_number, request_count, listing_info = scrape_by_location(zip_code, city, current_proxy_number, proxy_count, proxy_list, request_count)
        write_to_file(listing_info)
main()
