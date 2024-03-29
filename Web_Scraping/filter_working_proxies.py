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

    #for current_proxy in proxy_list:
    for n in range (len(proxy_list)-1): 
        current_proxy = proxy_list[n]
        proxy_info = {'http': 'http://'+ current_proxy['ip'] + ':' + current_proxy['port']}

        #Test each SSL proxy 10x to see if its still active
        for n in range(10):    
            try:
                proxy_ip = requests.get(ip_url, proxies = proxy_info)
            except: # If error, delete this proxy and find another
                print('Proxy ' + current_proxy['ip'] + ':' + current_proxy['port'] + ' deleted.')
                del proxy_list[n]

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
        print("I/O ERROR: file not found!") 

    return

proxy_list = scrape_proxies()
active_proxies = test_proxies(proxy_list)
write_active_proxy_list(active_proxies)
