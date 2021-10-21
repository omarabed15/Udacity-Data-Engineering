import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    '''Load staging tables in AWS Redshift from JSON log files.'''
    
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    '''Calls queries to insert table data.'''
    
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    '''Loads staging tables in AWS Reshift, then inserts data from the staging tables into the star schema tables.'''

    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()