import requests
import random
import csv
import time
import psycopg2
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

#Pulls all models for every make
def makes():
    #begin timing (for ease of benchmarking)
    start = time.time()

    make_ua = UserAgent()
    make_url = 'http://www.fuelly.com/car'
    make_page = requests.get(make_url,headers={'user-agent':make_ua.random})
    make_soup = BeautifulSoup(make_page.content,'lxml')

    make_divs = make_soup.find_all('div', class_ = "col-sm-12 col-md-12")

    #pull all possible car model page links and store in array
    all_car_model_links = [atag.get('href') for atag in make_divs[1].find_all('a')] #make_divs[1] accesses div with model info

    for car_model_link in all_car_model_links:
        models(car_model_link)

    #end timing
    print("total time: " + str(round(time.time() - start)) + " sec.")

#Pulls links for every year of the current model and store in array
def models(car_model_link):
    model_ua = UserAgent()
    model_page = requests.get(car_model_link,headers={'user-agent':model_ua.random})
    model_soup = BeautifulSoup(model_page.content,'lxml')

    model_uls = model_soup.find_all('ul', class_ = "model-year-summary")

    all_model_year_links = [ul.get('data-clickable') for ul in model_uls]

    for model_year_link in all_model_year_links:
        years(model_year_link)

#Pulls all model years available for every make and model of car
def years(model_year_link):
    individual_car_data = {}

    year_ua = UserAgent()
    year_page = requests.get(model_year_link,headers={'user-agent':year_ua.random})
    year_soup = BeautifulSoup(year_page.content,'lxml')

    year_ul_container = year_soup.find_all('ul',class_="browse-by-vehicle-display")

    for result in year_ul_container:
        individual_url = result.get('data-clickable')
        individual_mpg = result.find('div',class_='vertical-stat').find('strong').text
        car_info = individual_url.split('/')
        individual_make = car_info[4]
        individual_model = car_info[5]
        individual_year = car_info[6]

        #Data Quality Tests

        #filtering out non-numeric mpgs
        try:
            float(individual_mpg)
        except ValueError:
            continue

        #filtering out non-numeric mpgs
        if individual_year.isnumeric() == False:
            continue

        #Store Individual Car Data into a Dict Where URL is Key and MPG is Value
        individual_car_data[individual_url]={'individual_mpg' : individual_mpg, 'individual_make' : individual_make, 'individual_model' : individual_model, 'individual_year' : individual_year}

    #NOTE For now we will write for every model year, because it's more intuitive...
    #NOTE Can move this call to a model/make instead.. depends on implications
    db_write(individual_car_data)

#write car mpg info to postgress
def db_write(car_data):
    connection = psycopg2.connect(  host='',
                                    database='',
                                    user='',
                                    password = '')

    cursor = connection.cursor()

    for key,values in car_data.items():
        cursor.execute("INSERT INTO car_mpgs_test(url, mpg, make, model, year) VALUES (%s, %s, %s, %s, %s) ON CONFLICT ON CONSTRAINT car_mpgs_test_pkey DO NOTHING",(key, values['individual_mpg'], values['individual_make'], values['individual_model'], values['individual_year']))
    connection.commit()

makes()
