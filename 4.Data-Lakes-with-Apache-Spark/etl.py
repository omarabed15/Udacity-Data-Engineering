import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS']['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    """
    Creates a Spark session.
    """
    
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """
    Extracts data from song JSON files.
    Processes the data into songs and artists tables.
    Writes the generated data tables to an output destination.
    """
        
    # get filepath to song data file
    song_data = input_data + "song_data/*/*/*/*.json"
    
    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    df.createOrReplaceTempView("songs")
    songs_table = spark.sql("""
                    SELECT
                        song_id,
                        title,
                        artist_id,
                        year,
                        duration
                    FROM songs
                    WHERE song_id IS NOT NULL
                """)
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.mode('overwrite').partitionBy("year", "artist_id").parquet(output_data + 'songs/')

    # extract columns to create artists table
    artists_table = spark.sql("""
                        SELECT
                            DISTINCT artist_id, 
                            artist_name name,
                            artist_location location,
                            artist_latitude latitude,
                            artist_longitude longitude
                        FROM songs
                        WHERE artist_id IS NOT NULL
                    """)

    
    # write artists table to parquet files
    artists_table.write.mode('overwrite').parquet(output_data + 'artists/')


def process_log_data(spark, input_data, output_data):
    """
    Extracts data from log JSON files.
    Processes the data into user, time, and songplays tables.
    Writes the generated data tables to an output destination.
    """

    # get filepath to log data file
    log_data = input_data + "log_data/*/*/*.json"

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df = df.filter(df.page == 'NextSong')
    
    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x: x/1000)
    df = df.withColumn('timestamp', get_timestamp(df.ts))
    
    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: datetime.fromtimestamp(x))
    df = df.withColumn("datetime", get_datetime(df.timestamp))

    # extract columns for users table    
    df.createOrReplaceTempView("logs") 
    users_table = spark.sql("""
                    SELECT
                        DISTINCT userId user_id, 
                        firstName first_name,
                        lastName last_name,
                        gender,
                        level
                    FROM logs
                    WHERE userId IS NOT NULL
                """)
    
    # write users table to parquet files
    users_table.write.mode('overwrite').parquet(output_data + 'users/')
    
    # extract columns to create time table
    time_table = spark.sql("""
                    SELECT
                        DISTINCT timestamp,
                        hour(timestamp) hour,
                        dayofmonth(datetime) day,
                        weekofyear(datetime) week,
                        month(datetime) month,
                        year(datetime) year,
                        dayofweek(datetime) weekday
                    FROM logs
                    WHERE ts IS NOT NULL
                """)
    
    # write time table to parquet files partitioned by year and month
    time_table.write.mode('overwrite').partitionBy("year", "month").parquet(output_data + 'time/')

    # read in song data to use for songplays table
    song_df = spark.read.json(input_data + "song_data/*/*/*/*.json")

    # extract columns from joined song and log datasets to create songplays table
    song_df.createOrReplaceTempView("songs")
    songplays_table = spark.sql("""
                    SELECT
                        timestamp start_time,
                        year(datetime) year,
                        month(datetime) month,
                        logs.userId user_id,
                        logs.level level,
                        songs.song_id song_id,
                        songs.artist_id artist_id,
                        logs.sessionId session_id,
                        logs.location location,
                        logs.userAgent user_agent
                    FROM logs
                    LEFT JOIN songs ON logs.artist = songs.artist_name AND logs.song = songs.title
                    WHERE logs.page = "NextSong"
                """)
    
    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.mode('overwrite').partitionBy("year", "month").parquet(output_data + 'songplays/')


def main():
    """
    Creates Spark session.
    Extracts data from song and log files.
    Processes the extracted data.
    Moves processed data to output destination.
    """

    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "s3a://udacity-dend/oabed_etl_out/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
