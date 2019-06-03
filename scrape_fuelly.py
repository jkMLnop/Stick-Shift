import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


user_agent = UserAgent()
main_url = 'http://www.fuelly.com/car'
page = requests.get(main_url,headers={'user-agent':user_agent.chrome})
soup = BeautifulSoup(page.content,'lxml')

all_h4s = soup.find_all('h4',class_='make-header')

# Stores all links (h4.a['href']) into a dictionary for ease of access
all_links = [h4.a['href'] for h4 in all_h4s]

#TODO 1) pull the links for all models from this page as it is much cleaner!
print(all_links)

#TODO 2) do this for each model page
'''
# Loop through Car Model page to find all model years
for link in all_links: #TODO change to full dataset later
    inner_page = requests.get(link, headers={'user-agent':user_agent.chrome})
    inner_soup = BeautifulSoup(inner_page.content,'lxml')

    print(link)

    all_uls = inner_soup.find('ul',class_='model-year-summary')

    #all_years = [ul['data-clickable'] for ul in all_uls]

    print(all_uls)

    #print(all_years)
'''
