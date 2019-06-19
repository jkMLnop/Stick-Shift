import findspark
#findspark.init('/usr/local/spark')

from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext

#conf = SparkConf().setAppName("building a fuel price data warehouse")
sc = SparkContext('local','building a fuel price data warehouse')#conf=conf)
sqlContext = SQLContext(sc)

# Load data from CSV
file_location = "/Desktop/Web_Scraping/Scraping_Backups/recent_listings.csv"
df = sqlContext.read.format("CSV").option("inferSchema", True).option("header", True).load(file_location)
display(df.take(5))
