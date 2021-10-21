import configparser
import datetime as dt


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs;"
songplay_table_drop = "DROP TABLE IF EXISTS songplay;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS song;"
artist_table_drop = "DROP TABLE IF EXISTS artist;"
time_table_drop = "DROP TABLE IF EXISTS time;"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events (
    id int IDENTITY(0,1) PRIMARY KEY,
    artist varchar(max),
    auth varchar(max),
    firstName varchar(max),
    gender char(1),
    itemInSession int,
    lastName varchar(max),
    length float,
    level varchar(max),
    location varchar(max),
    method varchar(max),
    page varchar(max),
    registration float,
    sessionId int,
    song varchar(max),
    status int,
    ts timestamp,
    userAgent varchar(max),
    userId int
);
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs (
    id int IDENTITY(0,1) PRIMARY KEY,
    num_songs int,
    artist_id varchar(max),
    artist_latitude float,
    artist_longitude float,
    artist_location varchar(max),
    artist_name varchar(max),
    song_id varchar(max),
    title varchar(max),
    duration float,
    year int
);
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplay (
    songplay_id int IDENTITY(0,1) PRIMARY KEY,
    start_time timestamp,
    user_id int,
    level varchar(max),
    song_id varchar(max),
    artist_id varchar(max),
    session_id int,
    location varchar(max),
    user_agent varchar(max),
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(song_id) REFERENCES song(song_id),
    FOREIGN KEY(artist_id) REFERENCES artist(artist_id),
    FOREIGN KEY(start_time) REFERENCES time(start_time)
);
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users (
    user_id int IDENTITY(0,1) PRIMARY KEY,
    first_name varchar(max),
    last_name varchar(max),
    gender char(1),
    level varchar(max)
);
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS song (
    song_id varchar(max) PRIMARY KEY,
    title varchar(max),
    artist_id varchar(max),
    year int,
    duration float,
    FOREIGN KEY(artist_id) REFERENCES artist(artist_id)
);
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artist (
    artist_id varchar(max) PRIMARY KEY,
    name varchar(max),
    location varchar(max),
    latitude float,
    longitude float
);
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time (
    start_time timestamp PRIMARY KEY,
    hour int NOT NULL,
    day int NOT NULL,
    week int,
    month int NOT NULL,
    year int NOT NULL,
    weekday int
);
""")

# STAGING TABLES

LOG_DATA_DIR = config.get("S3","LOG_DATA")
SONG_DATA_DIR = config.get("S3","SONG_DATA")
ARN = config.get("IAM_ROLE", "ARN")

staging_events_copy = ("""
    copy staging_events from {} 
    credentials 'aws_iam_role={}'
    json 'auto'
    timeformat 'epochmillisecs'
    region 'us-west-2';
""").format(LOG_DATA_DIR, ARN)

staging_songs_copy = ("""
    copy staging_songs from {}
    credentials 'aws_iam_role={}'
    json 'auto'
    timeformat 'epochmillisecs'
    region 'us-west-2';
""").format(SONG_DATA_DIR, ARN)

# FINAL TABLES

songplay_table_insert = ("""
    INSERT INTO songplay (
        start_time, user_id, level, song_id, artist_id, session_id, location, user_agent
    )
    SELECT DISTINCT se.ts, se.userId, se.level, ss.song_id, ss.artist_id, se.sessionId, se.location, se.userAgent
    FROM staging_events se
    LEFT JOIN staging_songs ss ON se.artist = ss.artist_name AND se.song = ss.title
    WHERE se.page = "NextSong"
""")

user_table_insert = ("""
    INSERT INTO users (first_name, last_name, gender, level)
    SELECT DISTINCT firstName, lastName, gender, level
    FROM staging_events
    WHERE page = "NextSong"
""")

song_table_insert = ("""
    INSERT INTO song (song_id, title, artist_id, year, duration)
    SELECT DISTINCT song_id, title, artist_id, year, duration
    FROM staging_songs
""")

artist_table_insert = ("""
    INSERT INTO artist (artist_id, name, location, latitude, longitude)
    SELECT DISTINCT artist_id, artist_name, artist_location, artist_latitude, artist_longitude
    FROM staging_songs
""")

time_table_insert = ("""
    INSERT INTO time (start_time, hour, day, week, month, year, weekday)
    SELECT DISTINCT start_time, EXTRACT(hr FROM start_time), EXTRACT(dy FROM start_time), EXTRACT(w FROM start_time), EXTRACT(mon FROM start_time), EXTRACT(yr FROM start_time), EXTRACT(weekday FROM start_time)
    FROM songplay
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, artist_table_create, user_table_create, song_table_create, time_table_create, songplay_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
