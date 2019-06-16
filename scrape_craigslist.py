import requests
import random
import csv
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
    max_attempts = 5                #NOTE arbitrarily set this value. Update later!
    proxy_rotation_interval = 15    #NOTE also arbitrarily set also subject to change

    #TODO START HERE:
        #3) implement the common scraping code + copy one last time to gasbuddy code
        #4) fully implement the scraping code for CL first page & return the data to main
        #5) add CSV writing functionality
        #6) push to AWS
        #7) implement boto3 S3 bucket writing functionality

    for failed_attempts in range(max_attempts):
        ip_url = 'http://icanhazip.com'#TODO Remove after test!

        #iterate to next proxy once proxy rotation interval has been exceeded
        if request_count >= proxy_rotation_interval:
            if current_proxy_number < (proxy_count - 1):
                current_proxy_number += 1
            elif current_proxy_number == (proxy_count - 1):
                current_proxy_number = 0
            request_count = 0
            print("proxy rotation interval exceeded, current proxy number: " + str(current_proxy_number) + " request count reset to: " + str(request_count))

        proxy_info = {'http': 'http://'+ proxy_list[current_proxy_number]['ip'] + ':' + proxy_list[current_proxy_number]['port']}

        try:    #
            '''
            listings_page = requests.get(listings_url,headers={'user-agent':listings_ua.random}, proxies = proxy_info)
            '''
            proxy_ip = requests.get(ip_url, proxies = proxy_info, timeout = 5)  #TODO Remove after test!
            request_count += 1
            failed_attempts = 0 #NOTE might change this if we scrape deeper and fail on subsequent pages..
            #TODO scraping code goes here!

        except: # If error, cycle to next proxy and reset request count for that proxy to 0 TODO make more specific error conditions!!
            if current_proxy_number < (proxy_count - 1):
                current_proxy_number += 1
            elif current_proxy_number == (proxy_count - 1):
                current_proxy_number = 0

            request_count = 0
            failed_attempts += 1
            print("connection error encountered, rotating to proxy number: " + str(current_proxy_number))

            #TODO Possibly add proxy deletion capacity here

    print("current proxy number: " + str(current_proxy_number) + " current request count: " + str(request_count))
    return current_proxy_number, request_count #TODO add scraped page data output parameter here

def main():
    proxy_list = import_proxy_list()
    zip_list   = import_zip_list()
    proxy_count = len(proxy_list)
    current_proxy_number  = 0    #TODO: Can I initialize in the loop?
    request_count = 0

    #scrapes all listings by zip and write to file (in S3) for every zip in user's range of interest
    for zip_code,city in zip_list.items():
        current_proxy_number, request_count = scrape_by_location(zip_code, city, current_proxy_number, proxy_count, proxy_list, request_count)
        #write_to_file(listings)
main()
