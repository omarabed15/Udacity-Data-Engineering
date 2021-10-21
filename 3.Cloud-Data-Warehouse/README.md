# Project Write-up: Data Warehouse

## How to Run

The project can be run by executing the following commands:
- `python3 create_tables.py`
- `python3 etl.py`

## Explanation of Files

This section explains the purpose of each file.

- `sql_queries.py`
  This file defines the table create, drop, and insert operations.

- `create_tables.py`
  This file calls the create table and drop table SQL functions in `sql_queries.py` to create and delete the database tables.

- `etl.py`
  This file performs the AWS Redshift operations to load the staging tables and insert data from the staging tables to the star schema tables.

- `dwh.cfg`
  This file stores the credentials for the AWS Redshift instance.


## Database Purpose in Sparkify Context

The purpose of the database is to determine listening patterns by users for various artists, albums, and songs. Sparkify is interested in knowing what songs users are listening to, but with the data stored in separate JSON files, there isn't an easy way to aggregate and analyze the data collectively. By transferring the individual data into a shared database, it can be queried together as a collective unit to determine trends.

## Database Schema Design and ETL Pipeline

The AWS Redshift database star-schema design can be seen [here](https://udacity-reviews-uploads.s3.us-west-2.amazonaws.com/_attachments/38715/1584109948/Song_ERD.png).

The focus of the data anlysis is to detect trends in songs and artist listens, rather than trends in an individual user's listening patterns. That is why the database schema is designed as it is, with song id, artist id, and start time together. The specifics of the song (such as duration, title, and year) are not needed to determine the patterns of users listening to the song. If additional information is needed from the song or artist, those dimension tables can be joined with the songplays fact table to gather that info.

The ETL Pipeline first focuses on transferring the data from log files into the AWS Redshift staging tables. From there, the data is extracted from the staging tables into the individual star schema tables in AWS Redshift. That way, it gets easier to manipulate the data as desired from compartmentalized tables. The song data from the `song_data` JSON files can be self-contained in the `songs` and `artists` tables. The log data is focused on user actions, and can be split into the `users` and `time` tables. The convenience of all the song/artist/user ids in the `songplays` table requires references from several tables, so it is created after the individual tables are created. Creating the `songplays` table is a bit more complex, but since it will only be created once, it is worth the time investment to create that as the fact table, since it will be queried more often than it will be written from the log files (i.e. once), it makes the most sense to invest in the time creation of that table at front, and then benefit from that data organization thereafter.

## [Optional] Example Queries and Results for Song Play Analysis

Here are two examples of queries you could run on this database:

### 1. What was the most popular song on a given date?

QUERY:
`SELECT song_id, COUNT(*) FROM songplay WHERE start_time > '2018-11-30' AND start_time < '2018-12-01' GROUP BY song_id;`

This query shows the song id, and the count of times that it shows up in the results for the specified time frame (which is our measure of "popularity"). The `WHERE / AND` clause here are just sample dates. We group by song because we want to aggregate the data for songs across users.

This result isn't truly indicative because the dataset does not have the song_ids and artist_ids matching cleanly with the other log files, so there are no results regarding this listening behavior.

### 2. Do artists from certain areas have longer or shorter song durations?

QUERY:
`SELECT artist.location as artist_location, AVG(song.duration) FROM song JOIN artist ON song.artist_id = artist.artist_id GROUP BY artist.location ORDER BY AVG(song.duration) DESC;`

This query groups artists by their location to determine if song length varies significantly by location. We calculate the average duration of all an artists songs, and match that with the artist's location. We must join two tables here, because one holds the song duration info, and the other holds the artist location info.

Based on this query, artists from Anoka, MN had the longest songs (1491 seconds), while artists from Putney, England had the shortest (31 seconds).