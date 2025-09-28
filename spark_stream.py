from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, avg, min as spark_min, max as spark_max, sum as spark_sum, window
from pyspark.sql.types import StructType, StringType, DoubleType, LongType

# Initialize Spark
spark = SparkSession.builder \
    .appName("crypto-stream") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "2") \
    .config("spark.jars", "postgresql.jar") \
    .getOrCreate()

# Define schema
schema = StructType() \
    .add("symbol", StringType()) \
    .add("price", DoubleType()) \
    .add("volume", DoubleType()) \
    .add("ts", LongType())

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "crypto.ticks") \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON
json_df = df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("event_time", to_timestamp((col("ts")/1000).cast("double")))

# --- Write raw stream to Parquet ---
parquet_query = json_df.writeStream \
    .format("parquet") \
    .option("path", "./data/parquet/crypto") \
    .option("checkpointLocation", "./data/checkpoints/crypto") \
    .trigger(processingTime="30 seconds") \
    .start()

# --- Aggregation (minute OHLC) with watermark ---
agg = json_df.withWatermark("event_time", "2 minutes") \
    .groupBy(
        window(col("event_time"), "1 minute"),
        col("symbol")
    ).agg(
        spark_min("price").alias("min_price"),
        spark_max("price").alias("max_price"),
        avg("price").alias("avg_price"),
        spark_sum("volume").alias("sum_volume")
    )

# Write to Postgres
def write_to_postgres(batch_df, batch_id):
    batch_df \
        .withColumn("start_time", col("window.start")) \
        .withColumn("end_time", col("window.end")) \
        .select("symbol", "start_time", "end_time", "min_price", "max_price", "avg_price", "sum_volume") \
        .write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://localhost:5433/crypto") \
        .option("dbtable", "public.minute_ohlc") \
        .option("user", "dev") \
        .option("password", "example") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

# Start streaming
agg.writeStream.foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .start()

spark.streams.awaitAnyTermination()
