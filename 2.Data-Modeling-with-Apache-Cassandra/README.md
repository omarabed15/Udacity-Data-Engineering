# Project Write-up: Data Modeling with Apache Cassandra

## How to Run

The project can be run by selecting `Restart kernel and run all` from the `Run` menu within Jupyter notebook while having the `Project_1B_Project_Template.ipynb` file active.

## Explanation of Files

This section explains the purpose of each file.

- `event_datafile_new.csv`
  This file is generated from the log files in the event_data folder, and includes a combination of all row entries across all log files.

- `Project_1B_Project_Template.ipynb`
  This file contains all Apache Cassandra statements and is used to connect to the database instance, create tables, answer each query with SELECT statements, and more.

## Database Purpose in Sparkify Context

The purpose of the database is to populate tables from the log entries to ensure fast querying of various song metrics. The tables duplicate some data, and are designed to respond to specific queries efficiently. Sparkify is interested in knowing what songs users are listening to, but with the data stored in separate JSON files, there isn't an easy way to aggregate and analyze the data collectively. By transferring the individual data into a shared database, it can be queried together as a collective unit to determine trends.

## Table Queries and Results for Song Play Analysis

### 1. Query 1:  Give me the artist, song title and song's length in the music app history that was heard during \
## sessionId = 338, and itemInSession = 4

Primary Key: sessionId, itemInSession
Partition Key: sessionId
Clustering Column: itemInSession

#### Results
Artist: Faithless
Song: Music Matters (Mark Knight Dub)
Length: 495.3073

#### Summary
The sessionId and itemInSession are used as the primary key together because they are not unique on their own. The sessionId is a good way to segment the data into semi-equal chunks, which is why it is used as the partition key.

### 2. Query 2: Give me only the following: name of artist, song (sorted by itemInSession) and user (first and last name)\
## for userid = 10, sessionid = 182

Primary Key: userId, sessionId, itemInSession
Partition Key: userId, sessionId
Clustering Column: itemInSession

#### Results
Down To The Bone Keep On Keepin' On Sylvie Cruz
Three Drives Greece 2000 Sylvie Cruz
Sebastien Tellier Kilometer Sylvie Cruz
Lonnie Gordon Catch You Baby (Steve Pitron & Max Sanna Radio Edit) Sylvie Cruz

#### Summary
The itemInSession is used as a clustering column for ordering the results.
The combination of userId, sessionId, and itemInSession are used as the primary key because they are not unique on their own, but together they are. The userId and sessionId combined are also not unique, but they are a good way to segment the data, which is why they are used as the partition key.
Since the firstname and lastname are not used independently from each other, I combine them into a single field in the table (username).

### 3. Query 3: Give me every user name (first and last) in my music app history who listened to the song 'All Hands Against His Own'

Primary Key: song, userId
Partition Key: song
Clustering Column: userId

#### Results
All Hands Against His Own Jacqueline Lynch
All Hands Against His Own Tegan Levine
All Hands Against His Own Sara Johnson

#### Summary
The song and username are not necessarily unique in the full dataset, so we use the song and userId in case users with the same name are listening to the same song.