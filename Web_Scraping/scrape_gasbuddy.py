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
        print('ERROR: INPUT File I/O Error')

def import_zip_list():
    #NOTE this assumes that zip codes for a given city will be concurrent.. Might need to change later
    zip_code = range(10001,11700)
    city = ['New York']*(11700-10001)
    location_info = {x:y for x,y in zip(zip_code,city)}
    return location_info

def scrape_by_location(zip_code, city, current_proxy_number, proxy_count, proxy_list, request_count):
    prices_ua = UserAgent()
    prices_url = 'https://www.gasbuddy.com/home?search=' + str(zip_code) + '&fuel=1'      #EXAMPLE URL: https://www.gasbuddy.com/home?search=10001&fuel=1

    station_info = {}

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

        try:    #
            prices_page = requests.get(prices_url, headers = {'user-agent':prices_ua.random}, proxies = proxy_info, timeout = 5)
            prices_soup = BeautifulSoup(prices_page.content,'lxml')
            prices_h3_container = prices_soup.find_all('h3', class_= "header__header3___1b1oq header__header___1zII0 header__snug___lRSNK GenericStationListItem__stationNameHeader___3qxdy")

            #NOTE because gasbuddy tags of interest aren't nested must iterate by 'h3' tag and use find_next to find all subsequent fields desired
            for indidividual_posting in prices_h3_container:
                station_name = indidividual_posting.string
                station_price_reg = indidividual_posting.find_next('span', class_ = "GenericStationListItem__price___3GpKP").string
                station_address = indidividual_posting.find_next('div', class_ = "GenericStationListItem__address___1VFQ3").get_text(" ")   #NOTE adress broken up by <br/> used get_text to join text segments on a space!
                station_distance = indidividual_posting.find_next('div', class_ = "StationDistance__distanceContainer___3JFP6").string

                try:
                    station_link = indidividual_posting.find_next('div', class_ = "GenericStationListItem__mainInfoColumn___2kuPq GenericStationListItem__column___2Yqh-").find_next('a').get('href')
                    station_id = station_link[(station_link.find('/station/') + 9):]
                    station_url = "https://www.gasbuddy.com" + str(station_link)
                except AttributeError:
                    station_link = ""
                    station_id = ""
                    station_url = ""

                station_zip = zip_code

                #clears last updated for stations where price is not known 
                if "---" not in str(station_price_reg):
                    station_last_update = indidividual_posting.find_next('span', class_ = "ReportedBy__postedTime___J5H9Z").string
                else:
                    station_last_update = "---"

                station_info[station_id] = {'station_name'      : station_name,
                                            'station_price_reg' : station_price_reg,
                                            'station_address'   : station_address,
                                            'station_distance'  : station_distance,
                                            'station_url'       : station_url,
                                            'station_zip'       : station_zip}
            
            request_count += 1
            failed_attempts = max_attempts #NOTE set failed_attempts to max_attempts so loop terminates instead of making further requests upon successful connection!
            break

        except Exception as e:  # If error, cycle to next proxy and reset request count for that proxy to 0
            if current_proxy_number < (proxy_count - 1):
                current_proxy_number += 1
            elif current_proxy_number == (proxy_count - 1):
                current_proxy_number = 0

            request_count = 0
            failed_attempts += 1
            print("connection error _" + str(e) + "_ encountered at station link: " +  str(station_link) + " and station id: "+ str(station_last_update) + ", rotating to proxy number: " + str(current_proxy_number))   #NOTE might keep for error trapping..

    return current_proxy_number, request_count, station_info

def write_to_file(listing_info):
    try:
        with open('recent_gas_prices.csv', 'a') as outfile:
            out_head = [    'STATION_ZIP',
                            'STATION_ID',
                            'STATION_NAME',
                            'STATION_PRICE_REGULAR',
                            'STATION_ADRESS',
                            'STATION_DISTANCE',
                            'STATION_URL',
                            'TIMESTAMP']

            writer = csv.DictWriter(outfile, fieldnames=out_head)

            for key, values in listing_info.items():
                writer.writerow(
                        {   'STATION_ZIP'           :   values['station_zip'],
                            'STATION_ID'            :   key,
                            'STATION_NAME'          :   values['station_name'],
                            'STATION_PRICE_REGULAR' :   values['station_price_reg'],
                            'STATION_ADRESS'        :   values['station_address'],
                            'STATION_DISTANCE'      :   values['station_distance'],
                            'STATION_URL'           :   values['station_url'],
                            'TIMESTAMP'             :   time.time()}
                )

    except IOError:
        print("ERROR: OUTPUT File I/O Error")

def main():
    proxy_list = import_proxy_list()
    zip_list   = import_zip_list()
    proxy_count = len(proxy_list)
    current_proxy_number, request_count = 0, 0

    #scrapes all prices by zip and write to file (in S3) for every zip in user's range of interest
    for zip_code,city in zip_list.items():
        current_proxy_number, request_count, station_info = scrape_by_location(zip_code, city, current_proxy_number, proxy_count, proxy_list, request_count)
        write_to_file(station_info)
main()
