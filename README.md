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
**Fuel Consumption Data:**

[Scraped from fuelly.com](https://github.com/jkMLnop/Stick-Shift/blob/master/Web_Scraping/scrape_fuelly.py) once a week (for every unique make model year). This data is inserted into a postgres table called ['car_mpgs'](https://github.com/jkMLnop/Stick-Shift/blob/master/Database/create_car_mpgs_final.sql) which is keyed on URL, and has numeric MPG and Year fields. At last benchmark car_mpgs contained 18,558 unique models, with a total of 153,758 rows taking up a total of 37MB. 

**Gas Price Information:**

[Scraped from gasbuddy.com](https://github.com/jkMLnop/Stick-Shift/blob/master/Web_Scraping/scrape_gasbuddy.py) daily for [every US ZIP code](https://raw.githubusercontent.com/jkMLnop/Stick-Shift/master/Web_Scraping/us_zips.csv). This data is inserted into a postgres table called ['gas_prices'](https://github.com/jkMLnop/Stick-Shift/blob/master/Database/create_gas_prices_final.sql) which is keyed on ID (posting ID specifically), and has numeric ZIP, and gas_regular fields. 

**Car Listings:**

[Scraped from craigslist.com](https://github.com/jkMLnop/Stick-Shift/blob/master/Web_Scraping/scrape_craigslist.py) daily. This data is inserted into a postgres table called ['car_listings'](https://github.com/jkMLnop/Stick-Shift/blob/master/Database/create_car_listings_final.sql) which is keyed on ID (again posting ID), and has numeric Price and Model Year fields. At last benchmark car_listings contained a total of 89,726 rows (unique listings) taking up a total of 23MB. 

**US City ZIP Codes:**

[Dowloaded from a database that maps US cities to ZIPs](https://simplemaps.com/data/us-cities), these data contain over 37,000 unique US Cities contained in a .CSV file 4.1MB in size.

### Database Schema:

![alt text][database_schema]

[database_schema]: https://github.com/jkMLnop/Stick-Shift/blob/master/database_schema.PNG "Database Schema"


### Proxies:
**Proxy Rotation & User Agent Cycling:**

When making large ammounts of requests to a target site from same IP address in rapid succession we are likely to eventually get blocked by the server. In order to avoid this outcome both [Craigslist](https://github.com/jkMLnop/Stick-Shift/blob/master/Web_Scraping/scrape_craigslist.py) and [Gasbuddy](https://github.com/jkMLnop/Stick-Shift/blob/master/Web_Scraping/scrape_gasbuddy.py) scrapers rotate through a list of proxies and randomly cycle through user agents, appearing to the target site's server as distinct users accessing the site from various IPs and using various web browsers.  
![alt text][proxy_rotation]


**Proxy IP Scraping & Testing:**

The proxy list is obtained from a [Free Proxy List website](https://www.sslproxies.org/) by the [proxy scraping / testing program](https://github.com/jkMLnop/Stick-Shift/blob/master/Web_Scraping/filter_working_proxies.py). The proxy scraping program tests each proxy scraped from the proxy list page by making requests to http://icanhazip.com which returns the IP of the proxy from which it is recieving requests. If the proxy IP is successfully returned by icanhazip then we know the proxy is currently operational and it is written to [active_proxies.csv](https://github.com/jkMLnop/Stick-Shift/blob/master/Web_Scraping/active_proxies.csv).
![alt text][proxy_scraping]


**Craigslist Routing & Workaround:**

When we make requests of Craigslist using a proxy, craigslist returns us classifieds local to the proxy server's IP, therefore to circumvent this we need to make use of a [database that maps US cities to ZIPs](https://simplemaps.com/data/us-cities), and force craigslist to the specific URL of the target classified instead of letting it route us.
![alt text][craigslist_routing]

[proxy_scraping]: https://github.com/jkMLnop/Stick-Shift/blob/master/proxy_scraping_image.PNG "Proxy Scraping Method"
[proxy_rotation]: https://github.com/jkMLnop/Stick-Shift/blob/master/proxy_rotation_image.PNG "Proxy Rotation Rationale & Method"
[craigslist_routing]: https://github.com/jkMLnop/Stick-Shift/blob/master/craigslist_routing.PNG "Craigslist Routing Workaround"

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
