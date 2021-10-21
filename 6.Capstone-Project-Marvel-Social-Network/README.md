# The Marvel Comics Social Network
### Data Engineering Capstone Project

#### Project Summary
This project analyzes the relationships between characters in the Marvel comics as a social network. The source data provides insight into how often various characters meet throughout the comics, and in which comics they appear. The goal of this project is to use the source data to make predictions about future appearances of characters in Marvel Cinimatic Universe (MCU) movies based on character "popularity" from the original source comics. In addition, we will seek to derive social conclusions from the character relationships.

The project follows the follow steps:
* Step 1: Scope the Project and Gather Data
* Step 2: Explore and Assess the Data
* Step 3: Define the Data Model
* Step 4: Run ETL to Model the Data
* Step 5: Complete Project Write Up

### Step 1: Scope the Project and Gather Data

#### Scope 
`Explain what you plan to do in the project in more detail. What data do you use? What is your end solution look like? What tools did you use? etc>`

This project analyzes the relationships between characters in the Marvel comics as if they were people in a real social network. The source data provides insight into how often various characters meet throughout the comics, and in which comics they appear. This information could be used to assess which characters are the most "popular", by way of which character makes the most connections and appears in the most comics. Thinking of this in a "social network" context, we could make "People You May Know" recommendations for various characters with common connections (edges). The "People You May Know" output of this data exploration is similar to common functionality offered by other social media platforms, including Facebook, Instagram, LinkedIn, Twitter, and more.
Also, by cross-referencing this information with character appearances in the Marvel Cinimatic Universe (MCU), we may be able to project which characters are most likely to next appear in the upcoming Marvel movies based on character "popularity" in the comics.

#### Describe and Gather Data 
`Describe the data sets you're using. Where did it come from? What type of information is included?`

