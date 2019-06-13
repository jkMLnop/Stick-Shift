import requests
import random
import csv
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()
proxies = []

def main():

    #Retrieve latest proxies
    prox_ua = UserAgent()
    prox_url = 'https://www.sslproxies.org/'
    prox_page = requests.get(prox_url,headers={'user-agent':prox_ua.random})
    prox_soup = BeautifulSoup(prox_page.content,'lxml')

    proxies_table = prox_soup.find(id='proxylisttable')

    # Save proxies in an array
    for row in proxies_table.tbody.find_all('tr'):
        proxies.append({
            'ip':   row.find_all('td')[0].string,
            'port': row.find_all('td')[1].string
        })

    #Choose a random proxy
    proxy_index = random_proxy()
    proxy = proxies[proxy_index]

    for n in range(1, 100):

        ip_url = 'http://icanhazip.com'

        #Every 10 requests, generates a new proxy
        if n % 10 == 0:
            proxy_index = random_proxy()
            proxy = proxies[proxy_index]
            prox = {'http': 'http://'+ proxy['ip'] + ':' + proxy['port']}
            #print(prox)

        # Make the call
        try:
            my_ip = requests.get(ip_url, proxies = prox)
            print('#' + str(n) + ': ' + my_ip)
        except: # If error, delete this proxy and find another
            del proxies[proxy_index]
            #print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + 'deleted.')
            proxy_index = random_proxy()
            proxy = proxies[proxy_index]

            print("remaining proxies: ")
            print(proxies)

#Retrieve a random index proxy (we need the index to delete it if its not working)
def random_proxy():
    return random.randint(0, len(proxies) - 1)


if __name__ == '__main__':
    main()
