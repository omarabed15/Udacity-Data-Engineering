# Project Write-up: Data Modeling with Postgres

## How to Run

The project can be run by executing the following commands:
- `%run create_tables.py`
- `%run etl.py`

These files can be run manually, and independently, from the Python runner, or they can be run from the `Python3Runner.ipynb` file in this notebook.

To test the successful execution of this ETL pipeline, you can use `test.ipynb`. Run this file through the notebook runner or through the command line.

## Explanation of Files

This section explains the purpose of each file.

- `sql_queries.py`
  This file defines the table create, delete, and insert operations.

- `create_tables.py`
  This file calls the table create SQL functions in `sql_queries.py` to create and delete the database tables.

- `etl.ipynb`
  This notebook file tests various database commands on single files from the dataset to ensure expected behavior of the SQL statements being developed, before they are incorporated into the `etl.py` file to operate on the full data source.

- `etl.py`
  This file executes the SQL commands developed in `etl.ipynb` on the entire dataset. It processes the song and log source data files and inserts their data into the new database.

- `test.ipynb`
  This file executes SQL queries on each table with limits applied to ensure proper operation of the CREATE and INSERT statements from the previous files.

- `Python3Runner.ipynb`
  This notebook file combines the `create_tables.py` and `etl.py` pipelines to facilitate restarting the entire project and executing it on the source dataset.


## Database Purpose in Sparkify Context

The purpose of the database is to determine listening patterns by users for various artists, albums, and songs. Sparkify is interested in knowing what songs users are listening to, but with the data stored in separate JSON files, there isn't an easy way to aggregate and analyze the data collectively. By transferring the individual data into a shared database, it can be queried together as a collective unit to determine trends.

## Database Schema Design and ETL Pipeline

The focus of the data anlysis is to detect trends in songs and artist listens, rather than trends in an individual user's listening patterns. That is why the database schema is designed as it is, with song id, artist id, and start time together. The specifics of the song (such as duration, title, and year) are not needed to determine the patterns of users listening to the song. If additional information is needed from the song or artist, those dimension tables can be joined with the songplays fact table to gather that info.

The ETL Pipeline first focuses on transferring the data from log files into the individual dimension tables. That way, it gets easier to manipulate the data. The song data from the `song_data` JSON files can be self-contained in the `songs` and `artists` tables. The log data is focused on user actions, and can be split into the `users` and `time` tables. The convenience of all the song/artist/user ids in the `songplays` table requires references from several tables, so it is created after the individual tables are created. Creating the `songplays` table is a bit more complex, but since it will only be created once, it is worth the time investment to create that as the fact table, since it will be queried more often than it will be written from the log files (i.e. once), it makes the most sense to invest in the time creation of that table at front, and then benefit from that data organization thereafter.

## Example Queries and Results for Song Play Analysis

Here are two examples of queries you could run on this database:

### 1. What was the most popular song on a given date?

QUERY:
`SELECT song_id, COUNT(*) FROM songplays WHERE start_time > '2018-11-30' AND start_time < '2018-12-01' GROUP BY song_id;`

This query shows the song id, and the count of times that it shows up in the results for the specified time frame (which is our measure of "popularity"). The `WHERE / AND` clause here are just sample dates. We group by song because we want to aggregate the data for songs across users.

This result isn't truly indicative because the dataset does not have the song_ids and artist_ids matching cleanly with the other log files, so there are no results regarding this listening behavior.

### 2. Do artists from certain areas have longer or shorter song durations?

QUERY:
`SELECT artists.location as artist_location, AVG(songs.duration) FROM songs JOIN artists ON songs.artist_id = artists.artist_id GROUP BY artists.location ORDER BY AVG(songs.duration) DESC;`

This query groups artists by their location to determine if song length varies significantly by location. We calculate the average duration of all an artists songs, and match that with the artist's location. We must join two tables here, because one holds the song duration info, and the other holds the artist location info.

Based on this query, artists from Toronto, Ontario, Canada had the longest songs (491 seconds), while artists from New York had the shortest (43 seconds).

### 3. Verify a single entry in the `songplays` table

QUERY:
`SELECT * FROM songplays WHERE song_id is NOT NULL and artist_id is NOT NULL LIMIT 5;`

This query has been included at the bottom of `test.ipynb` for convenience.

As instructed by the course advisor, the query above should only generate a single row result. This has been tested and validated. The resulting row is:

| songplay_id | start_time | user_id | level | song_id | artist_id | session_id | location | user_agent |
| ---------- | ---------- | ------- | ----- | ------- | --------- | ---------- | -------- | ---------- |
| 4108 | 2018-11-21 21:56:47.796000 | 15 | paid | SOZCTXZ12AB0182364 | AR5KOSW1187FB35FF4 | 818 | Chicago-Naperville-Elgin, IL-IN-WI | "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/36.0.1985.125 Chrome/36.0.1985.125 Safari/537.36"