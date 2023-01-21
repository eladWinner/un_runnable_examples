if __name__ == '__main__':
	import os
	import findspark
	from pyspark.sql import SparkSession

	def init_spark(app_name: str):
 	  spark = SparkSession.builder.appName(app_name).getOrCreate()
	  sc = spark.sparkContext
	  return spark, sc

	spark, sc = init_spark('demo')
	data_file = './data_HW1.csv'
	curtains_rdd = sc.textFile(data_file)
	csv_rdd = curtains_rdd.map(lambda row: row.split(','))
	header = csv_rdd.first()
	data_rdd = csv_rdd.filter(lambda row: row != header)
	tdata= data_rdd.map( lambda row : ((row[0].split(' ')[0] ,row[2],row[3]),(float(row[1]),1)))\
	  .reduceByKey(lambda a,b: (a[0] + b[0], a[1] + b[1]))\
	    .map(lambda row: ((row[0][0].split('/')[1],row[0][1]),round(row[1][0]/row[1][1],3)))\
	      .reduceByKey(lambda a,b: min(a,b)).filter(lambda row: row[1]>=0.05)\
	        .map(lambda row :(row[0][0],[row[0][1]]) ).reduceByKey(lambda a,b: a+b)
	ll=tdata.collect()
	ll.sort()
	for row in ll:
	  print(str(row[0])+":"+str(row[1]))