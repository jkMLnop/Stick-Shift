from flask import render_template
from flaskexample import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask import request
import pandas as pd
import psycopg2

user = ''
host = ''
dbname = ''
password = ''

db = create_engine('postgresql://%s:%s@%s/%s'%(user,password,host,dbname))

print("engine created")

con = None
con = psycopg2.connect( host=host,
                        database=dbname,
                        user=user,
                        password = password)

print("psycopg2 connection made")

@app.route('/main_page', methods = ['POST'] )
def main_page_fancy():
    if request.method == 'POST':
        #pull 'zip' from input field and store it as location
        location = request.form.get('zip_code')
        default_distance = 12000 #Average miles driven / yr

        query_gas_on_zip =  """
                            SELECT * FROM gas_prices_final WHERE zip = '%s' ORDER BY price_regular ASC, distance ASC LIMIT 1;
                            """ %location

        query_gas_result=pd.read_sql_query(query_gas_on_zip,con)
        min_local_gas_price = query_gas_result.iloc[0]['price_regular']
        station_url = query_gas_result.iloc[0]['url']
        print("best gas price: " + str(min_local_gas_price))

        #NOTE sub-$500 posts appear to be mostly leases, therefore excluded them
        sql_query = """
                    SELECT mpg.make, mpg.model, mpg.year, cl.price AS asking_price,
                    cl.date AS posting_date,
                    cl.thumbnail_url,
                    mpg.average_mpgs,
                    ROUND((cl.price + ('%.2f'*(12000 / mpg.average_mpgs))),2) AS total_cost_of_ownership,
                    cl.url
                    FROM car_listings_test as cl
                    INNER JOIN car_avg_mpgs as mpg
                    ON LOWER(cl.make) = LOWER(mpg.make)
                    AND LOWER(cl.model) = LOWER(mpg.model)
                    AND cl.model_year = mpg.year
                    WHERE cl.price > 499
                    ORDER BY total_cost_of_ownership ASC
                    LIMIT 10;
                    """ %min_local_gas_price

        query_results=pd.read_sql_query(sql_query,con)
        cars = []

        for i in range(0,query_results.shape[0]):
            average_mpgs = query_results.iloc[i]['average_mpgs']

            cars.append(dict(   model_year=int(query_results.iloc[i]['year']),\
                                make=query_results.iloc[i]['make'], \
                                model=query_results.iloc[i]['model'],\
                                price=query_results.iloc[i]['asking_price'], \
                                posting_date=query_results.iloc[i]['posting_date'],\
                                total_cost_of_ownership=query_results.iloc[i]['total_cost_of_ownership'],\
                                url=query_results.iloc[i]['url'],\
                                thumbnail_url=query_results.iloc[i]['thumbnail_url'],\
                                estimated_fuel_cost=round((min_local_gas_price*(default_distance/average_mpgs)),2)
                                ))

        return render_template('main_page.html',cars=cars)

@app.route('/')
@app.route('/index')

@app.route('/landing')
def landing():
  return render_template("landing_page.html")
