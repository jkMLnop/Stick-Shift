from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext

#conf = SparkConf().setAppName("building a fuel price data warehouse")
sc = SparkContext('local','building a fuel price data warehouse')#conf=conf)
sqlContext = SQLContext(sc)

# Load data from CSV
file_location = "/home/ubuntu/Stick-Shift/Web_Scraping/recent_listings.csv"
df = sqlContext.read.format("CSV").option("inferSchema", True).option("header", True).load(file_location)
df.show()

df.write.format("jdbc").options( 
    url="jdbc:postgresql://ec2-18-206-181-71.compute-1.amazonaws.com:5432/fuel_consumption", 
    dbtable="car_listings", 
    driver="org.postgresql.Driver", 
    user = "postgres", 
    password="postgres", 
    mode = "append").save()







