# Stick-Shift - *Kicking Car Buying into High Gear*
A tool to help car-buyers find the best deals in the country and inform them about what they can expect to spend when they do!

[Presentation link](https://docs.google.com/presentation/d/1wDi4mnvDYej3x5vrNPCKJv7Hc8r0qw_UOUuXyXFpN_w/edit#slide=id.p)

[Website](http://www.stick-shift.ca/)

# Table of Contents
1. [Problem](README.md#problem)
1. [Solution](README.md#solution)
1. [Directory Structure](README.md#directory-structure)
1. [Contact Information](README.md#contact-information)

# Problem:

The average American spent an average of [$1400](https://www.fool.com/investing/2017/01/14/heres-how-much-gasoline-the-average-american-consu.aspx) on gasoline in 2015, and in 2018 would go on to spend an average of [$20,084](https://www.usatoday.com/story/money/cars/2018/11/08/used-car-prices/1928840002/) on the purchase of a pre-owned vehicle. Needless to say car ownership is an expensive endeavor, and buyers often don’t fully realize the costs of owning and driving a particular car until after they have already taken the leap and bought a vehicle. To make matters even more complicated, both the vehicle prices and the cost of gas vary widely from one region to the next (over [$900 in some cases](https://www.businessinsider.com/how-much-the-average-person-spends-on-gas-in-every-state-2019-2)). To help connect car buyers with the best local deals and also empower them to broaden their search radius to find even better deals I built Stick-Shift. 

# Solution:

### Introduction:
Stick-Shift is a scalable scraping system which combines car and gas prices by area with real-world fuel consumption data for every vehicle; users will instantly see the top 10 cheapest cars to buy and drive nation-wide with current annual fuel consumption estimates based on prices in their local area.

### Data Pipeline:
![alt text][pipeline]

[pipeline]: https://github.com/jkMLnop/Stick-Shift/blob/master/pipeline_image.PNG "Stick-Shift Data Pipeline"

### Data Sources:
**Fuel consumption data:**
[Scraped from fuelly.com](https://github.com/jkMLnop/Stick-Shift/blob/master/Web_Scraping/scrape_fuelly.py) once a week (for every unique make model year). This data is inserted into a postgres table called ['car_mpgs'](https://github.com/jkMLnop/Stick-Shift/blob/master/Database/create_car_mpgs_final.sql) which is keyed on URL, and has numeric MPG and Year fields.

### Proxies:

# Directory Structure:

    ├── README.md 
    ├── Database
    │   └── create_car_listings_final.sql
    │   └── create_car_mpgs_final.sql
    │   └── create_gas_prices_final.sql
    ├── Web_Scraping
    │   └── active_proxies.csv
    │   └── filter_working_proxies.py
    │   └── node_scraper_setup.sh
    │   └── scrape_craigslist.py
    │   └── scrape_fuelly.py
    │   └── scrape_gasbuddy.py
    │   └── us_zips.csv
    └── Flask_WebApp
        └── Flask_WebApp
            └── run.py
            └── flaskexample
                ├── __pycache__
                │   └── ...
                ├── static
                │   └── ...
                ├── templates
                │   └── landing_page.html
                │   └── main_page.html
                │   └── starter-template.css
                ├── __init__.py
                └── views.py

# Contact Information:
* Email:    konradkarolak87@gmail.com
* LinkedIn: linkedin.com/in/konradkarolak
* GitHub:   https://github.com/jkMLnop
* Project Website: http://stick-shift.ca
