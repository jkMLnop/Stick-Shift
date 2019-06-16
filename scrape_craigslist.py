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
    proxy_info = {'http': 'http://'+ proxy_list[current_proxy_number]['ip'] + ':' + proxy_list[current_proxy_number]['port']}
    listings_ua = UserAgent()
    listings_url = 'https://' + "".join(city.split(" ")).lower() + '.craistlist.org/search/cta?postal=' + str(zip_code) #TODO Change for gasbuddy scraper!

    #TODO START HERE:
        #1) fix the except block, why is it not immediately rotating to the next proxy?
        #2) fix the proxy test code - find and reference your previous implementation of danilo's code perhaps?
        #3) implement the common scraping code + copy one last time to gasbuddy code
        #4) fully implement the scraping code for CL first page & return the data to main
        #5) add CSV writing functionality
        #6) push to AWS
        #7) implement boto3 S3 bucket writing functionality
    try:    #
        '''
        listings_page = requests.get(listings_url,headers={'user-agent':listings_ua.random}, proxies = proxy_info)
        '''
        #TODO scraping code goes here!
        #listings_page = requests.get(listings_url,headers={'user-agent':listings_ua.random})
        #make_soup = BeautifulSoup(listings_page.content,'lxml')

        #TODO Test that proxy IP is the one being used here!!
        ip_url = 'http://icanhazip.com'
        proxy_ip = requests.get(ip_url, proxies = proxy_info)
        print('proxy_ip get request: ' + proxy_ip)

    except: # If error, cycle to next proxy
        if current_proxy_number < (proxy_count - 1):
            current_proxy_number += 1
            request_count = 0
            print("rotating to next proxy!!!!!")    #TODO Test this by doing ctrl + x  while it runs later!
        elif current_proxy_number == (proxy_count - 1):
            current_proxy_number = 0
            request_count = 0
            print("rotating to first proxy!!!!!")    #TODO Test this by doing ctrl + x  while it runs later!

        #TODO Possibly add proxy deletion capacity

    print("proxy_info: " + str(proxy_info))

    return(current_proxy_number, proxy_count, proxy_list, request_count) #TODO RETURN ALL DATA FOR THAT PAGE + ALL VARIABLES RELATING TO PROXY!

def main():
    proxy_list = import_proxy_list()
    zip_list   = import_zip_list()
    proxy_count = len(proxy_list)
    current_proxy_number  = 0    #TODO: Can I initialize in the loop?
    request_count = 0
    proxy_rotation_interval = 15

    for zip_code,city in zip_list.items():

        listings = scrape_by_location(zip_code, city, current_proxy_number, proxy_count, proxy_list, request_count)
        #write_to_file(listings)

        request_count += 1
        #print("request count: " + str(request_count))
        #print("current proxy number: " + str(current_proxy_number)  + " ip: " + str(proxy_list[current_proxy_number]['ip']) + " port: " + str(proxy_list[current_proxy_number]['port']))

        #iterate to next proxy
        if request_count >= proxy_rotation_interval:
            if current_proxy_number < (proxy_count - 1):
                current_proxy_number += 1
                request_count = 0
            elif current_proxy_number == (proxy_count - 1):
                current_proxy_number = 0
                request_count = 0

main()
