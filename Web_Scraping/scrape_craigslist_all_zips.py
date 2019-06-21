import requests
import random
import csv
import time
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
    try:
        with open('us_zips.csv', mode = 'r') as zip_code_file:
            reader = csv.DictReader(zip_code_file)
            location_info = {row['zip']:row['city'] for row in reader}

            return location_info

    except IOError:
        print('ERROR: Input File I/O Error - Zip Codes')

    return location_info

    #TODO update this later to obtain range of all ZIP/cities within x mile radius of user's search

def scrape_by_location(zip_code, city, current_proxy_number, proxy_count, proxy_list, request_count):
    listings_ua = UserAgent()
    listings_url = 'https://' + "".join(city.split(" ")).lower() + '.craigslist.org/search/cta?postal=' + str(zip_code) #TODO Change for gasbuddy scraper!

    listing_info = {}

    max_attempts = 5                #NOTE arbitrarily set this value. Update later!
    proxy_rotation_interval = 15    #NOTE also arbitrarily set also subject to change

    #TODO START HERE:
        #1) Connection error trapping code,
        #2) Figure out parallel scraping
        #3) START HERE Figure out error trapping for error: 'HTTPSConnectionPool(host='sabanahoyos.craigslist.org', port=443): Max retries exceeded with url: /search/cta?postal=00688 (Caused by NewConnectionError('<urllib3.connection.VerifiedHTTPSConnection object at 0x7f7b1ef778d0>: Failed to establish a new connection: [Errno -2] Name or service not known',))'
        #   Is this different then a server blocking my IP? can i create a map of valid urls from this run - ADD TO EXCEPTION and exclude it! then write to a valid zip csv file so next time you dont try invalid zips!

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
                post_price = indidividual_posting.find('span', class_='result-price').string

                #write each entry to listing_info dictionary keyed on post id
                listing_info[post_id] = {'post_zip' : post_zip, 'post_date' : post_date, 'post_url' : post_url, 'post_title' : post_title, 'post_price' : post_price}

            #print("connected successfully: " + str(listings_page)) #TODO REMOVE FOR PROD

            request_count += 1
            failed_attempts = max_attempts #NOTE set failed_attempts to max_attempts so loop terminates instead of making further requests upon successful connection!

            break
        #ADD THE ERROR TRAPPING HERE!
        #except requests.ConnectTimeout:
        #    pass

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

def write_to_file(listing_info):
    try:
        with open('recent_listings.csv', 'a') as outfile:
            out_head = ['POST_ZIP','POST_ID','POST_URL','POST_DATE','POST_TITLE','POST_PRICE', 'TIMESTAMP']

            writer = csv.DictWriter(outfile, fieldnames=out_head)

            for key, values in listing_info.items():
                writer.writerow(
                        {   'POST_ZIP'  :    values['post_zip'],
                            'POST_ID'   :    key,
                            'POST_URL'  :    values['post_url'],
                            'POST_DATE' :    values['post_date'],
                            'POST_TITLE':    values['post_title'],
                            'POST_PRICE':    values['post_price'],
                            'TIMESTAMP' :    time.time()}
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
