from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext

sc = SparkContext('local','building a fuel price data warehouse')
sqlContext = SQLContext(sc)

#TODO 1) Load Data from S3
#TODO 2) Add Insert or update functionality
#TODO 3) figure out how to define key fields (IDs) for duplicate updating/exclusion functionality
#TODO 4) EXCLUDE PASSWORD WHEN YOU GET TO LATER STAGE! DEFINITELY BEFORE YOU MAKE REPO PUBLIC!!

# Load data from CSV
file_location = "/home/ubuntu/Stick-Shift/Web_Scraping/recent_gas_prices.csv"
df = sqlContext.read.format("CSV").option("inferSchema", True).option("header", True).load(file_location)
df.show()

df.write.format("jdbc").options(
    url="jdbc:postgresql://ec2-18-206-181-71.compute-1.amazonaws.com:5432/fuel_consumption",
    dbtable="gas_prices",
    driver="org.postgresql.Driver",
    user = "postgres",
    password="postgres",
    mode = "append").save()
