import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

#Pulls links for every year of the current model and store in dict
def model_years(car_model_link):
    #TODO do I need seperate UA or can I pass it in?
    year_ua = UserAgent()
    year_page = requests.get(car_model_link,headers={'user-agent':year_ua.chrome})
    year_soup = BeautifulSoup(year_page.content,'lxml')

    uls = year_soup.find_all('ul', class_ = "model-year-summary")

    all_model_year_links = [ul.get('data-clickable') for ul in uls]

    print(all_model_year_links)
    #TODO START HERE: Why are there empty dicts sometimes?
    #TODO   write next function for each model year to store all fuel data for a
    #       model year to a file

user_agent = UserAgent()
main_url = 'http://www.fuelly.com/car'
page = requests.get(main_url,headers={'user-agent':user_agent.chrome})
soup = BeautifulSoup(page.content,'lxml')

all_divs = soup.find_all('div', class_ = "col-sm-12 col-md-12")

#NOTE do this to get to the second div which contains car model info
div_container = all_divs[1]

#pull all possible car model page links and store in dict
all_car_model_links = [atag.get('href') for atag in div_container.find_all('a')]

#print(all_car_model_links)

for car_model_link in all_car_model_links:
    model_years(car_model_link)
