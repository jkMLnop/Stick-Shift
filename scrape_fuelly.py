import requests
import random
import csv
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

#TODO START HERE: RUN THIS ON CLOUD AND SEE HOW LONG UNTIL YOU GET BLOCKED/HOW BIG DATA WILL BE!!

def write_file(car_data):   #TODO - GET FEEDBACK!: may consider writing less often...
    try:
        with open('individual_car_data.csv', 'a') as outfile:   #TODO Data integrity - if fail, how handle duplicates?
            out_head = ['INDIVIDUAL_URL','AVERAGE_MPG','TIME']
            #TODO Add sorting if default behaviour is not ideal
            sort_by_url_and_mpg = sorted(car_data, key = lambda car_url : (car_url,car_url[1]))

            writer = csv.DictWriter(outfile, fieldnames=out_head)
            #TODO Decide if you need headings written into file or not, if yes do a check to see
            #     if rows exist...
            #writer.writeheader()

            for row in sort_by_url_and_mpg:
                '''
                print("PRINTING ROW!")
                print(row)
                '''
                writer.writerow(
                        {   'INDIVIDUAL_URL'   :    row,
                            'AVERAGE_MPG'      :    22,
                            'TIME'             :    time.time()}
                )
                #TODO Figure out how to pull individual_mpg's (value of our individual_car_data dictionary!)

    except IOError:
        print("I/O ERROR: file not found!") #TODO this error doesnt work.. fix it!

def years(model_year_link):
    individual_car_data = {}

    year_ua = UserAgent()
    year_page = requests.get(model_year_link,headers={'user-agent':year_ua.random})
    year_soup = BeautifulSoup(year_page.content,'lxml')

    year_ul_container = year_soup.find_all('ul',class_="browse-by-vehicle-display")

    for result in year_ul_container:
        individual_url = result.get('data-clickable')
        individual_mpg = result.find('div',class_='vertical-stat').find('strong').text

        #Store Individual Car Data into a Dict Where URL is Key and MPG is Value
        individual_car_data[individual_url]=individual_mpg

    #NOTE For now we will write for every model year, because it's more intuitive...
    #NOTE Can move this call to a model/make instead.. depends on implications
    write_file(individual_car_data)

#Pulls links for every year of the current model and store in array
def models(car_model_link):
    model_ua = UserAgent()
    model_page = requests.get(car_model_link,headers={'user-agent':model_ua.random})
    model_soup = BeautifulSoup(model_page.content,'lxml')

    model_uls = model_soup.find_all('ul', class_ = "model-year-summary")

    all_model_year_links = [ul.get('data-clickable') for ul in model_uls]

    for model_year_link in all_model_year_links:
        years(model_year_link)

def makes():
    make_ua = UserAgent()
    make_url = 'http://www.fuelly.com/car'
    make_page = requests.get(make_url,headers={'user-agent':make_ua.random})
    make_soup = BeautifulSoup(make_page.content,'lxml')

    make_divs = make_soup.find_all('div', class_ = "col-sm-12 col-md-12")

    #pull all possible car model page links and store in array
    all_car_model_links = [atag.get('href') for atag in make_divs[1].find_all('a')] #make_divs[1] accesses div with model info

    for car_model_link in all_car_model_links:
        models(car_model_link)

makes()