The source data is located in the `marvel_data` directory. The three main CSV files were sourced from [The Marvel Universe Social Network dataset on Kaggle](https://www.kaggle.com/csanhueza/the-marvel-universe-social-network). These files, along with a description of their contents, follows:
- edges.csv: Indicates which comics that each hero appears in.
- hero-network.csv: Indicates which heroes appear together in the comics.
- nodes.csv: Describes the node types (i.e. either "hero" or "comic").

The final CSV (screentime.csv) was gathered from [an MCU quiz on Sporkle](https://www.sporcle.com/games/wearevenom2/mcu-screen-time-2021). It contains the screentime for each comic book character in the Marvel Cinematic Universe (MCU) movies.

### Step 2: Explore and Assess the Data
#### Explore the Data 
`Identify data quality issues, like missing values, duplicate data, etc.`

1. Hero names don't match up between the "Screentime" table and the other tables, due to them coming from different sources.

2. Hero names in the hero-network.csv source are truncated.

3. Some characters in the "Screentime" table are not present as "Heroes" in the other tables because they are supporting characters, not heroes.

#### Cleaning Steps
`Document steps necessary to clean the data`

1. Here, I provide a map to standardize the hero names in the screentime table to have the names from the other tables, for consistency and cross-referencing the hero names as foreign keys between the tables. I don't include all names for now, to save time, but as time permits, I will finish this mapping.

2. This will require queries using "LIKE%" instead of "=". Also, names don't always align across tables. For instance, the nodes.csv has Spider-man as "SPIDER-MAN/PETER PARKERKER" (typo with "KER" repeated twice at the end), but the edges.csv table has him as "SPIDER-MAN/PETER PARKER" (correct spelling) and the hero-network.csv table has him as "SPIDER-MAN/PETER PAR" (truncated). This will require some tweaking of the data along the way. If results seem unintuitive, I will compare the hero and comic names and correct as I go.

3. This does not require cleanup, but is just additional information. It may result in some NULL values in derived tables, but that is expected. We will have to filter out NULL values in any analyses.


### Step 3: Define the Data Model
#### 3.1 Conceptual Data Model
`Map out the conceptual data model and explain why you chose that model`

The [schema diagram](./schema_diagram.png) illustrates the data model. An asterisk (*) indicates a primary key, and multiple asterisks on a single table indicate a composite primary key.
This data model uses a Star schema with fact and dimension tables.
The "comic_appearances" table is the fact table, as the fact of this data model is which heroes appeared in which comics. The combination of hero and comic is unique in the "comic_appearances" table, so those two fields together form the composite primary key.
The "screentime" table is a dimension of the data model. The hero name is the primary key here, and also the foreign key from the "comic_appearances" table.
The "directed_network" table is a dimension based off the hero_network source CSV. This table may have duplicate entries, and is treated more as a graph source than as a normalized database table. For that reason, there is no primary key.
The "undirected_network" table is derived from the "directed_network" table. However, it is separated into its own table to improve the ability to query the database for valuable information. For instance, in this project, we assume that a hero's "popularity" is dependent on their interactions with others, but not on the direction of those interactions. By transforming the hero_network source CSV into both a directed and undirected network table, we preserve the data integrity of the source data in the directed_network table while improving the time to perform common queries from the undirected_network table. Going forward in our use of this database, we would need to insert hero interactions into each table. This improvement to querying the database would come at the expense of some database write performance, but this is a tradeoff we're willing to make, based on the assumption that we will be drawing analytics about character relationships much more often than we will be writing new interactions to the database.


#### 3.2 Mapping Out Data Pipelines
`List the steps necessary to pipeline the data into the chosen data model`

First, the edges.csv should be read into the "comic_appearances" table.

Next, the screentime.csv should be read into a "screentime" table. I choose to rename the column labels on this table to remove spaces and standardize the language. I also chose to parse the initial time string from "mm:ss" format into just "ss" format, to facilitate numeric operations on the duration. This requires parsing the time by splitting the string on the ":", multiplying the "mm" portion by 60, and adding that to the "ss" value.

Then, the hero-network.csv should be read into the "directed_hero_network" table.

Finally, the "hero_network" dataframe must be parsed to generate the "undirected_hero_network" table. This step includes:
1. Standardize the order of the hero relationships. i.e. Remove the "directed" nature of the network.
This step will require comparing hero1 and hero2 alphabetically and putting the alphabetically-first hero in the hero1 column and and the second hero in the hero2 column. This will standardize entries such as "A -> B" and "B -> A" to both be "A -> B". This will remove the directed nature of the network in the table.
2. Removing duplicates
Once each relationship is stored in alphabetical order, we can aggregate by each hero1-hero2 pair and add a "sum" column to count how many times each interaction occurred. This essentially removes duplicates, while maintaining the magnitude of interactions in the "sum" column. This table can then be more easily queried for network relationships.

### Step 4: Run Pipelines to Model the Data 
#### 4.1 Create the data model
`Build the data pipelines to create the data model.`

This step is done with Apache Spark dataframe operations in Python in the .ipynb file. The .ipynb file contains the entirety of the data operations, and can be opened with a Jupyter notebook.

#### 4.2 Data Quality Checks
```
Explain and run the data quality checks you'll perform to ensure the pipeline ran as expected. These could include:
 * Integrity constraints on the relational database (e.g., unique key, data type, etc.)
 * Unit tests for the scripts to ensure they are doing the right thing
 * Source/Count checks to ensure completeness
```

##### 4.2.1. Integrity constraints:
First, I check the screentime table for the datatype of the duration column. I do this because the "screentime" is initially stored as a string in the source data, so this check allows me to validate my "duration_to_seconds" udf transformer to some degree.

Next, I join the screentime table with the undirected network table to validate that I get expected NULL duration results for a hero who has not yet appeared in MCU movies (i.e. screentime duration = NULL) but who do have undirected hero network interactions. At the same time, I validate that I get non-NULL duration results for a hero who I know to have appeared in MCU movies.

These results reveal something interesting. Iron Man has the most screentime duration according to the screentime table, but does not appear at the top of the joined table, even when we sort by duration descending. This reveals the data error that Iron Man is stored under different names in the two tables. On closer inspection, the name has a space (' ') character at the end in the undirected_hero_network table. This error in the source data would have to be corrected upstream, prior to loading the dataframe data into the SQL tables.

##### 4.2.2. Unit test scripts:
I perform simple unit tests for the map_names and duration_to_seconds udf transformer functions outside of a dataframe and with known values, to validate their operation.
For completeness, I use the previous test function to perform a search in the screentime table on a hero name that was translated from the edges.csv to ensure that the map_names udf function was properly performed.

##### 4.2.3. Soure/Count checks: 
I perform a filter on the directed_hero_network for a hero with both initiating and receiving interactions in the hero-network source. I then perform the same filter in the undirected_hero_network table to ensure that the number of row results in the directed_hero_network table filter matches the "interactions_count" value in the undirected_hero_network table.


#### 4.3 Data dictionary 
`Create a data dictionary for your data model. For each field, provide a brief description of what the data is and where it came from. You can include the data dictionary in the notebook or in a separate file.`

"comic_appearances" table

| Row         | Data Type                    | Description                      | Source      |
| ----------- | ---------------------------- | -------------------------------- | ----------- |
| hero        | string (all caps, truncated) | Hero Name                        | edges.csv   |
| comic       | string (all caps)            | Comic Title (Series and Edition) | edges.csv   |


"screentime" table

| Row         | Data Type | Description                                | Source           |
| ----------- | --------- | ------------------------------------------ | ---------------- |
| hero        | string    | Hero Name                                  | screentime.csv   |
| duration    | int       | Screen time in MCU movies (in seconds)     | screentime.csv   |
| debut_movie | string    | First movie that the character appeared in | screentime.csv   |


"directed_hero_network" table

| Row      | Data Type | Description                     | Source             |
| -------- | --------- | ------------------------------- | ------------------ |
| hero1    | string    | Hero initiating the interaction | hero-network.csv   |
| hero2    | string    | Hero receiving the interaction  | hero-network.csv   |


"undirected_hero_network" table

| Row                | Data Type | Description                                            | Source             |
| ------------------ | --------- | ------------------------------------------------------ | ------------------ |
| first_hero         | string    | One of the heroes in the interation                    | hero-network.csv   |
| second_hero        | string    | One of the heroes in the interation                    | hero-network.csv   |
| interactions_count | int       | Number of recorded interactions between the two heroes | hero-network.csv   |

#### Step 5: Complete Project Write Up
```
* Clearly state the rationale for the choice of tools and technologies for the project.
* Propose how often the data should be updated and why.
* Write a description of how you would approach the problem differently under the following scenarios:
 * The data was increased by 100x.
 * The data populates a dashboard that must be updated on a daily basis by 7am every day.
 * The database needed to be accessed by 100+ people.
```

This project was chosen to explore my interest in Marvel movies in a context with social media applicability. I chose to use Apache Spark for its simplicity in extracting CSV data, transforming it in dataframes, and loading it into SQL tables.

Also, since this project simulates social network functionality, which is an excellent choice for running on a distributed network, Spark is an excellent technology choice, as it can be easily configured to run on a distributed cluster. I ultimately chose not to actually execute this pipeline on an AWS cluster, due to a lack of AWS credits remaining.

The initial data import gets the database up-to-date with the current state of hero relationships in the MCU movies and Marvel comics. Going forward, it would be sufficient to update the data once per day, during low-traffic hours. User relationship data is not more time-sensitive than per day, so it should be enough to have an updated representation of user relationships daily, for making new relationship recommendations and for deriving new analytics.

If the data was increased by 100x, I would partition the data by hero. Individual users have less frequent interactions than a large mass of user. This partioning would support hero-based queries, including relationship recommendations and analytics around hero inclusion in the MCU movies. Partitioning the data helps with storage and organization, but we can also make improvements to processing the data at a larger scale. Spark can process the results in parallel across several cores. While this parallelization can occur locally, it is more beneficial to execute these queries, analytics, and processes on a remote, distributed cluster optimized for this purpose. I would likely execute analytics on an AWS Redshift cluster on the partitioned data. The cores, memory, and other parameters could be configured and scaled to grow or shrink easily with the data.

If a dashboard needed to be populated daily at 7am, I would use an Airflow pipeline. Airflow pipelines support scheduled tasks, and they could easily perform queries on the past day of new data entries, aggregate them into a larger repository of aggregated data, and report on the developments.

If the data needed to be accessed by 100+ people, I would implement an AWS cloud data warehouse. A distributed database network could be accessed more easily globally. And while this would result in data duplication, it would improve data redundancy for data integrity and backup purposes while improving database read times. I would also implement a caching solution in front of the database at various levels (i.e. server, CDN, etc.) to improve read times.

# Analysis

The initial purpose of this project was to analyze the relationships between heroes in the Marvel movies and comics. The data has several source inconsistencies, primarily with hero names, which make some analysis results a bit skewed, but we are still able to derive general takeaways from the project.

One of the main questions initially was "Who are some of the most prominent/active characters from the comics who have yet to debut in the Marvel movies?". This question can be answered with the query below.

Interestingly, it would seem that "Beast" and "Human Torch" are two of the top candidates for Marvel movie screentime, based on their interactions in the comics. However, it's important to remember that they have both appeared in several other movie franchises already. Beast has been prevalent in X-Men movies, and Human Torch has been in Fantastic Four movies. Thus, this dataset tells the story in regards to the MCU, but may be missing some data if we want to tell a broader picture about general screentime.

These prior two queries depict the difference between a character having a lot of back-and-forth interactions versus having interactions with many different characters. After the first few rows, the results vary widely.

#### Acquaintance Referral Scenario

In a social network, a realistic query analysis may be used to suggest a new relationship to a user. This can be done using the undirected_hero_network table. Assuming we are looking for a recommendation for a certain hero (say, Spider-Man), we can inspect the table to see who they interact with most. We see that that hero is Mary Jane Watson. Then, we can perform a query for Mary Jane Watson's interactions, where we search for the first hero who does not appear to have any interactions with Spider-Man (call them, Person X). We could then refer Person X to Spider-Man as a referral. The logic here is that, if Spider-Man and Mary Jane Watson have many interactions together, perhaps Spider-Man would be interested to know Person X, who also has relatively many interactions with Mary Jane Watson.

The query discussed here can be found in the .ipynb file in this repository's root directory. The .ipynb file contains all the data operations, and can be opened in a Jupyter notebook.

The acquaintance recommendation query is a bit complex, but it's a result of not knowing which of the "hero1" and "hero2" columns will store which hero name. The "SELECT-CASE" statement in each subquery is meant to create a new column with a known hero name to correct for that.

To break down this query: We use a subquery to get a list of acquaintainces to "WATSON-PARKER, MARY" (after querying the undirected_hero_network table for Spider-Man's top acquaintance, and getting that it is "WATSON-PARKER, MARY"). We also execute the same query to get the Spider-man filtered version of the undirected_hero_network table with the acquaintance name in a predetermined column. We then filter for instances where Spider-Man has no interactions (i.e. NULL) where "WATSON-PARKER, MARY" does have interactions with the acquaintance. Finally, we sort in descending order by "WATSON-PARKER, MARY"'s interactions, and filter out Spider-Man's entry as well (since he can't be his own acquaintance). This leaves us with a short list of two characters whom "WATSON-PARKER, MARY" interacted with and who Spider-Man did not. "WATSON-PARKER, MARY" has very few interactions with these characters (just one each), but if we were to make a recommendation to Spider-Man for a new acquaintance based on his strong relationship with "WATSON-PARKER, MARY", we would recommend them.

Due to the low level of interactions depicted in this example between "WATSON-PARKER, MARY" and the recommended characters, I added several parameters to the recommendation function.

First, I added an optional minimum threshold to acquaintance recommendations. If the secondary hero does not surpass that level of interaction with the "recommended" characters, then they won't be recommended. I also added an optional limit for an upper limit of how many recommendations to return.

### Summary

These examples demonstrate how the source dataset can be used to provide valuable insights into a social networking application. While it is assumed that a graph, rather than a relational database, is a better representation of nodes in a social network, this example utilizes the tools we've learned in this course with a real-world scenario.