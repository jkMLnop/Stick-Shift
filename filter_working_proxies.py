import requests
import csv
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

#Retrieves latest proxies
def scrape_proxies():
    ssl_proxies = []

    ssl_ua = UserAgent()
    ssl_url = 'https://www.sslproxies.org/'
    ssl_page = requests.get(ssl_url,headers={'user-agent':ssl_ua.random})
    ssl_soup = BeautifulSoup(ssl_page.content,'lxml')

    ssl_proxy_table = ssl_soup.find(id='proxylisttable')

    # Save proxies in an array
    for row in ssl_proxy_table.tbody.find_all('tr'):
        ssl_proxies.append({
            'ip':   row.find_all('td')[0].string,
            'port': row.find_all('td')[1].string
        })

    return ssl_proxies

def test_proxies(proxy_list):
    ip_url = 'http://icanhazip.com'

    #TODO ADRI SAYS: Change this to go through the proxy list instead of using index - python not optimized for iterating with indexes!
    #for current_proxy in proxy_list:
    for n in range (len(proxy_list)-1):    #TODO possibly fix this? index out of bounds error encountered towards the end of it
        current_proxy = proxy_list[n]
        proxy_info = {'http': 'http://'+ current_proxy['ip'] + ':' + current_proxy['port']}

        #Test each SSL proxy 10x to see if its still active
        for n in range(10):    #TODO Get Feedback, 1) is 10 requests good? 2) is using icanhazip even relevant? 3) test on scrape target?
            try:
                proxy_ip = requests.get(ip_url, proxies = proxy_info)
                #TODO ADRI SAYS: append to a new list of working proxies instead of deleting from current
            except: # If error, delete this proxy and find another
                #TODO add some kind of error logging to better identify when its being rejected/blocked by server
                print('Proxy ' + current_proxy['ip'] + ':' + current_proxy['port'] + ' deleted.')
                del proxy_list[n]   #TODO ADRI SAYS: remove once you add append to new list functionality above

        return  proxy_list

def write_active_proxy_list(active_proxies):

    try:
        with open('active_proxies.csv', 'w') as outfile:
            out_head = ['IP','PORT']

            writer = csv.DictWriter(outfile, fieldnames=out_head)
            writer.writeheader()

            for row in active_proxies:

                writer.writerow(
                        {   'IP'   :    row['ip'],
                            'PORT' :    row['port']}
                )

    except IOError:
        print("I/O ERROR: file not found!") #TODO this error doesnt work.. fix it!

    return

#TODO 4) will have to update scrapers to read into array a list of working proxies and to rotate through them and remove dead ones also!

proxy_list = scrape_proxies()
active_proxies = test_proxies(proxy_list)
write_active_proxy_list(active_proxies)
